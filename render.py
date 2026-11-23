#!/usr/bin/env python3
"""Render news-image-20261123 entry.png (1024x1024) from stories.json.

Fresh code written 23 Nov 2026 for this competition only.
Deterministic: fixed fonts, fixed layout, no timestamps, no randomness.
Usage: python3 render.py [stories.json] [out.png]
"""
import json
import sys
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
MARGIN = 28
FONT_DIR = "/usr/share/fonts/truetype/dejavu/"

BG_TOP = (16, 32, 54)
BG_BOT = (8, 18, 32)
PANEL = (24, 44, 70)
PANEL_EDGE = (52, 84, 120)
GOLD = (232, 184, 88)
WHITE = (245, 247, 250)
MUTED = (168, 186, 205)
LEAD_BG = (124, 26, 20)
LEAD_EDGE = (232, 184, 88)
CHECK_BG = (34, 16, 18)
CHECK_EDGE = (198, 60, 48)
CHECK_TXT = (240, 170, 160)


def font(name, size):
    return ImageFont.truetype(FONT_DIR + name, size)


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap; returns list of lines."""
    words, lines, cur = text.split(), [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def fit_lines(draw, text, fnt, max_w, max_lines):
    """Wrap to at most max_lines, ellipsising the last line if needed."""
    lines = wrap(draw, text, fnt, max_w)
    if len(lines) <= max_lines:
        return lines
    lines = lines[:max_lines]
    while lines and draw.textlength(lines[-1] + " …", font=fnt) > max_w:
        lines[-1] = lines[-1].rsplit(" ", 1)[0] if " " in lines[-1] else lines[-1][:-1]
    lines[-1] = lines[-1] + " …"
    return lines


def rounded(draw, box, radius, fill, outline=None, width=1):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else "stories.json"
    out = sys.argv[2] if len(sys.argv) > 2 else "entry.png"
    with open(src, encoding="utf-8") as fh:
        data = json.load(fh)

    img = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(img)
    for y in range(H):  # vertical gradient, deterministic
        t = y / (H - 1)
        d.line([(0, y), (W, y)], fill=tuple(
            int(BG_TOP[i] + (BG_BOT[i] - BG_TOP[i]) * t) for i in range(3)))

    f_title = font("DejaVuSans-Bold.ttf", 46)
    f_sub = font("DejaVuSans.ttf", 19)
    f_lead_tag = font("DejaVuSans-Bold.ttf", 14)
    f_lead_head = font("DejaVuSans-Bold.ttf", 25)
    f_lead_det = font("DejaVuSans.ttf", 15)
    f_num = font("DejaVuSans-Bold.ttf", 17)
    f_head = font("DejaVuSans-Bold.ttf", 16)
    f_det = font("DejaVuSans.ttf", 12)
    f_src = font("DejaVuSans-Bold.ttf", 11)
    f_check_t = font("DejaVuSans-Bold.ttf", 15)
    f_check = font("DejaVuSans.ttf", 12)
    f_foot = font("DejaVuSans.ttf", 11)

    # ---- header ----
    d.text((MARGIN, 26), data["title"], font=f_title, fill=WHITE)
    d.text((MARGIN, 82), data["subtitle"], font=f_sub, fill=GOLD)
    d.line([(MARGIN, 112), (W - MARGIN, 112)], fill=GOLD, width=2)

    # ---- lead story ----
    lead = data["lead"]
    lx0, ly0, lx1, ly1 = MARGIN, 122, W - MARGIN, 210
    rounded(d, (lx0, ly0, lx1, ly1), 10, LEAD_BG, outline=LEAD_EDGE, width=2)
    d.text((lx0 + 16, ly0 + 10), "★  LEAD — FIRST REPORTED TODAY", font=f_lead_tag, fill=GOLD)
    head_lines = fit_lines(d, lead["headline"], f_lead_head, lx1 - lx0 - 32, 1)
    d.text((lx0 + 16, ly0 + 32), head_lines[0], font=f_lead_head, fill=WHITE)
    d.text((lx0 + 16, ly0 + 64), lead["detail"], font=f_lead_det, fill=(225, 215, 205))
    d.text((lx1 - 16, ly0 + 10), lead["source"], font=f_src, fill=GOLD, anchor="ra")

    # ---- story grid: 16 stories, 2 cols x 8 rows ----
    stories = data["stories"]
    gx, gy = MARGIN, 222
    col_w = (W - 2 * MARGIN - 14) // 2
    row_h, row_gap = 76, 4
    for i, st in enumerate(stories):
        r, c = divmod(i, 2)
        x0 = gx + c * (col_w + 14)
        y0 = gy + r * (row_h + row_gap)
        x1, y1 = x0 + col_w, y0 + row_h
        rounded(d, (x0, y0, x1, y1), 8, PANEL, outline=PANEL_EDGE, width=1)
        # number badge
        cx, cy = x0 + 22, y0 + 22
        d.ellipse([cx - 13, cy - 13, cx + 13, cy + 13], fill=GOLD)
        num = str(st["num"])
        tw = d.textlength(num, font=f_num)
        d.text((cx - tw / 2, cy - 10), num, font=f_num, fill=(16, 32, 54))
        tx = x0 + 42
        tw_max = x1 - tx - 10
        hlines = fit_lines(d, st["headline"], f_head, tw_max, 2)
        yy = y0 + 8
        for ln in hlines:
            d.text((tx, yy), ln, font=f_head, fill=WHITE)
            yy += 19
        dlines = fit_lines(d, st["detail"], f_det, tw_max, 1)
        if dlines:
            d.text((tx, y0 + 48), dlines[0], font=f_det, fill=MUTED)
        d.text((tx, y0 + 63), st["source"], font=f_src, fill=GOLD)

    # ---- DATE CHECK box ----
    cx0, cy0, cx1, cy1 = MARGIN, 866, W - MARGIN, 988
    rounded(d, (cx0, cy0, cx1, cy1), 10, CHECK_BG, outline=CHECK_EDGE, width=2)
    d.text((cx0 + 16, cy0 + 9), "DATE CHECK — DELIBERATELY LEFT OUT (NOT FROM TODAY):",
           font=f_check_t, fill=(255, 120, 105))
    items = data["date_check"]
    col_w2 = (cx1 - cx0 - 32 - 16) // 2
    for i, item in enumerate(items):
        r, c = divmod(i, 2)
        x = cx0 + 16 + c * (col_w2 + 16)
        y = cy0 + 36 + r * 26
        d.text((x, y), "✕  " + item, font=f_check, fill=CHECK_TXT)

    # ---- footer ----
    fw = d.textlength(data["footer"], font=f_foot)
    d.text(((W - fw) / 2, 996), data["footer"], font=f_foot, fill=MUTED)

    img.save(out, format="PNG", optimize=True)
    print("wrote", out, img.size)


if __name__ == "__main__":
    main()
