"""Renders the 512x512 square logo used in structured data into site/logo.png.
It draws the same shapes as favicon.svg. Run from the repo root: python3 tools/make_logo.py"""
from pathlib import Path
from PIL import Image, ImageDraw

OUT = Path(__file__).resolve().parent.parent / "site" / "logo.png"
S = 16  # favicon.svg is drawn on a 32x32 grid

img = Image.new("RGBA", (32 * S, 32 * S), (0, 0, 0, 0))
d = ImageDraw.Draw(img)
d.rounded_rectangle((0, 0, 32 * S - 1, 32 * S - 1), radius=4 * S, fill="#1c272c")
d.rounded_rectangle((4 * S, 9 * S, 28 * S - 1, 23 * S - 1), radius=7 * S, fill="#1d6a48")
d.rectangle((4 * S, 19 * S, 28 * S - 1, 23 * S - 1), fill="#f0c02b")
img.save(OUT, optimize=True)
print("wrote", OUT)
