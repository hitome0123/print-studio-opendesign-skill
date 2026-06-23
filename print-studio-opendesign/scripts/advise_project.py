#!/usr/bin/env python3
"""Image-first guided advisor for Print Studio OpenDesign.

Given a folder of illustrations/images, produce a first-pass design intake report:
- image traits
- product/size/material/layout/typography recommendations
- reasons and cautions

This is intentionally deterministic and lightweight. It is not a replacement for
human design judgment; it gives the next Codex/Claude turn better grounded choices.
"""
import argparse
import colorsys
import json
import math
import statistics
from pathlib import Path

from PIL import Image, ImageChops, ImageFilter, ImageStat


IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp"}


def _find_images(folder):
    folder = Path(folder).expanduser().resolve()
    if not folder.exists():
        raise SystemExit(f"图片文件夹不存在: {folder}")
    paths = [p for p in folder.iterdir() if p.suffix.lower() in IMAGE_EXTS and not p.name.startswith(".")]
    def sort_key(path):
        stem = path.stem.strip()
        prefix = ""
        for char in stem:
            if char.isdigit():
                prefix += char
            else:
                break
        return (int(prefix) if prefix else 10**9, path.name.lower())
    return sorted(paths, key=sort_key)


def _safe_mean(values):
    return statistics.mean(values) if values else 0


def _safe_stdev(values):
    return statistics.pstdev(values) if len(values) > 1 else 0


def _corner_color(img):
    w, h = img.size
    points = [
        img.getpixel((0, 0)),
        img.getpixel((w - 1, 0)),
        img.getpixel((0, h - 1)),
        img.getpixel((w - 1, h - 1)),
    ]
    return tuple(round(_safe_mean([p[i] for p in points])) for i in range(3))


def _subject_bbox_score(img):
    """Estimate subject bbox from alpha or corner-background difference."""
    rgb = img.convert("RGB")
    if img.mode in ("RGBA", "LA"):
        alpha = img.getchannel("A")
        bbox = alpha.point(lambda a: 255 if a > 16 else 0).getbbox()
    else:
        bg = Image.new("RGB", rgb.size, _corner_color(rgb))
        diff = ImageChops.difference(rgb, bg).convert("L")
        bbox = diff.point(lambda value: 255 if value > 28 else 0).getbbox()
    if not bbox:
        return {
            "bbox": None,
            "centered": 0.5,
            "coverage": 1.0,
            "edge_margin": 0.0,
        }
    w, h = rgb.size
    left, top, right, bottom = bbox
    bw, bh = right - left, bottom - top
    cx, cy = left + bw / 2, top + bh / 2
    dist = math.sqrt(((cx - w / 2) / w) ** 2 + ((cy - h / 2) / h) ** 2)
    centered = max(0, 1 - dist * 3)
    coverage = (bw * bh) / (w * h)
    edge_margin = min(left / w, top / h, (w - right) / w, (h - bottom) / h)
    return {
        "bbox": [left, top, right, bottom],
        "centered": round(centered, 3),
        "coverage": round(coverage, 3),
        "edge_margin": round(edge_margin, 3),
    }


def _analyze_image(path):
    with Image.open(path) as original:
        img = original.convert("RGB")
        img.thumbnail((900, 900))
        w, h = img.size
        stat = ImageStat.Stat(img)
        r, g, b = stat.mean
        brightness = (0.299 * r + 0.587 * g + 0.114 * b) / 255
        warmth = (r - b) / 255
        raw = img.resize((80, 80)).tobytes()
        pixels = [tuple(raw[i:i + 3]) for i in range(0, len(raw), 3)]
        hsv = [colorsys.rgb_to_hsv(px[0] / 255, px[1] / 255, px[2] / 255) for px in pixels]
        saturation = _safe_mean([item[1] for item in hsv])
        value = _safe_mean([item[2] for item in hsv])
        gray = img.convert("L")
        contrast = ImageStat.Stat(gray).stddev[0] / 128
        edge_density = ImageStat.Stat(gray.filter(ImageFilter.FIND_EDGES)).mean[0] / 255
        subject = _subject_bbox_score(img)
        ratio = w / h
        if ratio > 1.18:
            orientation = "横图"
        elif ratio < 0.85:
            orientation = "竖图"
        else:
            orientation = "近方图"
        return {
            "file": path.name,
            "width": w,
            "height": h,
            "ratio": round(ratio, 3),
            "orientation": orientation,
            "brightness": round(brightness, 3),
            "saturation": round(saturation, 3),
            "value": round(value, 3),
            "warmth": round(warmth, 3),
            "contrast": round(contrast, 3),
            "edge_density": round(edge_density, 3),
            **subject,
        }


