#!/usr/bin/env python3
"""
③ AI Layout Planner · 排版脑
- API 只做版式顾问:视觉分析每张插画 → 输出受限 layout_plan
- 渲染器只吃 plan 的:vbias(主体重心)+ accent(标题色,复古调色板内)
- 无 API key 或分析失败 → 降级 default_plan(零成本也能跑)
- 输出经严格校验:非法值一律 clamp 回默认,AI 无法把图搞坏
"""
import base64
import json
import mimetypes
import os
import re
import time
import urllib.error
import urllib.request

# 受限解空间(AI 只能在这里选)
SUBJECT = {"center", "left", "right", "top-heavy", "bottom-heavy"}
DENSITY = {"airy", "medium", "dense"}
# 复古调色板:标题色只能落这几个(保证整套系列协调)
PALETTE = {
    "pink":   "#c4738a", "red":    "#c1604f", "yellow": "#b8893a",
    "green":  "#7a8a6a", "blue":   "#6a7a9a", "purple": "#8a6a8a",
    "warm":   "#b07a5a", "neutral": "#a8806a",
}
_VBIAS = {"top-heavy": "top-heavy", "bottom-heavy": "bottom-heavy",
          "center": "center", "left": "center", "right": "center"}


def default_plan(hue="warm", source="default"):
    return {"subject_position": "center", "density": "medium",
            "dominant_hue": hue, "accent": PALETTE.get(hue, PALETTE["red"]),
            "vbias": "center", "source": source, "confidence": 0.0,
            "reason": "使用本地默认版式;API 未启用或不可用"}


def _validate(raw, source="api"):
    """把 AI 原始输出 clamp 进受限解空间"""
    sp = raw.get("subject_position")
    sp = sp if sp in SUBJECT else "center"
    dn = raw.get("density")
    dn = dn if dn in DENSITY else "medium"
    hue = raw.get("dominant_hue")
    hue = hue if hue in PALETTE else "warm"
    confidence = raw.get("confidence", 0.5)
    try:
        confidence = max(0.0, min(1.0, float(confidence)))
    except Exception:
        confidence = 0.5
    reason = str(raw.get("reason") or "API 版式顾问建议;最终由确定性渲染器落图")[:160]
    return {"subject_position": sp, "density": dn, "dominant_hue": hue,
            "accent": PALETTE[hue], "vbias": _VBIAS[sp], "source": source,
            "confidence": confidence, "reason": reason}


def _prompt():
    return (
        "You are an art director for a print-ready illustration card/calendar series. "
        "Analyze this single illustration. You are NOT allowed to crop, rewrite, redraw, or compose the final artwork. "
        "Only suggest a constrained layout plan that a deterministic renderer will execute. "
        "Reply with ONLY a JSON object, no prose:\n"
        '{"subject_position": one of [center,left,right,top-heavy,bottom-heavy],'
        ' "density": one of [airy,medium,dense],'
        ' "dominant_hue": one of [pink,red,yellow,green,blue,purple,warm,neutral],'
        ' "confidence": number 0-1,'
        ' "reason": short Chinese reason}\n'
        "subject_position = where the visual weight sits. density = amount of detail/ornament. "
        "dominant_hue = main flower/subject color family."
    )


def _mime(path):
    guessed = mimetypes.guess_type(str(path))[0]
    return guessed if guessed in {"image/png", "image/jpeg", "image/webp"} else "image/png"


def _read_image_data_url(path):
    data = open(path, "rb").read()
    return f"data:{_mime(path)};base64,{base64.b64encode(data).decode('ascii')}"


def _extract_json(text):
    if not text:
        return None
    match = re.search(r"\{.*\}", text.strip(), re.S)
    return json.loads(match.group(0)) if match else None


