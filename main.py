#!/usr/bin/env python3
"""THE WORLD IN ONE DAY — 23 November 2026 (v3).

Reads stories.json next to this script and draws one deterministic
1024x1024 PNG newspaper front page. Pillow only, no network, no clock,
no randomness: identical input bytes give identical output bytes.

Output: $MAKEFUN_OUTPUT_DIR/entry.png, else <script dir>/output/entry.png.
"""
import json
import os
import sys

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
MARGIN = 24

# ---------------------------------------------------------------- fonts
def _font(name, size):
    bases = [
        "/usr/share/fonts/truetype/dejavu/",
        "/usr/share/fonts/truetype/liberation/",
        "/usr/share/fonts/truetype/noto/",
    ]
    for b in bases:
        p = os.path.join(b, name)
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default(size)


F_TITLE = _font("DejaVuSerif-Bold.ttf", 46)
F_SUB = _font("DejaVuSans.ttf", 15)
F_LEAD_H = _font("DejaVuSans-Bold.ttf", 25)
F_LEAD_D = _font("DejaVuSans.ttf", 14)
F_LEAD_S = _font("DejaVuSans-Bold.ttf", 11)
F_SEC = _font("DejaVuSans-Bold.ttf", 15)
F_NUM = _font("DejaVuSans-Bold.ttf", 13)
F_HEAD = _font("DejaVuSans-Bold.ttf", 15)
F_DET = _font("DejaVuSans.ttf", 12)
F_SRC = _font("DejaVuSans.ttf", 10)
F_SCORE = _font("DejaVuSans-Bold.ttf", 26)
F_CHART_L = _font("DejaVuSans-Bold.ttf", 10)
F_CHART_V = _font("DejaVuSans.ttf", 10)
F_DC_H = _font("DejaVuSans-Bold.ttf", 12)
F_DC = _font("DejaVuSans.ttf", 11)
F_FOOT = _font("DejaVuSans.ttf", 10)

INK = (18, 18, 18)
MUTED = (90, 90, 90)
RULE = (200, 200, 200)


def wrap(draw, text, font, width):
    """Greedy word wrap; returns list of lines, each fitting `width`."""
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=font) <= width or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def fit_lines(draw, text, font, width, max_lines):
    lines = wrap(draw, text, font, width)
    if len(lines) > max_lines:
        lines = lines[:max_lines]
        # trim last line with an ellipsis until it fits
        while lines and draw.textlength(lines[-1] + " …", font=font) > width:
            lines[-1] = lines[-1][:-1]
        lines[-1] = lines[-1] + " …"
    return lines


# ---------------------------------------------------------------- visuals
def draw_globe(draw, cx, cy, r):
    """Cracked globe: circle, meridians, and a jagged crack."""
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(255, 255, 255), width=3)
    draw.ellipse([cx - r * 0.55, cy - r, cx + r * 0.55, cy + r],
                 outline=(255, 255, 255), width=2)
    draw.line([cx - r, cy, cx + r, cy], fill=(255, 255, 255), width=2)
    draw.arc([cx - r, cy - r * 0.45, cx + r, cy + r * 0.45],
             0, 360, fill=(255, 255, 255), width=2)
    crack = [(cx - r * 0.15, cy - r * 0.95), (cx + r * 0.1, cy - r * 0.55),
             (cx - r * 0.2, cy - r * 0.2), (cx + r * 0.25, cy + r * 0.15),
             (cx - r * 0.05, cy + r * 0.5), (cx + r * 0.3, cy + r * 0.85)]
    draw.line(crack, fill=(255, 176, 32), width=4, joint="curve")
    # small "NO DEAL" tag under the globe
    draw.rectangle([cx - r, cy + r + 8, cx + r, cy + r + 30],
                   fill=(255, 176, 32))
    draw.text((cx, cy + r + 19), "NO DEAL", font=F_CHART_L,
              fill=(18, 18, 18), anchor="mm")


