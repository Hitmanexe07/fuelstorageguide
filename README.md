# FuelStorageGuide.com

Static site for FuelStorageGuide.com, hosted on Cloudflare Pages.

- `build.py` generates every page into `site/`. Edit content in `build.py`, then run `python3 build.py`.
- `site/` is the published output. Cloudflare Pages serves this folder as-is.

## Cloudflare Pages settings

- Framework preset: None
- Build command: (leave empty)
- Build output directory: `site`
