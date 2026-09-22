import json
import os
from pathlib import Path

import requests
import yaml


def load_label_config():
    labels_path = Path("/opt/nuclio/labels.yaml")
    if not labels_path.exists():
        labels_path = Path(__file__).with_name("labels.yaml")
    with labels_path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    labels = data.get("labels") or []
    prompts = dict(data.get("prompts") or {})
    for item in labels:
        name = item["name"]
        prompts.setdefault(name, item.get("prompt") or name)
    types = {item["name"]: item.get("type", "mask") for item in labels}
    return labels, prompts, types


def _modal_headers():
    key = os.environ.get("MODAL_PROXY_KEY", "")
    secret = os.environ.get("MODAL_PROXY_SECRET", "")
    if not key or not secret:
        raise RuntimeError("MODAL_PROXY_KEY / MODAL_PROXY_SECRET are not set")
    return {"Modal-Key": key, "Modal-Secret": secret, "Content-Type": "application/json"}


def _rle_to_detector_mask(rle, width, height):
    """Rebuild CVAT detector mask from interactor RLE when Modal has no `mask` field."""
    if not rle or width <= 0 or height <= 0:
        return []
    counts = rle[:-4] if len(rle) >= 4 else rle
    expected = width * height
    pixels = []
    val = 0
    for count in counts:
        n = int(count)
        remaining = expected - len(pixels)
        if remaining <= 0:
            break
        if n > 0:
            take = n if n <= remaining else remaining
            pixels.extend([val] * take)
        val = 1 - val
    if len(pixels) < expected:
        pixels.extend([0] * (expected - len(pixels)))

    xtl, ytl, xbr, ybr = width, height, -1, -1
    for index, pixel in enumerate(pixels):
        if not pixel:
            continue
        x = index % width
        y = index // width
        if x < xtl:
            xtl = x
        if y < ytl:
            ytl = y
        if x > xbr:
            xbr = x
        if y > ybr:
            ybr = y
    if xbr < 0 or xbr < xtl or ybr < ytl:
        return []

    crop = []
    for y in range(ytl, ybr + 1):
        row = y * width
        crop.extend(pixels[row + xtl : row + xbr + 1])
    crop.extend([xtl, ytl, xbr, ybr])
    return crop


def call_text(image_b64, prompts, threshold):
    url = os.environ.get("SAM3_MODAL_TEXT_URL", "").strip()
    if not url:
        raise RuntimeError("SAM3_MODAL_TEXT_URL is not set")
    timeout = float(os.environ.get("SAM3_TIMEOUT_SEC", "170"))
    response = requests.post(
        url,
        json={"image_base64": image_b64, "prompts": prompts, "threshold": threshold},
        headers=_modal_headers(),
        timeout=timeout,
        allow_redirects=True,
    )
    response.raise_for_status()
    body = response.json()
    if not body.get("ok"):
        raise RuntimeError(body.get("error") or "SAM 3 text inference failed")
    return {
        "objects": body.get("objects") or [],
        "width": int(body.get("width") or 0),
        "height": int(body.get("height") or 0),
    }
