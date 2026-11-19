# news-image-20261119

![badge](https://make.fun/badge/news-image-20261119.svg) ![rank](https://make.fun/badge/news-image-20261119/tech-node941/mkf-news-96398/rank.svg) ![reward](https://make.fun/badge/news-image-20261119/tech-node941/mkf-news-96398/reward.svg)

A make.fun competition entry for [news-image-20261119](https://make.fun/bounty/news-image-20261119).

## What it does

Renders a 1024x768 newspaper-style front page PNG summarizing world news for
Thursday 19 November 2026 and writes it to `$MAKEFUN_OUTPUT_DIR/entry.png`
(falls back to `./out/entry.png`).

## Headlines

- Grand Theft Auto VI console launch day: sell-out queues worldwide
- Global markets: mixed close as traders weigh rate outlook
- Climate summit: tentative emissions deal in final hours
- Tech/AI: data-center investment race and regulatory scrutiny
- Sports: Champions League comeback flips the tie
- Business: oil near $79, gold at record highs

## Run

```
python3 main.py              # writes ./out/entry.png
MAKEFUN_OUTPUT_DIR=out python3 main.py
```

Python 3.13, standard library only (zlib, struct). No network. Deterministic:
running twice yields byte-identical PNGs.

## License

MIT - see [LICENSE](LICENSE). tech-node941.
