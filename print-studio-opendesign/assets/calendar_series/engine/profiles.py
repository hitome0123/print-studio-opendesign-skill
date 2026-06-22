#!/usr/bin/env python3
"""
② 印刷体系 · 三套色彩 profile + 材质补偿接口
- screen_preview:客户线上看,柔和轻盈(接近原渲染)
- print_output  :印刷交付,高级饱和(+~12%)+对比+锐化,暖白底不发灰,文字可读
- commerce_mockup:D/E 电商图,更亮更通透
材质补偿(PAPER_COMP)= 基于客户纸张清单的预估分组;未打样前均视为初始值。
铁律:印刷源(print)与电商图(commerce)分开,互不污染。
"""
from PIL import Image, ImageEnhance, ImageFilter

# ── 暖白基准(印刷底色不能灰,偏奶油/象牙)──
WARM_WHITE = (250, 247, 240)

# ── 三套版本基准参数(乘数)──
VERSION_BASE = {
    "screen_preview":  {"saturation": 1.00, "contrast": 1.00, "brightness": 1.00, "sharpness": 1.00},
    "print_output":    {"saturation": 1.12, "contrast": 1.06, "brightness": 1.00, "sharpness": 1.12},
    "commerce_mockup": {"saturation": 1.06, "contrast": 1.03, "brightness": 1.05, "sharpness": 1.05},
}

# ── 材质补偿(预估值):批量印刷前仍需打样校准 ──
PAPER_COMP = {
    "standard": {"saturation": 1.00, "contrast": 1.00, "brightness": 1.00, "detail_blur": 0.0, "text_gamma": 1.00},
    "fine_textured":  {"saturation": 1.05, "contrast": 1.04, "brightness": 1.00, "detail_blur": 0.0, "text_gamma": 0.96},
    "textured":       {"saturation": 1.08, "contrast": 1.06, "brightness": 1.00, "detail_blur": 0.15, "text_gamma": 0.94},
    "heavy_textured": {"saturation": 1.12, "contrast": 1.08, "brightness": 1.01, "detail_blur": 0.25, "text_gamma": 0.92},
    "kraft":          {"saturation": 1.14, "contrast": 1.12, "brightness": 1.04, "detail_blur": 0.15, "text_gamma": 0.90},
    "pearl":          {"saturation": 1.06, "contrast": 1.08, "brightness": 0.99, "detail_blur": 0.0, "text_gamma": 0.93},
    "pvc":            {"saturation": 0.98, "contrast": 1.04, "brightness": 1.00, "detail_blur": 0.0, "text_gamma": 1.00},
    "budget_core":    {"saturation": 1.10, "contrast": 1.08, "brightness": 1.01, "detail_blur": 0.0, "text_gamma": 0.94},
    "premium_core":   {"saturation": 1.04, "contrast": 1.04, "brightness": 1.00, "detail_blur": 0.0, "text_gamma": 0.98},
    "matte":          {"saturation": 1.07, "contrast": 1.06, "brightness": 1.00, "detail_blur": 0.0, "text_gamma": 0.96},
}


def _paper_for(material):
    """material = resolved.material dict(含 color_comp);返回补偿乘数,未知→白卡基准"""
    key = (material or {}).get("color_comp", "standard")
    return PAPER_COMP.get(key, PAPER_COMP["standard"])


def apply_profile(img, version, material=None, saturation_boost_pct=None):
    """对已渲染图应用某版本色彩 profile(+材质补偿)。version 取 VERSION_BASE 的 key。"""
    base = VERSION_BASE.get(version, VERSION_BASE["screen_preview"])
    pc = _paper_for(material)
    img = img.convert("RGB")

    sat = base["saturation"] * pc["saturation"]
    if saturation_boost_pct is not None:          # advanced 覆盖(0~30 → 额外乘数)
        sat *= (1 + saturation_boost_pct / 100.0)
    img = ImageEnhance.Color(img).enhance(sat)
    img = ImageEnhance.Contrast(img).enhance(base["contrast"] * pc["contrast"])
    img = ImageEnhance.Brightness(img).enhance(base["brightness"] * pc["brightness"])
    img = ImageEnhance.Sharpness(img).enhance(base["sharpness"])
    if pc.get("detail_blur", 0):                  # 纹理纸减细节(防细线印断)
        img = img.filter(ImageFilter.GaussianBlur(pc["detail_blur"]))
    if pc.get("text_gamma", 1.0) != 1.0:          # 加深文字(吸墨纸)
        g = pc["text_gamma"]
        lut = [min(255, int((i / 255) ** (1 / g) * 255)) for i in range(256)] * 3
        img = img.point(lut)
    return img


if __name__ == "__main__":
    import sys
    src = sys.argv[1]
    im = Image.open(src)
    for v in VERSION_BASE:
        apply_profile(im, v).save(f"/tmp/profile_{v}.jpg", quality=95, dpi=(300, 300))
        print("ok", v)
