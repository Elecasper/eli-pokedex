#!/usr/bin/env python3
"""Write sprites used by a guide to guides/img: Pokémon from data.json, items from the PokeAPI sprites repo."""
import base64, json, sys, urllib.request
from pathlib import Path
SITE = Path(__file__).resolve().parent.parent
used = json.loads((SITE / 'src' / 'guides-tr' / sys.argv[1] / 'source' / 'used.json').read_text())
data = json.loads((SITE / 'data.json').read_text(encoding='utf-8'))
img = {p['id']: p['img'] for p in data['pokemon']}
(SITE / 'guides' / 'img' / 'pm').mkdir(parents=True, exist_ok=True)
for i in used['pm']:
    f = SITE / 'guides' / 'img' / 'pm' / f'{i}.png'
    if not f.exists():
        f.write_bytes(base64.b64decode(img[i].split(',', 1)[1]))
miss = []
for s in used['items']:
    f = SITE / 'guides' / 'img' / 'items' / f'{s}.png'
    if not f.exists():
        try:
            b = urllib.request.urlopen(f'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/items/{s}.png', timeout=20).read()
            f.write_bytes(b)
        except Exception:
            miss.append(s)
print('pm', len(used['pm']), 'items', len(used['items']), 'missing item sprites', miss)
