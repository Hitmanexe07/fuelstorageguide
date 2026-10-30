"""Renders 1200x630 share images into site/og/. Run from the repo root: python3 tools/make_og.py"""
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "site" / "og"
FONTS = ROOT / "tools" / "fonts"

CARDS = [
    ("home", "Straight answers about the fuel in your tank", "Practical guides for farm, fleet, and small-business fuel storage"),
    ("do-i-need-an-spcc-plan", "Do I need an SPCC plan?", "The 1,320-gallon rule, farm thresholds, and a one-minute checker"),
    ("winter-diesel-additive", "Winter diesel additives", "What anti-gel does, when to add it, and how much"),
    ("how-long-does-diesel-last", "How long does diesel last?", "Shelf life, testing, and how to make stored fuel last"),
    ("fuel-quality", "Fuel quality guides", "Water, microbes, gelling, and old fuel: start with what you're seeing"),
    ("diesel-biocide", "Diesel bugs and biocides", "How to spot microbial growth and treat it, step by step"),
    ("water-in-diesel-tank", "Water in your diesel tank", "How it gets in, how to check, and how to get it out"),
    ("diesel-transfer-tank", "Diesel transfer tanks", "Sizing, the 119-gallon rule, and setup"),
    ("12v-fuel-transfer-pump", "Choosing a 12V fuel transfer pump", "Flow, duty cycle, and wiring, with Fill-Rite and GPI compared"),
    ("diesel-gelling-temperature", "Diesel gelling", "When it happens and how to prevent it"),
]

TEMPLATE = """<!doctype html><html><head><meta charset="utf-8"><style>
@font-face {{ font-family: 'BC'; src: url('{bc}') format('woff2'); font-weight: 700; }}
@font-face {{ font-family: 'SS'; src: url('{ss}') format('woff2'); font-weight: 400; }}
html, body {{ margin: 0; width: 1200px; height: 630px; }}
body {{ background: #1c272c; color: #fff; position: relative; overflow: hidden; }}
.bar {{ position: absolute; left: 0; top: 0; bottom: 0; width: 22px; background: #1d6a48; }}
.mark {{ position: absolute; left: 86px; top: 64px; display: inline-flex; border: 3px solid #fff; border-radius: 4px; overflow: hidden;
        font-family: 'BC'; font-weight: 700; font-size: 38px; letter-spacing: .02em; }}
.mark span {{ padding: 2px 14px; }} .mark .f {{ background: #1d6a48; }}
h1 {{ position: absolute; left: 86px; right: 90px; top: 190px; margin: 0; font-family: 'BC'; font-weight: 700;
     font-size: {size}px; line-height: 1.02; letter-spacing: -0.005em; }}
p {{ position: absolute; left: 86px; right: 120px; bottom: 112px; margin: 0; font-family: 'SS'; font-size: 34px; line-height: 1.3; color: #d6e0de; }}
.strip {{ position: absolute; left: 22px; right: 0; bottom: 0; height: 64px; background: #f0c02b; color: #1c272c;
         font-family: 'BC'; font-weight: 700; font-size: 30px; display: flex; align-items: center; padding-left: 64px; }}
</style></head><body><div class="bar"></div>
<div class="mark"><span class="f">Fuel</span><span>StorageGuide</span></div>
<h1>{title}</h1><p>{sub}</p><div class="strip">fuelstorageguide.com</div></body></html>"""

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 1200, "height": 630})
        for slug, title, sub in CARDS:
            size = 104 if len(title) <= 28 else 88
            html = TEMPLATE.format(bc=(FONTS / "barlow-condensed-latin-700-normal.woff2").as_uri(),
                                   ss=(FONTS / "source-serif-4-latin-400-normal.woff2").as_uri(),
                                   title=title, sub=sub, size=size)
            tmp = OUT / "_tmp.html"; tmp.write_text(html)
            pg.goto(tmp.as_uri()); pg.wait_for_timeout(300)
            pg.screenshot(path=str(OUT / f"{slug}.png"))
            tmp.unlink()
        b.close()
    print("rendered", len(CARDS))

if __name__ == "__main__":
    main()
