// THE WORLD IN ONE DAY — 23 November 2026 (make.fun news-image-20261123)
// Fresh Node 22 entrypoint. STANDARD LIBRARY ONLY: fs, path, url, zlib.
// Renders a 1024x1024 newspaper front page from stories.json into entry.png.
// Technique: raw RGBA pixel buffer + hand-rolled 5x7 bitmap font embedded
// below (scaled per element) + manual PNG encoder (zlib deflate + CRC32).
// Deterministic: no clock, no randomness, no network, no font files on disk.
// Output: $MAKEFUN_OUTPUT_DIR/entry.png (default: <script dir>/output).

import { readFileSync, writeFileSync, mkdirSync } from "node:fs";
import { deflateSync } from "node:zlib";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

// ---------------------------------------------------------------- font ----
// 5x7 bitmap glyphs. Each glyph is 7 rows of 5 cells ('#' = ink, '.' = blank).
// Written from scratch for this entry. Unknown characters fall back to '?'.
const FONT: Record<string, string[]> = {
  " ": [".....", ".....", ".....", ".....", ".....", ".....", "....."],
  "!": ["..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."],
  '"': [".#.#.", ".#.#.", ".#.#.", ".....", ".....", ".....", "....."],
  "#": [".#.#.", ".#.#.", "#####", ".#.#.", "#####", ".#.#.", ".#.#."],
  "$": ["..#..", ".####.", "#.#...", ".###..", "..#.#.", ".####.", "..#.."],
  "%": ["#...#", "#..#.", "....#", "...#.", "..#..", ".#...", "#...#"],
  "&": [".##..", "#..#.", "#..#.", ".#...", "#.#.#", "#..#.", ".##.#"],
  "'": ["..#..", "..#..", ".#...", ".....", ".....", ".....", "....."],
  "(": ["...##", "..#..", ".#...", ".#...", ".#...", "..#..", "...##"],
  ")": ["##...", "..#..", "...#.", "...#.", "...#.", "..#..", "##..."],
  "*": [".....", "..#..", "#.#.#", ".###.", "#.#.#", "..#..", "....."],
  "+": [".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."],
  ",": [".....", ".....", ".....", ".....", ".##..", ".##..", ".#..."],
  "-": [".....", ".....", ".....", "#####", ".....", ".....", "....."],
  ".": [".....", ".....", ".....", ".....", ".....", ".##..", ".##.."],
  "/": ["....#", "...#.", "...#.", "..#..", ".#...", ".#...", "#...."],
  "0": [".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."],
  "1": ["..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."],
  "2": [".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"],
  "3": [".###.", "#...#", "....#", "..##.", "....#", "#...#", ".###."],
  "4": ["...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."],
  "5": ["#####", "#....", "####.", "....#", "....#", "#...#", ".###."],
  "6": ["..##.", ".#...", "#....", "####.", "#...#", "#...#", ".###."],
  "7": ["#####", "....#", "...#.", "..#..", ".#...", ".#...", ".#..."],
  "8": [".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."],
  "9": [".###.", "#...#", "#...#", ".####", "....#", "...#.", ".##.."],
  ":": [".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."],
  ";": [".....", ".##..", ".##..", ".....", ".##..", ".#...", "#...."],
  "<": ["...#.", "..#..", ".#...", "#....", ".#...", "..#..", "...#."],
  "=": [".....", ".....", "#####", ".....", "#####", ".....", "....."],
  ">": [".#...", "..#..", "...#.", "....#", "...#.", "..#..", ".#..."],
  "?": [".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."],
  "@": [".###.", "#...#", "#.#.#", "#.#.#", "#.#..", "#....", ".###."],
  "A": [".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"],
  "B": ["####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."],
  "C": [".###.", "#...#", "#....", "#....", "#....", "#...#", ".###."],
  "D": ["####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."],
  "E": ["#####", "#....", "#....", "####.", "#....", "#....", "#####"],
  "F": ["#####", "#....", "#....", "####.", "#....", "#....", "#...."],
  "G": [".###.", "#...#", "#....", "#.###", "#...#", "#...#", ".###."],
  "H": ["#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"],
  "I": [".###.", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."],
  "J": ["..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."],
  "K": ["#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"],
  "L": ["#....", "#....", "#....", "#....", "#....", "#....", "#####"],
  "M": ["#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"],
  "N": ["#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#"],
  "O": [".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."],
  "P": ["####.", "#...#", "#...#", "####.", "#....", "#....", "#...."],
  "Q": [".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"],
  "R": ["####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"],
  "S": [".####", "#....", "#....", ".###.", "....#", "....#", "####."],
  "T": ["#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."],
  "U": ["#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."],
  "V": ["#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."],
  "W": ["#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"],
  "X": ["#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"],
  "Y": ["#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."],
  "Z": ["#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"],
  "[": [".###.", ".#...", ".#...", ".#...", ".#...", ".#...", ".###."],
  "\\": ["#....", ".#...", ".#...", "..#..", "..#..", "...#.", "....#"],
  "]": [".###.", "...#.", "...#.", "...#.", "...#.", "...#.", ".###."],
  "^": ["..#..", ".#.#.", ".....", ".....", ".....", ".....", "....."],
  "_": [".....", ".....", ".....", ".....", ".....", ".....", "#####"],
  "`": ["..#..", "..#..", ".#...", ".....", ".....", ".....", "....."],
  "a": [".....", ".....", ".####", "....#", ".####", "#...#", ".####"],
  "b": ["#....", "#....", "####.", "#...#", "#...#", "#...#", "####."],
  "c": [".....", ".....", ".###.", "#....", "#....", "#....", ".###."],
  "d": ["....#", "....#", ".####", "#...#", "#...#", "#...#", ".####"],
  "e": [".....", ".....", ".###.", "#...#", "#####", "#....", ".###."],
  "f": ["..##.", ".#..#", ".#...", "###..", ".#...", ".#...", ".#..."],
  "g": [".....", ".####", "#...#", "#...#", ".####", "....#", ".###."],
  "h": ["#....", "#....", "####.", "#...#", "#...#", "#...#", "#...#"],
  "i": ["..#..", ".....", ".##..", "..#..", "..#..", "..#..", ".###."],
  "j": ["...#.", ".....", "..##.", "...#.", "...#.", "...#.", ".##.."],
  "k": ["#....", "#....", "#..#.", "#.#..", "##...", "#.#..", "#..#."],
  "l": [".##..", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."],
  "m": [".....", ".....", "##.#.", "#.#.#", "#.#.#", "#.#.#", "#.#.#"],
  "n": [".....", ".....", "####.", "#...#", "#...#", "#...#", "#...#"],
  "o": [".....", ".....", ".###.", "#...#", "#...#", "#...#", ".###."],
  "p": [".....", ".....", "####.", "#...#", "#...#", "####.", "#...."],
  "q": [".....", ".....", ".####", "#...#", "#...#", ".####", "....#"],
  "r": [".....", ".....", "#.##.", "##..#", "#....", "#....", "#...."],
  "s": [".....", ".....", ".####", "#....", ".###.", "....#", "####."],
  "t": ["..#..", "..#..", ".###.", "..#..", "..#..", "..#..", ".##.."],
  "u": [".....", ".....", "#...#", "#...#", "#...#", "#..##", ".##.#"],
  "v": [".....", ".....", "#...#", "#...#", "#...#", ".#.#.", "..#.."],
  "w": [".....", ".....", "#...#", "#.#.#", "#.#.#", "#.#.#", ".#.#."],
  "x": [".....", ".....", "#...#", ".#.#.", "..#..", ".#.#.", "#...#"],
  "y": [".....", ".....", "#...#", "#...#", ".####", "....#", ".###."],
  "z": [".....", ".....", "#####", "...#.", "..#..", ".#...", "#####"],
  "{": ["...##", "..#..", "..#..", ".##..", "..#..", "..#..", "...##"],
  "|": ["..#..", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."],
  "}": ["##...", "..#..", "..#..", "..##.", "..#..", "..#..", "##..."],
  "~": [".....", ".....", ".##.#", "#.#..", ".....", ".....", "....."],
  "—": [".....", ".....", ".....", "#####", ".....", ".....", "....."],
  "–": [".....", ".....", ".....", ".###.", ".....", ".....", "....."],
  "•": [".....", "..#..", ".###.", ".###.", "..#..", ".....", "....."],
  "‘": ["..#..", "..#..", "...#.", ".....", ".....", ".....", "....."],
  "’": ["..#..", "..#..", ".#...", ".....", ".....", ".....", "....."],
  "¥": ["#...#", "#...#", ".#.#.", "..#..", ".###.", "..#..", "..#.."],
  "ñ": [".#.#.", ".....", "####.", "#...#", "#...#", "#...#", "#...#"],
  "ó": ["...#.", "..#..", ".###.", "#...#", "#...#", "#...#", ".###."],
  "é": ["...#.", "..#..", ".###.", "#...#", "#####", "#....", ".###."],
};

// Advance of one glyph cell (6 units) times the horizontal scale.
function textWidth(s: string, xs: number): number {
  let w = 0;
  for (const ch of s) w += 6 * xs;
  return w - xs; // no trailing advance after the last glyph
}

// ------------------------------------------------------------- PNG out ---
const CRC_TABLE: Uint32Array = (() => {
  const t = new Uint32Array(256);
  for (let n = 0; n < 256; n++) {
    let c = n;
    for (let k = 0; k < 8; k++) c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1;
    t[n] = c >>> 0;
  }
  return t;
})();

function crc32(buf: Buffer): number {
  let c = 0xffffffff;
  for (let i = 0; i < buf.length; i++) c = CRC_TABLE[(c ^ buf[i]) & 0xff] ^ (c >>> 8);
  return (c ^ 0xffffffff) >>> 0;
}

function chunk(type: string, data: Buffer): Buffer {
  const out = Buffer.alloc(12 + data.length);
  out.writeUInt32BE(data.length, 0);
  out.write(type, 4, "ascii");
  data.copy(out, 8);
  out.writeUInt32BE(crc32(Buffer.concat([Buffer.from(type, "ascii"), data])), 8 + data.length);
  return out;
}

// Encode an RGBA buffer (W x H, 4 bytes/px) as a PNG. Filter 0 per row.
function encodePng(rgba: Buffer, w: number, h: number): Buffer {
  const ihdr = Buffer.alloc(13);
  ihdr.writeUInt32BE(w, 0);
  ihdr.writeUInt32BE(h, 4);
  ihdr[8] = 8; // bit depth
  ihdr[9] = 6; // color type RGBA
  ihdr[10] = 0; // compression
  ihdr[11] = 0; // filter
  ihdr[12] = 0; // interlace
  const raw = Buffer.alloc(h * (1 + w * 4));
  for (let y = 0; y < h; y++) {
    raw[y * (1 + w * 4)] = 0;
    rgba.copy(raw, y * (1 + w * 4) + 1, y * w * 4, (y + 1) * w * 4);
  }
  const idat = deflateSync(raw, { level: 9 });
  return Buffer.concat([
    Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]),
    chunk("IHDR", ihdr),
    chunk("IDAT", idat),
    chunk("IEND", Buffer.alloc(0)),
  ]);
}

// --------------------------------------------------------------- canvas --
type RGB = [number, number, number];

const WHITE: RGB = [255, 255, 255];
const INK: RGB = [17, 17, 17];
const MUTED: RGB = [102, 102, 102];
const NAVY: RGB = [18, 59, 79];
const NAVY_DARK: RGB = [11, 44, 61];
const GOLD: RGB = [232, 163, 61];
const GOLD_DARK: RGB = [201, 133, 32];
const RULE: RGB = [204, 204, 204];
const DIVIDER: RGB = [221, 221, 221];
const AMBER: RGB = [176, 120, 26];
const AMBER_BG: RGB = [255, 248, 230];

function hexRgb(hex: string): RGB {
  return [
    parseInt(hex.slice(1, 3), 16),
    parseInt(hex.slice(3, 5), 16),
    parseInt(hex.slice(5, 7), 16),
  ];
}

class Canvas {
  w: number;
  h: number;
  buf: Buffer;
  constructor(w: number, h: number) {
    this.w = w;
    this.h = h;
    this.buf = Buffer.alloc(w * h * 4);
    this.fillRect(0, 0, w, h, WHITE);
  }
  px(x: number, y: number, c: RGB): void {
    const xi = Math.round(x);
    const yi = Math.round(y);
    if (xi < 0 || yi < 0 || xi >= this.w || yi >= this.h) return;
    const o = (yi * this.w + xi) * 4;
    this.buf[o] = c[0];
    this.buf[o + 1] = c[1];
    this.buf[o + 2] = c[2];
    this.buf[o + 3] = 255;
  }
  fillRect(x: number, y: number, w: number, h: number, c: RGB): void {
    const x0 = Math.max(0, Math.round(x));
    const y0 = Math.max(0, Math.round(y));
    const x1 = Math.min(this.w, Math.round(x + w));
    const y1 = Math.min(this.h, Math.round(y + h));
    for (let yy = y0; yy < y1; yy++) {
      for (let xx = x0; xx < x1; xx++) {
        const o = (yy * this.w + xx) * 4;
        this.buf[o] = c[0];
        this.buf[o + 1] = c[1];
        this.buf[o + 2] = c[2];
        this.buf[o + 3] = 255;
      }
    }
  }
  hline(x: number, y: number, w: number, c: RGB, t = 1): void {
    this.fillRect(x, y, w, t, c);
  }
  vline(x: number, y: number, h: number, c: RGB, t = 1): void {
    this.fillRect(x, y, t, h, c);
  }
  // Bresenham line, thickness t (square brush).
  line(x0: number, y0: number, x1: number, y1: number, c: RGB, t = 1): void {
    let ax = Math.round(x0);
    let ay = Math.round(y0);
    const bx = Math.round(x1);
    const by = Math.round(y1);
    const dx = Math.abs(bx - ax);
    const dy = -Math.abs(by - ay);
    const sx = ax < bx ? 1 : -1;
    const sy = ay < by ? 1 : -1;
    let err = dx + dy;
    const r = Math.floor(t / 2);
    for (;;) {
      this.fillRect(ax - r, ay - r, t, t, c);
      if (ax === bx && ay === by) break;
      const e2 = 2 * err;
      if (e2 >= dy) {
        err += dy;
        ax += sx;
      }
      if (e2 <= dx) {
        err += dx;
        ay += sy;
      }
    }
  }
  circle(cx: number, cy: number, r: number, c: RGB, t = 2): void {
    for (let a = 0; a < 360; a += 1) {
      const rad = (a * Math.PI) / 180;
      this.fillRect(
        Math.round(cx + r * Math.cos(rad)) - Math.floor(t / 2),
        Math.round(cy + r * Math.sin(rad)) - Math.floor(t / 2),
        t,
        t,
        c,
      );
    }
  }
  // Ellipse outline, parametric.
  ellipse(cx: number, cy: number, rx: number, ry: number, c: RGB, t = 1): void {
    for (let a = 0; a < 360; a += 1) {
      const rad = (a * Math.PI) / 180;
      this.fillRect(
        Math.round(cx + rx * Math.cos(rad)),
        Math.round(cy + ry * Math.sin(rad)),
        t,
        t,
        c,
      );
    }
  }
  // Draw one glyph at (x, y); xs/ys are the pixel scales. Returns advance.
  glyph(ch: string, x: number, y: number, xs: number, ys: number, c: RGB): number {
    const g = FONT[ch] ?? FONT["?"];
    for (let r = 0; r < 7; r++) {
      const row = g[r];
      for (let col = 0; col < 5; col++) {
        if (row[col] !== "#") continue;
        const px0 = Math.round(x + col * xs);
        const px1 = Math.round(x + (col + 1) * xs);
        const py0 = Math.round(y + r * ys);
        const py1 = Math.round(y + (r + 1) * ys);
        this.fillRect(px0, py0, Math.max(1, px1 - px0), Math.max(1, py1 - py0), c);
      }
    }
    return 6 * xs;
  }
  text(s: string, x: number, y: number, xs: number, ys: number, c: RGB): number {
    let cx = x;
    for (const ch of s) cx += this.glyph(ch, cx, y, xs, ys, c);
    return cx - x;
  }
  textCentered(s: string, cx: number, y: number, xs: number, ys: number, c: RGB): void {
    this.text(s, cx - textWidth(s, xs) / 2, y, xs, ys, c);
  }
}

// Word-wrap plain text to a pixel width; returns lines (no trailing spaces).
function wrap(s: string, maxW: number, xs: number): string[] {
  const words = s.split(/\s+/).filter((w) => w.length > 0);
  const lines: string[] = [];
  let cur = "";
  for (const w of words) {
    const cand = cur === "" ? w : cur + " " + w;
    if (textWidth(cand, xs) <= maxW || cur === "") {
      cur = cand;
    } else {
      lines.push(cur);
      cur = w;
    }
  }
  if (cur !== "") lines.push(cur);
  return lines;
}

// ------------------------------------------------------------ layout -----
interface Story {
  headline: string;
  detail: string;
  source: string;
  score?: string;
  chart?: { label: string; values: [string, number][] };
}
interface Section {
  name: string;
  color: string;
  stories: Story[];
}
interface Data {
  title: string;
  subtitle: string;
  lead: { headline: string; detail: string; source: string };
  sections: Section[];
  date_check: string[];
  footer: string;
}

const W = 1024;
const H = 1024;
const MX = 24; // page margin
const CW = W - 2 * MX; // 976 content width
const COLW = 480; // column width
const COL2X = MX + COLW + 16; // right column x = 520

// Body type: headline 5x7 @ 2x (14px tall, 16px leading), detail/source
// 5x7 @ 1.5x (10.5px tall, 9px advance, 12px leading). Integer x-scale
// 1.25x was tried first and smeared (uneven 1px/2px strokes); 1.5x is the
// smallest fractional scale with regular strokes that stays legible.
const H_XS = 2;
const H_YS = 2;
const H_LH = 15;
const B_XS = 1.5;
const B_YS = 1.5;
const B_LH = 12;

function drawSectionBand(cv: Canvas, x: number, y: number, w: number, name: string, color: string): void {
  cv.fillRect(x, y, w, 26, hexRgb(color));
  cv.text(name, x + 10, y + 3, 2, 2, WHITE);
}

// One body story. Returns the y just below the story (before the gap).
// num is the printed number ("02" …) or "" for none; chartW reserves
// space at the right of the headline for a mini bar chart, and chartH
// (the chart's full height) pushes the detail below the chart so the
// full-width detail can never run under the chart rows.
function drawStory(
  cv: Canvas,
  s: Story,
  x: number,
  y: number,
  num: string,
  color: string,
  chartW: number,
  chartH = 0,
): number {
  const textX = num === "" ? x : x + 34;
  const textW = COLW - (num === "" ? 0 : 34) - chartW;
  let cy = y;
  if (num !== "") {
    cv.text(num, x + 2, y + 1, H_XS, H_YS, hexRgb(color));
  }
  const hLines = wrap(s.headline, textW, H_XS);
  for (const ln of hLines) {
    cv.text(ln, textX, cy, H_XS, H_YS, INK);
    cy += H_LH;
  }
  if (chartH > 0 && cy < y + chartH) cy = y + chartH;
  const dLines = wrap(s.detail, COLW - (num === "" ? 0 : 34), B_XS);
  for (const ln of dLines) {
    cv.text(ln, textX, cy, B_XS, B_YS, INK);
    cy += B_LH;
  }
  cv.text(s.source, textX, cy, B_XS, B_YS, MUTED);
  cy += B_LH;
  return cy;
}

// Mini horizontal bar chart drawn at (x, y). Rows: label + bar + value.
function drawChart(
  cv: Canvas,
  chart: { label: string; values: [string, number][] },
  x: number,
  y: number,
  w: number,
  color: string,
  pct: boolean,
): void {
  cv.text(chart.label, x, y, B_XS, B_YS, MUTED);
  let cy = y + B_LH + 2;
  const maxV = Math.max(...chart.values.map((v) => v[1]));
  const barX = x + 42;
  const barMax = w - 42 - 52;
  for (const [lab, val] of chart.values) {
    cv.text(lab, x, cy + 1, B_XS, B_YS, INK);
    const bw = Math.max(6, Math.round((val / maxV) * barMax));
    cv.fillRect(barX, cy + 1, bw, 9, hexRgb(color));
    cv.fillRect(barX + bw, cy + 1, barMax - bw, 9, [238, 238, 238]);
    const vtxt = pct ? val.toFixed(1) + "%" : val.toFixed(1);
    cv.text(vtxt, barX + barMax + 6, cy + 1, B_XS, B_YS, INK);
    cy += 16;
  }
}

// Cracked globe for the lead panel, centred at (cx, cy), radius r.
function drawGlobe(cv: Canvas, cx: number, cy: number, r: number): void {
  cv.circle(cx, cy, r, WHITE, 2);
  cv.ellipse(cx, cy, Math.round(r * 0.42), r, WHITE, 1);
  cv.ellipse(cx, cy, r, Math.round(r * 0.32), WHITE, 1);
  cv.ellipse(cx, cy - Math.round(r * 0.55), Math.round(r * 0.72), Math.round(r * 0.3), WHITE, 1);
  cv.ellipse(cx, cy + Math.round(r * 0.55), Math.round(r * 0.72), Math.round(r * 0.3), WHITE, 1);
  // Gold lightning crack, top to bottom.
  const pts: [number, number][] = [
    [cx + 2, cy - r + 2],
    [cx - 8, cy - 14],
    [cx + 6, cy - 2],
    [cx - 6, cy + 12],
    [cx + 4, cy + 24],
    [cx - 2, cy + r - 2],
  ];
  for (let i = 0; i + 1 < pts.length; i++) {
    cv.line(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1], GOLD, 3);
  }
}

