import json
import os

import requests


def _modal_headers():
    key = os.environ.get("MODAL_PROXY_KEY", "")
    secret = os.environ.get("MODAL_PROXY_SECRET", "")
    if not key or not secret:
        raise RuntimeError("MODAL_PROXY_KEY / MODAL_PROXY_SECRET are not set")
    return {"Modal-Key": key, "Modal-Secret": secret, "Content-Type": "application/json"}


def call_visual(image_b64, pos_points, neg_points, obj_bbox, threshold):
    url = os.environ.get("SAM3_MODAL_VISUAL_URL", "").strip()
    if not url:
        raise RuntimeError("SAM3_MODAL_VISUAL_URL is not set")
    timeout = float(os.environ.get("SAM3_TIMEOUT_SEC", "170"))
    payload = {
        "image_base64": image_b64,
        "pos_points": pos_points or [],
        "neg_points": neg_points or [],
        "box": obj_bbox,
        "threshold": threshold,
    }
    response = requests.post(
        url, json=payload, headers=_modal_headers(), timeout=timeout, allow_redirects=True
    )
    response.raise_for_status()
    body = response.json()
    if not body.get("ok"):
        raise RuntimeError(body.get("error") or "SAM 3 visual inference failed")
    return body["rle"]
