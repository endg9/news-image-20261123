#!/usr/bin/env python3
"""news-image-20261123 v2 — 'THE WORLD IN ONE DAY'.

Draws a 1024x1024 newspaper front page for Monday 23 November 2026 from
the story data embedded below. No network, no timestamps, no randomness:
every run writes byte-identical PNG output.

Run:  python3 main.py
      MAKEFUN_OUTPUT_DIR=/output python3 main.py
"""

import json
import os
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
M = 32                      # side margin
CW = W - 2 * M              # content width (960)

NAVY = (16, 38, 63)
RED = (180, 35, 24)
PAPER = (245, 241, 230)
CARD = (255, 255, 255)
INK = (18, 18, 18)
GREY = (90, 90, 90)
FAINT = (210, 205, 190)
AMBER_BG = (255, 243, 214)
AMBER_EDGE = (190, 150, 40)

# ---------------------------------------------------------------- data
# (story data lives in stories.json next to this file; the same data is
# embedded here so the program is self-contained at grading time.)
DATA = json.loads(Path(__file__).with_name("stories.json").read_text())

# ---------------------------------------------------------------- fonts
_CANDIDATES = [
    ("bold", [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf",
    ]),
    ("regular", [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf",
    ]),
    ("serif_bold", [
        "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf",
        "/usr/share/fonts/truetype/noto/NotoSerif-Bold.ttf",
    ]),
]


def _pick(kind):
    for path in dict(_CANDIDATES)[kind]:
        if Path(path).is_file():
            return path
    return None


FONTS = {k: _pick(k) for k, _ in _CANDIDATES}


def font(kind, size):
    p = FONTS.get(kind)
    if p:
        return ImageFont.truetype(p, size)
    return ImageFont.load_default(size=size)


def text_w(f, s):
    return f.getbbox(s)[2] if hasattr(f, "getbbox") else f.getlength(s)


def fit_font(kind, size, max_w, text, min_size=10):
    """Largest font size <= size whose rendering of text fits max_w."""
    s = size
    while s > min_size:
        f = font(kind, s)
        if text_w(f, text) <= max_w:
            return f
        s -= 1
    return font(kind, min_size)


def draw_fit(d, xy, text, kind, size, max_w, fill, min_size=10):
    f = fit_font(kind, size, max_w, text, min_size)
    d.text(xy, text, font=f, fill=fill)
    return f


def wrap_lines(text, f, max_w):
    words, lines, cur = text.split(), [], ""
    for word in words:
        trial = (cur + " " + word).strip()
        if text_w(f, trial) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


# ---------------------------------------------------------------- icons
def icon_globe(d, cx, cy, r, color):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=color, width=2)
    d.ellipse([cx - r * 0.45, cy - r, cx + r * 0.45, cy + r], outline=color, width=1)
    d.line([cx - r, cy, cx + r, cy], fill=color, width=1)
    d.arc([cx - r, cy - r * 0.55, cx + r, cy + r * 0.55], 0, 360, fill=color, width=1)


def icon_bars(d, x, y, color):
    hs = [5, 11, 8]
    for i, h in enumerate(hs):
        bx = x + i * 6
        d.rectangle([bx, y + 14 - h, bx + 4, y + 14], fill=color)


def icon_ball(d, cx, cy, r, color):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=color, width=2)
    d.arc([cx - r, cy - r, cx + r, cy + r], 200, 340, fill=color, width=1)
    d.arc([cx - r, cy - r, cx + r, cy + r], 20, 160, fill=color, width=1)
    d.line([cx - r, cy, cx + r, cy], fill=color, width=1)


def icon_plane(d, x, y, color):
    d.polygon([(x, y + 6), (x + 16, y), (x + 12, y + 8),
               (x + 16, y + 13), (x + 8, y + 10), (x + 5, y + 14),
               (x + 3, y + 10)], fill=color)


