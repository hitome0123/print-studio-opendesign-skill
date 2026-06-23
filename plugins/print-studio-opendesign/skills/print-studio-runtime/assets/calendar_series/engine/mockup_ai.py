#!/usr/bin/env python3
"""
D 产品白底图 / E 产品氛围图 — AI 生图(锚图法把成品卡放进场景)
铁律补充:排版成品(B 单图)是"锚",生图只负责"摆进场景",不改版面内容。
注意:AI mockup 可能微调卡面细节 → 电商展示可用;印刷件请用 B 原件。

后端:gemini(nano-banana,默认) / gpt_image / gpt_image2(需 OPENAI_API_KEY) / jimeng(需自行接入 API)
对外统一接口:render_whitebg(card, out, ...) / render_ambiance(card, out, ...)
"""
import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageOps

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


class _Jimeng:
    """即梦图像接口占位适配器。

    不同账号/API 网关的即梦接入方式可能不同。若要启用,请在这里接入实际 HTTP API,
    保持 generate(prompt, anchor_bytes) 返回图片 bytes 即可。
    """
    def __init__(self, model="jimeng-image"):
        self.model = model
        if not os.getenv("JIMENG_API_KEY"):
            raise RuntimeError("缺 JIMENG_API_KEY 环境变量;请接入实际即梦图像 API 后启用")

    def generate(self, prompt, anchor_bytes):
        raise NotImplementedError("jimeng 后端需要按实际账号/API 网关补充实现")


_BACKENDS = {
    "gemini": _NanoBanana,
    "gpt_image": _GptImage,
    "gpt_image2": _GptImage,
    "jimeng": _Jimeng,
}


def _gen(card_path, out_path, prompt, backend, model, retries=3):
    if backend not in _BACKENDS:
        raise RuntimeError(f"未知生图后端: {backend};可选 {', '.join(sorted(_BACKENDS))}")
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


def _fit_card(card_path, max_w, max_h):
    card = ImageOps.exif_transpose(Image.open(card_path)).convert("RGB")
    card.thumbnail((max_w, max_h), Image.LANCZOS)
    return card


def _paste_with_shadow(canvas, card, x, y, radius=26, shadow=(70, 45, 25, 70)):
    shadow_img = Image.new("RGBA", (card.width + 80, card.height + 80), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow_img)
    sd.rounded_rectangle((40, 40, card.width + 40, card.height + 40), radius=radius, fill=shadow)
    shadow_img = shadow_img.filter(ImageFilter.GaussianBlur(22))
    canvas.paste(shadow_img, (x - 40, y - 28), shadow_img)
    canvas.paste(card, (x, y))


def render_whitebg_local(card_path, out_path):
    """本地白底图兜底:不调用模型,用于 API 不可用时保持展示交付完整。"""
    size = 1600
    canvas = Image.new("RGB", (size, size), (255, 255, 255))
    card = _fit_card(card_path, 980, 1280)
    x = (size - card.width) // 2
    y = (size - card.height) // 2 - 20
    _paste_with_shadow(canvas, card, x, y)
    draw = ImageDraw.Draw(canvas)
    stand_y = y + card.height - 10
    draw.rounded_rectangle((x + 90, stand_y, x + card.width - 90, stand_y + 58),
                           radius=18, fill=(171, 121, 73), outline=(140, 92, 52), width=2)
    draw.ellipse((x + 160, stand_y + 38, x + card.width - 160, stand_y + 96), fill=(0, 0, 0, 18))
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    canvas.save(out_path, quality=94, dpi=(300, 300))
    return out_path


def render_ambiance_local(card_path, out_path):
    """本地氛围图兜底:浅木桌+花朵/杯子抽象道具,不改卡面。"""
    size = 1600
    canvas = Image.new("RGB", (size, size), (239, 222, 198))
    draw = ImageDraw.Draw(canvas)
    for y in range(0, size, 42):
        draw.line((0, y, size, y + 8), fill=(226, 204, 176), width=3)
    # background props
    draw.ellipse((1050, 170, 1460, 580), fill=(248, 241, 229), outline=(218, 198, 171), width=5)
    draw.ellipse((1120, 245, 1380, 505), fill=(231, 201, 166), outline=(183, 139, 93), width=5)
    draw.rounded_rectangle((160, 1050, 620, 1330), radius=34, fill=(247, 239, 225), outline=(214, 191, 160), width=4)
    for cx, cy, col in [(220, 330, (190, 82, 72)), (300, 260, (221, 154, 70)), (370, 360, (160, 110, 74)), (260, 410, (123, 145, 95))]:
        draw.ellipse((cx - 46, cy - 46, cx + 46, cy + 46), fill=col)
    card = _fit_card(card_path, 880, 1220)
    x = (size - card.width) // 2
    y = 190
    _paste_with_shadow(canvas, card, x, y, shadow=(65, 38, 20, 88))
    stand_y = y + card.height - 6
    draw.rounded_rectangle((x + 88, stand_y, x + card.width - 88, stand_y + 64),
                           radius=18, fill=(161, 111, 66), outline=(130, 83, 47), width=3)
    canvas = canvas.filter(ImageFilter.UnsharpMask(radius=1.2, percent=105, threshold=3))
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    canvas.save(out_path, quality=94, dpi=(300, 300))
    return out_path


def render_whitebg(card_path, out_path, backend="gemini", model=None, extra=""):
    if backend == "local_mockup":
        return render_whitebg_local(card_path, out_path)
    return _gen(card_path, out_path, (WHITEBG_PROMPT + " " + extra).strip(), backend, model)


def render_ambiance(card_path, out_path, backend="gemini", model=None, extra=""):
    if backend == "local_mockup":
        return render_ambiance_local(card_path, out_path)
    return _gen(card_path, out_path, (AMBIANCE_PROMPT + " " + extra).strip(), backend, model)


if __name__ == "__main__":
    import sys
    card = sys.argv[1] if len(sys.argv) > 1 else "card.jpg"
    print(render_whitebg(card, "whitebg_test.jpg"))
    print(render_ambiance(card, "ambiance_test.jpg"))