def _classify(summary):
    brightness = summary["avg_brightness"]
    saturation = summary["avg_saturation"]
    contrast = summary["avg_contrast"]
    edge = summary["avg_edge_density"]
    warmth = summary["avg_warmth"]
    centered = summary["avg_centered"]
    coverage = summary["avg_coverage"]
    aspect = summary["avg_ratio"]
    count = summary["count"]
    if aspect > 1.18:
        orientation = "横向为主"
    elif aspect < 0.85:
        orientation = "竖向为主"
    else:
        orientation = "方形/接近方形为主"
    color_mood = "柔和浅色" if brightness > 0.72 and saturation < 0.35 else "鲜明高对比" if saturation > 0.42 or contrast > 0.52 else "中性色彩"
    detail_level = "细节丰富" if edge > 0.16 or contrast > 0.55 else "画面干净" if edge < 0.09 else "细节适中"
    composition = "主体居中" if centered > 0.72 else "主体偏移/构图自由"
    fill = "主体较满" if coverage > 0.62 else "留白较多" if coverage < 0.34 else "主体占比适中"
    temperature = "偏暖" if warmth > 0.05 else "偏冷" if warmth < -0.05 else "冷暖中性"
    series = "适合做完整系列" if count >= 10 else "适合做小套装" if count >= 4 else "适合先做单张/小样"
    return {
        "orientation": orientation,
        "color_mood": color_mood,
        "detail_level": detail_level,
        "composition": composition,
        "fill": fill,
        "temperature": temperature,
        "series": series,
    }


def _add_reco(items, title, reason, caution=None, default=False):
    items.append({
        "title": title,
        "reason": reason,
        "caution": caution or "",
        "default": default,
    })