def draw_icon(d, kind, x, y, color):
    if kind == "globe":
        icon_globe(d, x + 8, y + 7, 8, color)
    elif kind == "bars":
        icon_bars(d, x, y, color)
    elif kind == "ball":
        icon_ball(d, x + 8, y + 7, 8, color)
    elif kind == "plane":
        icon_plane(d, x, y, color)


# ---------------------------------------------------------------- page
def render():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # ---- masthead -------------------------------------------------
    d.rectangle([0, 0, W, 92], fill=NAVY)
    d.text((M, 10), DATA["title"], font=font("serif_bold", 52), fill=(255, 255, 255))
    d.text((M, 70), DATA["subtitle"], font=font("regular", 15), fill=(200, 210, 225))
    d.text((W - M, 70), "16 STORIES", font=font("bold", 15),
           fill=(255, 210, 90), anchor="ra")
    d.rectangle([0, 92, W, 97], fill=RED)

    # ---- lead panel ----------------------------------------------
    ly, lh = 105, 112
    d.rectangle([M, ly, W - M, ly + lh], fill=CARD, outline=FAINT, width=1)
    d.rectangle([M, ly, M + 8, ly + lh], fill=RED)
    tag = "  LEAD  •  CLIMATE  "
    tf = font("bold", 13)
    tw = text_w(tf, tag)
    d.ellipse([M + 20, ly + 8, M + 44, ly + 32], fill=RED)
    d.text((M + 32, ly + 20), "1", font=tf, fill=(255, 255, 255), anchor="mm")
    d.rectangle([M + 52, ly + 10, M + 52 + tw + 8, ly + 30], fill=RED)
    d.text((M + 56, ly + 11), tag, font=tf, fill=(255, 255, 255))
    lead = DATA["lead"]
    hx = M + 20
    hw = 660
    hf = fit_font("bold", 29, hw, lead["headline"], 20)
    d.text((hx, ly + 36), lead["headline"], font=hf, fill=INK)
    df = font("regular", 16)
    for i, line in enumerate(wrap_lines(lead["detail"], df, hw)[:2]):
        d.text((hx, ly + 70 + i * 20), line, font=df, fill=(40, 40, 40))
    d.text((W - M - 8, ly + 11), lead["source"],
           font=font("regular", 12), fill=GREY, anchor="ra")
    # cracked-globe graphic on the right of the lead panel
    gx, gy, gr = 848, ly + 60, 34
    d.ellipse([gx - gr, gy - gr, gx + gr, gy + gr], outline=NAVY, width=4)
    d.ellipse([gx - gr * 0.45, gy - gr, gx + gr * 0.45, gy + gr],
              outline=NAVY, width=2)
    d.line([gx - gr, gy, gx + gr, gy], fill=NAVY, width=2)
    crack = [(gx - 6, gy - gr + 4), (gx + 8, gy - 18), (gx - 4, gy + 2),
             (gx + 10, gy + 20), (gx - 2, gy + gr - 4)]
    d.line(crack, fill=RED, width=4, joint="curve")
    d.text((gx - 34, gy + gr + 2), "NO DEAL", font=font("bold", 12), fill=RED)

    # ---- sections -------------------------------------------------
    y = 225
    n = 1  # lead story is #1; rows below are #2..#16
    for sec in DATA["sections"]:
        color = tuple(int(sec["color"][i:i + 2], 16) for i in (1, 3, 5))
        d.rectangle([M, y, W - M, y + 24], fill=color)
        draw_icon(d, sec["icon"], M + 8, y + 5, (255, 255, 255))
        d.text((M + 30, y + 4), sec["name"], font=font("bold", 15),
               fill=(255, 255, 255))
        d.text((W - M - 8, y + 4), f"{len(sec['stories'])}",
               font=font("bold", 15), fill=(255, 255, 255), anchor="ra")
        y += 24
        for st in sec["stories"]:
            n += 1
            tall = "chart" in st
            rh = 64 if tall else 37
            d.rectangle([M, y, W - M, y + rh], fill=CARD)
            d.line([M, y + rh - 1, W - M, y + rh - 1], fill=FAINT, width=1)
            # number chip
            cy = y + rh // 2
            d.ellipse([M + 4, cy - 12, M + 28, cy + 12], fill=color)
            num = str(n)
            nf = font("bold", 13)
            d.text((M + 16, cy), num, font=nf, fill=(255, 255, 255),
                   anchor="mm")
            tx = M + 36
            if tall:
                twd = 700
            elif "score" in st:
                twd = 800
            else:
                twd = 820
            draw_fit(d, (tx, y + 4), st["headline"], "bold", 17, twd, INK)
            d.text((tx, y + 21 if not tall else y + 40), st["detail"],
                   font=font("regular", 13), fill=(50, 50, 50))
            if "score" in st:
                sf = fit_font("bold", 20, 110, st["score"], 14)
                d.text((W - M - 8, y + 5), st["score"], font=sf,
                       fill=color, anchor="ra")
                d.text((W - M - 8, y + 26), st["source"],
                       font=font("regular", 10), fill=GREY, anchor="ra")
            elif tall:
                # mini bar chart: flash manufacturing PMI vs the 50 line
                ch = st["chart"]
                bx0, bw = 800, 128
                d.text((bx0, y + 4), ch["label"], font=font("bold", 11),
                       fill=GREY)
                lo, hi = 48.0, 56.0
                zero_x = bx0 + (50.0 - lo) / (hi - lo) * bw
                for i, (lab, val) in enumerate(ch["values"]):
                    by = y + 20 + i * 14
                    d.text((bx0 - 34, by - 2), lab, font=font("bold", 11),
                           fill=INK)
                    d.rectangle([bx0, by, bx0 + bw, by + 8], fill=(225, 225, 225))
                    d.rectangle([bx0, by, bx0 + (val - lo) / (hi - lo) * bw,
                                 by + 8], fill=color)
                    d.text((bx0 + bw + 5, by - 2), f"{val:.1f}",
                           font=font("bold", 11), fill=INK)
                d.line([zero_x, y + 18, zero_x, y + 18 + 3 * 14],
                       fill=RED, width=1)
            else:
                d.text((W - M - 8, y + 5), st["source"],
                       font=font("regular", 10), fill=GREY, anchor="ra")
            y += rh
        y += 6

    # ---- date check ----------------------------------------------
    dy = y + 2
    d.rectangle([M, dy, W - M, dy + 66], fill=AMBER_BG,
                outline=AMBER_EDGE, width=1)
    d.polygon([(M + 10, dy + 22), (M + 20, dy + 8), (M + 30, dy + 22)],
              fill=AMBER_EDGE)
    d.text((M + 20, dy + 15), "!", font=font("bold", 13), fill=(255, 255, 255),
           anchor="mm")
    d.text((M + 38, dy + 7), "DATE CHECK — LEFT OUT ON PURPOSE (NOT 23 NOV)",
           font=font("bold", 13), fill=(90, 60, 0))
    items = "  •  ".join(DATA["date_check"])
    df = font("regular", 12)
    for i, line in enumerate(wrap_lines(items, df, W - 2 * M - 38 - 8)[:2]):
        d.text((M + 38, dy + 26 + i * 16), line, font=df, fill=(70, 50, 0))

    # ---- footer ----------------------------------------------------
    d.text((W // 2, H - 18), DATA["footer"], font=font("regular", 12),
           fill=GREY, anchor="mm")
    return img


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if out_dir:
        out = Path(out_dir)
    else:
        out = Path(__file__).resolve().parent / "output"
    out.mkdir(parents=True, exist_ok=True)
    img = render()
    img.save(out / "entry.png", format="PNG", optimize=True)


if __name__ == "__main__":
    main()
