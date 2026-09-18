"""SAM 3 image inference on Modal GPU for local CVAT.

Visual (click/box) uses Sam3Tracker. Text (concept) uses Sam3Model.
Endpoints require Modal proxy auth (Modal-Key / Modal-Secret).
"""

from __future__ import annotations

import base64
import io
from typing import Any

import modal

MINUTES = 60
CACHE_DIR = "/cache"
MODEL_ID = "facebook/sam3"

image = (
    modal.Image.debian_slim(python_version="3.12")
    .uv_pip_install(
        "torch",
        "torchvision",
        "transformers>=4.57.0",
        "accelerate",
        "huggingface_hub",
        "safetensors",
        "pillow",
        "numpy",
        "opencv-python-headless",
        "fastapi[standard]",
    )
    .env(
        {
            "HF_HUB_CACHE": CACHE_DIR,
            "HF_HOME": CACHE_DIR,
            "HF_XET_HIGH_PERFORMANCE": "1",
        }
    )
)

hf_cache = modal.Volume.from_name("sam3-hf-cache", create_if_missing=True)
app = modal.App("sam3-cvat", image=image)


def mask_to_cvat_rle(mask) -> list[int]:
    """CVAT mask RLE (IOG-style): run lengths in row-major order + [0, 0, w-1, h-1]."""
    import numpy as np

    arr = np.asarray(mask)
    if arr.ndim > 2:
        arr = arr.squeeze()
    binary = (arr != 0).astype(np.uint8)
    height, width = binary.shape
    pixels = binary.reshape(-1)
    if pixels.size == 0:
        return []
    changes = np.flatnonzero(pixels[1:] != pixels[:-1]) + 1
    rle = np.diff(np.concatenate(([0], changes, [pixels.size]))).tolist()
    if pixels[0] == 1:
        rle.insert(0, 0)
    rle.extend([0, 0, width - 1, height - 1])
    return rle


def _decode_image(image_base64: str):
    from PIL import Image

    raw = base64.b64decode(image_base64)
    return Image.open(io.BytesIO(raw)).convert("RGB")


def _to_xyxy_box(box: Any) -> list[float] | None:
    if not box:
        return None
    if isinstance(box[0], (list, tuple)):
        (x1, y1), (x2, y2) = box[0], box[1]
        return [float(x1), float(y1), float(x2), float(y2)]
    if len(box) >= 4:
        return [float(box[0]), float(box[1]), float(box[2]), float(box[3])]
    return None


