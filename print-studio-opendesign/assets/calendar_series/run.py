#!/usr/bin/env python3
"""
插画日历 skill · 入口(配置骨架 + 印刷体系)
流程:resolve_config → 护栏校验 → 渲染 B/C(+D/E 生图)= masters
     → 按 outputs.versions 导出 screen / print(300dpi+出血) / commerce 三版本 → 打包

产物布局:
  output/<theme>/
    almanac/ products/      ← 基础渲染 masters
    screen/  print/  commerce/  ← 三版本交付件
    <theme>_交付包.zip
    resolved.json           ← 本次解析参数留痕

用法:python run.py [config.json]    |    lint:python engine/config_schema.py
"""
import html, json, os, re, sys, time
from pathlib import Path
from PIL import Image

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "engine"))
from config_schema import resolve_config, _fmt                       # noqa: E402
from layout_engine import render_page, render_series_grid            # noqa: E402
from generic_card_engine import render_generic_card                  # noqa: E402
import ai_planner                                                    # noqa: E402
from profiles import apply_profile                                   # noqa: E402
from print_export import build_print_file, build_package            # noqa: E402
from qc import run_qc                                                # noqa: E402


TARGET_4K_LONG_EDGE = 4096


def find_illustrations(folder, count=None):
    folder = Path(folder)
    if not folder.is_absolute():
        folder = (HERE / folder).resolve()
    if not folder.exists():
        sys.exit(f"❌ illustrations_dir 不存在: {folder}")
    found = []
    for p in sorted(folder.iterdir()):
        if p.suffix.lower() in (".png", ".jpg", ".jpeg") and re.match(r"\s*(\d+)", p.name):
            found.append((int(re.match(r"\s*(\d+)", p.name).group(1)), p))
    found.sort(key=lambda x: x[0])
    if not found:
        sys.exit(f"❌ {folder} 没找到带月份序号的插画(命名以数字开头,如 1_xxx.png)")
    if count and len(found) < count:
        print(f"⚠️  需要 {count} 张,但只找到 {len(found)} 张;将循环复用已有素材")
    mapped = {}
    total = count or len(found)
    for idx in range(1, total + 1):
        if idx in dict(found):
            mapped[idx] = dict(found)[idx]
        else:
            mapped[idx] = found[(idx - 1) % len(found)][1]
    return mapped


def _save_4k(img, out_path, long_edge=TARGET_4K_LONG_EDGE):
    img = img.convert("RGB")
    w, h = img.size
    scale = long_edge / max(w, h)
    target = (max(1, round(w * scale)), max(1, round(h * scale)))
    if target != img.size:
        img = img.resize(target, Image.LANCZOS)
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    img.save(out_path, quality=94, dpi=(300, 300))
    return Path(out_path)


def _write_download_gallery(out_dir, title, files):
    cards = []
    for label, path in files:
        rel = path.name
        cards.append(
            f"<figure><a href='{html.escape(rel)}' download>"
            f"<img src='{html.escape(rel)}' alt='{html.escape(label)}'></a>"
            f"<figcaption><b>{html.escape(label)}</b><br><a href='{html.escape(rel)}' download>下载保存 4K 图</a></figcaption></figure>"
        )
    page = f"""<!doctype html><meta charset="utf-8"><title>{html.escape(title)} · 4K 单张下载</title>
<style>
body{{margin:0;background:#f6f0e8;color:#2f2a24;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;padding:28px}}
header{{max-width:1180px;margin:0 auto 22px}} h1{{margin:0 0 8px;font-size:28px}} p{{color:#756b60;line-height:1.55}}
.grid{{max-width:1180px;margin:auto;display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:18px}}
figure{{margin:0;background:white;border:1px solid #e5dacd;border-radius:14px;padding:12px;box-shadow:0 8px 28px rgba(62,49,35,.08)}}
img{{width:100%;display:block;border-radius:10px}} figcaption{{font-size:13px;line-height:1.5;margin-top:10px;color:#5e554c}} a{{color:#8b5a2b}}
</style><header><h1>{html.escape(title)} · 4K 单张下载</h1>
<p>每张图都可单独打开或下载保存。这里是展示/确认用 4K 长边版本,印刷生产仍以 <code>print/</code> 目录为准。</p></header>
<main class="grid">{''.join(cards)}</main>"""
    (out_dir / "index.html").write_text(page, encoding="utf-8")


