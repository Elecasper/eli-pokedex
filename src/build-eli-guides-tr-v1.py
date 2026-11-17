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
head = head.replace("connect-src 'none';", "connect-src 'none'; img-src 'self' data: https://cdn.wikimg.net;", 1)
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
.mapbtn{display:block;text-align:center;padding:14px;border-radius:12px;background:#c9e265;color:#1f2a24;font-weight:700;text-decoration:none;font-size:16px;margin:4px 0 8px}
.pinbox{position:relative;display:block}.pin{position:absolute;z-index:2;font-size:12px;line-height:1;pointer-events:none}
.pin.dot{width:22px;height:22px;margin:-11px 0 0 -11px;border-radius:50%;background:#c9e265;color:#1f2a24;font-weight:700;display:grid;place-items:center;border:2px solid #1f2a24;box-shadow:0 0 0 2px #c9e265}
.pin.exit{background:rgba(31,42,36,.9);color:#c9e265;padding:5px 9px;border-radius:999px;border:1px solid #c9e265;white-space:nowrap;font-weight:600}
.pin.exit.w{transform:translate(6px,-50%)}.pin.exit.e{transform:translate(calc(-100% - 6px),-50%)}.pin.exit.n{transform:translate(-50%,6px)}.pin.exit.s{transform:translate(-50%,calc(-100% - 6px))}
.pinlist{list-style:none;margin:8px 0 0;padding:0;text-align:left;font-size:13px;color:#d6dccf}.pinlist li{padding:2px 0}.pinlist b{display:inline-grid;place-items:center;width:18px;height:18px;margin-right:8px;border-radius:50%;background:#c9e265;color:#1f2a24;font-size:11px}
.mapgrid{display:grid;gap:12px;margin:14px 0;grid-template-columns:1fr}.mapgrid.n2,.mapgrid.n3{grid-template-columns:repeat(auto-fit,minmax(240px,1fr))}.mapgrid figure.map{margin:0}.mapgrid.n1 figure.map{max-width:560px;margin:0 auto}figure.map a{display:block}figure.map img{width:100%;image-rendering:auto;border:1px solid #36463c}figure.map figcaption{font-size:13px;color:#a9b5a6;margin-top:6px}
.maplink{margin:-2px 0 12px;font-size:13px;color:#a9b5a6;line-height:1.9}.maplink span{display:inline-block;margin-right:8px;padding:0 7px;border-radius:5px;background:#2a372f;color:#c9e265;font-size:12px}.maplink a{color:#a9b5a6;text-decoration:underline;text-decoration-color:#44574b;text-underline-offset:3px}.maplink a:hover{color:#c9e265}.hmap{margin-left:8px;padding:1px 8px;border-radius:5px;background:#2a372f;color:#c9e265;font-size:12px;font-weight:400;text-decoration:none;vertical-align:middle}
.tip{background:#2a372f;border:1px solid #44574b;border-left:4px solid #c9e265;border-radius:10px;padding:4px 16px;margin:16px 0}
.tip h4{margin:12px 0 0;font-size:15px;color:#c9e265}.tip p,.tip li{font-size:15px}
table.data{width:100%;border-collapse:collapse;margin:14px 0;font-size:14px;background:#2a372f;border-radius:10px;overflow:hidden}
table.data caption{text-align:left;font-weight:700;padding:0 0 8px;font-size:15px}
table.data th,table.data td{padding:9px 12px;border-bottom:1px solid #36463c;text-align:left;vertical-align:top;line-height:1.6}
table.data th{width:30%;color:#a9b5a6;font-weight:600;white-space:nowrap}table.data th small{font-weight:400}
.medal{color:#c9e265;font-weight:700}
img.icon{width:24px;height:24px;vertical-align:-6px;margin-right:2px;image-rendering:pixelated}img.pm{width:40px;height:30px;vertical-align:-8px}
li.loc{list-style:none;margin:18px 0 6px -22px}li.loc>span{display:block;font-size:17px;font-weight:700;color:#c9e265;border-bottom:1px solid #36463c;padding-bottom:4px;margin-bottom:4px}
i{color:#a9b5a6}
div.box{background:#2a372f;border:1px solid #44574b;border-left:4px solid #c9e265;border-radius:10px;padding:4px 16px;margin:16px 0}div.box h4{margin:12px 0 4px;color:#c9e265;font-size:15px}div.box h2,div.box h3{font-size:15px;border:0;margin:12px 0 4px}details.box{background:#2a372f;border:1px solid #44574b;border-radius:10px;padding:2px 14px;margin:14px 0}details.box>summary{cursor:pointer;min-height:42px;display:flex;align-items:center;font-weight:700;color:#c9e265}table.grid caption{text-align:left;font-weight:700;padding:4px 0 8px;font-size:15px;color:#f1f0e6}tr.div th{background:#1f2a24;color:#c9e265}
table.grid{width:100%;border-collapse:collapse;margin:14px 0;font-size:14px;background:#2a372f;border-radius:10px;overflow:hidden}table.grid th,table.grid td{padding:8px 10px;border-bottom:1px solid #36463c;text-align:left;vertical-align:middle;line-height:1.6}table.grid th{color:#a9b5a6;font-weight:600}
.pager{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin:32px 0 10px}
.pager a{display:block;background:#2a372f;border:1px solid #44574b;border-radius:12px;padding:12px 14px;text-decoration:none;color:#f1f0e6;font-size:15px;min-height:64px}
.pager a small{display:block;color:#a9b5a6;font-size:12px;margin-bottom:2px}.pager .next{text-align:right;grid-column:2}
.toc{list-style:none;padding:0;margin:0}.toc li{border-bottom:1px solid #36463c}.toc a{display:flex;justify-content:space-between;padding:13px 4px;text-decoration:none;color:#f1f0e6}
.toc a span{color:#a9b5a6;font-size:13px}.toc h3{font-size:14px;color:#a9b5a6;margin:20px 0 4px;font-weight:600}
.src{font-size:12px;color:#a9b5a6;line-height:1.8;border-top:1px solid #36463c;margin-top:28px;padding-top:12px}.src a{color:#a9b5a6}
.node.l2{margin:30px 0 0}.node.l2>h2{margin-top:0}
.node.l3{border-left:2px solid #36463c;margin:16px 0 0 5px;padding-left:16px}.node.l3>h3{position:relative}.node.l3>h3::before{content:'';position:absolute;left:-23px;top:.62em;width:10px;height:10px;border-radius:50%;background:#1f2a24;border:2px solid #c9e265}
.nextstop{margin:22px 0 0;padding:9px 14px;border:1px dashed #44574b;border-radius:10px;font-size:14px;color:#a9b5a6;text-align:center}.nextstop a{color:#c9e265;text-decoration:none;font-weight:600}
nav.tree{font-size:13.5px;background:#2a372f;border:1px solid #44574b;border-radius:12px;padding:8px 14px;margin:0 0 18px}nav.tree summary{cursor:pointer;font-weight:700;color:#c9e265;padding:4px 0}
nav.tree ol{list-style:none;margin:0;padding:0}nav.tree ol ol{margin:2px 0 6px 10px;padding-left:10px;border-left:1px solid #44574b}
nav.tree li{line-height:1.5}nav.tree a{display:block;padding:3px 6px;border-radius:6px;color:#d6dccf;text-decoration:none}nav.tree a:hover{background:#34443a}nav.tree a.on{background:#3b4d3f;color:#c9e265;font-weight:600}
nav.tree ol.t2>li+li::before{content:'\\2193';display:block;color:#6e8575;font-size:12px;line-height:1;padding:1px 0 1px 8px}
nav.tree a i{font-style:normal;color:#8fa592;font-size:11.5px;margin-left:4px}nav.tree ol ol a{color:#aebaa9}
@media(min-width:1280px){nav.tree{position:fixed;top:70px;left:calc(50% + 396px);width:236px;max-height:calc(100vh - 92px);overflow:auto;margin:0}nav.tree summary{pointer-events:none}}
.pt{border-bottom:1px solid #36463c}.pt>summary{cursor:pointer;display:flex;justify-content:space-between;gap:10px;padding:13px 4px;list-style:none}.pt>summary::-webkit-details-marker{display:none}.pt>summary b{color:#f1f0e6}.pt>summary span{color:#a9b5a6;font-size:13px;white-space:nowrap}
.pt>ol{list-style:none;margin:0 0 12px;padding:0 0 0 14px;border-left:2px solid #36463c}.pt>ol a{display:block;padding:5px 8px;text-decoration:none;color:#d6dccf;font-size:15px}.pt>ol li+li::before{content:'\\2193';display:block;color:#6e8575;font-size:12px;padding-left:8px;line-height:1}
.pt>ol a i{font-style:normal;color:#8fa592;font-size:12px;margin-left:6px}
#tq{width:100%;box-sizing:border-box;margin:6px 0 10px;padding:10px 14px;border-radius:10px;border:1px solid #44574b;background:#2a372f;color:#f1f0e6;font-size:15px}
@media(min-width:900px){main{max-width:900px}h1{font-size:28px}.mapgrid.n1 figure.map{max-width:640px}}
@media(min-width:1400px){main{max-width:1000px}p,li{font-size:17px}}
@media(max-width:560px){h1{font-size:22px}p,li{font-size:15.5px}table.data th{white-space:normal;width:34%}}
</style>'''


def page_html(title, body):
    return f'{head}<title>{e(title)} · Eli</title>{CSS}{theme}</head><body>{bar}<main>{body}</main></body></html>\n'


TAG = re.compile(r'<div[^>]*>|</div>|<h([23])>(.*?)</h\1>', re.S)


def plain(t):
    return re.sub(r'<[^>]+>', '', re.sub(r'<a class="hmap".*?</a>', '', t)).strip()


def treeify(body, nxt):
    """Split body at h2/h3 into nested <section class=node>; return (html, outline_items)."""
    marks, depth = [], 0
    for m in TAG.finditer(body):
        t = m.group(0)
        if t.startswith('<div'):
            depth += 1
        elif t == '</div>':
            depth -= 1
        elif depth == 0:
            marks.append((m.start(), m.end(), int(m.group(1)), m.group(2)))
    if not any(l == 2 for _, _, l, _ in marks):
        return body, []
    out, items, pos = [body[:marks[0][0]]], [], 0
    ids = 0
    segs = []
    for i, (st, en, lvl, h) in enumerate(marks):
        end = marks[i + 1][0] if i + 1 < len(marks) else len(body)
        ids += 1
        segs.append({'id': f'n{ids}', 'lvl': lvl, 'h': h, 'c': body[en:end]})
    h2s = [x for x in segs if x['lvl'] == 2]
    html_, open2, open3 = '', False, False
    for x in segs:
        maps = len(re.findall(r'<figure class="map">', x['c']))
        if x['lvl'] == 2:
            if open3:
                html_ += '</section>'; open3 = False
            if open2:
                html_ += nextstop(h2s, cur, nxt) + '</section>'
            cur = x
            items.append({'id': x['id'], 'h': plain(x['h']), 'maps': maps, 'kids': []})
            html_ += f'<section class="node l2" id="{x["id"]}"><h2>{x["h"]}</h2>{x["c"]}'
            open2 = True
        else:
            if open3:
                html_ += '</section>'
            if items:
                items[-1]['kids'].append({'id': x['id'], 'h': plain(x['h']), 'maps': maps})
            html_ += f'<section class="node l3" id="{x["id"]}"><h3>{x["h"]}</h3>{x["c"]}'
            open3 = True
    if open3:
        html_ += '</section>'
    if open2:
        html_ += nextstop(h2s, cur, nxt) + '</section>'
    return out[0] + html_, items


def nextstop(h2s, cur, nxt):
    i = h2s.index(cur)
    if i + 1 < len(h2s):
        n = h2s[i + 1]
        return f'<p class="nextstop">\u2193 下一站：<a href="#{n["id"]}">{plain(n["h"])}</a></p>'
    if nxt:
        return f'<p class="nextstop">\u2193 下一页：<a href="{nxt[0]}.html">{e(nxt[1]["title"])}</a></p>'
    return ''


def outline(items):
    def li(x, sub=''):
        mp = f'<i>\U0001F5FA{x["maps"]}</i>' if x['maps'] else ''
        return f'<li><a href="#{x["id"]}">{e(x["h"])}{mp}</a>{sub}</li>'
    lis = ''.join(li(x, ('<ol>' + ''.join(li(k) for k in x['kids']) + '</ol>') if x['kids'] else '') for x in items)
    return ('<nav class="tree"><details open><summary>本节地点树</summary><ol class="t2">' + lis + '</ol></details></nav>'
            "<script>(function(){var d=document.querySelector('nav.tree>details');if(!d)return;"
            "if(innerWidth<1280)d.open=false;var L=[].slice.call(d.querySelectorAll('a[href^=\"#\"]')),H=L.map(function(a){return document.getElementById(a.getAttribute('href').slice(1))});"
            "function f(){var k=0;for(var i=0;i<H.length;i++){if(H[i]&&H[i].getBoundingClientRect().top<110)k=i}L.forEach(function(a,i){a.classList.toggle('on',i==k)})}"
            "addEventListener('scroll',f,{passive:true});f()})()</script>")


def write_map(folder, g, out, pages):
    wm = json.loads((folder / 'worldmap.json').read_text(encoding='utf-8'))
    by = {n['k']: n for n in wm['nodes']}
    titles = {slug: info['title'] for slug, info, _ in pages}
    sea = {tuple(x) for x in wm['sea']}
    svg = ''
    for a, b in wm['edges']:
        A, B = by[a], by[b]
        svg += f'<line x1="{A["x"]}" y1="{A["y"]}" x2="{B["x"]}" y2="{B["y"]}" class="ed{" sea" if (a, b) in sea else ""}"/>'
    # long sea links drawn as curves dipping to the bottom
    for a, b in (('浅葱市', '海王丸号'), ('海王丸号', '枯叶市')):
        A, B = by[a], by[b]
        svg += f'<path d="M{A["x"]} {A["y"]} Q{(A["x"] + B["x"]) // 2} {max(A["y"], B["y"]) + 120} {B["x"]} {B["y"]}" class="ed sea" fill="none"/>'
    for n in wm['nodes']:
        h, w = 30, n['w']
        post = n['p'] > 16
        cls = f'nd {n["t"]}{" post" if post else ""}'
        href = f'part-{n["p"]}.html#{n["id"]}'
        svg += (f'<a href="{href}"><g class="{cls}"><title>{e(n["k"])} · 第 {n["p"]} 节：{e(titles["part-" + str(n["p"])])}</title>'
                f'<rect x="{n["x"] - w // 2}" y="{n["y"] - h // 2}" width="{w}" height="{h}" rx="{15 if n["t"] != "r" else 8}"/>'
                f'<text x="{n["x"]}" y="{n["y"] + 5}" text-anchor="middle">{e(n["k"])}</text></g></a>')
    css = """<style>main{max-width:none;padding:8px 12px 40px}.mapwrap{overflow:auto;border:1px solid #44574b;border-radius:12px;background:#18221d;max-height:78vh;max-height:78dvh;cursor:grab;-webkit-overflow-scrolling:touch}.mapwrap.dr{cursor:grabbing;user-select:none}
.mapwrap svg{display:block;min-width:1100px;width:1900px}.ed{stroke:#5d7566;stroke-width:3}.ed.sea{stroke:#4a8fb0;stroke-dasharray:8 6}
.nd rect{fill:#2f4336;stroke:#c9e265;stroke-width:2}.nd text{fill:#f1f0e6;font-size:15px;font-weight:700;font-family:-apple-system,'PingFang SC','Microsoft YaHei',sans-serif}
.nd.r rect{fill:#26332b;stroke:#6e8575;stroke-width:1.5}.nd.r text{font-size:13px;font-weight:500;fill:#cdd6c8}.nd.d rect{fill:#3a2f45;stroke:#b79ae0}.nd.post rect{stroke:#6cc3f0}.nd.d.post rect{stroke:#6cc3f0}
.nd:hover rect{fill:#c9e265}.nd:hover text{fill:#1f2a24}.leg{display:flex;flex-wrap:wrap;gap:6px 16px;font-size:13px;color:#a9b5a6;margin:6px 0 12px}.leg i{display:inline-block;width:14px;height:14px;border-radius:5px;vertical-align:-2px;margin-right:5px;border:2px solid}
.zb{display:flex;gap:8px;margin:0 0 10px}.zb button{background:#2a372f;border:1px solid #44574b;color:#f1f0e6;border-radius:8px;padding:6px 14px;font-size:15px}</style>"""
    legend = ('<div class="leg"><span><i style="border-color:#c9e265;background:#2f4336"></i>城镇（主线 1–16 节）</span>'
              '<span><i style="border-color:#6cc3f0;background:#2f4336"></i>城镇（通关后 17–32 节）</span>'
              '<span><i style="border-color:#b79ae0;background:#3a2f45"></i>洞窟 / 塔 / 特殊地点</span>'
              '<span><i style="border-color:#6e8575;background:#26332b"></i>道路</span>'
              '<span><i style="border:0;border-top:3px dashed #4a8fb0;height:0;width:18px;vertical-align:4px"></i>海路</span></div>')
    js = ("<script>(function(){var s=document.querySelector('.mapwrap svg'),m=document.querySelector('.mapwrap'),w=0;"
          "function set(v){var c=(m.scrollLeft+m.clientWidth/2)/w;w=Math.max(700,Math.min(3200,v));s.style.width=w+'px';if(c)m.scrollLeft=c*w-m.clientWidth/2}"
          "function z(f){set(w*f)}"
          "document.getElementById('zi').onclick=function(){z(1.25)};document.getElementById('zo').onclick=function(){z(.8)};"
          "w=Math.max(1000,Math.min(1900,m.clientWidth-2));s.style.width=w+'px';m.scrollLeft=Math.max(0,.49*w-m.clientWidth/2);"
          "var d=null;m.addEventListener('pointerdown',function(e){if(e.pointerType==='mouse'&&!e.target.closest('a'))d={x:e.clientX,y:e.clientY,l:m.scrollLeft,t:m.scrollTop,mv:0}});"
          "addEventListener('pointermove',function(e){if(!d)return;var dx=e.clientX-d.x,dy=e.clientY-d.y;if(Math.abs(dx)+Math.abs(dy)>3)m.classList.add('dr');m.scrollLeft=d.l-dx;m.scrollTop=d.t-dy});"
          "addEventListener('pointerup',function(){d=null;m.classList.remove('dr')})})()</script>")
    body = (f'<p class="crumb"><a href="../">攻略大全</a> / <a href="./">{e(g["game"])}</a></p><h1>地图总览</h1>'
            '<p class="chap">按城都和关都的地理位置排列，点任意地点跳到对应的攻略段落。左边是城都，右边是关都，两地由 27 号道路相连。</p>'
            f'{legend}<div class="zb"><button id="zi">放大 +</button><button id="zo">缩小 −</button></div>'
            f'<div class="mapwrap"><svg viewBox="0 0 1900 960" xmlns="http://www.w3.org/2000/svg">{svg}</svg></div>{js}')
    (out / 'map.html').write_text(page_html(f'地图总览 - {g["game"]}', css + body), encoding='utf-8')


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
                + (f'本页由 Eli 的杂货间转载，并有改动（重新排版、去掉站内链接）。原文与本页均以 ' if g.get('kind') == 'repost' else
                   f'本页由 Eli 的杂货间翻译为中文，并有改动（重新排版、精简部分图注）。原文与译文均以 ')
                + f'<a href="{g["licenseUrl"]}" target="_blank" rel="noopener noreferrer">{g["license"]}</a> 授权。'
                f'配图来自原站，版权归原作者与游戏厂商；地图截图来自 <a href="https://archives.bulbagarden.net/wiki/Category:HeartGold_and_SoulSilver_maps" target="_blank" rel="noopener noreferrer">Bulbagarden Archives</a>，游戏画面版权归 Nintendo / Game Freak / The Pokémon Company。</p>')

    tocs = {}
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
        crumb = f'<p class="crumb"><a href="../">攻略大全</a> / <a href="./">{e(g["game"])}</a>' + (' / <a href="map.html">地图总览</a>' if (folder / 'worldmap.json').exists() else '') + '</p>'
        tree = ''
        if g.get('tree'):
            body, items = treeify(body, nxt)
            tocs[slug] = items
        (out / f'{slug}.html').write_text(page_html(f'{info["title"]} - {g["game"]}',
            f'{crumb}<h1>{e(info["title"])}</h1><p class="chap">{e(info["chapter"])}</p>{tree}{body}{pager}{credit(slug)}'), encoding='utf-8')

    toc, last = '', None
    for slug, info, _ in pages:
        if info['chapter'] != last:
            toc += ('</ul>' if last else '') + f'<h3>{e(info["chapter"])}</h3><ul class="toc">'
            last = info['chapter']
        if True:
            toc += f'<li><a href="{slug}.html">{e(info["title"])}<span>→</span></a></li>'
    toc += '</ul>'
    if (folder / 'worldmap.json').exists():
        toc = ('<p><a class="mapbtn" href="map.html">\U0001F5FA 打开地图总览（点地点跳到攻略）</a></p>' + toc)
        write_map(folder, g, out, pages)
    srct = g.get('sourceTitle', g['en'])
    first = g['sourceBase'] + srct.replace(' ', '_')
    (out / 'index.html').write_text(page_html(f'{g["game"]} 中文攻略',
        f'<p class="crumb"><a href="../">攻略大全</a></p><h1>{e(g["game"])} 中文攻略</h1>'
        f'<p class="chap">{e(g["plat"])} · {e(g["total"])}</p><p class="note">{e(g["intro"])}</p>{toc}'
        f'<p class="src">原文：{g["source"]}《<a href="{e(first)}" target="_blank" rel="noopener noreferrer">{e(srct)}</a>》，'
        f'以 <a href="{g["licenseUrl"]}" target="_blank" rel="noopener noreferrer">{g["license"]}</a> 授权；本站的{"转载" if g.get("kind") == "repost" else "译文"}同样以 {g["license"]} 授权。'
        f'每页底部注明对应的原文修订版本。</p>'), encoding='utf-8')
    print('built', out, len(pages), 'pages')
    return g


TR = [build(f) for f in sorted((SITE / 'src' / 'guides-tr').iterdir()) if (f / 'guide.json').exists()]
(SITE / 'src' / 'guides-tr' / 'index.json').write_text(json.dumps(
    {g['game']: {'slug': g['slug'], 'total': g['total']} for g in TR}, ensure_ascii=False, indent=1), encoding='utf-8')
