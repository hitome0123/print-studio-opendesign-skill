#!/usr/bin/env python3
"""
③ Rule Renderer · 自适应版式渲染器(复古植物志风,任意比例原生出图)
- 版式族:portrait(H≥W,竖版/方版) / landscape(W>H,横版)
- 自底向上算布局:日历 6 行先锚底,再往上推标题/插画,保证任意尺寸都装得下
- 复用 almanac_engine 的视觉基元(抠白底/字体/色/居中/真实日期)= 同一套护城河视觉
- AI 只通过 plan 影响:主体重心(vbias)、标题色(accent);坐标/字号/日期全由规则算
"""
import calendar
from pathlib import Path
from PIL import Image, ImageDraw
import almanac_engine as A   # 复用基元

MONTH_EN = A.MONTH_EN
KEYWORD = A.KEYWORD
BG, INK, GRAY, FAINT = A.BG, A.INK, A.GRAY, A.FAINT
DEFAULT_ACCENT = A.SCRIPT


def _weekhdr(week_start):
    return (["M", "T", "W", "T", "F", "S", "S"], 0) if week_start == "monday" \
        else (["S", "M", "T", "W", "T", "F", "S"], 6)


def _draw_calendar(d, year, month, x0, top, cols_w, row_h, hdr_sz, day_sz, week_start):
    """无格线日历(真实日期引擎)。返回占用高度。"""
    hdr, firstwd = _weekhdr(week_start)
    colw = cols_w / 7
    f_hdr, f_day = A._font(A.F_DIDOT, hdr_sz), A._font(A.F_DIDOT, day_sz)
    for i, wd in enumerate(hdr):
        A._ctext(d, x0 + i * colw + colw / 2, top, wd, f_hdr, INK)
    grid_top = top + round(hdr_sz * 1.5)
    cal = calendar.Calendar(firstweekday=firstwd)
    for r, week in enumerate(cal.monthdayscalendar(year, month)):
        for c, day in enumerate(week):
            if day:
                A._ctext(d, x0 + c * colw + colw / 2, grid_top + r * row_h, str(day), f_day, INK)


def _draw_illo(cv, illustration, x, y, w, h, vbias="center"):
    illo = A._knockout_white(illustration)
    illo = A._contain(illo, w, h)
    iw, ih = illo.size
    ix = x + (w - iw) // 2
    if vbias == "top-heavy":
        iy = y
    elif vbias == "bottom-heavy":
        iy = y + (h - ih)
    else:
        iy = y + (h - ih) // 2
    cv.paste(illo, (ix, iy), illo)


def _decor(d, W, H, poem_l, poem_r, seal, poem_sz):
    f = A._font(A.F_SCRIPT, poem_sz)
    m = round(0.05 * W)
    for i, ln in enumerate((poem_l or "").split("\n")):
        d.text((m, round(0.035 * H) + i * round(poem_sz * 1.15)), ln, font=f, fill=FAINT)
    for i, ln in enumerate((poem_r or "").split("\n")):
        tw = d.textlength(ln, font=f)
        d.text((W - m - tw, round(0.035 * H) + i * round(poem_sz * 1.15)), ln, font=f, fill=FAINT)
    if seal:
        sr = round(0.025 * W)
        sx, sy = W - round(0.10 * W), round(0.30 * H)
        d.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], outline=(206, 150, 138), width=3)
        A._ctext(d, sx, sy - round(0.013 * W), seal, A._font(A.F_DIDOT, round(0.017 * W)), (206, 150, 138))


