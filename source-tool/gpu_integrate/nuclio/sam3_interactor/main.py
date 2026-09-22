import json

from model_handler import call_visual


def init_context(context):
    context.logger.info("SAM 3 Modal interactor ready")


def handler(context, event):
    try:
        data = event.body
        if isinstance(data, (bytes, bytearray)):
            data = json.loads(data.decode("utf-8"))
        elif isinstance(data, str):
            data = json.loads(data)

        image_b64 = data["image"]
        pos_points = data.get("pos_points") or []
        neg_points = data.get("neg_points") or []
        obj_bbox = data.get("obj_bbox")
        threshold = float(data.get("threshold", 0.5))

        rle = call_visual(image_b64, pos_points, neg_points, obj_bbox, threshold)

        return context.Response(
            body=json.dumps(
                {
                    "shapes": [
                        {
                            "points": rle,
                            "group": 0,
                            "source": "semi-auto",
                            "attributes": [],
                            "occluded": False,
                            "rotation": 0,
                            "type": "mask",
                        }
                    ]
                }
            ),
            headers={},
            content_type="application/json",
            status_code=200,
        )
    except Exception as exc:
        context.logger.error("SAM 3 interactor failed: %s", exc)
        return context.Response(
            body=json.dumps({"error": str(exc)}),
            headers={},
            content_type="application/json",
            status_code=500,
        )
