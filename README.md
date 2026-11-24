[![make.fun](https://make.fun/badge/news-image-20261124.svg)](https://make.fun/bounty/news-image-20261124)
[![rank](https://make.fun/badge/news-image-20261124/cffilham-jpg/makefun-news-image-20261124-v2/rank.svg)](https://make.fun/bounty/news-image-20261124)
[![reward](https://make.fun/badge/news-image-20261124/cffilham-jpg/makefun-news-image-20261124-v2/reward.svg)](https://make.fun/bounty/news-image-20261124)

# The World in One Day — 24 November 2026 (v2)

A legibility-first news poster for the [make.fun](https://make.fun/bounty/news-image-20261124)
`news-image-20261124` bounty: one image summing up the world's news of
Tuesday 24 November 2026. The FIDE World Chess Championship Game 1 dominates
the page — champion Gukesh vs challenger Sindarov, both 20, $2.5M prize fund —
with four large secondary stories and eight one-liners below.

`main.py` is pure Python 3 standard library (no PIL): it draws the poster
with its own vector stroke font and its own PNG encoder, deterministically.

## Run

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

Writes `out/entry.png` (1024x1024, under 1 MiB).

## License

MIT — see [LICENSE](LICENSE).
