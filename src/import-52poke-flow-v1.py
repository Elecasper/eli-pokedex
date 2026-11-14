#!/usr/bin/env python3
"""Import 神奇宝贝百科 walkthrough appendix pages into src/guides-tr/<slug>/.

Usage: import-52poke-flow-v1.py [slug ...]   (default: all in GAMES)
Fetches the zh-hans rendering, strips wiki links and site templates, splits the
page at each <h2> into its own guide page, and swaps the wiki's icons for local
sprites (Pokémon from data.json, items from guides/img/items). Content license:
CC BY-NC-SA 3.0 (神奇宝贝百科).
"""
import html, json, re, sys, time, urllib.parse, urllib.request
from html.parser import HTMLParser
from pathlib import Path

SITE = Path(__file__).resolve().parent.parent
GAMES = {
    'pokemon-bw': ('黑 / 白', 'NDS', '附录:寶可夢 黑／白流程'),
    'pokemon-b2w2': ('黑2 / 白2', 'NDS', '附录:寶可夢 黑２／白２流程'),
    'pokemon-pt': ('白金', 'NDS', '附录:寶可夢 白金流程'),
    'pokemon-hgss': ('心金 / 魂银', 'NDS', '附录:寶可夢 心金／魂銀流程'),
    'pokemon-xy': ('X / Y', '3DS', '附录:寶可夢 Ｘ／Ｙ流程'),
    'pokemon-oras': ('欧米伽红宝石 / 阿尔法蓝宝石', '3DS', '附录:寶可夢 歐米加紅寶石／阿爾法藍寶石流程'),
    'pokemon-usum': ('究极之日 / 究极之月', '3DS', '附录:精灵宝可梦 究极之日／究极之月流程'),
    'pokemon-frlg': ('火红 / 叶绿', 'GBA', '附录:寶可夢 火紅／葉綠流程'),
    'pokemon-e': ('绿宝石', 'GBA', '附录:寶可夢 綠寶石流程'),
}
UA = {'User-Agent': 'Mozilla/5.0 (Macintosh) EliSiteGuide/1.0'}
data = json.loads((SITE / 'data.json').read_text(encoding='utf-8'))
SPRITE = {p['id']: p['img'] for p in data['pokemon']}
NAME = {p['id']: p['n'] for p in data['pokemon']}
# Item sprites from the PokeAPI sprites repo, stored in guides/img/items/
ICONS = json.loads((SITE / 'src' / 'item-icons-v1.json').read_text(encoding='utf-8'))
e = html.escape


class Clean(HTMLParser):
    KEEP = {'p', 'ul', 'ol', 'li', 'b', 'i', 'small', 'br', 'h2', 'h3', 'h4', 'table', 'tr', 'td', 'th', 'dl', 'dt', 'dd'}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.out, self.skip, self.stack = [], 0, []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        cls = a.get('class', '') or ''
        if self.skip:
            if tag not in ('br', 'img'):
                self.skip += 1
            return
        if tag == 'table' and ('神奇寶貝百科' in cls or 'bd-蓝宝石 at-c' in cls):
            self.skip = 1
            return
        if tag in ('sup', 'style', 'script') or 'mw-editsection' in cls or tag == 'meta':
            if tag not in ('meta',):
                self.skip = 1
            return
        if tag == 'span':
            m = re.search(r'sprite-icon-(\d+)', cls)
            if m and int(m.group(1)) in SPRITE:
                pid = int(m.group(1))
                self.out.append(f'<img class="pm" src="{SPRITE[pid]}" alt="{e(NAME[pid])}" width="40" height="30">')
            self.stack.append(None)
            return
        if tag == 'img':
            slug = ICONS.get(a.get('alt', ''))
            if slug:
                self.out.append(f'<img class="icon" src="../img/items/{slug}.png" alt="{e(a["alt"])}" width="30" height="30" loading="lazy">')
            return
        if tag in self.KEEP:
            if tag == 'h4':
                tag = 'h3'
            extra = ' class="grid"' if tag == 'table' else ''
            if tag in ('td', 'th'):
                for k in ('colspan', 'rowspan'):
                    if a.get(k, '').isdigit():
                        extra += f' {k}="{a[k]}"'
            self.out.append(f'<{tag}{extra}>')
            if tag != 'br':
                self.stack.append(tag)
        elif tag not in ('br',):
            self.stack.append(None)

    def handle_endtag(self, tag):
        if self.skip:
            self.skip -= 1
            return
        if tag in ('img', 'br', 'meta'):
            return
        if self.stack:
            t = self.stack.pop()
            if t:
                self.out.append(f'</{t}>')

    def handle_data(self, d):
        if not self.skip:
            self.out.append(e(d))