def export_download_4k(out_base, theme, pages, grid, prod, material, sat_boost):
    out_dir = out_base / "download_4k"
    out_dir.mkdir(exist_ok=True)
    files = []
    for m, p in sorted(pages.items()):
        img = apply_profile(Image.open(p), "commerce_mockup", material, sat_boost)
        saved = _save_4k(img, out_dir / f"B_{m:02d}_4k.jpg")
        files.append((f"单张 {m:02d}", saved))
    if grid:
        img = apply_profile(Image.open(grid), "commerce_mockup", material, sat_boost)
        saved = _save_4k(img, out_dir / "C_series_4k.jpg")
        files.append(("系列总览", saved))
    for name, p in sorted(prod.items()):
        saved = _save_4k(Image.open(p), out_dir / f"{name}_4k.jpg")
        files.append((name, saved))
    if files:
        _write_download_gallery(out_dir, theme, files)
    return out_dir if files else None


def _provider_label(provider):
    return provider.get("label") or provider.get("backend") or "provider"


def _write_provider_preview_html(out_dir, theme, results):
    rows = []
    for item in results:
        media = ""
        if item.get("path"):
            rel = item["path"].relative_to(out_dir)
            media = f"<img src='{html.escape(str(rel))}' alt='{html.escape(item['label'])}'>"
        else:
            media = f"<div class='error'>{html.escape(item.get('error') or '未生成')}</div>"
        rows.append(
            f"<figure>{media}<figcaption><b>{html.escape(item['label'])}</b><br>"
            f"{html.escape(item['kind'])} · {html.escape(item['backend'])} · {html.escape(item.get('model') or '')}</figcaption></figure>"
        )
    page = f"""<!doctype html><meta charset="utf-8"><title>{html.escape(theme)} · 多模型预览</title>
<style>
body{{margin:0;background:#f6f0e8;color:#2f2a24;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;padding:28px}}
header{{max-width:1280px;margin:0 auto 22px}} h1{{margin:0 0 8px;font-size:28px}} p{{color:#756b60;line-height:1.55}}
.grid{{max-width:1280px;margin:auto;display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:18px}}
figure{{margin:0;background:white;border:1px solid #e5dacd;border-radius:14px;padding:12px;box-shadow:0 8px 28px rgba(62,49,35,.08)}}
img{{width:100%;display:block;border-radius:10px}} figcaption{{font-size:13px;line-height:1.5;margin-top:10px;color:#5e554c}}
.error{{min-height:220px;display:flex;align-items:center;justify-content:center;text-align:center;background:#fbf1ea;color:#9b3d2e;border-radius:10px;padding:18px;line-height:1.5}}
</style><header><h1>{html.escape(theme)} · 即梦 / Gemini / GPT-Image2 预览对比</h1>
<p>用于首轮确认不同图像模型对白底图、氛围图的理解差异。模型预览只用于展示选择,不替代印刷源文件。</p></header>
<main class="grid">{''.join(rows)}</main>"""
    (out_dir / "index.html").write_text(page, encoding="utf-8")


def render_provider_previews(out_base, theme, pages, outs, image_gen):
    cfg = image_gen.get("provider_previews") or {}
    if not cfg.get("enabled"):
        return None
    providers = cfg.get("providers") or [
        {"backend": "jimeng", "label": "即梦"},
        {"backend": "gemini", "model": "gemini-2.5-flash-image", "label": "Gemini"},
        {"backend": "gpt_image2", "model": "gpt-image-1", "label": "GPT-Image2"},
    ]
    kinds = cfg.get("types") or ["whitebg", "ambiance"]
    months = cfg.get("months") or outs.get("product_shot_months", [1])
    out_dir = out_base / "provider_previews"
    out_dir.mkdir(exist_ok=True)
    results = []
    try:
        from mockup_ai import render_whitebg, render_ambiance
    except Exception as e:
        _write_provider_preview_html(out_dir, theme, [{"label": "mockup_ai", "kind": "load", "backend": "-", "error": str(e)}])
        return out_dir
    for mon in months:
        if mon not in pages:
            continue
        for provider in providers:
            backend = provider.get("backend")
            model = provider.get("model")
            label = _provider_label(provider)
            for kind in kinds:
                path = out_dir / f"{label}_{kind}_{mon:02d}.jpg"
                item = {"label": label, "kind": kind, "backend": backend or "", "model": model, "path": None}
                try:
                    if kind == "whitebg":
                        render_whitebg(str(pages[mon]), str(path), backend=backend, model=model)
                    elif kind == "ambiance":
                        render_ambiance(str(pages[mon]), str(path), backend=backend, model=model)
                    else:
                        raise RuntimeError(f"未知预览类型: {kind}")
                    item["path"] = path
                except Exception as e:
                    item["error"] = str(e)
                results.append(item)
    _write_provider_preview_html(out_dir, theme, results)
    return out_dir