def _recommend(summary, traits):
    count = summary["count"]
    aspect = summary["avg_ratio"]
    brightness = summary["avg_brightness"]
    saturation = summary["avg_saturation"]
    contrast = summary["avg_contrast"]
    edge = summary["avg_edge_density"]
    centered = summary["avg_centered"]
    coverage = summary["avg_coverage"]

    products = []
    if aspect < 0.85:
        _add_reco(products, "5×7 英寸贺卡 / 插画卡", "这组图偏竖向，5×7 能保留主体完整，也有空间放标题或祝福语。", default=True)
        if count >= 10:
            _add_reco(products, "12 张月历卡", "图片数量足够做月份系列，竖向构图也适合上图下日历。", "需要检查每张图风格是否足够统一。")
        _add_reco(products, "8×12 英寸挂历", "竖向图片适合做大尺寸展示，视觉冲击更强。", "顶部线圈/挂孔要预留装订安全区。")
    elif aspect > 1.18:
        _add_reco(products, "7×5 英寸横版明信片", "这组图偏横向，横版明信片能减少裁切，适合风景或横向场景图。", default=True)
        _add_reco(products, "横版邀请卡 / 包装插卡", "横图适合一侧放图、一侧放文字信息。", "文字区要避免压住主体。")
    else:
        _add_reco(products, "5×5 英寸方卡", "图片接近方形，方卡会更有礼品感和套装感。", default=True)
        _add_reco(products, "5×7 英寸贺卡", "如果需要更多文字空间，可以使用竖版卡并保留上下留白。")
        if count >= 10:
            _add_reco(products, "12 张月历卡", "图片数量足够做完整月份系列，方形图也适合做上方插画、下方日历的结构。", "需要确认是否要真实日期，以及月份文字放在何处。")
    if count >= 4:
        _add_reco(products, f"{count} 张自定义套装", "素材数量已经具备系列化基础，可以先按现有张数做一套。")

    sizes = []
    if aspect < 0.85:
        _add_reco(sizes, "5×7 英寸", "最适合竖向插画，画面空间够，印刷和展示都稳。", default=True)
        _add_reco(sizes, "4×6 英寸", "更轻巧，适合随包卡或小贺卡。", "细节丰富的图缩小后要检查清晰度。")
        _add_reco(sizes, "8×12 英寸", "适合挂历或大图展示。", "需要更多图片分辨率和装订预留。")
    elif aspect > 1.18:
        _add_reco(sizes, "7×5 英寸", "匹配横向构图，裁切风险低。", default=True)
        _add_reco(sizes, "4×6 英寸横版", "适合轻量明信片或信息卡。")
    else:
        _add_reco(sizes, "5×5 英寸", "匹配方形构图，适合可爱、艺术、礼品感系列。", default=True)
        _add_reco(sizes, "5×7 英寸", "需要标题和文案时更好排。")

    materials = []
    _add_reco(materials, "300g 超白白卡纸", "最稳定，能保持图片干净明亮，适合首轮打样。", default=True)
    if brightness > 0.68 and saturation < 0.38:
        _add_reco(materials, "300g 冰白珠光纸", "图片偏柔和浅色，珠光能增加礼品感和梦幻感。", "小字要加深，浅色区域要检查发灰。")
        _add_reco(materials, "300g 雅白细莱妮纹", "适合温柔、复古、高级留白方向。", "纹理会削弱极细线条。")
        _add_reco(materials, "不优先选牛皮纸", "这组图偏浅，牛皮底色可能让画面变灰变脏。", "除非明确想要复古手作感。")
    elif saturation > 0.42 or contrast > 0.52:
        _add_reco(materials, "300g 超白白卡纸", "高饱和或高对比图用白卡最容易保住色彩。", default=True)
        _add_reco(materials, "310g 黑芯纸", "如果想做更厚、更高级的卡牌感，可以考虑黑芯。", "浅色边缘和温柔风格需先看预览。")
    else:
        _add_reco(materials, "300g 超白细莱妮纹", "画面细节适中，细纹理能增加纸品质感。")
        _add_reco(materials, "300g 白芯纸", "适合预算型厚卡，但透光性和纸芯效果要预览确认。")
    if edge > 0.16:
        _add_reco(materials, "谨慎选择强纹理纸", "图片细节丰富，强纹理可能吃掉小细节。")

    layouts = []
    if centered > 0.72 and coverage < 0.62:
        _add_reco(layouts, "插画居中 + 下方标题", "主体居中且有留白，经典稳定，适合贺卡和月历卡。", default=True)
        _add_reco(layouts, "小插画 + 大留白 + 手写风文字", "留白条件不错，可以做更文艺、更轻盈的高级感。")
    elif coverage > 0.62:
        _add_reco(layouts, "大插画满版 + 小标题", "主体占比较满，应该突出图本身，减少文字干扰。", default=True)
        _add_reco(layouts, "底部窄信息区", "如果必须放标题/日期，建议只留底部一条清楚信息区。", "避免文字压在复杂画面上。")
    else:
        _add_reco(layouts, "上方插画 + 下方留白文字区", "主体占比适中，适合在下方放标题、日期或祝福语。", default=True)
        _add_reco(layouts, "AI 自动排版", "不同图片构图可能不同，让系统逐张选择更稳。")
    if aspect > 1.18:
        _add_reco(layouts, "左右分栏", "横图适合左图右文或上图下文，信息层级更清楚。")
    if count >= 4:
        _add_reco(layouts, "系列总览网格", "多张图需要放在一起看统一性，建议输出系列总览。")

    typography = []
    if traits["color_mood"] == "柔和浅色":
        _add_reco(typography, "优雅衬线标题 + 低调无衬线小字", "柔和图片适合轻盈、有礼品感的文字层级。", default=True)
        _add_reco(typography, "手写风点缀", "可以增加温度，但只适合标题或短句。", "手写小字不能太小，印刷容易糊。")
    elif traits["detail_level"] == "细节丰富":
        _add_reco(typography, "清晰无衬线标题 + 中等字重", "复杂画面需要字体更清楚，避免被背景吃掉。", default=True)
        _add_reco(typography, "避免过细花体", "细花体在复杂背景和印刷中识别风险高。")
    else:
        _add_reco(typography, "复古衬线 + 小号大写副标题", "适合中性色彩、自然插画、植物志方向。", default=True)
        _add_reco(typography, "圆润无衬线", "如果图片偏可爱，可以提升亲和力。")

    provider = [
        {
            "title": "先跑即梦 / Gemini / GPT-Image2 三模型预览",
            "reason": "先用 1 张图比较白底图和氛围图稳定性，再决定后续批量使用哪个模型。",
            "caution": "默认不要全量跑，避免浪费额度；缺 API 时只生成错误说明页。",
            "default": True,
        }
    ]

    prepress = []
    if brightness > 0.72 and saturation < 0.35:
        _add_reco(prepress, "印刷版提高饱和度和文字对比", "图片偏浅，印出来容易更灰，需要比屏幕版更扎实。", default=True)
    if edge > 0.16:
        _add_reco(prepress, "检查细节缩小后的清晰度", "细节丰富的图做小卡时容易糊，需要看 100% 输出。", default=True)
    _add_reco(prepress, "保留出血和安全边距", "所有重要文字和主体不能靠边，避免裁切误差。", default=True)
    _add_reco(prepress, "展示图与印刷文件分离", "白底图/氛围图用于确认和展示，生产仍以 print/ 为准。", default=True)

    return {
        "products": products,
        "sizes": sizes,
        "materials": materials,
        "layouts": layouts,
        "typography": typography,
        "provider_previews": provider,
        "prepress_checks": prepress,
    }