def fetch(title):
    u = 'https://wiki.52poke.com/zh-hans/' + urllib.parse.quote(title.replace(' ', '_'))
    s = urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=60).read().decode()
    rev = int(re.search(r'"wgRevisionId":(\d+)', s).group(1))
    q = 'https://wiki.52poke.com/api.php?' + urllib.parse.urlencode(
        {'format': 'json', 'action': 'query', 'prop': 'revisions', 'rvprop': 'timestamp', 'revids': rev})
    page = next(iter(json.load(urllib.request.urlopen(urllib.request.Request(q, headers=UA), timeout=30))['query']['pages'].values()))
    i = s.rfind('<div', 0, s.index('mw-parser-output'))
    j = s.index('printfooter', i)
    return s[i:j], rev, page['revisions'][0]['timestamp'], page['title']


def build(slug, game, plat, title):
    raw, rev, ts, canon = fetch(title)
    folder = SITE / 'src' / 'guides-tr' / slug
    (folder / 'source').mkdir(parents=True, exist_ok=True)
    (folder / 'source' / 'page.html').write_text(raw, encoding='utf-8')
    c = Clean(); c.feed(raw)
    body = ''.join(c.out)
    body = re.sub(r'<p>\s*</p>|<li>\s*</li>', '', body)
    body = re.sub(r'<li>([^<]+?)\s*<ul>', r'<li class="loc"><span>\1</span><ul>', body)
    parts = re.split(r'<h2>(.*?)</h2>', body, flags=re.S)
    intro, parts = parts[0], parts[1:]
    pages, meta = [], {}
    for n in range(0, len(parts), 2):
        head = re.sub(r'<[^>]+>', '', parts[n]).strip()
        content = parts[n + 1].strip()
        if not re.sub(r'<[^>]+>|\s', '', content):
            continue
        ps = f'part-{len(pages) + 1}'
        info = {'title': head, 'chapter': '剧情流程'}
        note = '<p class="note">斜体的步骤是支线剧情，不是必须进行的流程。名称用简体中文官方译名。</p>' if not pages else ''
        (folder / f'{ps}.html').write_text(f'<!--{json.dumps(info, ensure_ascii=False)}-->\n{note}{content}\n', encoding='utf-8')
        pages.append(ps)
        meta[ps] = {'title': canon, 'revid': rev, 'timestamp': ts}
    (folder / 'source' / 'meta.json').write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding='utf-8')
    (folder / 'source' / 'images.json').write_text('{}', encoding='utf-8')
    g = {
        'slug': slug, 'game': game, 'en': canon, 'sourceTitle': canon, 'plat': plat, 'kind': 'repost',
        'source': '神奇宝贝百科', 'sourceBase': 'https://wiki.52poke.com/wiki/',
        'license': 'CC BY-NC-SA 3.0', 'licenseUrl': 'https://creativecommons.org/licenses/by-nc-sa/3.0/deed.zh-hans',
        'intro': '转载自神奇宝贝百科的剧情流程：每一步去哪、和谁对战、拿到什么。名称都是官方简体中文译名。这是简版，详细的图文攻略之后会逐个补上。',
        'pages': pages, 'total': f'简版流程，{len(pages)} 页',
    }
    (folder / 'guide.json').write_text(json.dumps(g, ensure_ascii=False, indent=1), encoding='utf-8')
    print(slug, rev, ts, [((folder / f'{p}.html').read_text().split('-->')[0][4:]) for p in pages])


for slug in sys.argv[1:] or GAMES:
    build(slug, *GAMES[slug])
    time.sleep(1)
