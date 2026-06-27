#!/usr/bin/env python3
"""
M6b 复古植物年历排版引擎 (almanac style) — 对齐参考图
铁律:版式 100% 代码锁死,AI 不碰排版;日期=真实日期引擎。
风格:做旧米白纸底 · 插画无框融入(白底抠除) · 手写花体月份+关键词 ·
      无格线极简日历 · 四角古典诗句/植物学线描/火漆印。
全部 1:1。
"""
import calendar
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# ───────── 版式常量(1:1 像素级锁死)─────────
CANVAS = 1500
BG = (246, 242, 232)        # 做旧米白
INK = (74, 68, 58)          # 主墨
SCRIPT = (193, 96, 80)      # 花体月份 砖粉
GRAY = (151, 143, 131)      # 关键词/副字
FAINT = (181, 171, 156)     # 四角诗句 浅褐灰

# 插画区(contain 不裁切,白底抠透贴纸上)
ILLO_TOP, ILLO_BOT = 150, 940
ILLO_MAX_W = 1120
# 文字区
POEM_Y = 60
MONTH_Y = 900               # 花体月份基线
KW_Y = 1075                 # 关键词
HDR_Y = 1135                # 星期表头
GRID_TOP = 1185             # 日期首行(留足 6 行)
COLS_W = 1120
COL_X0 = (CANVAS - COLS_W) // 2
COLW = COLS_W // 7
ROWH = 52                   # 6 行 × 52 + 字高 ≈ 装进 1500 底边

F_SCRIPT = "/System/Library/Fonts/Supplemental/SnellRoundhand.ttc"
F_DIDOT = "/System/Library/Fonts/Supplemental/Didot.ttc"
F_HOEFLER = "/System/Library/Fonts/Supplemental/Hoefler Text.ttc"
F_CN = "/System/Library/Fonts/Hiragino Sans GB.ttc"  # 页脚中文兜底

MONTH_EN = [None, "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"]
WEEK_HDR = ["S", "M", "T", "W", "T", "F", "S"]
# 关键词默认(花语感,可改)
KEYWORD = [None, "HOPE", "LOVE", "DREAM", "BLOOM", "GRACE", "JOY",
           "WARMTH", "SHINE", "CALM", "HARVEST", "GRATITUDE", "PEACE"]
# 四角短句(通用文学感,可改)
POEM_L = "A quiet beginning,\nsoft as morning light."
POEM_R = "Where small things\nbloom in their season."


def _font(path, size, index=0):
    return ImageFont.truetype(path, size, index=index)


def _knockout_white(src_path, thresh=32):
    """白底抠透:四角 flood-fill,返回 RGBA(白底→alpha0)"""
    im = Image.open(src_path).convert("RGB")
    w, h = im.size
    SENT = (255, 0, 255)
    work = im.copy()
    for seed in [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]:
        ImageDraw.floodfill(work, seed, SENT, thresh=thresh)
    px_w, px_o = work.load(), im.load()
    out = Image.new("RGBA", (w, h))
    po = out.load()
    for y in range(h):
        for x in range(w):
            if px_w[x, y] == SENT:
                po[x, y] = (0, 0, 0, 0)
            else:
                r, g, b = px_o[x, y]
                po[x, y] = (r, g, b, 255)
    return out


def _contain(img, max_w, max_h):
    w, h = img.size
    s = min(max_w / w, max_h / h)
    return img.resize((max(1, round(w * s)), max(1, round(h * s))), Image.LANCZOS)


def _ctext(d, cx, y, text, font, fill, ls=0):
    """居中文字(可加字距)"""
    if ls == 0:
        tw = d.textlength(text, font=font)
        d.text((cx - tw / 2, y), text, font=font, fill=fill)
        return
    tw = sum(d.textlength(c, font=font) + ls for c in text) - ls
    x = cx - tw / 2
    for c in text:
        d.text((x, y), c, font=font, fill=fill)
        x += d.textlength(c, font=font) + ls


