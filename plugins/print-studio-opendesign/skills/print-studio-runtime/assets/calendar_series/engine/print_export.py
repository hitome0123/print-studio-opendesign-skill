#!/usr/bin/env python3
"""
② 印刷体系 · 尺寸模板 + 出血/安全边距 + 300dpi 印刷文件 + 打包
- build_print_file:把渲染好的设计图 → 目标尺寸印刷文件(暖白底,含出血,300dpi)
  + 同时出一张 _guide 预览(画 trim 裁切线 + safe 安全线,仅供内部核对,不进交付)
- build_package:把 screen/print/commerce 各版本打包成交付 zip
注意:当前渲染器是 1:1 版式;目标尺寸非 1:1 时,设计居中置于暖白卡面(留边),
      并在日志提示"满版适配(full-bleed 自适应版式)属 ③ AI排版脑"。
"""
import zipfile
from pathlib import Path
from PIL import Image, ImageDraw
from profiles import apply_profile, WARM_WHITE

MM_PER_IN = 25.4


def _contain(img, w, h):
    iw, ih = img.size
    s = min(w / iw, h / ih)
    return img.resize((max(1, round(iw * s)), max(1, round(ih * s))), Image.LANCZOS)


def build_print_file(design_img, size, material, out_path, saturation_boost_pct=None):
    """design_img: PIL(已渲染设计) ; size: resolved.size dict ; 返回 (print_path, guide_path, note)"""
    dpi = size.get("dpi", 300)
    trim_w, trim_h = size["trim_px"]
    bleed_w, bleed_h = size["bleed_px"]
    bl_x = (bleed_w - trim_w) // 2
    bl_y = (bleed_h - trim_h) // 2
    safe_mm = size.get("safe_margin_mm", 5.0)
    safe_px = round(safe_mm / MM_PER_IN * dpi)

    # 1) 色彩:印刷 profile + 材质补偿
    art = apply_profile(design_img, "print_output", material, saturation_boost_pct)

    # 2) 出血底色 = 取设计角落自身底色(暖,且与设计无缝),取不到再兜底暖白
    try:
        fill = art.getpixel((1, 1))
    except Exception:
        fill = WARM_WHITE
    canvas = Image.new("RGB", (bleed_w, bleed_h), fill)
    fitted = _contain(art, trim_w, trim_h)
    fx = bl_x + (trim_w - fitted.size[0]) // 2
    fy = bl_y + (trim_h - fitted.size[1]) // 2
    canvas.paste(fitted, (fx, fy))

    note = ""
    aspect_design = design_img.size[0] / design_img.size[1]
    aspect_trim = trim_w / trim_h
    if abs(aspect_design - aspect_trim) > 0.02:
        note = f"设计{aspect_design:.2f} vs 成品{aspect_trim:.2f} 比例不同→设计居中留暖白边;满版自适应版式属③"

    # 3) 存印刷文件(300dpi)
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    canvas.save(out_path, quality=96, dpi=(dpi, dpi))

    # 4) 出一张 guide(trim 红线 + safe 青线),仅内部核对
    guide = canvas.copy()
    g = ImageDraw.Draw(guide)
    g.rectangle([bl_x, bl_y, bl_x + trim_w - 1, bl_y + trim_h - 1], outline=(220, 60, 60), width=4)        # 裁切线
    g.rectangle([bl_x + safe_px, bl_y + safe_px, bl_x + trim_w - safe_px, bl_y + trim_h - safe_px],
                outline=(60, 160, 200), width=3)                                                            # 安全线
    guide_path = str(Path(out_path).with_name("_guide_" + Path(out_path).name))
    guide.save(guide_path, quality=88, dpi=(dpi, dpi))
    return out_path, guide_path, note


def build_package(version_dirs, zip_path):
    """version_dirs: {版本名: 目录Path} → 打成一个交付 zip(跳过 _guide 与 resolved 之外的内部件)"""
    zip_path = Path(zip_path)
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        for ver, d in version_dirs.items():
            d = Path(d)
            if not d.exists():
                continue
            if d.is_file():
                z.write(d, arcname=ver)
                continue
            for f in sorted(d.rglob("*")):
                if f.is_file() and not f.name.startswith("_guide_"):
                    z.write(f, arcname=f"{ver}/{f.relative_to(d)}")
    return str(zip_path)
