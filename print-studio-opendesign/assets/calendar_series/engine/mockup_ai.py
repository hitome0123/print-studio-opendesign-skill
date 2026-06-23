#!/usr/bin/env python3
"""
D 产品白底图 / E 产品氛围图 — AI 生图(锚图法把成品卡放进场景)
铁律补充:排版成品(B 单图)是"锚",生图只负责"摆进场景",不改版面内容。
注意:AI mockup 可能微调卡面细节 → 电商展示可用;印刷件请用 B 原件。

后端:gemini(nano-banana,默认) / gpt_image(需 OPENAI_API_KEY)
对外统一接口:render_whitebg(card, out, ...) / render_ambiance(card, out, ...)
"""
import os
from pathlib import Path

# ── 场景提示词(锁定风格,一般不动;config 可追加 *_prompt_extra)──
WHITEBG_PROMPT = (
    "A vertical paper desk calendar card standing in a natural wooden display "
    "stand, photographed on a pure clean white seamless background. Front-facing "
    "e-commerce main image, minimal perspective, the product should fill about "
    "70-80% of the square frame with balanced white margin. Soft even studio "
    "lighting, gentle clean shadow under the wooden base. Use the attached "
    "calendar page as a printed surface on the product; preserve the overall "
    "artwork, month title, keyword and date grid placement from the reference. "
    "Do not invent new text, logos, stickers, labels, props or extra decoration. "
    "If tiny printed text cannot be perfectly readable, keep it visually quiet "
    "rather than replacing it with garbled text. Realistic product photography, "
    "square 1:1 composition, the card centered and large."
)
AMBIANCE_PROMPT = (
    "A vertical paper desk calendar card in a natural wooden display stand, "
    "placed on a light wooden desk in a cozy, warm Instagram-style home interior. "
    "The calendar product is the clear hero and should fill about 55-70% of the "
    "square frame. Keep the front face visible, not overly angled, with the card "
    "large enough to recognize the design. Soft natural daylight from the side, "
    "a blurred background with fresh flowers in a glass vase, a ceramic coffee "
    "cup and a notebook as secondary props only. Use the attached calendar page "
    "as a printed surface on the product; preserve the overall artwork, month "
    "title, keyword and date grid placement from the reference. Do not invent "
    "new text, logos, stickers, labels or extra decoration on the card. If tiny "
    "printed text cannot be perfectly readable, keep it visually quiet rather "
    "than replacing it with garbled text. Lifestyle product photography, shallow "
    "depth of field, warm and homey mood, square 1:1 composition."
)


class _NanoBanana:
    """Gemini 2.5 Flash Image — 原生支持锚图,1:1。GEMINI_API_KEY 环境变量。"""
    def __init__(self, model="gemini-2.5-flash-image"):
        from google import genai
        self.genai, self.model = genai, model
        key = os.getenv("GEMINI_API_KEY")
        if not key:
            raise RuntimeError("缺 GEMINI_API_KEY 环境变量(使用者自行配置 API)")
        self.client = genai.Client(api_key=key)

    def generate(self, prompt, anchor_bytes):
        from google.genai import types
        resp = self.client.models.generate_content(
            model=self.model,
            contents=[prompt, types.Part.from_bytes(data=anchor_bytes, mime_type="image/jpeg")],
            config=types.GenerateContentConfig(
                response_modalities=["IMAGE", "TEXT"], temperature=0.7,
                image_config=types.ImageConfig(aspect_ratio="1:1")))  # 不指定必出 1:1 之外
        for part in resp.candidates[0].content.parts:
            if part.inline_data and part.inline_data.mime_type.startswith("image/"):
                return part.inline_data.data
        return None


class _GptImage:
    """GPT-Image via OpenAI images.edit。OPENAI_API_KEY 环境变量。"""
    def __init__(self, model="gpt-image-1"):
        from openai import OpenAI
        self.client, self.model = OpenAI(), model

    def generate(self, prompt, anchor_bytes):
        import base64, io
        r = self.client.images.edit(
            model=self.model, prompt=prompt, size="1024x1024",
            image=[("card.jpg", io.BytesIO(anchor_bytes), "image/jpeg")])
        return base64.b64decode(r.data[0].b64_json)


_BACKENDS = {"gemini": _NanoBanana, "gpt_image": _GptImage}


def _gen(card_path, out_path, prompt, backend, model, retries=3):
    eng = _BACKENDS[backend](model) if model else _BACKENDS[backend]()
    anchor = Path(card_path).read_bytes()
    last = None
    for i in range(retries):
        try:
            data = eng.generate(prompt, anchor)
            if data:
                Path(out_path).parent.mkdir(parents=True, exist_ok=True)
                Path(out_path).write_bytes(data)
                return out_path
            last = "no image returned"
        except Exception as e:
            last = str(e)
    raise RuntimeError(f"{backend} 生图失败({retries}次): {last}")


def render_whitebg(card_path, out_path, backend="gemini", model=None, extra=""):
    return _gen(card_path, out_path, (WHITEBG_PROMPT + " " + extra).strip(), backend, model)


def render_ambiance(card_path, out_path, backend="gemini", model=None, extra=""):
    return _gen(card_path, out_path, (AMBIANCE_PROMPT + " " + extra).strip(), backend, model)


if __name__ == "__main__":
    import sys
    card = sys.argv[1] if len(sys.argv) > 1 else "card.jpg"
    print(render_whitebg(card, "whitebg_test.jpg"))
    print(render_ambiance(card, "ambiance_test.jpg"))