def _summarize(images):
    return {
        "count": len(images),
        "avg_ratio": round(_safe_mean([i["ratio"] for i in images]), 3),
        "ratio_stdev": round(_safe_stdev([i["ratio"] for i in images]), 3),
        "avg_brightness": round(_safe_mean([i["brightness"] for i in images]), 3),
        "avg_saturation": round(_safe_mean([i["saturation"] for i in images]), 3),
        "avg_warmth": round(_safe_mean([i["warmth"] for i in images]), 3),
        "avg_contrast": round(_safe_mean([i["contrast"] for i in images]), 3),
        "avg_edge_density": round(_safe_mean([i["edge_density"] for i in images]), 3),
        "avg_centered": round(_safe_mean([i["centered"] for i in images]), 3),
        "avg_coverage": round(_safe_mean([i["coverage"] for i in images]), 3),
        "brightness_stdev": round(_safe_stdev([i["brightness"] for i in images]), 3),
        "saturation_stdev": round(_safe_stdev([i["saturation"] for i in images]), 3),
    }


def _md_choice_list(items):
    lines = []
    for idx, item in enumerate(items, 1):
        marker = "（默认推荐）" if item.get("default") else ""
        lines.append(f"{idx}. **{item['title']}**{marker}")
        lines.append(f"   - 理由：{item['reason']}")
        if item.get("caution"):
            lines.append(f"   - 注意：{item['caution']}")
    return "\n".join(lines)