// ---------------------------------------------------------------- main ---
function main(): void {
  const here = dirname(fileURLToPath(import.meta.url));
  const data: Data = JSON.parse(readFileSync(join(here, "stories.json"), "utf8"));
  const cv = new Canvas(W, H);

  // ---- masthead ----
  cv.textCentered(data.title, W / 2, 8, 6, 6, INK);
  cv.textCentered(data.subtitle, W / 2, 54, 2, 2, MUTED);
  cv.hline(MX, 76, CW, INK, 2);

  // ---- lead panel (navy) ----
  // leadH 97 (was 92): the extra 5px funds the clearance below the
  // headline so the detail line never crowds the last headline line.
  // (Kept to +5: the page bottom has only 5px of slack in v5, so a
  // taller panel must be paid for below — see the DATE CHECK gap.)
  const leadY = 84;
  const leadH = 97;
  cv.fillRect(MX, leadY, CW, leadH, NAVY);
  drawGlobe(cv, MX + 66, leadY + 42, 32);
  // NO DEAL tag under the globe.
  cv.fillRect(MX + 16, leadY + 74, 100, 18, GOLD);
  cv.textCentered("NO DEAL", MX + 66, leadY + 77, 2, 2, NAVY_DARK);
  const lx = MX + 148;
  const lw = CW - 148 - 16;
  const leadHead = wrap(data.lead.headline, lw, 3);
  let ly = leadY + 8;
  for (const ln of leadHead) {
    cv.text(ln, lx, ly, 3, 3, WHITE);
    ly += 22;
  }
  // Clearance between the last headline line and the first detail line:
  // headline ink ends 1px above the detail in v5; 5px of leading here
  // leaves a 6px blank gap (funded by the taller lead panel above).
  ly += 5;
  const leadDet = wrap(data.lead.detail, lw, B_XS);
  for (const ln of leadDet) {
    cv.text(ln, lx, ly, B_XS, B_YS, [220, 230, 235]);
    ly += B_LH;
  }
  cv.text(data.lead.source, lx, ly + 1, 2, 2, GOLD);

  // ---- body columns ----
  const bandY = leadY + leadH + 6; // 182
  const bodyY = bandY + 26 + 6; // 214
  const world = data.sections[0];
  const economy = data.sections[1];
  const tech = data.sections[2];
  const sport = data.sections[3];

  drawSectionBand(cv, MX, bandY, COLW, world.name, world.color);
  drawSectionBand(cv, COL2X, bandY, COLW, economy.name, economy.color);

  // LEFT: WORLD stories 02–09.
  let y = bodyY;
  let n = 2;
  for (const s of world.stories) {
    const end = drawStory(cv, s, MX, y, String(n).padStart(2, "0"), world.color, 0);
    y = end + 3;
    n++;
  }
  const leftEnd = y - 3;

  // RIGHT: ECONOMY (10–12) then TECH band + stories (13–14).
  // Right-column stories are spread out (40px gaps vs 3px on the left)
  // so the column ends level with the left column instead of ~190px
  // above the SPORT band (measured last-ink-row to band: ~44px).
  const RIGHT_STORY_GAP = 40;
  let y2 = bodyY;
  let m = 10;
  for (const s of economy.stories) {
    const chartW = s.chart ? 220 : 0;
    const chartH = s.chart ? B_LH + 2 + 16 * s.chart.values.length : 0;
    const end = drawStory(cv, s, COL2X, y2, String(m).padStart(2, "0"), economy.color, chartW, chartH);
    if (s.chart) {
      drawChart(cv, s.chart, COL2X + COLW - 220, y2 + 2, 220, economy.color, m === 11);
    }
    y2 = end + RIGHT_STORY_GAP;
    m++;
  }
  const techBandY = y2 + 2;
  drawSectionBand(cv, COL2X, techBandY, COLW, tech.name, tech.color);
  y2 = techBandY + 26 + 8;
  for (const s of tech.stories) {
    const end = drawStory(cv, s, COL2X, y2, String(m).padStart(2, "0"), tech.color, 0);
    y2 = end + RIGHT_STORY_GAP;
    m++;
  }
  const rightEnd = y2 - 3;

  // ---- SPORT band (full width) ----
  const sportY = Math.max(leftEnd, rightEnd) + 5;
  drawSectionBand(cv, MX, sportY, CW, sport.name, sport.color);
  const cellW = Math.floor(CW / 3);
  let cy = sportY + 26 + 6;
  const cellTop = cy;
  for (let i = 0; i < sport.stories.length; i++) {
    const s = sport.stories[i];
    const cx0 = MX + i * cellW;
    if (i > 0) cv.vline(cx0 - 8, cellTop, 84, DIVIDER, 1);
    const scoreW = textWidth(s.score ?? "", 4);
    // Fixed 130px numeral zone at the cell's right: the headline wraps
    // only within the remaining width, so no headline glyph can ever
    // reach the big score (min ink gap 31px: widest score "51–30" is
    // 116px, leaving 14px of zone + its own left bearing).
    const SCORE_ZONE = 130;
    const headW = cellW - 24 - SCORE_ZONE;
    const hLines = wrap(s.headline, headW, H_XS);
    let sy = cellTop;
    for (const ln of hLines) {
      cv.text(ln, cx0, sy, H_XS, H_YS, INK);
      sy += H_LH;
    }
    const dLines = wrap(s.detail, cellW - 24, B_XS);
    for (const ln of dLines) {
      cv.text(ln, cx0, sy, B_XS, B_YS, INK);
      sy += B_LH;
    }
    cv.text(s.source, cx0, sy, B_XS, B_YS, MUTED);
    // Big score numeral at the right of the cell, vertically centred.
    cv.text(s.score ?? "", cx0 + cellW - 24 - scoreW, cellTop + 6, 4, 4, hexRgb(sport.color));
  }
  cy = cellTop + 84;

  // ---- DATE CHECK box (amber outline) ----
  // Gap 5px (was 8px): pays for 3 of the 5px the taller lead panel
  // added, keeping the footer inside the 1024px page.
  const dcY = cy + 5;
  const dcInner = "DATE CHECK — deliberately left out (not 23 Nov): " +
    data.date_check.join(" • ");
  const dcXs = 1.25; // fine print: narrower so all 12 items fit in 4 lines
  const dcLines = wrap(dcInner, CW - 24, dcXs);
  const dcLH = 11; // fine print inside the box: tight leading is fine here
  const dcH = 5 + dcLines.length * dcLH + 5;
  cv.fillRect(MX, dcY, CW, dcH, AMBER_BG);
  cv.hline(MX, dcY, CW, AMBER, 2);
  cv.hline(MX, dcY + dcH - 2, CW, AMBER, 2);
  cv.vline(MX, dcY, dcH, AMBER, 2);
  cv.vline(MX + CW - 2, dcY, dcH, AMBER, 2);
  let dy = dcY + 3;
  for (const ln of dcLines) {
    cv.text(ln, MX + 12, dy, dcXs, B_YS, INK);
    dy += dcLH;
  }

  // ---- footer ----
  const footY = dcY + dcH + 2;
  const f1 = "Every story first reported / landed on 23 Nov 2026 WIB";
  const f2 = "Sources: Reuters, CNN, AP, Fox News, S&P Global, Cricbuzz, The Hindu BusinessLine, CBS, ECB";
  cv.textCentered(f1, W / 2, footY, B_XS, B_YS, MUTED);
  cv.textCentered(f2, W / 2, footY + B_LH, B_XS, B_YS, MUTED);
  const bottom = footY + 2 * B_LH;
  if (bottom > H) throw new Error("layout overflow: bottom=" + bottom);

  // ---- write PNG ----
  const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? join(here, "output");
  mkdirSync(outDir, { recursive: true });
  const png = encodePng(cv.buf, W, H);
  writeFileSync(join(outDir, "entry.png"), png);
}

main();
