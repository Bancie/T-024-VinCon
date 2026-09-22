#!/usr/bin/env python3
"""Delete all shapes and tags on one frame of a local CVAT job. Tracks are left intact."""

from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse

import requests
from dotenv import load_dotenv

TOOL_DIR = Path(__file__).resolve().parent
DEFAULT_HOST = "http://localhost:8080"
TIMEOUT = 60
JOB_PATH_RE = re.compile(r"/jobs/(\d+)(?:/|$)")


class ToolError(Exception):
    """User-facing error; printed without a traceback."""


def load_env() -> None:
    load_dotenv(TOOL_DIR / ".env")


def normalize_host(host: str) -> str:
    return host.rstrip("/")


def parse_job_url(url: str) -> tuple[int | None, int | None, str | None]:
    parsed = urlparse(url)
    host = None
    if parsed.scheme and parsed.netloc:
        host = f"{parsed.scheme}://{parsed.netloc}"
    match = JOB_PATH_RE.search(parsed.path)
    job_id = int(match.group(1)) if match else None
    query = parse_qs(parsed.query)
    frame = int(query["frame"][0]) if query.get("frame") else None
    return job_id, frame, host


def resolve_abs_frame(user_frame: int, start_frame: int, stop_frame: int) -> int:
    if start_frame <= user_frame <= stop_frame:
        return user_frame
    span = stop_frame - start_frame
    if 0 <= user_frame <= span:
        return start_frame + user_frame
    raise ToolError(
        f"Frame {user_frame} không nằm trong job "
        f"(start_frame={start_frame}, stop_frame={stop_frame}; "
        f"job-relative 0..{span})."
    )


def job_frame_range(job: dict[str, Any], meta: dict[str, Any] | None) -> tuple[int, int]:
    start = job.get("start_frame")
    stop = job.get("stop_frame")
    if start is None or stop is None:
        segment = job.get("segment") or {}
        start = segment.get("start_frame", segment.get("start"))
        stop = segment.get("stop_frame", segment.get("stop"))
    if (start is None or stop is None) and meta:
        start = meta.get("start_frame", start)
        stop = meta.get("stop_frame", stop)
    if start is None or stop is None:
        raise ToolError(
            "Job không có start_frame/stop_frame. Không map được frame, dừng lại."
        )
    return int(start), int(stop)


def api_error_text(exc: requests.HTTPError) -> str:
    resp = exc.response
    if resp is None:
        return str(exc)
    try:
        body = resp.json()
        detail = body.get("detail") or body.get("message") or body
        return f"HTTP {resp.status_code}: {detail}"
    except ValueError:
        text = (resp.text or "").strip()
        return f"HTTP {resp.status_code}: {text[:500] or resp.reason}"


def login(session: requests.Session, host: str, username: str, password: str) -> None:
    try:
        session.get(f"{host}/api/server/about", timeout=TIMEOUT)
    except requests.RequestException as exc:
        raise ToolError(f"Không kết nối được CVAT tại {host}: {exc}") from exc

    csrf = session.cookies.get("csrftoken") or session.cookies.get("csrf")
    headers: dict[str, str] = {}
    if csrf:
        headers["X-CSRFTOKEN"] = csrf
        headers["Referer"] = f"{host}/"

    try:
        resp = session.post(
            f"{host}/api/auth/login",
            json={"username": username, "password": password},
            headers=headers,
            timeout=TIMEOUT,
        )
        resp.raise_for_status()
    except requests.HTTPError as exc:
        raise ToolError(f"Đăng nhập CVAT thất bại. {api_error_text(exc)}") from exc
    except requests.RequestException as exc:
        raise ToolError(f"Đăng nhập CVAT thất bại: {exc}") from exc

    try:
        data = resp.json()
    except ValueError as exc:
        raise ToolError("Đăng nhập CVAT không trả JSON token.") from exc

    key = data.get("key")
    if not key:
        raise ToolError("Đăng nhập CVAT không trả token (`key`).")
    session.headers["Authorization"] = f"Token {key}"


def get_json(session: requests.Session, url: str) -> Any:
    try:
        resp = session.get(url, timeout=TIMEOUT)
        resp.raise_for_status()
        return resp.json()
    except requests.HTTPError as exc:
        raise ToolError(f"GET {url} thất bại. {api_error_text(exc)}") from exc
    except requests.RequestException as exc:
        raise ToolError(f"GET {url} thất bại: {exc}") from exc


