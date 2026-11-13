#!/usr/bin/env python3
"""Build translated guides: src/guides-tr/<slug>/ -> guides/<slug>/.

Each guide folder holds guide.json, one HTML fragment per page (first line is a
JSON comment with title/chapter), and source/ with the original wikitext,
meta.json (revision ids) and images.json (thumbnail URLs from the source wiki).
Images are hotlinked from the source wiki's CDN, not copied.
"""
import html, json, re
from pathlib import Path

SITE = Path(__file__).resolve().parent.parent
e = html.escape

hh = (SITE / 'handheld' / 'index.html').read_text(encoding='utf-8')
head = hh[:hh.index('<title>')]
head = head.replace("connect-src 'none';", "connect-src 'none'; img-src https://cdn.wikimg.net;", 1)
assert 'img-src' in head
theme = re.search(r'<style id="eli-theme">.*?</style>', hh, re.S).group(0)
bar = re.search(r'<header class="eli-bar">.*?</header>', hh, re.S).group(0)
bar = bar.replace(' aria-current="page"', '').replace('href="../', 'href="../../')
bar = bar.replace('<a href="../../guides/">', '<a href="../../guides/" aria-current="page">')

CSS = '''<style>
*{box-sizing:border-box}body{margin:0;font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','Microsoft YaHei',sans-serif;background:#1f2a24;color:#f1f0e6}
main{max-width:760px;margin:auto;padding:8px 16px max(32px,env(safe-area-inset-bottom))}
a{color:#c9e265}.crumb{font-size:13px;color:#a9b5a6;margin:14px 0 4px}.crumb a{color:#a9b5a6}
h1{font-size:25px;margin:6px 0 4px;line-height:1.4}.chap{font-size:13px;color:#a9b5a6;margin:0 0 16px}
h2{font-size:19px;margin:28px 0 10px;padding-top:4px;border-top:1px solid #36463c}
p,li{font-size:16px;line-height:1.85}ol,ul{padding-left:22px}b{color:#fff}
.note{font-size:14px;color:#a9b5a6;background:#2a372f;border-radius:10px;padding:10px 14px}
figure{margin:14px 0;text-align:center}figure img{max-width:100%;height:auto;border-radius:8px;background:#2a372f}
figcaption{font-size:13px;color:#a9b5a6;margin-top:6px}
.tip{background:#2a372f;border:1px solid #44574b;border-left:4px solid #c9e265;border-radius:10px;padding:4px 16px;margin:16px 0}
.tip h4{margin:12px 0 0;font-size:15px;color:#c9e265}.tip p,.tip li{font-size:15px}
table.data{width:100%;border-collapse:collapse;margin:14px 0;font-size:14px;background:#2a372f;border-radius:10px;overflow:hidden}
table.data caption{text-align:left;font-weight:700;padding:0 0 8px;font-size:15px}
table.data th,table.data td{padding:9px 12px;border-bottom:1px solid #36463c;text-align:left;vertical-align:top;line-height:1.6}
table.data th{width:30%;color:#a9b5a6;font-weight:600;white-space:nowrap}table.data th small{font-weight:400}
.medal{color:#c9e265;font-weight:700}
.pager{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin:32px 0 10px}
.pager a{display:block;background:#2a372f;border:1px solid #44574b;border-radius:12px;padding:12px 14px;text-decoration:none;color:#f1f0e6;font-size:15px;min-height:64px}
.pager a small{display:block;color:#a9b5a6;font-size:12px;margin-bottom:2px}.pager .next{text-align:right;grid-column:2}
.toc{list-style:none;padding:0;margin:0}.toc li{border-bottom:1px solid #36463c}.toc a{display:flex;justify-content:space-between;padding:13px 4px;text-decoration:none;color:#f1f0e6}
.toc a span{color:#a9b5a6;font-size:13px}.toc h3{font-size:14px;color:#a9b5a6;margin:20px 0 4px;font-weight:600}
.src{font-size:12px;color:#a9b5a6;line-height:1.8;border-top:1px solid #36463c;margin-top:28px;padding-top:12px}.src a{color:#a9b5a6}
@media(max-width:560px){h1{font-size:22px}p,li{font-size:15.5px}table.data th{white-space:normal;width:34%}}
</style>'''


def page_html(title, body):
    return f'{head}<title>{e(title)} · Eli</title>{CSS}{theme}</head><body>{bar}<main>{body}</main></body></html>\n'


