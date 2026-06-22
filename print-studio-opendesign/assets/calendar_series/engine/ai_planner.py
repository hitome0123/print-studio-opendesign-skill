#!/usr/bin/env python3
"""
③ AI Layout Planner · 排版脑
- 视觉分析每张插画 → 输出受限 layout_plan(枚举/调色板内,AI 不能越界)
- 渲染器只吃 plan 的:vbias(主体重心)+ accent(标题色,复古调色板内)
- 无 GEMINI_API_KEY 或分析失败 → 降级 default_plan(零成本也能跑)
- 输出经严格校验:非法值一律 clamp 回默认,AI 无法把图搞坏
"""
import json, os, re, time

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


def default_plan(hue="warm"):
    return {"subject_position": "center", "density": "medium",
            "dominant_hue": hue, "accent": PALETTE.get(hue, PALETTE["red"]),
            "vbias": "center", "source": "default"}


def _validate(raw):
    """把 AI 原始输出 clamp 进受限解空间"""
    sp = raw.get("subject_position")
    sp = sp if sp in SUBJECT else "center"
    dn = raw.get("density")
    dn = dn if dn in DENSITY else "medium"
    hue = raw.get("dominant_hue")
    hue = hue if hue in PALETTE else "warm"
    return {"subject_position": sp, "density": dn, "dominant_hue": hue,
            "accent": PALETTE[hue], "vbias": _VBIAS[sp], "source": "ai"}


def plan_for(illustration_path, enabled=True, model="gemini-2.5-flash", retries=3):
    key = os.getenv("GEMINI_API_KEY")
    if not enabled or not key:
        return default_plan()
    prompt = (
        "You are an art director for a vintage botanical calendar series. "
        "Analyze this single illustration and reply with ONLY a JSON object, no prose:\n"
        '{"subject_position": one of [center,left,right,top-heavy,bottom-heavy],'
        ' "density": one of [airy,medium,dense],'
        ' "dominant_hue": one of [pink,red,yellow,green,blue,purple,warm,neutral]}\n'
        "subject_position = where the visual weight sits. dominant_hue = the main flower/subject color."
    )
    try:
        from google import genai
        from google.genai import types
        client = genai.Client(api_key=key)
        img = open(illustration_path, "rb").read()
    except Exception:
        return default_plan()
    for attempt in range(retries):
        try:
            resp = client.models.generate_content(
                model=model,
                contents=[prompt, types.Part.from_bytes(data=img, mime_type="image/png")],
                config=types.GenerateContentConfig(temperature=0.2))
            m = re.search(r"\{.*\}", resp.text.strip(), re.S)
            if m:
                return _validate(json.loads(m.group(0)))
        except Exception as e:
            time.sleep(6 if "429" in str(e) or "RESOURCE" in str(e).upper() else 2)
    return default_plan()


if __name__ == "__main__":
    import sys
    p = sys.argv[1]
    print(json.dumps(plan_for(p), ensure_ascii=False))
