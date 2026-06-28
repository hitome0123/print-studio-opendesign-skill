#!/usr/bin/env python3
"""
配置解析 + 护栏校验(地基层)
- 加载 presets.json + config.json
- 预设 merge 高级自定义 → 解析出可印尺寸/出血/安全边距等派生值
- 护栏:ERROR 阻断(图会被搞坏),WARN 放行+提示(高风险自定义不直接执行=改为警告)
- 诚实标注未实装能力(印刷 profile/中文月份/多版式族 = v1 后续模块),不假装已支持

用法(lint):python engine/config_schema.py [config.json]
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
PRINT_DPI = 300
DEFAULT_BLEED_MM = 3.0
DEFAULT_SAFE_MM = 5.0
MM_PER_IN = 25.4
MIN_PRINT_SHORT_IN = 3.5   # 短边小于此 + 真实日期 → 数字可印性存疑


def _load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def resolve_config(config_path=None):
    cfg = _load(config_path or HERE / "config.json")
    presets = _load(HERE / "presets.json")
    W, E = [], []        # warnings, errors

    def warn(m): W.append(m)
    def err(m):  E.append(m)

    pre = cfg.get("preset", {})
    content = cfg.get("content", {})
    adv = cfg.get("advanced", {}) or {}
    outs = cfg.get("outputs", {})
    series_cfg = cfg.get("series", {}) or {}
    production = cfg.get("production", {}) or {}

    # ── product / series ──
    pkey = pre.get("product_type", "calendar_card")
    pdef = presets.get("product_types", {}).get(pkey)
    if not pdef:
        err(f"preset.product_type '{pkey}' 不在 presets.product_types 中")
        pdef = {"label": pkey, "template": series_cfg.get("template", "generic_card"), "supports_dates": False}

    ser_key = series_cfg.get("type", "monthly_calendar")
    ser_def = presets.get("series_types", {}).get(ser_key)
    if not ser_def:
        err(f"series.type '{ser_key}' 不在 presets.series_types 中")
        ser_def = {"label": ser_key, "default_count": series_cfg.get("count", 1), "requires_dates": False}

    try:
        series_count = int(series_cfg.get("count") or ser_def.get("default_count") or 1)
    except Exception:
        err(f"series.count='{series_cfg.get('count')}' 不是有效数字")
        series_count = 1
    if not (1 <= series_count <= 60):
        warn(f"series.count={series_count} 超出建议范围 1~60,请复核")

    # ── size ──
    skey = pre.get("size")
    sdef = presets["sizes"].get(skey)
    if not sdef:
        err(f"preset.size '{skey}' 不在 presets.sizes 中")
        sdef = {"label": skey, "w_in": 6, "h_in": 6, "status": "?"}
    elif sdef.get("status") == "待确认":
        warn(f"尺寸『{sdef['label']}』规格待确认 — 暂按 {sdef['w_in']}×{sdef['h_in']}in")

    cs = adv.get("custom_size")
    if cs:
        try:
            unit = cs.get("unit", "cm")
            w, h = float(cs["w"]), float(cs["h"])
            w_in, h_in = (w / MM_PER_IN, h / MM_PER_IN) if unit == "mm" else \
                         (w / 2.54, h / 2.54) if unit == "cm" else \
                         (w / PRINT_DPI, h / PRINT_DPI) if unit == "px" else (w, h)
            warn(f"自定义尺寸覆盖预设 → {w}{unit}×{h}{unit}")
        except Exception as ex:
            err(f"advanced.custom_size 格式错误: {ex}")
            w_in = h_in = None
    else:
        w_in, h_in = sdef.get("w_in"), sdef.get("h_in")

    bleed_mm = adv.get("bleed_mm") if adv.get("bleed_mm") is not None else DEFAULT_BLEED_MM
    safe_mm = adv.get("safe_margin_mm") if adv.get("safe_margin_mm") is not None else DEFAULT_SAFE_MM
    size = {"key": skey, "label": sdef.get("label"), "w_in": w_in, "h_in": h_in,
            "bleed_mm": bleed_mm, "safe_margin_mm": safe_mm, "dpi": PRINT_DPI}
    if w_in and h_in:
        size["trim_px"] = (round(w_in * PRINT_DPI), round(h_in * PRINT_DPI))
        bl_in = bleed_mm / MM_PER_IN
        size["bleed_px"] = (round((w_in + 2 * bl_in) * PRINT_DPI),
                            round((h_in + 2 * bl_in) * PRINT_DPI))
        if content.get("real_dates", True) and ser_def.get("requires_dates", False) and min(w_in, h_in) < MIN_PRINT_SHORT_IN:
            warn(f"成品短边 {min(w_in, h_in)}in 偏小,真实日历数字可印性需复核(②印刷体系标定)")

    # ── material ──
    mkey = pre.get("material")
    mdef = presets["materials"].get(mkey)
    if not mdef:
        err(f"preset.material '{mkey}' 不在 presets.materials 中")
        mdef = {"label": mkey, "status": "?"}
    elif mdef.get("status") in ("待补", "待标定"):
        warn(f"材质『{mdef['label']}』profile 未实测标定 — 已按材质大类使用预估补偿,印刷前建议打样确认")

    # ── style / language(诚实标注未实装)──
    stkey = pre.get("style")
    stdef = presets["styles"].get(stkey) or {"label": stkey, "engine": "almanac", "status": "?"}
    if stdef.get("status") != "implemented":
        warn(f"风格『{stdef['label']}』版式族 v1 未实装 — 暂用『复古植物志/almanac』渲染(③ AI排版脑补)")

    lgkey = pre.get("language", "en")
    lgdef = presets["languages"].get(lgkey) or {"label": lgkey, "status": "?"}
    if lgdef.get("status") != "implemented":
        warn(f"语言『{lgdef['label']}』v1 未实装 — 暂出英文月份(②/③ 补中文与双语)")

    # ── outputs(诚实:印刷/电商 profile 未实装时说明)──
    versions = outs.get("versions", ["screen"])
    if "print" in versions and mdef.get("status") in ("待补", "待标定"):
        warn(f"印刷版色彩补偿:材质『{mdef.get('label')}』未实测标定,当前为系统预估补偿(批量前建议打样)")

    # ── advanced 取值护栏 ──
    sb = adv.get("saturation_boost_pct")
    if sb is not None and not (0 <= sb <= 30):
        warn(f"saturation_boost_pct={sb} 超出建议区间 0~30(印刷高级饱和上限),请复核")
    dc = adv.get("decor_complexity")
    if dc not in (None, "light", "normal", "rich"):
        warn(f"decor_complexity='{dc}' 非法,应为 light/normal/rich;按 normal 处理")

    # ── content 必填 ──
    if content.get("real_dates", True) and ser_def.get("requires_dates", False) and not content.get("year"):
        err("content.real_dates=true 且当前系列需要日期,但缺 content.year")

    if production.get("double_sided") and "back" not in outs.get("types", []):
        warn("production.double_sided=true 但 outputs.types 未包含 back; 将只出正面,如需背面请加入 back")
    if pkey == "wall_calendar":
        binding = production.get("binding") or pdef.get("default_binding") or "top_wire"
        if binding in ("none", ""):
            warn("挂历建议选择顶部装订方式: top_wire/top_hanger_hole/top_clip,否则只按普通日历页输出")
        elif binding not in ("top_wire", "top_hanger_hole", "top_clip", "wall_coil"):
            warn(f"挂历装订 binding='{binding}' 暂无专用预览,建议使用 top_wire/top_hanger_hole/top_clip")
        if not production.get("binding_reserved_mm"):
            warn("挂历顶部装订区使用默认预留 12mm;如已有线圈/夹条规格,请设置 production.binding_reserved_mm")

    resolved = {
        "theme": cfg.get("theme"),
        "illustrations_dir": cfg.get("illustrations_dir"),
        "series": {"key": ser_key, "count": series_count, "template": series_cfg.get("template") or pdef.get("template"), **ser_def},
        "product_type": {"key": pkey, **pdef},
        "size": size,
        "material": {"key": mkey, **mdef},
        "product_form": pre.get("product_form"),
        "production": production,
        "style": {"key": stkey, **stdef},
        "language": {"key": lgkey, **lgdef},
        "content": content,
        "outputs": outs,
        "advanced": adv,
        "image_gen": cfg.get("image_gen", {"backend": "gemini", "model": None}),
        "layout_ai": cfg.get("layout_ai", {"enabled": True, "provider": "auto"}),
        "layout_lock": cfg.get("layout_lock", {"enabled": False}),
        "ai_layout": cfg.get("ai_layout", True),
        "qc_ai": cfg.get("qc_ai", False),
        "warnings": W, "errors": E,
    }
    return resolved


def _fmt(r):
    s = r["size"]
    lines = [
        f"主题: {r['theme']}   素材: {r['illustrations_dir']}",
        f"尺寸: {s['label']}  trim={s.get('trim_px')}px  含出血={s.get('bleed_px')}px  "
        f"(出血{s['bleed_mm']}mm/安全{s['safe_margin_mm']}mm @ {s['dpi']}dpi)",
        f"产品: {r['product_type'].get('label')}  系列: {r['series'].get('label')}×{r['series'].get('count')}  "
        f"材质: {r['material'].get('label')}",
        f"形态: {r['product_form']}  风格: {r['style'].get('label')}  语言: {r['language'].get('label')}",
        f"年份: {r['content'].get('year')}  真实日期: {r['content'].get('real_dates')}  "
        f"周起始: {r['content'].get('week_start')}",
        f"输出版本: {r['outputs'].get('versions')}  类型: {r['outputs'].get('types')}  "
        f"系列: {r['outputs'].get('series_grid_layout')}",
    ]
    return "\n".join(lines)


if __name__ == "__main__":
    import sys
    r = resolve_config(sys.argv[1] if len(sys.argv) > 1 else None)
    print("=== 解析结果 ===")
    print(_fmt(r))
    if r["warnings"]:
        print("\n⚠️  警告(放行):")
        for w in r["warnings"]:
            print("  -", w)
    if r["errors"]:
        print("\n❌ 错误(阻断):")
        for e in r["errors"]:
            print("  -", e)
        sys.exit(1)
    print("\n✅ 校验通过")