def _write_report(payload, out_path):
    traits = payload["traits"]
    summary = payload["summary"]
    rec = payload["recommendations"]
    lines = [
        "# Print Studio OpenDesign · 图片优先打样建议",
        "",
        "## 1. 图片初步判断",
        "",
        f"- 图片数量：{summary['count']} 张",
        f"- 构图方向：{traits['orientation']}",
        f"- 色彩气质：{traits['color_mood']}，{traits['temperature']}",
        f"- 画面复杂度：{traits['detail_level']}",
        f"- 主体位置：{traits['composition']}，{traits['fill']}",
        f"- 系列判断：{traits['series']}",
        "",
        "## 2. 建议先问的选择",
        "",
        "### 产品方向",
        "",
        _md_choice_list(rec["products"]),
        "",
        "### 尺寸方向",
        "",
        _md_choice_list(rec["sizes"]),
        "",
        "### 材质方向",
        "",
        _md_choice_list(rec["materials"]),
        "",
        "### 排版方向",
        "",
        _md_choice_list(rec["layouts"]),
        "",
        "### 字体方向",
        "",
        _md_choice_list(rec["typography"]),
        "",
        "### 首轮模型预览",
        "",
        _md_choice_list(rec["provider_previews"]),
        "",
        "### 印刷检查重点",
        "",
        _md_choice_list(rec["prepress_checks"]),
        "",
        "## 3. 可以直接这样引导",
        "",
        "我先看了这组图片，建议我们不要盲选规格，而是按图片特征来定：",
        "",
        f"- 这组图整体是 **{traits['orientation']}**，所以优先推荐上面的产品和尺寸。",
        f"- 色彩属于 **{traits['color_mood']}**，材质上要优先考虑能保持干净度和对比的纸张。",
        f"- 画面是 **{traits['detail_level']}**，排版时要避免文字压住主体，也要检查缩小后的印刷清晰度。",
        "",
        "你可以先从默认推荐里选，也可以告诉我：更想要高级感、可爱感、礼品感，还是成本更友好。",
        "",
        "## 4. 图片明细",
        "",
        "| 文件 | 方向 | 亮度 | 饱和 | 对比 | 主体居中 | 主体占比 |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for item in payload["images"]:
        lines.append(
            f"| {item['file']} | {item['orientation']} | {item['brightness']} | {item['saturation']} | "
            f"{item['contrast']} | {item['centered']} | {item['coverage']} |"
        )
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description="Analyze images and produce guided print design recommendations.")
    parser.add_argument("illustrations_dir", help="图片文件夹，建议包含 1.png, 2.png ...")
    parser.add_argument("--out", default=None, help="Markdown 报告输出路径，默认写到图片文件夹旁边")
    parser.add_argument("--json", default=None, help="可选：同时输出结构化 JSON")
    parser.add_argument("--max-images", type=int, default=12, help="最多分析多少张图片")
    args = parser.parse_args()

    paths = _find_images(args.illustrations_dir)
    if not paths:
        raise SystemExit(f"未找到图片: {args.illustrations_dir}")
    sample_paths = paths[: args.max_images]
    images = [_analyze_image(path) for path in sample_paths]
    summary = _summarize(images)
    traits = _classify(summary)
    recommendations = _recommend(summary, traits)
    payload = {
        "source_dir": str(Path(args.illustrations_dir).expanduser().resolve()),
        "summary": summary,
        "traits": traits,
        "recommendations": recommendations,
        "images": images,
    }
    source_dir = Path(args.illustrations_dir).expanduser().resolve()
    out_path = Path(args.out).expanduser().resolve() if args.out else source_dir.parent / "print_studio_advice.md"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    _write_report(payload, out_path)
    if args.json:
        json_path = Path(args.json).expanduser().resolve()
        json_path.parent.mkdir(parents=True, exist_ok=True)
        json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"advice -> {out_path}")
    if args.json:
        print(f"json -> {json_path}")


if __name__ == "__main__":
    main()
