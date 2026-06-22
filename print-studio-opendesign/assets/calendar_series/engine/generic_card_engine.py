from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageFilter

MONTH_NAMES = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
]


def _font(size, italic=False):
    candidates = [
        "/System/Library/Fonts/Supplemental/Times New Roman Italic.ttf" if italic else "/System/Library/Fonts/Supplemental/Times New Roman.ttf",
        "/System/Library/Fonts/Supplemental/Georgia Italic.ttf" if italic else "/System/Library/Fonts/Supplemental/Georgia.ttf",
        "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            pass
    return ImageFont.load_default()


def _fit_text(draw, text, max_width, start_size, min_size=18, italic=False):
    size = start_size
    while size >= min_size:
        font = _font(size, italic=italic)
        if draw.textbbox((0, 0), text, font=font)[2] <= max_width:
            return font
        size -= 2
    return _font(min_size, italic=italic)


def _wrap(draw, text, font, max_width, max_lines=3):
    words = str(text or "").replace("\n", " ").split()
    if not words:
        return []
    lines, current = [], ""
    for word in words:
        test = word if not current else current + " " + word
        if draw.textbbox((0, 0), test, font=font)[2] <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = word
        if len(lines) >= max_lines:
            break
    if current and len(lines) < max_lines:
        lines.append(current)
    return lines[:max_lines]


def _cover(image, box_w, box_h):
    image = ImageOps.exif_transpose(image).convert("RGBA")
    scale = max(box_w / image.width, box_h / image.height)
    nw, nh = round(image.width * scale), round(image.height * scale)
    image = image.resize((nw, nh), Image.LANCZOS)
    left = max(0, (nw - box_w) // 2)
    top = max(0, (nh - box_h) // 2)
    return image.crop((left, top, left + box_w, top + box_h))


def _contain(image, box_w, box_h):
    image = ImageOps.exif_transpose(image).convert("RGBA")
    image.thumbnail((box_w, box_h), Image.LANCZOS)
    return image


def _draw_round_corner_guide(draw, w, h, radius):
    color = (188, 126, 94)
    r = radius
    for x, y, start, end in [(0, 0, 180, 270), (w - 2*r, 0, 270, 360), (w - 2*r, h - 2*r, 0, 90), (0, h - 2*r, 90, 180)]:
        draw.arc((x, y, x + 2*r, y + 2*r), start, end, fill=color, width=3)


def render_generic_card(W, H, index, image_path, out_path, resolved, side="front"):
    content = resolved.get("content", {})
    product = resolved.get("product_type", {}).get("key", "greeting_card")
    production = resolved.get("production", {}) or {}
    draw_bg = (252, 248, 239)
    if resolved.get("material", {}).get("paper_tone") == "雅白":
        draw_bg = (248, 243, 232)
    elif resolved.get("material", {}).get("paper_tone") == "牛皮":
        draw_bg = (222, 191, 139)

    im = Image.new("RGB", (W, H), draw_bg)
    draw = ImageDraw.Draw(im)
    safe_px = round(resolved["size"].get("safe_margin_mm", 5) / 25.4 * resolved["size"].get("dpi", 300))
    margin = max(42, safe_px + 8, round(min(W, H) * 0.07))
    accent = (139, 94, 58)
    text = (74, 63, 52)
    muted = (142, 126, 108)

    if side == "back":
        title = content.get("back_title") or "Thank you"
        body = content.get("back_body") or "Printed with care."
        font_title = _fit_text(draw, title, W - 2 * margin, round(min(W, H) * 0.09), italic=True)
        font_body = _font(round(min(W, H) * 0.035))
        tb = draw.textbbox((0, 0), title, font=font_title)
        draw.text(((W - (tb[2] - tb[0])) / 2, H * 0.30), title, fill=accent, font=font_title)
        lines = _wrap(draw, body, font_body, W - 2 * margin, max_lines=5)
        y = round(H * 0.45)
        for line in lines:
            lb = draw.textbbox((0, 0), line, font=font_body)
            draw.text(((W - (lb[2] - lb[0])) / 2, y), line, fill=text, font=font_body)
            y += round(font_body.size * 1.55)
        draw.rectangle((margin, margin, W - margin, H - margin), outline=(220, 207, 190), width=2)
    else:
        image = Image.open(image_path)
        title_list = content.get("card_titles") or []
        subtitle_list = content.get("card_subtitles") or []
        title = title_list[index - 1] if index - 1 < len(title_list) else content.get("front_title")
        subtitle = subtitle_list[index - 1] if index - 1 < len(subtitle_list) else content.get("front_subtitle")
        message = content.get("message") or ""
        if not title:
            title = MONTH_NAMES[(index - 1) % 12] if product == "calendar_card" else f"Card {index}"
        if not subtitle:
            subtitle = resolved.get("theme") or ""

        landscape = W > H
        narrow = W / H < 0.55
        if narrow:
            art_box = (margin, margin, W - margin, round(H * 0.54))
            title_y = round(H * 0.60)
        elif landscape:
            art_box = (margin, margin, round(W * 0.58), H - margin)
            title_y = round(H * 0.27)
        else:
            art_box = (margin, margin, W - margin, round(H * 0.58))
            title_y = round(H * 0.64)

        x1, y1, x2, y2 = art_box
        aw, ah = x2 - x1, y2 - y1
        art = _contain(image, aw, ah)
        shadow = Image.new("RGBA", (art.width + 26, art.height + 26), (0, 0, 0, 0))
        sd = ImageDraw.Draw(shadow)
        sd.rounded_rectangle((13, 13, art.width + 13, art.height + 13), radius=18, fill=(70, 50, 30, 32))
        shadow = shadow.filter(ImageFilter.GaussianBlur(9))
        px = x1 + (aw - art.width) // 2
        py = y1 + (ah - art.height) // 2
        im.paste(shadow, (px - 13, py - 13), shadow)
        im.paste(art, (px, py), art)

        if landscape:
            text_left = round(W * 0.63)
            max_text_w = W - text_left - margin
            align_x = text_left
        else:
            max_text_w = W - 2 * margin
            align_x = margin

        font_title = _fit_text(draw, title, max_text_w, round(min(W, H) * (0.12 if not narrow else 0.10)), italic=True)
        font_sub = _font(round(min(W, H) * 0.035))
        font_msg = _font(round(min(W, H) * 0.028))
        tb = draw.textbbox((0, 0), title, font=font_title)
        tx = align_x if landscape else (W - (tb[2] - tb[0])) / 2
        draw.text((tx, title_y), title, fill=accent, font=font_title)
        sb = draw.textbbox((0, 0), subtitle, font=font_sub)
        sx = align_x if landscape else (W - (sb[2] - sb[0])) / 2
        draw.text((sx, title_y + round(font_title.size * 0.95)), subtitle, fill=muted, font=font_sub)
        y = title_y + round(font_title.size * 1.55)
        for line in _wrap(draw, message, font_msg, max_text_w, max_lines=3):
            lb = draw.textbbox((0, 0), line, font=font_msg)
            lx = align_x if landscape else (W - (lb[2] - lb[0])) / 2
            draw.text((lx, y), line, fill=text, font=font_msg)
            y += round(font_msg.size * 1.45)

        seal = content.get("seal_initials") or ""
        if seal:
            rr = max(22, round(min(W, H) * 0.035))
            cx, cy = W - margin - rr, H - margin - rr
            draw.ellipse((cx - rr, cy - rr, cx + rr, cy + rr), outline=(202, 157, 130), width=3)
            sf = _font(round(rr * 0.65))
            bb = draw.textbbox((0, 0), seal, font=sf)
            draw.text((cx - (bb[2] - bb[0]) / 2, cy - (bb[3] - bb[1]) / 2 - 2), seal, fill=(202, 157, 130), font=sf)

    if product == "gift_tag" or production.get("binding") == "hole_punch":
        hole_r = max(18, round(min(W, H) * 0.035))
        cx, cy = W // 2, margin // 2 + hole_r
        draw.ellipse((cx - hole_r, cy - hole_r, cx + hole_r, cy + hole_r), outline=(150, 128, 106), width=3)

    rc = production.get("round_corners") or {}
    if rc.get("enabled"):
        radius = round(float(rc.get("radius_mm", 3)) / 25.4 * resolved["size"].get("dpi", 300))
        _draw_round_corner_guide(draw, W, H, radius)

    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    im.save(out_path, quality=94, dpi=(300, 300))
    return {
        "path": str(out_path),
        "family": "landscape" if W > H else "portrait",
        "canvas": [W, H],
        "content_bbox": [margin, margin, W - margin, H - margin],
        "day_sz_px": None,
        "days": None,
        "safe_margin_px": margin,
        "side": side,
        "template": "generic_card",
        "product_type": product,
    }