def draw_bars(draw, x, y, w, values, lo, hi, color, unit=""):
    """Small horizontal bar chart. values: [(label, number), ...]."""
    row_h, label_w = 18, 34
    for i, (label, val) in enumerate(values):
        ry = y + i * row_h
        draw.text((x, ry + 6), label, font=F_CHART_L, fill=MUTED, anchor="lm")
        bx = x + label_w
        bw = w - label_w - 44
        frac = max(0.0, min(1.0, (val - lo) / (hi - lo)))
        draw.rectangle([bx, ry, bx + bw, ry + 12], outline=RULE, width=1)
        draw.rectangle([bx, ry, bx + int(bw * frac), ry + 12], fill=color)
        draw.text((bx + bw + 4, ry + 6), f"{val:.1f}{unit}", font=F_CHART_V,
                  fill=INK, anchor="lm")
    return y + len(values) * row_h


# ---------------------------------------------------------------- sections
def section_header(draw, x, y, w, color, name):
    draw.rectangle([x, y, x + w, y + 28], fill=color)
    draw.text((x + 10, y + 14), name, font=F_SEC, fill=(255, 255, 255),
              anchor="lm")
    return y + 28


def story_block(draw, x, y, w, num, st, color, chart_w=0):
    """One numbered story. Returns height used."""
    text_w = w - 30 - (chart_w + 10 if chart_w else 0)
    draw.text((x + 2, y + 2), f"{num:02d}", font=F_NUM, fill=color)
    head = fit_lines(draw, st["headline"], F_HEAD, text_w, 2)
    hy = y
    for ln in head:
        draw.text((x + 30, hy), ln, font=F_HEAD, fill=INK)
        hy += 17
    det = fit_lines(draw, st["detail"], F_DET, text_w, 2)
    for ln in det:
        draw.text((x + 30, hy), ln, font=F_DET, fill=(60, 60, 60))
        hy += 14
    draw.text((x + 30, hy), st["source"], font=F_SRC, fill=MUTED)
    hy += 13
    block_h = hy - y
    if "chart" in st:
        ch = st["chart"]
        unit = "%" if "REBOUND" in ch["label"] else ""
        lo, hi = (0.0, 3.5) if unit else (50.0, 56.0)
        cx = x + w - chart_w
        draw.text((cx, y + 2), ch["label"], font=F_CHART_L, fill=MUTED)
        draw_bars(draw, cx, y + 18, chart_w, ch["values"], lo, hi, color, unit)
        block_h = max(block_h, 18 + len(ch["values"]) * 18 + 4)
    if "score" in st:
        sw = draw.textlength(st["score"], font=F_SCORE)
        draw.text((x + w - sw, y + 2), st["score"], font=F_SCORE, fill=color)
    draw.line([x, y + block_h + 4, x + w, y + block_h + 4], fill=(232, 232, 232))
    return block_h + 6


