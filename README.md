# THE WORLD IN ONE DAY — 23 November 2026

make.fun competition entry: **news-image-20261123** — "Sum up 23 November's
world news in one image".

## What it is

One 1024×1024 PNG (`entry.png`, via `main.ts`) summing up the world news of
Monday 23 November 2026: **17 stories, all first reported / landed on 23 Nov
2026 WIB**, led by the collapse of the COP31 climate talks. The image also
carries a **DATE CHECK** box naming the stale candidates deliberately left
out (India's 720/9 Wellington record — 22 Nov; UN killer-robot talks deal —
21 Nov; "El Chapo Isidro" captured — 21 Nov; Russian ship on fire off
Finland — 22 Nov; South Korea minister quits — 22 Nov; Indonesia factory
fire — 21–22 Nov).

## How it was built

- `stories.json` — the 17 verified stories (headline, detail, source, first-report time).
- `render.py` — fresh renderer (Python + PIL, fixed fonts/layout, no network,
  no timestamps) that draws `entry.png` deterministically from `stories.json`.
- `main.ts` — the entry program (Node 22, no network). It embeds the rendered
  PNG and writes it to `MAKEFUN_OUTPUT_DIR/entry.png` (default `./output`),
  creating the output directory first. Every run writes identical bytes.

## Run

```sh
node main.ts
# or: MAKEFUN_OUTPUT_DIR=/output node main.ts
```

## Sources

Reuters, CNN, Fox News, AP, BBC, Sportradar. First-report times checked live
per story; see `stories.json`. Two items are flagged BORDERLINE in the notes:
Nepal–Modi talks and JEE Main registration closing (events held today,
announced earlier).

## License

MIT — see `LICENSE`.
