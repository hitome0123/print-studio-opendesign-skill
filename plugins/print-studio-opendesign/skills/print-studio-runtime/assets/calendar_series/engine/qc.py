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

PASS, WARN, FAIL = "pass", "warn", "fail"
MIN_PT = 6.0          # 印刷可读最小字号(pt)
DPI = 300


def _pt(px):
    return round(px / DPI * 72, 1)


def _corner(im):
    return im.convert("RGB").getpixel((2, 2))


def _checks(out_base, resolved, pages, render_meta, prod):
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


def run_qc(out_base, resolved, pages, render_meta, prod, qc_ai=False):
    out_base = Path(out_base)
    report = _checks(out_base, resolved, pages, render_meta, prod)
    if qc_ai:
        report += _ai_visual(pages)
    n_fail = sum(1 for r in report if r["level"] == FAIL)
    n_warn = sum(1 for r in report if r["level"] == WARN)
    status = FAIL if n_fail else (WARN if n_warn else PASS)
    (out_base / "qc_report.json").write_text(
        json.dumps({"status": status, "fail": n_fail, "warn": n_warn, "items": report},
                   ensure_ascii=False, indent=2), encoding="utf-8")
    return {"status": status, "fail": n_fail, "warn": n_warn, "items": report}