def render_almanac_page(year, month, illustration, out_path,
                        keyword=None, theme_label="",
                        poem_left=POEM_L, poem_right=POEM_R, seal="JB",
                        week_start="sunday"):
    cv = Image.new("RGB", (CANVAS, CANVAS), BG)
    d = ImageDraw.Draw(cv)

    # 1) 插画:抠白底 → contain → 居中贴(无框融入)
    illo = _knockout_white(illustration)
    illo = _contain(illo, ILLO_MAX_W, ILLO_BOT - ILLO_TOP)
    iw, ih = illo.size
    ix = (CANVAS - iw) // 2
    iy = ILLO_TOP + (ILLO_BOT - ILLO_TOP - ih) // 2
    cv.paste(illo, (ix, iy), illo)

    # 2) 四角诗句(花体小字)
    f_poem = _font(F_SCRIPT, 40)
    for i, line in enumerate((poem_left or "").split("\n")):
        d.text((78, POEM_Y + i * 46), line, font=f_poem, fill=FAINT)
    for i, line in enumerate((poem_right or "").split("\n")):
        tw = d.textlength(line, font=f_poem)
        d.text((CANVAS - 78 - tw, POEM_Y + i * 46), line, font=f_poem, fill=FAINT)

    # 火漆印(右中,浅;seal 为空则不画)
    if seal:
        sx, sy, sr = CANVAS - 150, 470, 38
        d.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], outline=(206, 150, 138), width=3)
        _ctext(d, sx, sy - 16, seal, _font(F_DIDOT, 26), (206, 150, 138))

    # 3) 花体月份 + 分隔点
    f_month = _font(F_SCRIPT, 150)
    _ctext(d, CANVAS / 2, MONTH_Y, MONTH_EN[month], f_month, SCRIPT)
    d.text((CANVAS / 2 - 4, KW_Y - 36), "·", font=_font(F_DIDOT, 40), fill=SCRIPT)

    # 4) 关键词(字距大写衬线)
    kw = keyword or KEYWORD[month]
    if kw:
        _ctext(d, CANVAS / 2, KW_Y, kw, _font(F_DIDOT, 30), GRAY, ls=8)

    # 5) 星期表头(单字母衬线;周起始可配)
    if week_start == "monday":
        hdr, firstwd = ["M", "T", "W", "T", "F", "S", "S"], 0
    else:
        hdr, firstwd = WEEK_HDR, 6
    f_hdr = _font(F_DIDOT, 40)
    for i, wd in enumerate(hdr):
        cx = COL_X0 + i * COLW + COLW / 2
        _ctext(d, cx, HDR_Y, wd, f_hdr, INK)

    # 6) 日期(真实日期引擎,无格线)
    f_day = _font(F_DIDOT, 42)
    cal = calendar.Calendar(firstweekday=firstwd)
    for r, week in enumerate(cal.monthdayscalendar(year, month)):
        for c, day in enumerate(week):
            if day == 0:
                continue
            cx = COL_X0 + c * COLW + COLW / 2
            cy = GRID_TOP + r * ROWH
            _ctext(d, cx, cy, str(day), f_day, INK)

    # 7) 页脚主题(可选,极浅;中文走 CJK 字体兜底)
    if theme_label:
        _ctext(d, CANVAS / 2, CANVAS - 52, theme_label, _font(F_CN, 24), GRAY, ls=4)

    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    cv.save(out_path, quality=95)
    return out_path


def render_series_grid(page_paths, out_path, cols=4, gap=46, pad=80, title=""):
    """整套系列平面排版图:N 页平铺成 1:1 大图.

    Keep the title+grid block optically centered on the square canvas.
    Preserve the source page aspect ratio instead of forcing every card into
    a square thumbnail, otherwise 5×7 cards look distorted and bottom whitespace
    becomes visibly heavier than the top/side margins.
    """
    n = len(page_paths)
    rows = (n + cols - 1) // cols
    inner = 1900
    first = Image.open(page_paths[0]).convert("RGB")
    src_w, src_h = first.size
    aspect = src_h / src_w if src_w else 1
    title_h = 112 if title else 0
    S = pad * 2 + inner
    available_w = inner
    available_h = S - pad * 2 - title_h
    cell_by_w = (available_w - gap * (cols - 1)) / cols
    cell_h_by_h = (available_h - gap * (rows - 1)) / rows
    cell = max(1, round(min(cell_by_w, cell_h_by_h / aspect)))
    cell_h = max(1, round(cell * aspect))
    block_w = cell * cols + gap * (cols - 1)
    grid_h = cell_h * rows + gap * (rows - 1)
    block_h = title_h + grid_h
    cv = Image.new("RGB", (S, S), BG)
    d = ImageDraw.Draw(cv)
    ox = (S - block_w) // 2
    block_y = (S - block_h) // 2
    oy = block_y + title_h
    if title:
        # 含中文用 CJK 字体(花体无中文字形会出方块),纯西文才用花体
        has_cjk = any("一" <= ch <= "鿿" for ch in title)
        tfont = _font(F_CN, 64) if has_cjk else _font(F_SCRIPT, 88)
        _ctext(d, S / 2, block_y, title, tfont, SCRIPT, ls=6 if has_cjk else 0)
    for i, p in enumerate(page_paths):
        r, c = divmod(i, cols)
        im = Image.open(p).convert("RGB").resize((cell, cell_h), Image.LANCZOS)
        x = ox + c * (cell + gap)
        y = oy + r * (cell_h + gap)
        cv.paste(im, (x, y))
        d.rectangle([x, y, x + cell, y + cell_h], outline=(224, 218, 206), width=2)
    cv.save(out_path, quality=92)
    return out_path


if __name__ == "__main__":
    import sys
    SRC = Path.home() / "Downloads/小兔子文具主题1 ：1 比例"
    OUT = Path.home() / "接单工作区/插画日历项目/output/小兔子文具/almanac"
    OUT.mkdir(parents=True, exist_ok=True)
    # 试 1、2 月
    files = {int(p.name.split("—")[0].strip()): p for p in SRC.glob("*.png")}
    for m in (1, 2):
        render_almanac_page(2027, m, str(files[m]), str(OUT / f"almanac_{m:02d}.jpg"),
                            theme_label="小兔子文具 · 2027")
        print("ok", m)
