"""Convert downloaded HGSS map PNGs (hgss_maps.zip, unzipped) into guides/img/maps/*.webp.
Usage: python3 -I src/import-maps-v1.py <folder-with-pngs>"""
import re, sys
from pathlib import Path
from PIL import Image

SITE = Path(__file__).resolve().parent.parent
OUT = SITE / 'guides' / 'img' / 'maps'
OUT.mkdir(parents=True, exist_ok=True)
MAXW = 900
n = size = 0
for f in sorted(Path(sys.argv[1]).glob('*.png')):
    slug = re.sub(r'[^a-z0-9]+', '-', f.stem.lower()).strip('-')
    with Image.open(f) as im:
        im = im.convert('RGBA' if im.mode in ('RGBA', 'LA', 'P') else 'RGB')
        if im.width > MAXW:
            im = im.resize((MAXW, round(im.height * MAXW / im.width)), Image.LANCZOS)
        im.save(OUT / f'{slug}.webp', 'WEBP', quality=88, method=6)
    n += 1
    size += (OUT / f'{slug}.webp').stat().st_size
print(f'{n} maps, {size / 1e6:.1f} MB')
