import json

from model_handler import call_text, load_label_config


def init_context(context):
    labels, prompts, types = load_label_config()
    context.user_data.labels = labels
    context.user_data.prompts = prompts
    context.user_data.types = types
    context.logger.info("SAM 3 Modal detector ready (%s labels)", len(labels))


def handler(context, event):
    try:
        data = event.body
        if isinstance(data, (bytes, bytearray)):
            data = json.loads(data.decode("utf-8"))
        elif isinstance(data, str):
            data = json.loads(data)

        image_b64 = data["image"]
        threshold = float(data.get("threshold", 0.5))
        labels = context.user_data.labels
        prompt_map = context.user_data.prompts
        type_map = context.user_data.types

        unique_prompts = []
        prompt_to_label = {}
        for item in labels:
            name = item["name"]
            prompt = prompt_map.get(name, name)
            prompt_to_label.setdefault(prompt, name)
            if prompt not in unique_prompts:
                unique_prompts.append(prompt)

        objects = call_text(image_b64, unique_prompts, threshold)
        results = []
        for obj in objects:
            prompt = obj.get("prompt")
            label = prompt_to_label.get(prompt, prompt)
            shape_type = type_map.get(label, "mask")
            score = obj.get("score")
            entry = {
                "confidence": str(score if score is not None else 0.0),
                "label": label,
                "type": shape_type,
            }
            if shape_type == "rectangle":
                box = obj.get("box") or []
                if len(box) < 4:
                    continue
                entry["points"] = [
                    float(box[0]),
                    float(box[1]),
                    float(box[2]),
                    float(box[3]),
                ]
            else:
                entry["points"] = obj.get("rle") or []
                entry["type"] = "mask"
            results.append(entry)

        return context.Response(
            body=json.dumps(results),
            headers={},
            content_type="application/json",
            status_code=200,
        )
    except Exception as exc:
        context.logger.error("SAM 3 detector failed: %s", exc)
        return context.Response(
            body=json.dumps({"error": str(exc)}),
            headers={},
            content_type="application/json",
            status_code=500,
        )
