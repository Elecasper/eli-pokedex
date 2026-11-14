#!/usr/bin/env python3
"""After a converter change, move translations to their new keys.

Usage: bulba-remap-v1.py <guide-slug> <part> ...
Compares the committed part-N.keys.json (git HEAD) with a fresh conversion and,
per key prefix, re-attaches each translation to the new key whose English text matches.
"""
import importlib.util, json, re, subprocess, sys
from pathlib import Path

SITE = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location('bw', SITE / 'src' / 'bulba-walkthrough-v1.py')
bw = importlib.util.module_from_spec(spec)
sys.argv, args = ['x', 'none'], sys.argv[1:]
spec.loader.exec_module(bw)
slug, parts = args[0], [int(x) for x in args[1:]]
base = SITE / 'src' / 'guides-tr' / slug
for n in parts:
    rel = f'src/guides-tr/{slug}/source/part-{n}.keys.json'
    old = json.loads(subprocess.check_output(['git', 'show', f'HEAD:{rel}'], cwd=SITE))
    src = json.loads((base / 'source' / f'part-{n}.json').read_text(encoding='utf-8'))
    new = {}
    bw.convert(src['parse']['wikitext']['*'], new)
    f = base / 'zh' / f'part-{n}.txt'
    zh = {}
    for line in f.read_text(encoding='utf-8').splitlines():
        m = re.match(r'^([A-Z]\d+):\s?(.*)$', line)
        if m:
            zh[m.group(1)] = m.group(2)
    out = {}
    for pre in sorted({re.match(r'[A-Z]', k).group(0) for k in new}):
        o = [(k, v) for k, v in old.items() if re.match(pre + r'\d+$', k)]
        j = 0
        for k, v in ((k, v) for k, v in new.items() if re.match(pre + r'\d+$', k)):
            while j < len(o) and o[j][1] != v:
                j += 1
            if j < len(o) and o[j][0] in zh:
                out[k] = zh[o[j][0]]
                j += 1
    f.write_text('\n'.join(f'{k}: {v}' for k, v in out.items()) + '\n', encoding='utf-8')
    print(n, 'kept', len(out), 'of', len(zh), 'translations; new keys', len(new))
