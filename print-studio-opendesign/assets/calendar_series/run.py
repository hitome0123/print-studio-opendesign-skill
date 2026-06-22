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
import json, os, re, sys, time
from pathlib import Path
from PIL import Image

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "engine"))
from config_schema import resolve_config, _fmt                       # noqa: E402
from layout_engine import render_page, render_series_grid            # noqa: E402
import ai_planner                                                    # noqa: E402
from profiles import apply_profile                                   # noqa: E402
from print_export import build_print_file, build_package            # noqa: E402
from qc import run_qc                                                # noqa: E402


def find_illustrations(folder):
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
    if len(found) != 12:
        print(f"⚠️  找到 {len(found)} 张(非12),按现有序号映射月份")
    return {mon: path for mon, path in found}


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

    illos = find_illustrations(r["illustrations_dir"])
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
            if ai_on and mon != min(illos):
                time.sleep(1.0)            # 月间轻节流,降限速
            plan = ai_planner.plan_for(str(src), enabled=ai_on)
            plans[mon] = plan
            out = alm_dir / f"almanac_{mon:02d}.jpg"
            meta = render_page(W, H, family, year, mon, str(src), str(out),
                               keyword=(kws[mon - 1] if mon - 1 < len(kws) else None),
                               accent=plan["accent"], vbias=plan["vbias"],
                               poem_left=poem_l, poem_right=poem_r, seal=seal, week_start=week_start)
            pages[mon] = out
            render_meta[mon] = meta
        (out_base / "plans.json").write_text(
            json.dumps(plans, ensure_ascii=False, indent=2), encoding="utf-8")
        src0 = plans.get(1, {}).get("source", "?")
        print(f"  渲染 B masters ×{len(pages)}  (layout_plan 留痕 plans.json,source={src0})")
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

    # ── 导出三版本 ──
    vdirs = {}
    notes = set()
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