def render_page(W, H, family, year, month, illustration, out_path,
                keyword=None, accent=None, vbias="center",
                poem_left="", poem_right="", seal="", week_start="sunday"):
    cv = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(cv)
    accent = accent or DEFAULT_ACCENT
    kw = keyword or KEYWORD[month]

    if family == "landscape":
        S = H  # 文字尺度以短边为基准
        month_sz, kw_sz = round(0.085 * S), round(0.022 * S)
        hdr_sz = day_sz = round(0.026 * S)
        row_h = round(0.10 * S)
        # 右区自底向上
        rx0, rcols_w = round(0.55 * W), round(0.40 * W)
        bottom = H - round(0.06 * H)
        grid_top = bottom - 6 * row_h
        hdr_top = grid_top - round(hdr_sz * 1.5) - round(0.02 * H)
        kw_top = hdr_top - round(kw_sz * 2.2)
        month_top = kw_top - round(month_sz * 0.95)
        # 左区插画
        _draw_illo(cv, illustration, round(0.04 * W), round(0.08 * H),
                   round(0.47 * W), round(0.84 * H), vbias)
        A._ctext(d, rx0 + rcols_w / 2, month_top, MONTH_EN[month], A._font(A.F_SCRIPT, month_sz), accent)
        if kw:
            A._ctext(d, rx0 + rcols_w / 2, kw_top, kw, A._font(A.F_DIDOT, kw_sz), GRAY, ls=round(0.004 * S))
        _draw_calendar(d, year, month, rx0, hdr_top, rcols_w, row_h, hdr_sz, day_sz, week_start)
        cx0, cy0, cx1, cy1, dsz = round(0.04 * W), round(0.08 * H), rx0 + rcols_w, grid_top + 6 * row_h, day_sz
    else:  # portrait / square
        month_sz, kw_sz = round(0.10 * W), round(0.026 * W)
        hdr_sz = day_sz = round(0.032 * W)
        poem_sz = round(0.030 * W)
        row_h = round(0.045 * W)
        cols_w = round(0.76 * W)
        x0 = (W - cols_w) // 2
        bottom = H - round(0.035 * H)
        grid_top = bottom - 6 * row_h
        hdr_top = grid_top - round(hdr_sz * 1.5) - round(0.012 * H)
        kw_top = hdr_top - round(kw_sz * 2.0)
        month_top = kw_top - round(month_sz * 0.95)
        illo_y0 = round(0.05 * H)
        illo_y1 = month_top - round(0.012 * H)
        _decor(d, W, H, poem_left, poem_right, seal, poem_sz)
        _draw_illo(cv, illustration, x0, illo_y0, cols_w, illo_y1 - illo_y0, vbias)
        A._ctext(d, W / 2, month_top, MONTH_EN[month], A._font(A.F_SCRIPT, month_sz), accent)
        d.text((W / 2 - round(0.004 * W), kw_top - round(0.024 * W)), "·",
               font=A._font(A.F_DIDOT, round(0.027 * W)), fill=accent)
        if kw:
            A._ctext(d, W / 2, kw_top, kw, A._font(A.F_DIDOT, kw_sz), GRAY, ls=round(0.005 * W))
        _draw_calendar(d, year, month, x0, hdr_top, cols_w, row_h, hdr_sz, day_sz, week_start)
        cx0, cy0, cx1, cy1, dsz = x0, illo_y0, x0 + cols_w, grid_top + 6 * row_h, day_sz

    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    cv.save(out_path, quality=95)
    return {"path": out_path, "family": family, "canvas": [W, H], "day_sz_px": dsz,
            "content_bbox": [cx0, cy0, cx1, cy1], "days": calendar.monthrange(year, month)[1]}


def render_series_grid(page_paths, out_path, cols=4, title="", accent=None):
    return A.render_series_grid(page_paths, out_path, cols=cols, title=title)


if __name__ == "__main__":
    from pathlib import Path as P
    SRC = P.home() / "Downloads/小兔子文具主题1 ：1 比例"
    files = {int(p.name.split("—")[0].strip()): p for p in SRC.glob("*.png")}
    OUT = P("/tmp/layout_test"); OUT.mkdir(exist_ok=True)
    render_page(1500, 2100, "portrait", 2027, 2, str(files[2]), str(OUT / "portrait_5x7.jpg"),
                poem_left="A quiet beginning,\nsoft as morning light.", seal="JB")
    render_page(2100, 1500, "landscape", 2027, 2, str(files[2]), str(OUT / "landscape_7x5.jpg"))
    print("ok ->", OUT)