def main():
    cfg_path = sys.argv[1] if len(sys.argv) > 1 else HERE / "config.json"
    r = resolve_config(cfg_path)

    print("=== 解析结果 ===")
    print(_fmt(r))
    for w in r["warnings"]:
        print("⚠️ ", w)
    if r["errors"]:
        for e in r["errors"]:
            print("❌ ", e)
        sys.exit("配置有阻断性错误,已停止。")

    theme, c = r["theme"], r["content"]
    year = c.get("year", 2027)
    kws = c.get("month_keywords") or []
    poem_l = c.get("corner_poem_left", "") if c.get("keep_poems", True) else ""
    poem_r = c.get("corner_poem_right", "") if c.get("keep_poems", True) else ""
    seal = c.get("seal_initials", "") if c.get("keep_seal", True) else ""
    week_start = c.get("week_start", "sunday")

    outs = r["outputs"]
    types = set(outs.get("types", ["single", "grid"]))
    versions = set(outs.get("versions", ["screen"]))
    cols = 3 if outs.get("series_grid_layout") == "3x4" else 4
    size, material = r["size"], r["material"]
    sat_boost = (r["advanced"] or {}).get("saturation_boost_pct")
    template = r.get("series", {}).get("template") or r.get("product_type", {}).get("template") or "calendar_series"
    series_count = r.get("series", {}).get("count") or 12

    illos = find_illustrations(r["illustrations_dir"], count=series_count)
    out_root = Path(os.environ.get("PRINT_STUDIO_OUTPUT_ROOT", HERE / "output"))
    out_base = out_root / theme
    alm_dir = out_base / "almanac"
    alm_dir.mkdir(parents=True, exist_ok=True)
    (out_base / "resolved.json").write_text(
        json.dumps({k: v for k, v in r.items() if k != "warnings"}, ensure_ascii=False, indent=2),
        encoding="utf-8")

    # ── 版式族:按成品比例原生出图(非方尺寸不再 1:1 居中留边)──
    W, H = size.get("trim_px") or (1500, 1500)
    family = "landscape" if W > H else "portrait"
    ai_on = r.get("ai_layout", True)

    # ── 渲染 masters:AI 排版脑 plan → 自适应渲染器 ──
    pages, plans, render_meta = {}, {}, {}
    if types & {"single", "grid", "whitebg", "ambiance"}:
        print(f"  版式: {family} {W}×{H}  AI排版: {'on' if ai_on else 'off(默认计划)'}")
        for mon, src in illos.items():
            if ai_on and template == "calendar_series" and mon != min(illos):
                time.sleep(1.0)            # 月间轻节流,降限速
            plan = ai_planner.plan_for(str(src), enabled=ai_on and template == "calendar_series")
            plans[mon] = plan
            out = alm_dir / (f"almanac_{mon:02d}.jpg" if template == "calendar_series" else f"card_{mon:02d}_front.jpg")
            if template == "calendar_series":
                meta = render_page(W, H, family, year, mon, str(src), str(out),
                                   keyword=(kws[mon - 1] if mon - 1 < len(kws) else None),
                                   accent=plan["accent"], vbias=plan["vbias"],
                                   poem_left=poem_l, poem_right=poem_r, seal=seal, week_start=week_start,
                                   production=r.get("production"))
            else:
                meta = render_generic_card(W, H, mon, str(src), str(out), r, side="front")
            pages[mon] = out
            render_meta[mon] = meta
            if "back" in types:
                back = alm_dir / f"card_{mon:02d}_back.jpg"
                render_generic_card(W, H, mon, str(src), str(back), r, side="back")
        (out_base / "plans.json").write_text(
            json.dumps(plans, ensure_ascii=False, indent=2), encoding="utf-8")
        src0 = plans.get(1, {}).get("source", "?")
        print(f"  渲染 masters ×{len(pages)}  (template={template}, layout_plan 留痕 plans.json,source={src0})")
    grid = None
    if "grid" in types and pages:
        grid = alm_dir / "series_grid.jpg"
        render_series_grid([str(pages[m]) for m in sorted(pages)], str(grid), cols=cols,
                           title=f"{theme} · {year}")
        print(f"  渲染 C master ({outs.get('series_grid_layout')})")

    # ── D/E 生图 masters ──
    prod = {}
    if types & {"whitebg", "ambiance"}:
        try:
            from mockup_ai import render_whitebg, render_ambiance
            ig = r["image_gen"]
            pdir = out_base / "products"
            pdir.mkdir(parents=True, exist_ok=True)
            for mon in outs.get("product_shot_months", [1]):
                if mon not in pages:
                    continue
                card = str(pages[mon])
                if "whitebg" in types:
                    o = pdir / f"whitebg_{mon:02d}.jpg"
                    render_whitebg(card, str(o), ig["backend"], ig.get("model")); prod[f"whitebg_{mon:02d}"] = o
                if "ambiance" in types:
                    o = pdir / f"ambiance_{mon:02d}.jpg"
                    render_ambiance(card, str(o), ig["backend"], ig.get("model")); prod[f"ambiance_{mon:02d}"] = o
            print(f"  生图 D/E masters ×{len(prod)}")
        except Exception as e:
            print(f"  ⚠️  D/E 生图跳过: {e}")

    provider_preview_dir = render_provider_previews(out_base, theme, pages, outs, r.get("image_gen", {}))
    if provider_preview_dir:
        print(f"  ▸ provider_previews 多模型预览 → {provider_preview_dir.name}/index.html")

    # ── 导出三版本 ──
    vdirs = {}
    notes = set()
    if provider_preview_dir:
        vdirs["provider_previews"] = provider_preview_dir
    # screen:B + C,柔和预览
    if "screen" in versions:
        sd = out_base / "screen"; sd.mkdir(exist_ok=True); vdirs["screen"] = sd
        for m, p in pages.items():
            apply_profile(Image.open(p), "screen_preview", material).save(sd / f"B_{m:02d}.jpg", quality=92)
        if grid:
            apply_profile(Image.open(grid), "screen_preview", material).save(sd / "C_series.jpg", quality=92)
        print(f"  ▸ screen 预览版 → {sd.name}/")
    # print:仅 B 单图卡(300dpi+出血),C 整套图不进印刷卡
    if "print" in versions and pages:
        pd = out_base / "print"; pd.mkdir(exist_ok=True); vdirs["print"] = pd
        if not size.get("trim_px"):
            print("  ⚠️  尺寸无法解析为像素,跳过印刷版")
        else:
            for m, p in pages.items():
                _, _, note = build_print_file(
                    Image.open(p), size, material,
                    str(pd / f"B_{m:02d}_{size['key']}_print_300dpi.jpg"), sat_boost)
                if note:
                    notes.add(note)
            print(f"  ▸ print 印刷版 → {pd.name}/ ({size['label']} {size['trim_px']}px@300dpi,含出血+裁切线guide)")
    # commerce:C 整套 + D/E,更亮通透
    if "commerce" in versions and (grid or prod):
        cd = out_base / "commerce"; cd.mkdir(exist_ok=True); vdirs["commerce"] = cd
        if grid:
            apply_profile(Image.open(grid), "commerce_mockup", material).save(cd / "C_series.jpg", quality=92)
        for name, p in prod.items():
            apply_profile(Image.open(p), "commerce_mockup", material).save(cd / f"{name}.jpg", quality=92)
        print(f"  ▸ commerce 电商版 → {cd.name}/")

    if outs.get("download_4k", True):
        d4 = export_download_4k(out_base, theme, pages, grid, prod, material, sat_boost)
        if d4:
            vdirs["download_4k"] = d4
            print(f"  ▸ download_4k 单张保存版 → {d4.name}/index.html")

    for n in notes:
        print("  ℹ️ ", n)

    # ── ④ 自动质检 ──
    qc = run_qc(out_base, r, pages, render_meta, prod, qc_ai=r.get("qc_ai", False))
    icon = {"pass": "✅", "warn": "⚠️", "fail": "❌"}
    print(f"\n=== 质检 {icon[qc['status']]} {qc['status'].upper()}  (FAIL {qc['fail']} / WARN {qc['warn']}) ===")
    for it in qc["items"]:
        if it["level"] != "pass":
            print(f"  {icon[it['level']]} {it['check']}: {it['detail']}")
    print("  (完整报告 qc_report.json)")

    # ── 一键打包(质检 FAIL 时仍打包但提示)──
    if vdirs:
        zp = build_package(vdirs, out_base / f"{theme}_交付包.zip")
        print(f"  ▸ 打包 → {Path(zp).name}" + ("  ⚠️ 质检未过,慎交付" if qc["status"] == "fail" else ""))

    print(f"\ndone -> {out_base}  (resolved.json / plans.json / qc_report.json 留痕)")


if __name__ == "__main__":
    main()