def _call_gemini(illustration_path, model):
    key = os.getenv("GEMINI_API_KEY")
    if not key:
        raise RuntimeError("missing GEMINI_API_KEY")
    try:
        from google import genai
        from google.genai import types
        client = genai.Client(api_key=key)
        img = open(illustration_path, "rb").read()
        resp = client.models.generate_content(
            model=model,
            contents=[_prompt(), types.Part.from_bytes(data=img, mime_type=_mime(illustration_path))],
            config=types.GenerateContentConfig(temperature=0.1))
        raw = _extract_json(resp.text)
        if not raw:
            raise RuntimeError("Gemini returned no JSON")
        return _validate(raw, source=f"api:gemini:{model}")
    except Exception as exc:
        raise RuntimeError(f"gemini planner failed: {exc}") from exc


def _openai_output_text(payload):
    if payload.get("output_text"):
        return payload["output_text"]
    chunks = []
    for item in payload.get("output", []):
        for content in item.get("content", []):
            if content.get("type") in {"output_text", "text"} and content.get("text"):
                chunks.append(content["text"])
    return "\n".join(chunks)


def _call_openai(illustration_path, model):
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        raise RuntimeError("missing OPENAI_API_KEY")
    body = {
        "model": model,
        "temperature": 0.1,
        "input": [{
            "role": "user",
            "content": [
                {"type": "input_text", "text": _prompt()},
                {"type": "input_image", "image_url": _read_image_data_url(illustration_path)},
            ],
        }],
        "text": {
            "format": {
                "type": "json_schema",
                "name": "print_layout_plan",
                "strict": True,
                "schema": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "subject_position": {"type": "string", "enum": sorted(SUBJECT)},
                        "density": {"type": "string", "enum": sorted(DENSITY)},
                        "dominant_hue": {"type": "string", "enum": sorted(PALETTE)},
                        "confidence": {"type": "number", "minimum": 0, "maximum": 1},
                        "reason": {"type": "string"},
                    },
                    "required": ["subject_position", "density", "dominant_hue", "confidence", "reason"],
                },
            }
        },
    }
    req = urllib.request.Request(
        "https://api.openai.com/v1/responses",
        data=json.dumps(body).encode("utf-8"),
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=45) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        raw = _extract_json(_openai_output_text(data))
        if not raw:
            raise RuntimeError("OpenAI returned no JSON")
        return _validate(raw, source=f"api:openai:{model}")
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="ignore")[:500]
        raise RuntimeError(f"openai planner failed: HTTP {exc.code} {detail}") from exc
    except Exception as exc:
        raise RuntimeError(f"openai planner failed: {exc}") from exc


def _provider_order(provider):
    if provider == "openai":
        return ["openai"]
    if provider == "gemini":
        return ["gemini"]
    if provider == "local":
        return []
    return ["openai", "gemini"]


def plan_for(illustration_path, enabled=True, model=None, retries=2, options=None):
    options = options or {}
    enabled = bool(enabled and options.get("enabled", True))
    provider = options.get("provider") or os.getenv("PRINT_STUDIO_LAYOUT_PROVIDER") or "auto"
    models = {
        "openai": options.get("openai_model") or os.getenv("PRINT_STUDIO_OPENAI_LAYOUT_MODEL") or "gpt-4.1-mini",
        "gemini": options.get("gemini_model") or model or os.getenv("PRINT_STUDIO_GEMINI_LAYOUT_MODEL") or "gemini-2.5-flash",
    }
    if not enabled:
        return default_plan(source="default:layout_ai_disabled")

    last_error = None
    for api_provider in _provider_order(provider):
        for attempt in range(retries):
            try:
                if api_provider == "openai":
                    return _call_openai(illustration_path, models["openai"])
                if api_provider == "gemini":
                    return _call_gemini(illustration_path, models["gemini"])
            except Exception as exc:
                last_error = str(exc)
                time.sleep(2 if attempt + 1 < retries else 0)
    plan = default_plan(source=f"default:api_unavailable:{provider}")
    if last_error:
        plan["error"] = last_error[:220]
    return plan


if __name__ == "__main__":
    import sys
    p = sys.argv[1]
    print(json.dumps(plan_for(p), ensure_ascii=False))
