# FuelStorageGuide.com

Static site for FuelStorageGuide.com, hosted on Cloudflare Pages.

- `build.py` generates every page into `site/`. Edit content in `build.py`, then run `python3 build.py`.
- `site/` is the published output. Cloudflare Pages serves this folder as-is.

## Cloudflare Pages settings

- Framework preset: None
- Build command: (leave empty)
- Build output directory: `site`

## Images

- `tools/make_og.py` renders the 1200x630 share images into `site/og/`. Add a line to `CARDS` for each new guide, then run `python3 tools/make_og.py` before `python3 build.py`.
- `tools/diagrams.py` holds the inline SVG diagrams used in guides.