@app.cls(
    gpu="L4",
    timeout=180,
    startup_timeout=10 * MINUTES,
    scaledown_window=300,
    min_containers=0,
    secrets=[modal.Secret.from_name("huggingface")],
    volumes={CACHE_DIR: hf_cache},
)
class Sam3Service:
    @modal.enter()
    def load_models(self):
        import os

        import torch
        from transformers import (
            Sam3Model,
            Sam3Processor,
            Sam3TrackerModel,
            Sam3TrackerProcessor,
        )

        assert torch.cuda.is_available(), "CUDA is required for SAM 3 on Modal"
        self.device = "cuda"
        self.dtype = torch.bfloat16
        token = (
            os.environ.get("HF_TOKEN")
            or os.environ.get("HUGGING_FACE_HUB_TOKEN")
            or os.environ.get("HUGGINGFACE_TOKEN")
        )
        if token and not os.environ.get("HF_TOKEN"):
            os.environ["HF_TOKEN"] = token

        pretrained = {"torch_dtype": self.dtype}
        proc_kwargs = {}
        if token:
            pretrained["token"] = token
            proc_kwargs["token"] = token

        self.tracker = Sam3TrackerModel.from_pretrained(MODEL_ID, **pretrained).to(
            self.device
        )
        self.tracker.eval()
        self.tracker_processor = Sam3TrackerProcessor.from_pretrained(
            MODEL_ID, **proc_kwargs
        )

        self.concept = Sam3Model.from_pretrained(MODEL_ID, **pretrained).to(self.device)
        self.concept.eval()
        self.concept_processor = Sam3Processor.from_pretrained(MODEL_ID, **proc_kwargs)
        hf_cache.commit()

    @modal.fastapi_endpoint(
        method="GET",
        label="sam3-health",
        requires_proxy_auth=True,
    )
    def health(self) -> dict:
        import torch

        return {
            "status": "ok",
            "service": "sam3-cvat",
            "cuda": torch.cuda.is_available(),
        }

    @modal.method()
    def infer_visual(
        self,
        image_base64: str,
        pos_points: list | None = None,
        neg_points: list | None = None,
        box: list | None = None,
        threshold: float = 0.5,
    ) -> dict:
        import numpy as np
        import torch

        image = _decode_image(image_base64)
        width, height = image.size
        pos_points = pos_points or []
        neg_points = neg_points or []
        xyxy = _to_xyxy_box(box)

        if not pos_points and not neg_points and xyxy is None:
            return {"ok": False, "error": "Need pos_points, neg_points, or box"}

        kwargs: dict[str, Any] = {"images": image, "return_tensors": "pt"}
        if pos_points or neg_points:
            coords = list(pos_points) + list(neg_points)
            labels = [1] * len(pos_points) + [0] * len(neg_points)
            kwargs["input_points"] = [[coords]]
            kwargs["input_labels"] = [[labels]]
        if xyxy is not None:
            kwargs["input_boxes"] = [[xyxy]]

        inputs = self.tracker_processor(**kwargs).to(self.device)
        with torch.inference_mode():
            outputs = self.tracker(**inputs, multimask_output=True)

        masks = self.tracker_processor.post_process_masks(
            outputs.pred_masks.cpu(), inputs["original_sizes"]
        )[0]
        mask_t = masks
        if mask_t.ndim == 4:
            iou = outputs.iou_scores[0, 0].detach().float().cpu()
            mask_t = mask_t[0, int(iou.argmax().item())]
        elif mask_t.ndim == 3:
            mask_t = mask_t[0]
        binary = (np.asarray(mask_t) > threshold).astype(np.uint8)
        return {
            "ok": True,
            "width": width,
            "height": height,
            "rle": mask_to_cvat_rle(binary),
        }

    @modal.fastapi_endpoint(
        method="POST",
        label="sam3-visual",
        requires_proxy_auth=True,
    )
    def visual(self, data: dict) -> dict:
        try:
            image_base64 = data.get("image_base64") or data.get("image")
            if not image_base64:
                return {"ok": False, "error": "Missing image_base64"}
            return self.infer_visual.local(
                image_base64=image_base64,
                pos_points=data.get("pos_points") or [],
                neg_points=data.get("neg_points") or [],
                box=data.get("box") or data.get("obj_bbox"),
                threshold=float(data.get("threshold", 0.5)),
            )
        except Exception as exc:
            return {"ok": False, "error": str(exc)}

    @modal.method()
    def infer_text(
        self,
        image_base64: str,
        prompts: list[str],
        threshold: float = 0.5,
    ) -> dict:
        import numpy as np
        import torch

        image = _decode_image(image_base64)
        width, height = image.size
        objects: list[dict] = []

        for prompt in prompts:
            prompt = (prompt or "").strip()
            if not prompt:
                continue
            inputs = self.concept_processor(
                images=image, text=prompt, return_tensors="pt"
            ).to(self.device)
            with torch.inference_mode():
                outputs = self.concept(**inputs)
            target_sizes = inputs.get("original_sizes")
            if hasattr(target_sizes, "tolist"):
                target_sizes = target_sizes.tolist()
            results = self.concept_processor.post_process_instance_segmentation(
                outputs,
                threshold=threshold,
                mask_threshold=threshold,
                target_sizes=target_sizes,
            )[0]
            masks = results.get("masks")
            boxes = results.get("boxes")
            scores = results.get("scores")
            if masks is None:
                continue
            n = len(masks)
            for i in range(n):
                mask = masks[i]
                if hasattr(mask, "cpu"):
                    mask = mask.cpu().numpy()
                binary = (np.asarray(mask) > 0.5).astype(np.uint8)
                box = None
                score = None
                if boxes is not None:
                    b = boxes[i]
                    box = b.tolist() if hasattr(b, "tolist") else list(b)
                if scores is not None:
                    s = scores[i]
                    score = float(s.item() if hasattr(s, "item") else s)
                objects.append(
                    {
                        "prompt": prompt,
                        "score": score,
                        "box": box,
                        "rle": mask_to_cvat_rle(binary),
                    }
                )

        return {
            "ok": True,
            "width": width,
            "height": height,
            "objects": objects,
        }

    @modal.fastapi_endpoint(
        method="POST",
        label="sam3-text",
        requires_proxy_auth=True,
    )
    def text(self, data: dict) -> dict:
        try:
            image_base64 = data.get("image_base64") or data.get("image")
            if not image_base64:
                return {"ok": False, "error": "Missing image_base64"}
            prompts = data.get("prompts")
            if not prompts:
                single = data.get("prompt")
                prompts = [single] if single else []
            if not prompts:
                return {"ok": False, "error": "Missing prompts"}
            return self.infer_text.local(
                image_base64=image_base64,
                prompts=list(prompts),
                threshold=float(data.get("threshold", 0.5)),
            )
        except Exception as exc:
            return {"ok": False, "error": str(exc)}


@app.local_entrypoint()
def main():
    print("Deploy with: modal deploy source-tool/gpu_integrate/modal/sam3_app.py")
    print("Then: python source-tool/gpu_integrate/scripts/test_modal.py")
    print("Create HF secret first: modal secret create huggingface HF_TOKEN=hf_...")
