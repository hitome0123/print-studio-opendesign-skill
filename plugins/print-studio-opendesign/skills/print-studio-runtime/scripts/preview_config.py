#!/usr/bin/env python3
"""Generate fast no-AI previews for the selected size/material/product config."""
import json
import re
import sys
from copy import deepcopy
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

SKILL_ROOT = Path(__file__).resolve().parents[1]
ENGINE_ROOT = SKILL_ROOT / "assets" / "calendar_series"
sys.path.insert(0, str(ENGINE_ROOT / "engine"))

from config_schema import resolve_config, _fmt  # noqa: E402
from layout_engine import render_page  # noqa: E402
from generic_card_engine import render_generic_card  # noqa: E402
from profiles import apply_profile  # noqa: E402
from print_export import build_print_file  # noqa: E402
import ai_planner  # noqa: E402


def _prepare_config(config_path: Path) -> Path:
    cfg = json.loads(config_path.read_text(encoding="utf-8"))
    illustrations = Path(cfg.get("illustrations_dir", "example_illustrations"))
    if not illustrations.is_absolute():
        local_candidate = (config_path.parent / illustrations).resolve()
        bundled_candidate = (ENGINE_ROOT / illustrations).resolve()
        if local_candidate.exists():
            cfg["illustrations_dir"] = str(local_candidate)
        elif bundled_candidate.exists():
            cfg["illustrations_dir"] = str(bundled_candidate)
        else:
            cfg["illustrations_dir"] = str(local_candidate)
    tmp_dir = SKILL_ROOT / ".tmp"
    tmp_dir.mkdir(exist_ok=True)
    prepared = tmp_dir / "preview_config.resolved.json"
    prepared.write_text(json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8")
    return prepared


def _find_first_illustration(folder):
    folder = Path(folder)
    candidates = []
    for path in folder.iterdir():
        if path.suffix.lower() in (".png", ".jpg", ".jpeg"):
            match = re.match(r"\s*(\d+)", path.name)
            if match:
                candidates.append((int(match.group(1)), path))
    if not candidates:
        raise SystemExit(f"No numbered illustrations found in {folder}")
    return sorted(candidates)[0]


def _texture_overlay(img, material):
    im = img.convert("RGB")
    tone = material.get("paper_tone", "超白")
    texture = material.get("texture_level", "none")
    color_comp = material.get("color_comp", "standard")
    paper_type = material.get("paper_type", "")
    overlay = Image.new("RGB", im.size, (255, 255, 255))
    draw = ImageDraw.Draw(overlay)
    tone_color = {
        "超白": (252, 251, 247),
        "雅白": (248, 243, 232),
        "冰白": (250, 250, 244),
        "牛皮": (215, 181, 124),
        "白芯": (250, 248, 241),
        "蓝芯": (248, 249, 246),
        "黑芯": (247, 247, 244),
    }.get(tone, (250, 247, 240))
    im = Image.blend(im, Image.new("RGB", im.size, tone_color), 0.10 if tone != "牛皮" else 0.22)
    width, height = im.size
    if texture in ("fine", "medium", "strong", "pearl", "plastic") or color_comp in ("textured", "fine_textured", "heavy_textured", "pearl"):
        step = 9 if texture == "fine" else 13 if texture == "medium" else 18
        alpha = 30 if texture == "fine" else 42 if texture == "medium" else 56
        if texture == "pearl" or color_comp == "pearl":
            alpha = 44
            for x in range(-height, width, 24):
                draw.line([(x, height), (x + height, 0)], fill=(238, 232, 210), width=2)
            for x in range(36, width, 120):
                for y in range(28, height, 180):
                    draw.ellipse((x, y, x + 5, y + 5), fill=(255, 250, 220))
        elif texture == "plastic" or color_comp == "pvc":
            for y in range(0, height, 24):
                draw.line([(0, y), (width, y)], fill=(238, 238, 235), width=1)
            for x in range(-height, width, 110):
                draw.line([(x, height), (x + height, 0)], fill=(255, 255, 255), width=7)
            alpha = 34
        else:
            for y in range(0, height, step):
                draw.line([(0, y), (width, y + (y % 3) - 1)], fill=(226, 218, 203), width=1)
            for x in range(0, width, step + 4):
                draw.line([(x, 0), (x + (x % 5) - 2, height)], fill=(232, 226, 214), width=1)
        overlay = overlay.filter(ImageFilter.GaussianBlur(0.4))
        im = Image.blend(im, overlay, alpha / 255.0)
    if "白芯" in paper_type or "蓝芯" in paper_type or "黑芯" in paper_type:
        core_color = (236, 236, 230)
        if "蓝芯" in paper_type:
            core_color = (88, 128, 178)
        elif "黑芯" in paper_type:
            core_color = (45, 45, 43)
        draw = ImageDraw.Draw(im)
        strip = max(10, round(width * 0.025))
        shadow = max(4, round(strip * 0.25))
        draw.rectangle((0, 0, strip, height), fill=core_color)
        draw.rectangle((strip, 0, strip + shadow, height), fill=(226, 220, 210))
        draw.rectangle((0, 0, width - 1, height - 1), outline=core_color, width=max(3, round(strip * 0.22)))
    return im


def _sales_tip(material):
    paper_type = material.get("paper_type", "")
    texture = material.get("texture_level", "")
    color_comp = material.get("color_comp", "")
    tone = material.get("paper_tone", "")
    if "牛皮" in paper_type:
        return "适合复古自然风；浅色图和小字需加深对比"
    if color_comp == "pvc":
        return "适合防水耐磨卡牌；注意光面/磨砂面确认"
    if color_comp == "pearl":
        return "适合礼品感和节日卡；小字不要太浅"
    if "蓝芯" in paper_type:
        return "适合中高端卡牌；蓝色为纸芯抗透光层"
    if "黑芯" in paper_type:
        return "适合高端卡牌；抗透光强，侧边可见深色芯"
    if "白芯" in paper_type:
        return "适合预算档卡片；普通纸感，透光性需注意"
    if texture == "strong":
        return "强纹理手作感；细线小字需谨慎"
    if texture in ("fine", "medium"):
        return "适合艺术卡/礼品卡；纹理会削弱极细细节"
    if tone == "雅白":
        return "适合柔和复古主题；背景避免过灰"
    return "通用安全材质；适合日历卡/贺卡/明信片"


def _load_presets():
    return json.loads((ENGINE_ROOT / "presets.json").read_text(encoding="utf-8"))


def _write_html(out_dir, resolved, paths):
    material = resolved["material"]
    size = resolved["size"]
    rows = "".join(f'<figure><img src="{path.name}"><figcaption>{label}</figcaption></figure>' for label, path in paths)
    html = f"""<!doctype html><html lang="zh"><meta charset="utf-8">
<title>{resolved['theme']} · 配置预览</title>
<style>
body{{font-family:-apple-system,BlinkMacSystemFont,'PingFang SC',sans-serif;background:#f6f2ea;color:#332f2a;margin:0;padding:36px}}
header{{max-width:1120px;margin:0 auto 24px}} h1{{font-size:30px;margin:0 0 8px}} p{{color:#7c746a;line-height:1.7}}
.meta{{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:10px;margin:18px 0}}
.card{{background:#fff;border:1px solid #e7ded2;border-radius:12px;padding:12px 14px}}
.grid{{max-width:1120px;margin:0 auto;display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:18px}}
figure{{margin:0;background:white;border:1px solid #e7ded2;border-radius:12px;padding:12px;box-shadow:0 6px 24px rgba(60,48,36,.06)}}
img{{width:100%;display:block;border-radius:8px}} figcaption{{font-size:13px;color:#7c746a;text-align:center;margin-top:8px}}
</style><header><h1>{resolved['theme']} · 配置预览</h1>
<p>用于确认尺寸、材质、版式和印刷边界。材质纹理为视觉模拟,不等同于真实打样。</p>
<div class="meta"><div class="card"><b>尺寸</b><br>{size['label']}<br>{size.get('trim_px')} px @ {size['dpi']}dpi</div>
<div class="card"><b>材质</b><br>{material['label']}<br>{material.get('use_case','')}</div>
<div class="card"><b>纸张补偿</b><br>{material.get('color_comp')} · {material.get('texture_level')}</div>
<div class="card"><b>输出</b><br>设计预览 / 材质模拟 / 印刷 guide</div></div></header><section class="grid">{rows}</section></html>"""
    (out_dir / "preview.html").write_text(html, encoding="utf-8")


def _write_material_selector(out_dir, resolved, material_cards):
    size = resolved["size"]
    rows = "".join(
        f"""
        <article class="material-card {'selected' if card['selected'] else ''}">
          <img src="{card['image']}" alt="{card['label']}">
          <div class="body"><div class="title">{card['label']}</div>
          <div class="meta">#{card['source_no']} · {card['status']} · {card['color_comp']} · {card['texture_level']}</div>
          <p>{card['use_case']}</p><div class="tip">{card['sales_tip']}</div><code>{card['key']}</code></div>
        </article>"""
        for card in material_cards
    )
    html = f"""<!doctype html><html lang="zh"><meta charset="utf-8">
<title>{resolved['theme']} · 材质选择预览</title>
<style>
body{{font-family:-apple-system,BlinkMacSystemFont,'PingFang SC',sans-serif;background:#f6f2ea;color:#332f2a;margin:0;padding:34px}}
header{{max-width:1280px;margin:0 auto 22px}} h1{{font-size:30px;margin:0 0 8px}} p{{color:#766f65;line-height:1.7;margin:6px 0}}
.toolbar{{display:flex;flex-wrap:wrap;gap:10px;margin:16px 0}} .pill{{background:#fff;border:1px solid #e5dbce;border-radius:999px;padding:8px 12px;font-size:13px;color:#675f55}}
.grid{{max-width:1280px;margin:0 auto;display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:16px}}
.material-card{{background:#fff;border:1px solid #e5dbce;border-radius:14px;overflow:hidden;box-shadow:0 8px 26px rgba(55,44,32,.06)}}
.material-card.selected{{border:2px solid #9b6d3c;box-shadow:0 10px 30px rgba(137,91,43,.18)}} .material-card img{{width:100%;display:block;background:#f4eee5}}
.body{{padding:12px 13px 14px}} .title{{font-weight:700;font-size:15px;line-height:1.45}} .meta{{font-size:12px;color:#8b8176;margin:6px 0}}
p{{font-size:13px;color:#625b52;margin:0 0 8px;line-height:1.55}} .tip{{font-size:12px;line-height:1.5;background:#fbf5ea;color:#7b5a36;border-left:3px solid #c9a56e;border-radius:7px;padding:7px 8px;margin:8px 0}}
code{{font-size:11px;background:#f4eee5;color:#7a5a3a;padding:3px 6px;border-radius:6px}}
</style><header><h1>{resolved['theme']} · 24 种材质选择预览</h1>
<p>用于印刷厂使用者快速查看“同一版式在不同纸张上的大致视觉差异”。这是屏幕模拟,不等同真实纸样或打样。</p>
<p>默认规则：纸芯类用侧边色条表达；PVC 模拟塑料高光；珠光纸模拟轻微反光；纹理纸会适度增强纹理，方便选择。</p>
<div class="toolbar"><span class="pill">当前尺寸：{size['label']}</span><span class="pill">当前选中：{resolved['material']['label']}</span><span class="pill">产品：{resolved.get('product_form')}</span><span class="pill">无 AI 调用，可快速反复生成</span></div>
</header><section class="grid">{rows}</section></html>"""
    (out_dir / "materials.html").write_text(html, encoding="utf-8")


def _generate_material_selector(out_dir, resolved, design_img):
    presets = _load_presets()
    cards = []
    thumbs_dir = out_dir / "materials"
    thumbs_dir.mkdir(parents=True, exist_ok=True)
    selected_key = resolved["material"]["key"]
    for key, material in presets["materials"].items():
        material_resolved = deepcopy(material)
        material_resolved["key"] = key
        sim = apply_profile(design_img, "print_output", material_resolved, resolved["advanced"].get("saturation_boost_pct"))
        sim = _texture_overlay(sim, material_resolved)
        sim.thumbnail((520, 728))
        image_path = thumbs_dir / f"{material_resolved.get('source_no', 'x'):02d}_{key}.jpg"
        sim.save(image_path, quality=88, dpi=(150, 150))
        cards.append({
            "key": key,
            "label": material.get("label", key),
            "status": material.get("status", ""),
            "source_no": material.get("source_no", ""),
            "color_comp": material.get("color_comp", ""),
            "texture_level": material.get("texture_level", ""),
            "use_case": material.get("use_case", ""),
            "sales_tip": _sales_tip(material_resolved),
            "image": image_path.relative_to(out_dir),
            "selected": key == selected_key,
        })
    _write_material_selector(out_dir, resolved, cards)


def main():
    config_path = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else SKILL_ROOT / "config.example.json"
    prepared = _prepare_config(config_path)
    resolved = resolve_config(prepared)
    if resolved["errors"]:
        raise SystemExit("\n".join(resolved["errors"]))
    print("=== Preview config ===")
    print(_fmt(resolved))
    for warning in resolved["warnings"]:
        print("⚠️", warning)
    month, illustration = _find_first_illustration(resolved["illustrations_dir"])
    size = resolved["size"]
    width, height = size["trim_px"]
    family = "landscape" if width > height else "portrait"
    content = resolved["content"]
    plan = ai_planner.default_plan()
    template = resolved.get("series", {}).get("template") or resolved.get("product_type", {}).get("template") or "calendar_series"
    out_dir = SKILL_ROOT / "output" / resolved["theme"] / "preview"
    out_dir.mkdir(parents=True, exist_ok=True)
    design = out_dir / "01_design_preview.jpg"
    if template == "calendar_series":
        render_page(
            width, height, family, content.get("year", 2027), month, str(illustration), str(design),
            keyword=(content.get("month_keywords") or [None])[month - 1] if content.get("month_keywords") else None,
            accent=plan["accent"], vbias=plan["vbias"],
            poem_left=content.get("corner_poem_left", "") if content.get("keep_poems", True) else "",
            poem_right=content.get("corner_poem_right", "") if content.get("keep_poems", True) else "",
            seal=content.get("seal_initials", "") if content.get("keep_seal", True) else "",
            week_start=content.get("week_start", "sunday"),
            production=resolved.get("production"),
        )
    else:
        render_generic_card(width, height, month, str(illustration), str(design), resolved, side="front")
    design_img = Image.open(design)
    material_img = apply_profile(design_img, "print_output", resolved["material"], resolved["advanced"].get("saturation_boost_pct"))
    material_img = _texture_overlay(material_img, resolved["material"])
    material = out_dir / "02_material_simulation.jpg"
    material_img.save(material, quality=94, dpi=(300, 300))
    print_file = out_dir / f"03_print_guide_{size['key']}.jpg"
    _, guide_path, _ = build_print_file(design_img, size, resolved["material"], str(print_file), resolved["advanced"].get("saturation_boost_pct"))
    paths = [("设计预览：当前尺寸版式", design), (f"材质模拟：{resolved['material']['label']}", material), ("印刷 guide：红线裁切 / 蓝线安全区", Path(guide_path))]
    _write_html(out_dir, resolved, paths)
    if "--all-materials" in sys.argv:
        _generate_material_selector(out_dir, resolved, design_img)
    print(f"done -> {out_dir}")
    print(f"open -> {out_dir / 'preview.html'}")
    if "--all-materials" in sys.argv:
        print(f"materials -> {out_dir / 'materials.html'}")


if __name__ == "__main__":
    main()