def objects_on_frame(
    annotations: dict[str, Any], abs_frame: int
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    shapes = [
        item
        for item in annotations.get("shapes") or []
        if item.get("id") is not None and item.get("frame") == abs_frame
    ]
    tags = [
        item
        for item in annotations.get("tags") or []
        if item.get("id") is not None and item.get("frame") == abs_frame
    ]
    return shapes, tags


def summarize(items: list[dict[str, Any]], kind: str) -> None:
    if not items:
        print(f"  {kind}: 0")
        return
    print(f"  {kind}: {len(items)}")
    for item in items:
        extra = item.get("type") or ""
        label = item.get("label_id")
        bits = [f"id={item['id']}"]
        if extra:
            bits.append(f"type={extra}")
        if label is not None:
            bits.append(f"label_id={label}")
        print(f"    - {', '.join(bits)}")


def confirm_delete(n_shapes: int, n_tags: int) -> bool:
    prompt = (
        f"Xoá {n_shapes} shape và {n_tags} tag trên frame này? Gõ yes để xác nhận: "
    )
    try:
        answer = input(prompt)
    except EOFError:
        return False
    return answer.strip().lower() == "yes"


def delete_objects(
    session: requests.Session,
    host: str,
    job_id: int,
    shapes: list[dict[str, Any]],
    tags: list[dict[str, Any]],
) -> None:
    payload: dict[str, Any] = {}
    if shapes:
        payload["shapes"] = [{"id": item["id"]} for item in shapes]
    if tags:
        payload["tags"] = [{"id": item["id"]} for item in tags]
    url = f"{host}/api/jobs/{job_id}/annotations"
    try:
        resp = session.patch(
            url,
            params={"action": "delete"},
            json=payload,
            timeout=TIMEOUT,
        )
        resp.raise_for_status()
    except requests.HTTPError as exc:
        raise ToolError(f"PATCH xoá annotation thất bại. {api_error_text(exc)}") from exc
    except requests.RequestException as exc:
        raise ToolError(f"PATCH xoá annotation thất bại: {exc}") from exc


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Xoá toàn bộ shape và tag trên một frame của job CVAT local. "
            "Không đụng track."
        )
    )
    parser.add_argument("--job", type=int, help="Job ID")
    parser.add_argument(
        "--frame",
        type=int,
        help="Số frame trên URL ?frame= (hoặc index 0 = ảnh đầu job)",
    )
    parser.add_argument(
        "--url",
        help="URL job CVAT, ví dụ http://localhost:8080/tasks/142/jobs/1420?frame=25",
    )
    parser.add_argument(
        "--host",
        help="CVAT host (mặc định CVAT_HOST hoặc http://localhost:8080)",
    )
    parser.add_argument(
        "--username",
        help="Username (mặc định CVAT_USERNAME)",
    )
    parser.add_argument(
        "--password",
        help="Password (mặc định CVAT_PASSWORD)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Chỉ in danh sách sẽ xoá, không PATCH",
    )
    parser.add_argument(
        "--yes",
        action="store_true",
        help="Không hỏi xác nhận",
    )
    return parser.parse_args(argv)


def resolve_inputs(args: argparse.Namespace) -> tuple[str, int, int]:
    job_id = args.job
    frame = args.frame
    host = args.host or os.environ.get("CVAT_HOST") or DEFAULT_HOST

    if args.url:
        url_job, url_frame, url_host = parse_job_url(args.url)
        if job_id is None:
            job_id = url_job
        if frame is None:
            frame = url_frame
        if not args.host and not os.environ.get("CVAT_HOST") and url_host:
            host = url_host

    if job_id is None:
        raise ToolError("Thiếu job ID. Dùng --job hoặc --url .../jobs/<id>.")
    if frame is None:
        raise ToolError("Thiếu frame. Dùng --frame hoặc --url với ?frame=.")
    return normalize_host(host), job_id, frame


def run(argv: list[str] | None = None) -> int:
    load_env()
    args = parse_args(argv)
    host, job_id, user_frame = resolve_inputs(args)

    username = args.username or os.environ.get("CVAT_USERNAME")
    password = args.password or os.environ.get("CVAT_PASSWORD")
    if not username or not password:
        raise ToolError(
            "Thiếu CVAT_USERNAME / CVAT_PASSWORD. Copy .env.example thành .env rồi điền."
        )

    session = requests.Session()
    login(session, host, username, password)

    job = get_json(session, f"{host}/api/jobs/{job_id}")
    try:
        meta = get_json(session, f"{host}/api/jobs/{job_id}/data/meta")
    except ToolError:
        meta = None
    start_frame, stop_frame = job_frame_range(job, meta)
    abs_frame = resolve_abs_frame(user_frame, start_frame, stop_frame)

    annotations = get_json(session, f"{host}/api/jobs/{job_id}/annotations")
    shapes, tags = objects_on_frame(annotations, abs_frame)
    tracks_on_frame = [
        item
        for item in annotations.get("tracks") or []
        if any(shape.get("frame") == abs_frame for shape in item.get("shapes") or [])
    ]

    print(f"CVAT {host}  job {job_id}  frame {user_frame} → abs {abs_frame}")
    print(f"Job span: {start_frame}–{stop_frame}")
    summarize(shapes, "shapes")
    summarize(tags, "tags")
    if tracks_on_frame:
        print(
            f"  tracks trên frame này: {len(tracks_on_frame)} (giữ nguyên, không xoá)"
        )

    if not shapes and not tags:
        print("Không có shape/tag để xoá.")
        return 0

    if args.dry_run:
        print("Dry-run: không PATCH.")
        return 0

    if not args.yes and not confirm_delete(len(shapes), len(tags)):
        print("Huỷ.")
        return 1

    delete_objects(session, host, job_id, shapes, tags)
    print(f"Đã xoá {len(shapes)} shape và {len(tags)} tag.")
    return 0


def main() -> None:
    try:
        raise SystemExit(run())
    except ToolError as exc:
        print(f"Lỗi: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