def build(folder):
    g = json.loads((folder / 'guide.json').read_text(encoding='utf-8'))
    meta = json.loads((folder / 'source' / 'meta.json').read_text(encoding='utf-8'))
    imgs = json.loads((folder / 'source' / 'images.json').read_text(encoding='utf-8'))
    out = SITE / 'guides' / g['slug']
    out.mkdir(parents=True, exist_ok=True)
    pages = []
    for slug in g['pages']:
        raw = (folder / f'{slug}.html').read_text(encoding='utf-8')
        info = json.loads(re.match(r'<!--(.*?)-->', raw).group(1))
        pages.append((slug, info, raw.split('-->', 1)[1]))

    def fig(m):
        im = imgs[m.group(1)]
        return (f'<figure><img src="{e(im["thumb"])}" width="{im["w"]}" height="{im["h"]}" loading="lazy" alt="{e(m.group(2))}">'
                f'<figcaption>{m.group(2)}</figcaption></figure>')

    def credit(slug):
        m = meta[slug]
        url = g['sourceBase'] + m['title'].replace(' ', '_')
        return (f'<p class="src">原文：{g["source"]}《<a href="{e(url)}" target="_blank" rel="noopener noreferrer">{e(m["title"])}</a>》'
                f'（<a href="{e(url)}?oldid={m["revid"]}" target="_blank" rel="noopener noreferrer">修订版本 {m["revid"]}</a>，{m["timestamp"][:10]}），'
                f'作者见<a href="{e(url)}?action=history" target="_blank" rel="noopener noreferrer">原文页面历史</a>。'
                f'本页由 Eli 的杂货间翻译为中文，并有改动（重新排版、精简部分图注）。原文与译文均以 '
                f'<a href="{g["licenseUrl"]}" target="_blank" rel="noopener noreferrer">{g["license"]}</a> 授权。'
                f'配图来自原站，版权归原作者与游戏厂商。</p>')

    for i, (slug, info, body) in enumerate(pages):
        body = re.sub(r'<figure data-img="([^"]+)">(.*?)</figure>', fig, body, flags=re.S)
        prev = pages[i - 1] if i else None
        nxt = pages[i + 1] if i + 1 < len(pages) else None
        pager = '<nav class="pager">'
        if prev:
            pager += f'<a href="{prev[0]}.html"><small>← 上一页</small>{e(prev[1]["title"])}</a>'
        if nxt:
            pager += f'<a class="next" href="{nxt[0]}.html"><small>下一页 →</small>{e(nxt[1]["title"])}</a>'
        else:
            pager += f'<a class="next" href="./"><small>本章完</small>回到目录</a>'
        pager += '</nav>'
        crumb = f'<p class="crumb"><a href="../">攻略大全</a> / <a href="./">{e(g["game"])}</a></p>'
        (out / f'{slug}.html').write_text(page_html(f'{info["title"]} - {g["game"]}',
            f'{crumb}<h1>{e(info["title"])}</h1><p class="chap">{e(info["chapter"])}</p>{body}{pager}{credit(slug)}'), encoding='utf-8')

    toc, last = '', None
    for slug, info, _ in pages:
        if info['chapter'] != last:
            toc += ('</ul>' if last else '') + f'<h3>{e(info["chapter"])}</h3><ul class="toc">'
            last = info['chapter']
        toc += f'<li><a href="{slug}.html">{e(info["title"])}<span>→</span></a></li>'
    toc += '</ul>'
    first = g['sourceBase'] + g['en'].replace(' ', '_')
    (out / 'index.html').write_text(page_html(f'{g["game"]} 中文攻略',
        f'<p class="crumb"><a href="../">攻略大全</a></p><h1>{e(g["game"])} 中文攻略</h1>'
        f'<p class="chap">{e(g["plat"])} · {e(g["total"])}</p><p class="note">{e(g["intro"])}</p>{toc}'
        f'<p class="src">原文：{g["source"]}《<a href="{e(first)}" target="_blank" rel="noopener noreferrer">{e(g["en"])}</a>》，'
        f'以 <a href="{g["licenseUrl"]}" target="_blank" rel="noopener noreferrer">{g["license"]}</a> 授权；译文同样以 {g["license"]} 授权。'
        f'每页底部注明对应的原文修订版本。</p>'), encoding='utf-8')
    print('built', out, len(pages), 'pages')
    return g


TR = [build(f) for f in sorted((SITE / 'src' / 'guides-tr').iterdir()) if (f / 'guide.json').exists()]
(SITE / 'src' / 'guides-tr' / 'index.json').write_text(json.dumps(
    {g['game']: {'slug': g['slug'], 'total': g['total']} for g in TR}, ensure_ascii=False, indent=1), encoding='utf-8')