# ---------------------------------------------------------------- main
def main():
    here = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(here, "stories.json"), encoding="utf-8") as fh:
        data = json.load(fh)

    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or os.path.join(here, "output")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "entry.png")

    img = Image.new("RGB", (W, H), (255, 255, 255))
    d = ImageDraw.Draw(img)

    # ---- masthead
    d.text((W // 2, 14), data["title"], font=F_TITLE, fill=INK, anchor="ma")
    d.text((W // 2, 64), data["subtitle"], font=F_SUB, fill=MUTED, anchor="ma")
    d.line([MARGIN, 84, W - MARGIN, 84], fill=INK, width=2)

    # ---- lead panel (COP31) with cracked-globe visual
    lx, ly, lw, lh = MARGIN, 92, W - 2 * MARGIN, 132
    d.rectangle([lx, ly, lx + lw, ly + lh], fill=(18, 59, 79))
    draw_globe(d, lx + 78, ly + 56, 42)
    lead = data["lead"]
    tx = lx + 160
    tw = lw - 180
    lines = fit_lines(d, lead["headline"], F_LEAD_H, tw, 2)
    hy = ly + 16
    for ln in lines:
        d.text((tx, hy), ln, font=F_LEAD_H, fill=(255, 255, 255))
        hy += 30
    for ln in fit_lines(d, lead["detail"], F_LEAD_D, tw, 2):
        d.text((tx, hy), ln, font=F_LEAD_D, fill=(210, 225, 232))
        hy += 18
    d.text((tx, ly + lh - 16), lead["source"], font=F_LEAD_S,
           fill=(255, 176, 32))

    # ---- body: WORLD left, ECONOMY + TECH right
    body_y = 236
    body_bottom = 806
    col_gap = 16
    left_w = 570
    right_w = W - 2 * MARGIN - col_gap - left_w
    lx0, rx0 = MARGIN, MARGIN + left_w + col_gap

    n = 1  # story counter (lead is story 01)
    n += 1
    eco_end = body_y
    for sec in data["sections"]:
        if sec["name"] == "WORLD":
            y = section_header(d, lx0, body_y, left_w, sec["color"], sec["name"])
            y += 4
            for st in sec["stories"]:
                y += story_block(d, lx0, y, left_w, n, st, sec["color"])
                n += 1
            assert y <= body_bottom + 2, f"WORLD overflows: {y}"
        elif sec["name"] in ("ECONOMY", "TECH"):
            start_y = body_y if sec["name"] == "ECONOMY" else eco_end + 10
            y = section_header(d, rx0, start_y, right_w, sec["color"],
                               sec["name"])
            y += 4
            for st in sec["stories"]:
                cw = 168 if "chart" in st else 0
                y += story_block(d, rx0, y, right_w, n, st, sec["color"],
                                 chart_w=cw)
                n += 1
            if sec["name"] == "ECONOMY":
                eco_end = y
            assert y <= body_bottom + 2, f"{sec['name']} overflows: {y}"

    # ---- SPORT: full-width band under the columns
    sport = next(s for s in data["sections"] if s["name"] == "SPORT")
    sy = body_bottom + 12
    sy = section_header(d, MARGIN, sy, W - 2 * MARGIN, sport["color"], "SPORT")
    sy += 6
    cell_w = (W - 2 * MARGIN - 2 * col_gap) // 3
    top = sy
    for i, st in enumerate(sport["stories"]):
        cx = MARGIN + i * (cell_w + col_gap)
        if i:
            d.line([cx - col_gap // 2, sy, cx - col_gap // 2, sy + 62],
                   fill=RULE)
        sw = d.textlength(st["score"], font=F_SCORE)
        d.text((cx + cell_w - sw, sy), st["score"], font=F_SCORE,
               fill=sport["color"])
        for j, ln in enumerate(fit_lines(d, st["headline"], F_HEAD,
                                         cell_w - int(sw) - 12, 2)):
            d.text((cx, sy + j * 17), ln, font=F_HEAD, fill=INK)
        for ln in fit_lines(d, st["detail"], F_DET, cell_w - 8, 1):
            d.text((cx, sy + 38), ln, font=F_DET, fill=(60, 60, 60))
        d.text((cx, sy + 54), st["source"], font=F_SRC, fill=MUTED)
        n += 1
    sport_bottom = sy + 68

    # ---- DATE CHECK box
    by = sport_bottom + 8
    d.rectangle([MARGIN, by, W - MARGIN, by + 68], outline=(160, 90, 0), width=2)
    d.text((MARGIN + 10, by + 6), "DATE CHECK — deliberately left out (not 23 Nov):",
           font=F_DC_H, fill=(160, 90, 0))
    dc = "  •  ".join(data["date_check"])
    dy = by + 24
    for ln in fit_lines(d, dc, F_DC, W - 2 * MARGIN - 20, 3):
        d.text((MARGIN + 10, dy), ln, font=F_DC, fill=(70, 70, 70))
        dy += 13

    # ---- footer
    d.line([MARGIN, H - 26, W - MARGIN, H - 26], fill=RULE)
    d.text((W // 2, H - 14), data["footer"], font=F_FOOT, fill=MUTED,
           anchor="mm")

    assert n - 1 == 17, f"story count {n - 1} != 17"
    img.save(out_path, format="PNG", optimize=True)
    print(f"wrote {out_path} ({W}x{H}, {n - 1} stories)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
