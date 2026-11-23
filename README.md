# THE WORLD IN ONE DAY — 23 November 2026

[![Reward $100](https://img.shields.io/badge/reward-%24100%20USDC-blue)](https://make.fun/bounty/news-image-20261123)
[![Places paid 50](https://img.shields.io/badge/places%20paid-50-green)](https://make.fun/bounty/news-image-20261123)
[![Ends 25 Nov 2026](https://img.shields.io/badge/ends-25%20Nov%202026-orange)](https://make.fun/bounty/news-image-20261123)

make.fun competition entry: **news-image-20261123** — "Sum up 23 November's
world news in one image".
Competition page: https://make.fun/bounty/news-image-20261123

## What it is

One 1024×1024 PNG (`entry.png`, via `main.py`) summing up the world news of
Monday 23 November 2026: **18 stories, all first reported / landed on 23 Nov
2026 WIB**, led by the collapse of the COP31 climate talks. The image is a
newspaper front page, not a plain list: a lead panel with a cracked-globe
graphic and a NO DEAL tag, colour-coded section bands (World / Economy /
Tech / Sport) with numbers, big score numerals for the sports results, a
mini bar chart for the flash PMI readings, a second mini chart for Monday's
market rebound (Nasdaq futures +3.0%, S&P +2.0%, gold +2.1%), and a
**DATE CHECK** box naming the stale candidates deliberately left out.

Sport is 3 of 18 stories (17%): Cowboys 51–30 Titans, Liverpool 4–0 Man Utd,
India–NZ Test draw. The two Trump–Iran items are merged into one story.
Travel has no section in this version: the US flights snarl was dropped
rather than carried as a lone item.

## How it was built

- `stories.json` — the 18 verified stories (headline, detail, source,
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

Reuters, CNN, AP, Fox News, S&P Global, Cricbuzz, The Hindu BusinessLine,
CBS, ECB. First-report times checked live per story; see `stories.json`.

Corrections and choices in this v3 rebuild: the flash PMI figures are the
released actuals (eurozone mfg 52.9, services 51.2; Germany 55.0 / 54.0;
UK 52.7 / 52.0), not the pre-release consensus. The US flash PMI is NOT
printed: it releases 21:45 WIB, after this build, and a "due" line would
read stale at judging time. New stories verified live for 23 Nov: Democrats
clinch 258 House seats (AP), Russia fires 153 drones at Ukraine overnight,
boy aged 7 pulled alive in Dymer (BBC), Bangladesh vows to jail Hasina if
she returns (Reuters), futures bounce as Asia halts the AI rout (Reuters),
Libya oil output down 365,000 bpd (Reuters/NOC), TD sees 3 straight Fed
hikes from December, Bessent presses Nvidia on China chips (CBS), ECB
clears DLT assets as collateral. Excluded as not 23 Nov: ICJ
Myanmar–Rohingya ruling (19 Nov), Riemann proof (posted 20 Nov, certified
21 Nov), pig-kidney 1-year record (NYT 22 Nov), Seattle jet-bridge ICE
arrests (21–22 Nov).

## License

MIT — see `LICENSE`.
