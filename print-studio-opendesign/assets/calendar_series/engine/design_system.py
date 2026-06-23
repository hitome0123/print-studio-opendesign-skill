#!/usr/bin/env python3
"""Design system helpers for Print Studio OpenDesign.

This module turns design inspirations into explicit artifacts:
- Figma-like typography/layout/color presets
- CreatiPoster-like structured design plans
- PromptInfuser-like explanations for why choices affect prompts/rules
"""
import json
from pathlib import Path
from PIL import Image

HERE = Path(__file__).resolve().parents[1]
PRESETS_PATH = HERE / "design_presets.json"


def load_design_presets():
    return json.loads(PRESETS_PATH.read_text(encoding="utf-8"))


def _select_typography(resolved, plan, template):
    presets = load_design_presets()["typography"]
    material = resolved.get("material", {}) or {}
    style = (resolved.get("style", {}) or {}).get("key", "")
    product = (resolved.get("product_type", {}) or {}).get("key", "")
    density = plan.get("density", "medium")
    if "child" in style or "kids" in style:
        key = "playful_rounded"
    elif template == "calendar_series" or "botanical" in style:
        key = "vintage_serif_caps"
    elif density == "dense" or product in {"packaging_insert", "postcard"}:
        key = "clean_sans"
    elif material.get("texture_level") in {"fine", "medium", "strong"}:
        key = "elegant_serif"
    else:
        key = "elegant_serif"
    return {"key": key, **presets[key]}


def _select_layout(meta, plan, template):
    presets = load_design_presets()["layouts"]
    family = meta.get("family")
    product = meta.get("product_type", "")
    density = plan.get("density", "medium")
    if template == "calendar_series":
        key = "center_art_title_bottom"
    elif family == "landscape":
        key = "left_right_split"
    elif product == "bookmark":
        key = "top_art_bottom_text"
    elif density == "dense":
        key = "full_art_small_title"
    elif density == "airy":
        key = "large_whitespace"
    else:
        key = "top_art_bottom_text"
    return {"key": key, **presets[key]}


def _select_color(resolved, plan):
    presets = load_design_presets()["colors"]
    material = resolved.get("material", {}) or {}
    tone = material.get("paper_tone", "")
    if tone == "超白":
        key = "clean_white"
    elif tone in {"雅白", "冰白"}:
        key = "ivory"
    else:
        key = "warm_cream"
    text_key = "deep_warm_text"
    return {
        "background": {"key": key, **presets[key]},
        "text": {"key": text_key, **presets[text_key]},
        "accent": {
            "label": "受限复古强调色",
            "value": plan.get("accent"),
            "reason": "标题强调色来自受限调色板，保证系列统一，不让 AI 随意漂色。"
        }
    }


def _image_info(image_path):
    path = Path(image_path)
    with Image.open(path) as img:
        width, height = img.size
    return {
        "file": path.name,
        "path": str(path),
        "width_px": width,
        "height_px": height,
        "ratio": round(width / height, 3) if height else None,
    }


def _prompt_effects(resolved, typography, layout, color):
    material = resolved.get("material", {}) or {}
    effects = [
        {
            "choice": layout["label"],
            "effect": "排版提示词会锁定图文结构，避免模型随意改产品形态。",
        },
        {
            "choice": typography["label"],
            "effect": "字体提示词会限制标题/小字层级，并提醒小字可读性。",
        },
        {
            "choice": color["background"]["label"],
            "effect": "背景和印刷补偿会优先保持纸感、对比和干净度。",
        },
    ]
    if material.get("texture_level") in {"fine", "medium", "strong"}:
        effects.append({
            "choice": material.get("paper_type", "纹理纸"),
            "effect": "纹理纸会提示减少极细线条、加深小字，避免印刷后被纹理吃掉。",
        })
    if material.get("color_comp") == "pearl":
        effects.append({
            "choice": "珠光纸",
            "effect": "展示图可模拟轻微反光，但印刷文件仍保持清晰文字和主体对比。",
        })
    return effects


def build_design_plan(index, image_path, raw_plan, render_meta, resolved, template):
    typography = _select_typography(resolved, raw_plan, template)
    layout = _select_layout(render_meta, raw_plan, template)
    color = _select_color(resolved, raw_plan)
    image = _image_info(image_path)
    size = resolved.get("size", {}) or {}
    material = resolved.get("material", {}) or {}
    production = resolved.get("production", {}) or {}
    layers = [
        {
            "name": "background",
            "type": "color/material",
            "preset": color["background"]["key"],
            "role": "承载纸张底色和材质感，不参与印刷尺寸变化。",
        },
        {
            "name": "illustration",
            "type": "image",
            "source": image["file"],
            "bbox": render_meta.get("content_bbox"),
            "role": "主视觉锚点，排版和展示图都必须保留主体完整。",
        },
        {
            "name": "title_text",
            "type": "text",
            "typography_preset": typography["key"],
            "role": "标题/月标题/主文案，必须保持印刷后可读。",
        },
    ]
    if template == "calendar_series":
        layers.append({
            "name": "calendar_grid",
            "type": "date/text",
            "role": "真实日期层，由规则引擎生成，不允许 AI 改日期。",
        })
    layers.append({
        "name": "production_safety",
        "type": "print-rule",
        "safe_margin_mm": size.get("safe_margin_mm"),
        "bleed_mm": size.get("bleed_mm"),
        "binding": production.get("binding", "none"),
        "role": "出血、安全边距、装订预留由确定性规则兜底。",
    })
    return {
        "index": index,
        "template": template,
        "source_image": image,
        "raw_layout_plan": raw_plan,
        "layout_preset": layout,
        "typography_preset": typography,
        "color_preset": color,
        "material_context": {
            "key": material.get("key"),
            "label": material.get("label"),
            "texture_level": material.get("texture_level"),
            "color_comp": material.get("color_comp"),
        },
        "layers": layers,
        "prompt_rule_effects": _prompt_effects(resolved, typography, layout, color),
        "manual_review": [
            "确认主体没有被裁切或压字。",
            "确认小字、日期、印章在实际尺寸下可读。",
            "确认材质纹理、珠光、PVC 光泽以实物纸样和打样为准。",
        ],
    }


def write_design_plan(out_base, design_plans):
    path = Path(out_base) / "design_plan.json"
    path.write_text(json.dumps(design_plans, ensure_ascii=False, indent=2), encoding="utf-8")
    return path
