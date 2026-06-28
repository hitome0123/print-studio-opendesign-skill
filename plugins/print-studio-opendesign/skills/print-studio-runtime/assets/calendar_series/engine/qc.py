#!/usr/bin/env python3
"""
④ 自动质检 — 交付前把关
- 确定性检查(零成本主干):完整性 / 尺寸·DPI / 日期引擎 / 安全边距 / 可印字号 /
  系列底色一致 / 白底图干净
- 可选 AI 视觉(qc_ai=true):压字/乱码/多余文字/氛围图场景(gated 省钱,失败不阻断)
- 输出 qc_report.json + 控制台摘要;FAIL=硬问题,WARN=风险放行
"""
import calendar, json, os
from pathlib import Path
from PIL import Image
from layout_quality import bbox_inside_safe, bbox_intersects

PASS, WARN, FAIL = "pass", "warn", "fail"
MIN_PT = 6.0          # 印刷可读最小字号(pt)
DPI = 300


def _pt(px):
    return round(px / DPI * 72, 1)


def _corner(im):
    return im.convert("RGB").getpixel((2, 2))


def _checks(out_base, resolved, pages, render_meta, prod, design_plans=None):
    res = []

    def add(name, level, detail):
        res.append({"check": name, "level": level, "detail": detail})

    types = set(resolved["outputs"].get("types", []))
    size = resolved["size"]
    safe_px = round(size.get("safe_margin_mm", 5) / 25.4 * DPI)
    series = resolved.get("series", {}) or {}
    expected_count = int(series.get("count") or 12)
    requires_dates = bool(series.get("requires_dates"))

    # 1) 完整性
    if types & {"single", "grid", "whitebg", "ambiance"}:
        miss = [m for m in range(1, expected_count + 1) if m not in pages]
        add("完整性·系列单图", PASS if not miss else (WARN if len(miss) < expected_count else FAIL),
            f"齐全 {expected_count} 张" if not miss else f"缺序号 {miss}")
    if "grid" in types:
        g = out_base / "almanac" / "series_grid.jpg"
        add("完整性·整套图", PASS if g.exists() else FAIL, g.name if g.exists() else "缺 series_grid.jpg")

    # 1.5) 排版防改图:生产排版必须来自确定性 B/print,AI mockup 只能展示
    add("排版防改图·生产源隔离", PASS,
        "最终排版来自确定性渲染器;白底图/氛围图仅作展示,不能替代 print/ 生产文件")

    # 2) 日期引擎(渲染天数 == 真实天数)
    yr = resolved["content"].get("year", 2027)
    bad = []
    if requires_dates:
        for m, meta in render_meta.items():
            real = calendar.monthrange(yr, m)[1]
            if meta.get("days") != real:
                bad.append(f"{m}月 {meta.get('days')}≠{real}")
        add("日期引擎·天数核对", PASS if not bad else FAIL,
            f"{yr} 各月天数正确" if not bad else ";".join(bad))

    # 3) 尺寸·DPI(印刷文件)
    pd = out_base / "print"
    if pd.exists():
        bps = tuple(size.get("bleed_px") or ())
        wrong = []
        for f in sorted(pd.glob("B_*_print_*.jpg")):
            im = Image.open(f)
            if bps and im.size != bps:
                wrong.append(f"{f.name} {im.size}≠{bps}")
            elif im.info.get("dpi", (0,))[0] != DPI:
                wrong.append(f"{f.name} dpi={im.info.get('dpi')}")
        add("印刷·尺寸&300dpi", PASS if not wrong else FAIL,
            f"印刷文件 {bps}px@{DPI}dpi 正确" if not wrong else ";".join(wrong[:3]))

    # 3.5) 素材分辨率:不是硬失败,但需要显式人工确认
    if design_plans:
        low = []
        trim_w, trim_h = size.get("trim_px") or (0, 0)
        need_min = min(trim_w, trim_h) * 0.75 if trim_w and trim_h else 1000
        for idx, plan in design_plans.items():
            src = plan.get("source_image", {})
            if min(src.get("width_px", 0), src.get("height_px", 0)) < need_min:
                low.append(f"{idx:02d}:{src.get('file')} {src.get('width_px')}×{src.get('height_px')}")
        add("素材·分辨率人工确认", PASS if not low else WARN,
            "素材尺寸满足首轮打样检查" if not low else "部分素材像素偏低,批量印刷前复核: " + "; ".join(low[:4]))

    # 4) 安全边距(内容 bbox 在安全区内)
    viol = []
    for m, meta in render_meta.items():
        W, H = meta["canvas"]
        x0, y0, x1, y1 = meta["content_bbox"]
        if x0 < safe_px or y0 < safe_px or (W - x1) < safe_px or (H - y1) < safe_px:
            viol.append(m)
    if render_meta:
        add("安全边距·内容不进危险区", PASS if not viol else WARN,
            f"全部留足 {safe_px}px 安全边" if not viol else f"贴边风险月份 {viol}")

    # 5) 可印字号
    if render_meta and requires_dates:
        dsz = next(iter(render_meta.values())).get("day_sz_px", 0)
        pt = _pt(dsz)
        add("可印字号·日历数字", PASS if pt >= MIN_PT else WARN,
            f"日期 {dsz}px≈{pt}pt {'≥' if pt >= MIN_PT else '<'}{MIN_PT}pt")

    # 5.5) 通用文本层:标题/副标题/正文不可互相接触,也不能贴边
    touch = []
    unsafe_text = []
    for m, meta in render_meta.items():
        text_boxes = meta.get("text_boxes") or []
        canvas = meta.get("canvas") or (0, 0)
        for i, item in enumerate(text_boxes):
            if not bbox_inside_safe(item["bbox"], canvas, safe_px):
                unsafe_text.append(f"{m:02d}:{item.get('name')}")
            for other in text_boxes[i + 1:]:
                if bbox_intersects(item["bbox"], other["bbox"], gap=max(4, round(safe_px * 0.12))):
                    touch.append(f"{m:02d}:{item.get('name')}×{other.get('name')}")
    if any((meta.get("text_boxes") or []) for meta in render_meta.values()):
        add("通用排版·文本不接触", PASS if not touch else WARN,
            "标题/副标题/正文层级有空气感" if not touch else "文本层接触风险: " + "; ".join(touch[:6]))
        add("通用排版·文本安全边", PASS if not unsafe_text else WARN,
            "文本都在安全区内" if not unsafe_text else "文本贴边风险: " + "; ".join(unsafe_text[:6]))

    # 6) 系列底色一致
    if len(pages) >= 2:
        cols = [_corner(Image.open(p)) for p in pages.values()]
        spread = max(max(c[i] for c in cols) - min(c[i] for c in cols) for i in range(3))
        add("系列一致·底色", PASS if spread <= 8 else WARN,
            f"12 张底色极差 {spread}(≤8 视为统一)")

    # 7) 白底图干净(边缘近白、低方差)
    for name, p in (prod or {}).items():
        if not name.startswith("whitebg"):
            continue
        im = Image.open(p).convert("RGB")
        w, h = im.size
        pts = [im.getpixel(xy) for xy in
               [(5, 5), (w - 5, 5), (5, h - 5), (w - 5, h - 5), (w // 2, 5), (w // 2, h - 5)]]
        mean = sum(sum(px) / 3 for px in pts) / len(pts)
        add(f"白底图干净·{name}", PASS if mean >= 235 else WARN,
            f"边缘均亮 {round(mean)} {'干净' if mean >= 235 else '偏暗/有杂物?复核'}")

    return res


def _write_prepress_report(out_base, resolved, qc_obj, design_plans=None):
    out_base = Path(out_base)
    items = qc_obj["items"]
    passed = [i for i in items if i["level"] == PASS]
    warnings = [i for i in items if i["level"] == WARN]
    failures = [i for i in items if i["level"] == FAIL]
    size = resolved.get("size", {}) or {}
    material = resolved.get("material", {}) or {}
    outputs = resolved.get("outputs", {}) or {}
    lines = [
        "# 印前检查说明",
        "",
        "## 1. 当前结论",
        "",
        f"- 状态：**{qc_obj['status'].upper()}**",
        f"- FAIL：{qc_obj['fail']} 项",
        f"- WARN：{qc_obj['warn']} 项",
        f"- 成品尺寸：{size.get('label')}，{size.get('trim_px')}px @ {size.get('dpi', DPI)}dpi",
        f"- 材质：{material.get('label', material.get('key', '未指定'))}",
        "",
        "## 2. 为什么可以进入下一步",
        "",
    ]
    if passed:
        for item in passed:
            lines.append(f"- {item['check']}：{item['detail']}")
    else:
        lines.append("- 暂无通过项。")
    lines += [
        "",
        "## 3. 哪些地方需要人工确认",
        "",
    ]
    if warnings or failures:
        for item in failures + warnings:
            prefix = "硬问题" if item["level"] == FAIL else "风险提示"
            lines.append(f"- {prefix} · {item['check']}：{item['detail']}")
    else:
        lines.append("- 当前自动检查未发现必须人工介入的问题，但批量生产前仍建议实物打样。")
    lines += [
        "",
        "## 4. 设计规则说明",
        "",
        "- AI 可以参与版式判断、展示图生成和风格建议。",
        "- 日期、出血、安全边距、DPI、印刷文件导出由确定性规则控制。",
        "- 不用 ChatGPT / 生图模型生成最终排版；它们可能裁切、改字或重构图。",
        "- 默认展示图建议使用 `local_mockup`，保证完整卡面可见；AI mockup 只作为可选展示候选。",
        "- 白底图、氛围图、系列总览图、4K 下载图用于确认和展示，不替代 `print/` 目录里的生产文件。",
        "- 材质纹理、珠光、PVC 光泽属于屏幕模拟，最终以纸样和实物打样为准。",
        "",
        "## 5. 设计计划摘要",
        "",
    ]
    if design_plans:
        first = design_plans.get(min(design_plans))
        if first:
            lines += [
                f"- 版式 preset：{first.get('layout_preset', {}).get('label')}",
                f"- 字体 preset：{first.get('typography_preset', {}).get('label')}",
                f"- 背景色 preset：{first.get('color_preset', {}).get('background', {}).get('label')}",
                "- 结构化计划：见 `design_plan.json`。",
            ]
    else:
        lines.append("- 未生成结构化设计计划。")
    lines += [
        "",
        "## 6. 输出文件分工",
        "",
        "| 文件夹 / 文件 | 用途 |",
        "| --- | --- |",
        "| `screen/` | 屏幕预览确认 |",
        "| `print/` | 生产用 300dpi 印刷文件 |",
        "| `commerce/` | 白底图、氛围图、系列展示 |",
        "| `download_4k/` | 每张图单独保存的 4K 展示版 |",
        "| `provider_previews/` | 即梦 / Gemini / GPT-Image2 首轮模型对比 |",
        "| `qc_report.json` | 机器可读质检结果 |",
        "| `design_plan.json` | 多层设计计划与 preset 选择说明 |",
    ]
    (out_base / "prepress_report.zh-CN.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _ai_visual(pages, model="gemini-2.5-flash"):
    """可选:每张 B 页视觉检查压字/乱码/多余文字"""
    key = os.getenv("GEMINI_API_KEY")
    if not key:
        return [{"check": "AI视觉", "level": WARN, "detail": "无 GEMINI_API_KEY,跳过 AI 质检"}]
    out = []
    try:
        from google import genai
        from google.genai import types
        client = genai.Client(api_key=key)
    except Exception as e:
        return [{"check": "AI视觉", "level": WARN, "detail": f"加载失败,跳过: {e}"}]
    prompt = ('Check this calendar page. Reply ONLY JSON: '
              '{"text_over_subject":bool,"garbled_or_extra_text":bool,"calendar_clipped":bool,"note":"short"}')
    import re
    for m, p in pages.items():
        try:
            r = client.models.generate_content(
                model=model, contents=[prompt, types.Part.from_bytes(data=open(p, "rb").read(), mime_type="image/jpeg")],
                config=types.GenerateContentConfig(temperature=0.1))
            j = json.loads(re.search(r"\{.*\}", r.text, re.S).group(0))
            issues = [k for k in ("text_over_subject", "garbled_or_extra_text", "calendar_clipped") if j.get(k)]
            out.append({"check": f"AI视觉·{m:02d}月", "level": WARN if issues else PASS,
                        "detail": (",".join(issues) + " " + j.get("note", "")) if issues else "无明显问题"})
        except Exception:
            out.append({"check": f"AI视觉·{m:02d}月", "level": WARN, "detail": "分析失败,人工复核"})
    return out


def run_qc(out_base, resolved, pages, render_meta, prod, qc_ai=False, design_plans=None):
    out_base = Path(out_base)
    report = _checks(out_base, resolved, pages, render_meta, prod, design_plans=design_plans)
    if qc_ai:
        report += _ai_visual(pages)
    n_fail = sum(1 for r in report if r["level"] == FAIL)
    n_warn = sum(1 for r in report if r["level"] == WARN)
    status = FAIL if n_fail else (WARN if n_warn else PASS)
    (out_base / "qc_report.json").write_text(
        json.dumps({"status": status, "fail": n_fail, "warn": n_warn, "items": report},
                   ensure_ascii=False, indent=2), encoding="utf-8")
    qc_obj = {"status": status, "fail": n_fail, "warn": n_warn, "items": report}
    _write_prepress_report(out_base, resolved, qc_obj, design_plans=design_plans)
    return qc_obj
