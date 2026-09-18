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
    return body.get("objects") or []
