#!/usr/bin/env python3
"""Smoke-test deployed SAM 3 Modal HTTP endpoints (visual + text)."""

from __future__ import annotations

import argparse
import base64
import io
import os
import sys
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
ENV_FILE = ROOT / ".env"
SAMPLE_URL = (
    "https://huggingface.co/datasets/huggingface/documentation-images/"
    "resolve/main/transformers/tasks/car.jpg"
)


def load_env(path: Path) -> None:
    if not path.is_file():
        return
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def headers() -> dict[str, str]:
    key = os.environ.get("MODAL_PROXY_KEY", "")
    secret = os.environ.get("MODAL_PROXY_SECRET", "")
    if not key or not secret:
        raise SystemExit("Set MODAL_PROXY_KEY and MODAL_PROXY_SECRET in .env")
    return {
        "Modal-Key": key,
        "Modal-Secret": secret,
        "Content-Type": "application/json",
    }


def fetch_sample_image() -> str:
    response = requests.get(SAMPLE_URL, timeout=60)
    response.raise_for_status()
    return base64.b64encode(response.content).decode("ascii")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--image", type=Path, help="Local image instead of the sample car.jpg")
    args = parser.parse_args()
    load_env(ENV_FILE)

    visual_url = os.environ.get("SAM3_MODAL_VISUAL_URL", "").strip()
    text_url = os.environ.get("SAM3_MODAL_TEXT_URL", "").strip()
    health_url = os.environ.get("SAM3_MODAL_HEALTH_URL", "").strip()
    if not visual_url or not text_url:
        raise SystemExit("Set SAM3_MODAL_VISUAL_URL and SAM3_MODAL_TEXT_URL in .env")

    timeout = float(os.environ.get("SAM3_TIMEOUT_SEC", "170"))
    auth = headers()

    if health_url:
        health = requests.get(health_url, headers=auth, timeout=timeout, allow_redirects=True)
        health.raise_for_status()
        print("health:", health.json())

    if args.image:
        image_b64 = base64.b64encode(args.image.read_bytes()).decode("ascii")
    else:
        print("Downloading sample image...")
        image_b64 = fetch_sample_image()

    from PIL import Image

    image = Image.open(io.BytesIO(base64.b64decode(image_b64)))
    cx, cy = image.size[0] // 2, image.size[1] // 2
    print(f"image size: {image.size}, click: ({cx}, {cy})")

    visual = requests.post(
        visual_url,
        headers=auth,
        json={"image_base64": image_b64, "pos_points": [[cx, cy]]},
        timeout=timeout,
        allow_redirects=True,
    )
    visual.raise_for_status()
    visual_body = visual.json()
    if not visual_body.get("ok"):
        print("visual failed:", visual_body, file=sys.stderr)
        return 1
    print(f"visual rle length: {len(visual_body.get('rle') or [])}")

    text = requests.post(
        text_url,
        headers=auth,
        json={"image_base64": image_b64, "prompts": ["car"]},
        timeout=timeout,
        allow_redirects=True,
    )
    text.raise_for_status()
    text_body = text.json()
    if not text_body.get("ok"):
        print("text failed:", text_body, file=sys.stderr)
        return 1
    objects = text_body.get("objects") or []
    print(f"text objects: {len(objects)}")
    for obj in objects[:5]:
        print(
            f"  prompt={obj.get('prompt')} score={obj.get('score')} "
            f"box={obj.get('box')} mask={len(obj.get('mask') or [])} "
            f"polygon={len(obj.get('polygon') or [])}"
        )
    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
