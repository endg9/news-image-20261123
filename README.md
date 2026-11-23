# THE WORLD IN ONE DAY — 23 November 2026

[![Reward $100](https://img.shields.io/badge/reward-%24100%20USDC-blue)](https://make.fun/bounty/news-image-20261123)
[![Places paid 50](https://img.shields.io/badge/places%20paid-50-green)](https://make.fun/bounty/news-image-20261123)
[![Ends 25 Nov 2026](https://img.shields.io/badge/ends-25%20Nov%202026-orange)](https://make.fun/bounty/news-image-20261123)

make.fun competition entry: **news-image-20261123** — "Sum up 23 November's
world news in one image".
Competition page: https://make.fun/bounty/news-image-20261123

## What it is

One 1024×1024 PNG (`entry.png`, via `main.py`) summing up the world news of
Monday 23 November 2026: **16 stories, all first reported / landed on 23 Nov
2026 WIB**, led by the collapse of the COP31 climate talks. The image is a
newspaper front page, not a plain list: a lead panel with a cracked-globe
graphic, colour-coded section bands (World / Economy / Sport / Travel) with
icons, numbered stories, big score numerals for the sports results, a mini
bar chart for the flash PMI readings, and a **DATE CHECK** box naming the
stale candidates deliberately left out (India's 720/9 Wellington record —
22 Nov; UN killer-robot talks deal — 21 Nov; "El Chapo Isidro" captured —
21 Nov; Russian ship on fire off Finland — 22 Nov; South Korea minister
quits — 22 Nov; Indonesia factory fire — 21–22 Nov; JEE Main Session 1
registration — closed 22 Nov 23:50, not 23 Nov).

## How it was built

- `stories.json` — the 16 verified stories (headline, detail, source,
  first-report time) plus the date-check list.
- `main.py` — the entry program (Python 3, Pillow only, no network). It
  reads `stories.json`, draws `entry.png` deterministically from it, and
  writes it to `MAKEFUN_OUTPUT_DIR/entry.png` (default `./output`),
  creating the output directory first. Every run writes identical bytes.

## Run

```sh
python3 main.py
# or: MAKEFUN_OUTPUT_DIR=/output python3 main.py
```

## Sources

Reuters, CNN, Fox News, S&P Global, Cricbuzz, The Hindu BusinessLine,
Sportradar. First-report times checked live per story; see `stories.json`.
Corrections applied in this v2 rebuild: the JEE Main story was dropped
(registration closed 22 Nov, not 23 Nov); the Jets–Chargers report now
reads correctly (Jets never trailed; Chargers chased late); the flash PMI
figures are the released actuals (eurozone mfg 52.9, services 51.2;
Germany 55.0 / 54.0; UK 52.7 / 52.0), not the pre-release consensus.

## License

MIT — see `LICENSE`.
