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
*{box-sizing:border-box}body{margin:0;font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','Microsoft YaHei',sans-serif;background:#f4efe4;color:#2a2623}
main{max-width:760px;margin:auto;padding:8px 16px max(32px,env(safe-area-inset-bottom))}
a{color:#c62828}.crumb{font-size:13px;color:#6f675c;margin:14px 0 4px}.crumb a{color:#6f675c}
h1{font-size:25px;margin:6px 0 4px;line-height:1.4}.chap{font-size:13px;color:#6f675c;margin:0 0 16px}
h2{font-size:19px;margin:28px 0 10px;padding-top:4px;border-top:1px solid #ddd3be}
p,li{font-size:16px;line-height:1.85}ol,ul{padding-left:22px}b{color:#2a2623}
.note{font-size:14px;color:#6f675c;background:#ffffff;border-radius:10px;padding:10px 14px}
figure{margin:14px 0;text-align:center}figure img{max-width:100%;height:auto;border-radius:8px;background:#ffffff}
figcaption{font-size:13px;color:#6f675c;margin-top:6px}
.mapbtn{display:block;text-align:center;padding:14px;border-radius:12px;background:#d32f2f;color:#ffffff;font-weight:700;text-decoration:none;font-size:16px;margin:4px 0 8px}
.pinbox{position:relative;display:block}.pin{position:absolute;z-index:2;font-size:12px;line-height:1;pointer-events:none}
.pin.dot{width:22px;height:22px;margin:-11px 0 0 -11px;border-radius:50%;background:#d32f2f;color:#ffffff;font-weight:700;display:grid;place-items:center;border:2px solid #ddd3be;box-shadow:0 0 0 2px #d32f2f}
.pin.exit{background:rgba(242,242,242,.9);color:#c62828;padding:5px 9px;border-radius:999px;border:1px solid #d32f2f;white-space:nowrap;font-weight:600}
.pin.exit.w{transform:translate(6px,-50%)}.pin.exit.e{transform:translate(calc(-100% - 6px),-50%)}.pin.exit.n{transform:translate(-50%,6px)}.pin.exit.s{transform:translate(-50%,calc(-100% - 6px))}
.pinlist{list-style:none;margin:8px 0 0;padding:0;text-align:left;font-size:13px;color:#6f675c}.pinlist li{padding:2px 0}.pinlist b{display:inline-grid;place-items:center;width:18px;height:18px;margin-right:8px;border-radius:50%;background:#d32f2f;color:#ffffff;font-size:11px}
.mapgrid{display:grid;gap:12px;margin:14px 0;grid-template-columns:1fr}.mapgrid.n2,.mapgrid.n3{grid-template-columns:repeat(auto-fit,minmax(240px,1fr))}.mapgrid figure.map{margin:0}.mapgrid.n1 figure.map{max-width:560px;margin:0 auto}figure.map a{display:block}figure.map img{width:100%;image-rendering:auto;border:1px solid #ddd3be}figure.map figcaption{font-size:13px;color:#6f675c;margin-top:6px}
.maplink{margin:-2px 0 12px;font-size:13px;color:#6f675c;line-height:1.9}.maplink span{display:inline-block;margin-right:8px;padding:0 7px;border-radius:5px;background:#ffffff;color:#c62828;font-size:12px}.maplink a{color:#6f675c;text-decoration:underline;text-decoration-color:#2a2623;text-underline-offset:3px}.maplink a:hover{color:#c62828}.hmap{margin-left:8px;padding:1px 8px;border-radius:5px;background:#ffffff;color:#c62828;font-size:12px;font-weight:400;text-decoration:none;vertical-align:middle}
.tip{background:#ffffff;border:1px solid #ddd3be;border-left:4px solid #d32f2f;border-radius:10px;padding:4px 16px;margin:16px 0}
.tip h4{margin:12px 0 0;font-size:15px;color:#c62828}.tip p,.tip li{font-size:15px}
table.data{width:100%;border-collapse:collapse;margin:14px 0;font-size:14px;background:#ffffff;border-radius:10px;overflow:hidden}
table.data caption{text-align:left;font-weight:700;padding:0 0 8px;font-size:15px}
table.data th,table.data td{padding:9px 12px;border-bottom:1px solid #ddd3be;text-align:left;vertical-align:top;line-height:1.6}
table.data th{width:30%;color:#6f675c;font-weight:600;white-space:nowrap}table.data th small{font-weight:400}
.medal{color:#c62828;font-weight:700}
img.icon{width:24px;height:24px;vertical-align:-6px;margin-right:2px;image-rendering:pixelated}img.pm{width:40px;height:30px;vertical-align:-8px}
li.loc{list-style:none;margin:18px 0 6px -22px}li.loc>span{display:block;font-size:17px;font-weight:700;color:#c62828;border-bottom:1px solid #ddd3be;padding-bottom:4px;margin-bottom:4px}
i{color:#6f675c}
div.box{background:#ffffff;border:1px solid #ddd3be;border-left:4px solid #d32f2f;border-radius:10px;padding:4px 16px;margin:16px 0}div.box h4{margin:12px 0 4px;color:#c62828;font-size:15px}div.box h2,div.box h3{font-size:15px;border:0;margin:12px 0 4px}details.box{background:#ffffff;border:1px solid #ddd3be;border-radius:10px;padding:2px 14px;margin:14px 0}details.box>summary{cursor:pointer;min-height:42px;display:flex;align-items:center;font-weight:700;color:#c62828}table.grid caption{text-align:left;font-weight:700;padding:4px 0 8px;font-size:15px;color:#2a2623}tr.div th{background:#f4efe4;color:#c62828}
table.grid{width:100%;border-collapse:collapse;margin:14px 0;font-size:14px;background:#ffffff;border-radius:10px;overflow:hidden}table.grid th,table.grid td{padding:8px 10px;border-bottom:1px solid #ddd3be;text-align:left;vertical-align:middle;line-height:1.6}table.grid th{color:#6f675c;font-weight:600}
.pager{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin:32px 0 10px}
.pager a{display:block;background:#ffffff;border:1px solid #ddd3be;border-radius:12px;padding:12px 14px;text-decoration:none;color:#2a2623;font-size:15px;min-height:64px}
.pager a small{display:block;color:#6f675c;font-size:12px;margin-bottom:2px}.pager .next{text-align:right;grid-column:2}
.toc{list-style:none;padding:0;margin:0}.toc li{border-bottom:1px solid #ddd3be}.toc a{display:flex;justify-content:space-between;padding:13px 4px;text-decoration:none;color:#2a2623}
.toc a span{color:#6f675c;font-size:13px}.toc h3{font-size:14px;color:#6f675c;margin:20px 0 4px;font-weight:600}
.src{font-size:12px;color:#6f675c;line-height:1.8;border-top:1px solid #ddd3be;margin-top:28px;padding-top:12px}.src a{color:#6f675c}
.node.l2{margin:30px 0 0}.node.l2>h2{margin-top:0}
.node.l3{border-left:2px solid #ddd3be;margin:16px 0 0 5px;padding-left:16px}.node.l3>h3{position:relative}.node.l3>h3::before{content:'';position:absolute;left:-23px;top:.62em;width:10px;height:10px;border-radius:50%;background:#f4efe4;border:2px solid #d32f2f}
.nextstop{margin:22px 0 0;padding:9px 14px;border:1px dashed #ddd3be;border-radius:10px;font-size:14px;color:#6f675c;text-align:center}.nextstop a{color:#c62828;text-decoration:none;font-weight:600}
nav.tree{font-size:13.5px;background:#ffffff;border:1px solid #ddd3be;border-radius:12px;padding:8px 14px;margin:0 0 18px}nav.tree summary{cursor:pointer;font-weight:700;color:#c62828;padding:4px 0}
nav.tree ol{list-style:none;margin:0;padding:0}nav.tree ol ol{margin:2px 0 6px 10px;padding-left:10px;border-left:1px solid #ddd3be}
nav.tree li{line-height:1.5}nav.tree a{display:block;padding:3px 6px;border-radius:6px;color:#6f675c;text-decoration:none}nav.tree a:hover{background:#e9e1cf}nav.tree a.on{background:#e9e1cf;color:#c62828;font-weight:600}
nav.tree ol.t2>li+li::before{content:'\\2193';display:block;color:#2a2623;font-size:12px;line-height:1;padding:1px 0 1px 8px}
nav.tree a i{font-style:normal;color:#6f675c;font-size:11.5px;margin-left:4px}nav.tree ol ol a{color:#6f675c}
@media(min-width:1280px){nav.tree{position:fixed;top:70px;left:calc(50% + 396px);width:236px;max-height:calc(100vh - 92px);overflow:auto;margin:0}nav.tree summary{pointer-events:none}}
.pt{border-bottom:1px solid #ddd3be}.pt>summary{cursor:pointer;display:flex;justify-content:space-between;gap:10px;padding:13px 4px;list-style:none}.pt>summary::-webkit-details-marker{display:none}.pt>summary b{color:#2a2623}.pt>summary span{color:#6f675c;font-size:13px;white-space:nowrap}
.pt>ol{list-style:none;margin:0 0 12px;padding:0 0 0 14px;border-left:2px solid #ddd3be}.pt>ol a{display:block;padding:5px 8px;text-decoration:none;color:#6f675c;font-size:15px}.pt>ol li+li::before{content:'\\2193';display:block;color:#2a2623;font-size:12px;padding-left:8px;line-height:1}
.pt>ol a i{font-style:normal;color:#6f675c;font-size:12px;margin-left:6px}
#tq{width:100%;box-sizing:border-box;margin:6px 0 10px;padding:10px 14px;border-radius:10px;border:1px solid #ddd3be;background:#ffffff;color:#2a2623;font-size:15px}
@media(min-width:900px){main{max-width:900px}.mapbtn{display:inline-block!important;padding:12px 28px!important;margin-right:10px!important}h1{font-size:28px}.mapgrid.n1 figure.map{max-width:640px}}
@media(min-width:1400px){main{max-width:1000px}p,li{font-size:17px}}
figure.map .nbr{display:flex;flex-wrap:wrap;gap:6px;align-items:center;margin:8px 0 2px}.nbr b{font-size:12.5px;color:#6f675c;font-weight:600;margin-right:2px}.nbr a{display:inline-block;padding:8px 14px;border-radius:999px;border:1px solid #ddd3be;background:#ffffff;color:#2a2623;text-decoration:none;font-size:14.5px}
a.pin.exit{text-decoration:none;color:inherit;cursor:pointer}.spb{font-size:13px;color:#6f675c;margin:6px 0 10px;padding:8px 12px;border:1px dashed #ddd3be;border-radius:10px}.spb button{background:#ffffff;border:1px solid #ddd3be;color:#c62828;border-radius:999px;padding:5px 12px;font-size:13px;cursor:pointer;margin-left:4px}.toc li.lk a{opacity:.6}.toc a i{font-style:normal}
.cl{margin:16px 0}.cl h4{margin:0 0 6px;font-size:15px;color:#c62828}ul.il{list-style:none;margin:0;padding:0;background:#ffffff;border-radius:10px;overflow:hidden}
.il li{padding:7px 12px;border-bottom:1px solid #ddd3be;font-size:15px;line-height:1.45}.il li:last-child{border-bottom:0}.il li.dv{background:#e9e1cf;font-size:12.5px;color:#6f675c;padding:5px 12px;font-weight:700}
.il .n{display:flex;align-items:center;gap:8px;font-weight:600}.il img{width:26px;height:26px;object-fit:contain;flex:none}.il img.pm{width:36px;height:27px}
.il .d{display:block;font-size:13px;color:#6f675c;line-height:1.5;margin-top:1px;padding-left:34px}.il img{align-self:center}
.il em,.mi em{font-style:normal;font-size:11.5px;background:#e9e1cf;color:#c62828;border-radius:6px;padding:1px 7px;font-weight:600;white-space:nowrap}
.il.pl li.pr{display:flex;align-items:center;justify-content:space-between;gap:10px}.il.pl .n{flex:1;min-width:0}.il.pl .tg{font-size:12.5px;color:#6f675c;text-align:right}
.tl .tn{display:flex;justify-content:space-between;gap:10px;font-weight:600}.tl .pz{color:#c62828;font-size:13px;white-space:nowrap;font-weight:500}.tl .mm{display:flex;flex-wrap:wrap;gap:4px 12px;margin-top:3px;font-size:13.5px;color:#6f675c}.tl .mc{display:inline-flex;align-items:center;gap:4px}.tl .mc img{width:30px;height:23px}
.party .mon{background:#ffffff;border-radius:10px;margin:0 0 8px;padding:9px 12px}.party .mh{display:flex;align-items:center;gap:8px;flex-wrap:wrap}.party .mh .n{font-weight:700}.party .mh small{color:#6f675c;font-size:12.5px}.party .mi{margin-top:4px;font-size:13.5px;color:#6f675c;line-height:1.6}
.tw{overflow-x:auto;margin:14px 0}.tw table.grid{margin:0;min-width:480px}
.toc a{display:flex;align-items:center;gap:12px}.toc .no{font-style:normal;flex:none;width:30px;height:30px;border-radius:50%;background:#e9e1cf;color:#c62828;font-size:13px;font-weight:700;display:flex;align-items:center;justify-content:center}.toc .tt{flex:1;min-width:0}.toc .tt i{font-style:normal;font-weight:600;display:block;color:#2a2623;font-size:16px}.toc .tt small{display:block;color:#6f675c;font-size:12.5px;line-height:1.4;margin-top:2px;font-weight:400}
.mapbtn.alt{background:#ffffff;color:#c62828;border:1px solid #ddd3be}
.av{image-rendering:pixelated;height:72px;width:auto;flex:none}.av.sm{height:34px;vertical-align:middle;margin:-6px 3px -6px 0}.av.md{height:56px}.av.lg{height:84px}
.npc{display:inline-block;white-space:nowrap;background:#e9e1cf;border:1px solid #ddd3be;border-radius:999px;padding:1px 10px 1px 6px;color:#2a2623;font-weight:600}
.cast{display:flex;flex-wrap:wrap;gap:10px 14px;align-items:flex-end;margin:6px 0 16px;padding:10px 12px;background:#ffffff;border:1px solid #ddd3be;border-radius:12px}.cast>b{width:100%;font-size:12.5px;color:#6f675c;font-weight:600}.ct{display:flex;flex-direction:column;align-items:center;gap:3px;min-width:54px}.ct i{font-style:normal;font-size:12.5px;color:#6f675c}
.gymbox{display:flex;align-items:flex-end;gap:14px;background:#ffffff;border:1px solid #ddd3be;border-radius:12px;padding:10px 14px;margin:14px 0}.gymbox b{color:#2a2623}
.cl.party>h4{display:flex;align-items:flex-end;gap:10px}
.il img,.tl .mc img,.party .mh img.pm{background:#c9d9b8;border:1px solid #8fa77c;border-radius:6px;padding:2px;box-sizing:content-box}
a,button,summary{touch-action:manipulation;-webkit-tap-highlight-color:rgba(201,226,101,.18)}
.dock{display:none}.backmap{position:fixed;left:12px;bottom:18px;z-index:41;padding:11px 18px;border-radius:999px;background:#d32f2f;color:#ffffff;font-weight:700;font-size:15px;text-decoration:none;box-shadow:0 3px 12px rgba(0,0,0,.4)}@media(max-width:720px){.backmap{bottom:calc(76px + env(safe-area-inset-bottom))}}
@media(max-width:720px){main{padding-bottom:calc(84px + env(safe-area-inset-bottom))}.crumb a{display:inline-block;padding:8px 2px}.pager a{min-height:72px;padding:14px}
.dock{display:grid;grid-template-columns:1fr auto auto 1fr;gap:8px;position:fixed;left:0;right:0;bottom:0;z-index:40;padding:8px 12px max(8px,env(safe-area-inset-bottom));background:rgba(242,242,242,.96);backdrop-filter:blur(8px);border-top:1px solid #ddd3be}
.dock a{display:flex;align-items:center;justify-content:center;min-height:46px;padding:0 14px;border-radius:12px;background:#ffffff;border:1px solid #ddd3be;color:#2a2623;text-decoration:none;font-size:15px;font-weight:600;white-space:nowrap}.dock a.dis{opacity:.35;pointer-events:none}.dock a.hl{color:#c62828}}
@media(max-width:560px){h1{font-size:22px}p,li{font-size:15.5px}table.data th{white-space:normal;width:34%}}
.tp{cursor:pointer;border-bottom:2px dotted #d32f2f;padding-bottom:1px;-webkit-tap-highlight-color:transparent}
.t2{border-bottom:1px dotted #8a7f6a}.tp:hover,.tp:focus-visible{background:#f3e6c9;outline:none}
#tip{position:fixed;z-index:60;background:#fff;color:#2a2623;border:1px solid #ddd3be;border-top:4px solid #d32f2f;border-radius:10px;box-shadow:0 8px 28px rgba(0,0,0,.22);padding:12px 14px 14px;width:min(340px,calc(100vw - 24px));font-size:15px;line-height:1.6;display:none;text-align:left;font-weight:400}
#tip.on{display:block}
#tip:before{content:'';position:absolute;top:-11px;left:var(--ax,24px);width:14px;height:14px;background:#d32f2f;transform:translateX(-50%) rotate(45deg);border-radius:2px;z-index:-1}
#tip .th{display:flex;align-items:center;gap:10px;margin:0 0 6px;padding-right:26px}
#tip .th img,#tip .th svg{width:40px;height:40px;flex:none;image-rendering:pixelated;background:#c9d9b8;border:1px solid #8fa77c;border-radius:8px;padding:3px;box-sizing:border-box}
#tip .th svg{image-rendering:auto}
#tip h4{margin:0;font-size:16px;line-height:1.3}
#tip .tk{display:inline-block;background:#d32f2f;color:#fff;border-radius:999px;font-size:12px;padding:0 9px;margin-bottom:2px;font-weight:600}
#tip .ta{color:#6f675c;font-size:13px;margin:2px 0 6px}
#tip .tx{position:absolute;right:6px;top:4px;border:0;background:none;font-size:22px;line-height:1;color:#6f675c;padding:4px 8px;cursor:pointer}
.mw{position:relative;line-height:0}
.ip,.ip:active,.ip:hover{transform:none!important}.ip{position:absolute;margin:-15px 0 0 -15px;min-height:0;min-width:0;width:30px;height:30px;border-radius:50%;background:#fff;border:2px solid #d32f2f;padding:0;box-shadow:0 2px 6px rgba(0,0,0,.35);cursor:pointer;display:flex;align-items:center;justify-content:center;-webkit-tap-highlight-color:transparent}
.ip img{pointer-events:none;-webkit-user-drag:none;width:24px;height:24px;image-rendering:pixelated;border:0!important;border-radius:0!important;background:none!important}
.ip:focus-visible,.ip.on{outline:3px solid #ffd54f}
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
        return f'<p class="nextstop">\u2193 本篇到此结束：<a href="{nxt[0]}.html">继续下一页</a></p>'
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



PLACES = {}
NODEIDX = {'by': {}, 'nb': {}}


def short_title(t):
    ps = [x for x in t.split('、') if x != '介绍'] or [t]
    main = ps[0] if len(ps) == 1 else ps[0] + ' → ' + ps[-1]
    return main, '、'.join(ps[1:-1]) if len(ps) > 2 else ''


def norm_place(t):
    t = re.sub(r'（.*?）|\(.*?\)', '', t).strip()
    t = re.sub(r'(\d+)号道路', r'\1号', t)
    return t


def place_href(name):
    n = NODEIDX['by'].get(norm_place(name))
    return (f'part-{n["p"]}.html#{n["id"]}', n['p'], n) if n else None


def disp(n):
    return n['k'] + '道路' if n['t'] == 'r' and n['k'].endswith('号') else n['k']



HMRE = re.compile(r'需要(?:居合斩|冲浪|怪力|碎岩|攀瀑|潮旋|飞翔|闪光|剪断|挖洞|飞天|瞬间移动)(?:[、，,和及]\s*(?:居合斩|冲浪|怪力|碎岩|攀瀑|潮旋|飞翔|闪光|剪断|挖洞|飞天|瞬间移动))*')


def clean_note(t):
    return HMRE.sub('需要特殊能力', t)


def cells(row):
    return re.findall(r'<t[dh][^>]*>(.*?)</t[dh]>', row, re.S)


def vbadge(v):
    v = re.sub(r'<[^>]+>', '', v).strip()
    return '' if v in ('心金 / 魂银', '') else f'<em>仅{e(v)}</em>'


def compact(body):
    def conv(m):
        tb = m.group(0)
        cls = m.group(1)
        cap = re.search(r'<caption>(.*?)</caption>', tb, re.S)
        cap = cap.group(1) if cap else ''
        rows = re.findall(r'<tr(?: class="div")?>.*?</tr>', tb, re.S)
        if not rows:
            return tb
        head = [re.sub(r'<[^>]+>', '', c).strip() for c in cells(rows[0])]
        rest = rows[1:]

        def div(r):
            return '<li class="dv">' + re.sub(r'<[^>]+>', '', cells(r)[0]) + '</li>' if 'class="div"' in r[:20] else None
        if head == ['道具', '版本', '位置 / 获得方法']:
            li = ''
            for r in rest:
                d = div(r)
                if d:
                    li += d; continue
                c = cells(r)
                li += f'<li><span class="n">{c[0]}{vbadge(c[1])}</span><span class="d">{clean_note(c[2])}</span></li>'
            return f'<div class="cl"><h4>{cap or "道具"}</h4><ul class="il">{li}</ul></div>'
        if head == ['宝可梦', '版本', '方式', '等级', '出现率']:
            li = ''
            for r in rest:
                d = div(r)
                if d:
                    li += d; continue
                c = cells(r)
                tg = ' · '.join(x for x in (re.sub(r'<[^>]+>', '', c[2]).strip(), re.sub(r'<[^>]+>', '', c[3]).strip(), re.sub(r'<[^>]+>', '', c[4]).strip()) if x)
                li += f'<li class="pr"><span class="n">{c[0]}{vbadge(c[1])}</span><span class="tg">{tg}</span></li>'
            return f'<div class="cl"><h4>{cap or "可遇到的宝可梦"}</h4><ul class="il pl">{li}</ul></div>'
        if head == ['训练家', '宝可梦', '奖金']:
            li = ''
            for r in rest:
                d = div(r)
                if d:
                    li += d; continue
                c = cells(r)
                mons = ''.join(f'<span class="mc">{x}</span>' for x in re.split(r'<br\s*/?>', c[1]) if x.strip())
                nm = re.sub(r'<small></small>', '', c[0]).replace('<br>', ' ')
                li += f'<li><div class="tn"><span>{nm}</span><span class="pz">{c[2]}</span></div><div class="mm">{mons}</div></li>'
            return f'<div class="cl"><h4>{cap or "训练家"}</h4><ul class="il tl">{li}</ul></div>'
        if cls and 'party' in cls and head[:2] == ['宝可梦', '详情']:
            mm = NPC_RE.search(re.sub(r'<[^>]+>', ' ', cap))
            out = f'<div class="cl party"><h4>{av(mm.group(0), "av md") if mm else ""}<span>{cap}</span></h4>'
            for r in rest:
                c = cells(r)
                sm = re.search(r'<small>(.*?)</small>', c[0])
                nm = re.sub(r'<small>.*?</small>', '', c[0]).replace('<br>', '')
                info = ''.join(f'<div>{x}</div>' for x in re.split(r'<br\s*/?>', c[1]) if x.strip())
                out += f'<div class="mon"><div class="mh"><span class="n">{nm}</span><small>{sm.group(1) if sm else ""}</small></div><div class="mi">{info}</div></div>'
            return out + '</div>'
        if len(rows) == 1 and len(cells(rows[0])) == 1:
            txt = re.sub(r'<[^>]+>', ' ', rows[0])
            mm = NPC_RE.search(txt)
            if mm:
                return f'<div class="gymbox">{av(mm.group(0), "av lg")}<div>{cells(rows[0])[0]}</div></div>'
        return f'<div class="tw">{tb}</div>'
    return re.sub(r'<table class="grid(?: (party))?">.*?</table>', conv, body, flags=re.S)



NPC = {'阿速': 'falkner', '阿笔': 'bugsy', '阿蜜': 'whitney', '松叶': 'morty', '阿四': 'chuck', '小茜': 'jasmine', '柳伯': 'pryce', '小椿': 'clair',
       '小刚': 'brock', '小霞': 'misty', '马志士': 'lt-surge', '莉佳': 'erika', '阿杏': 'janine', '娜姿': 'sabrina', '夏伯': 'blaine', '青绿': 'blue',
       '坂木': 'giovanni', '一树': 'will', '阿桔': 'koga', '希巴': 'bruno', '梨花': 'karen', '阿渡': 'lance', '大木博士': 'oak', '西尔弗': 'silver',
       '米纳奇': 'eusine', '空木博士': 'elm', '钢铁': 'kurt', 'Bill': 'bill', 'Monica': 'monica', 'Wesley': 'wesley', 'Sunny': 'sunny', '阿波罗': 'proton', '兰斯': 'archer', '雅典娜': 'ariana', '拉姆达': 'petrel', '赤红': 'red'}
NPC_RE = re.compile('|'.join((r'(?<![A-Za-z])' + re.escape(k) + r'(?![A-Za-z])') if k.isascii() else re.escape(k) for k in sorted(NPC, key=len, reverse=True)) + r'(?!色)')


def av(name, cls='av'):
    return f'<img class="{cls}" src="../img/npc/{NPC[name]}.png" alt="{name}" loading="lazy">'


def npcify(body):
    """Portraits: first mention per section as a chip, plus a cast strip for the page."""
    cast = []
    chunks = re.split(r'(?=<h2)', body)
    out = []
    for ch in chunks:
        seen = set()

        def para(m):
            parts = re.split(r'(<[^>]+>)', m.group(2))
            for i, t in enumerate(parts):
                if i % 2 or not t:
                    continue
                def one(mm):
                    n = mm.group(0)
                    if n in seen:
                        return n
                    seen.add(n)
                    return f'<span class="npc">{av(n, "av sm")}{n}</span>'
                parts[i] = NPC_RE.sub(one, t)
            return m.group(1) + ''.join(parts) + m.group(3)
        out.append(re.sub(r'(<p[^>]*>)(.*?)(</p>)', para, ch, flags=re.S))
    body = ''.join(out)
    for m in re.finditer(r'<div class="cl party"><h4>(.*?)</h4>|<div class="gymbox">.*?</div></div>', body, re.S):
        for n in NPC_RE.findall(re.sub(r'<[^>]+>', ' ', m.group(0))):
            if n not in cast:
                cast.append(n)
    return body, cast


def cast_strip(cast):
    if not cast:
        return ''
    return ('<div class="cast"><b>本节人物</b>' + ''.join(f'<span class="ct">{av(n, "av")}<i>{n}</i></span>' for n in cast) + '</div>')


def mappins(body, pins, terms=None):
    terms = terms or {}
    """overlay item icons on map figures; returns (body, extra popup data)"""
    extra = {}
    rows = {}
    for m in re.finditer(r'<tr><td>(?:<img class="icon" src="\.\./img/([^"]+)"[^>]*>)?([^<]*?)(?:\s*×\d+)?</td><td>[^<]*</td><td>(.*?)</td></tr>', body):
        rows.setdefault(m.group(2).strip(), (m.group(1), m.group(3)))
    def fig(m):
        inner, img = m.group(0), m.group(1)
        lst = pins.get(img)
        if not lst: return inner
        btns = ''
        for i, p in enumerate(lst):
            if p['n'] not in rows: continue
            ic, loc = rows[p['n']]
            parts = [x for x in re.split(r'<br\s*/?>', loc)]
            txt = re.sub(r'<[^>]+>', '', parts[p.get('l', 0)] if p.get('l', 0) < len(parts) else parts[0])
            key = f'@{img}:{i}'
            t = terms.get(p['n'])
            ent = {'k': '道具', 'n': p['n'], 'a': '拾取位置：' + txt, 'd': t['d'] if t else ''}
            if ic: ent['i'] = ic
            elif t and t.get('i'): ent['i'] = t['i']
            extra[key] = ent
            btns += f'<button class="ip" type="button" style="left:{p["x"]}%;top:{p["y"]}%" data-t="{e(key)}" aria-label="{e(p["n"])}">' + (f'<img src="../img/{ic}" alt="">' if ic else '●') + '</button>'
        if not btns: return inner
        return re.sub(r'(<img src="[^"]*' + re.escape(img) + r'[^>]*>)', r'<div class="mw">\1' + btns.replace('\\', '\\\\') + '</div>', inner, count=1)
    return re.sub(r'<figure class="map">(?:(?!</figure>).)*?maps/([^"/]+?)\.webp.*?</figure>', fig, body, flags=re.S), extra

def autoterm(body, terms):
    """make plain-text item / TM / HM names tappable (first mention per h2 section)"""
    names = sorted((n for n in terms if n not in ('大葱', '要害攻击') and len(n) >= 2 and terms[n].get('k') != '徽章'), key=len, reverse=True)
    if not names: return body, {}
    rx = re.compile('|'.join(re.escape(n) for n in names))
    used, seen, skip = {}, set(), 0
    out = []
    for part in re.split(r'(<[^>]+>)', body):
        if part.startswith('<'):
            m = re.match(r'</?([a-zA-Z0-9]+)', part)
            tag = m.group(1).lower() if m else ''
            closing = part.startswith('</')
            if tag == 'h2' and not closing: seen = set()
            if tag in ('a', 'button', 'script', 'style', 'option', 'h1', 'h2', 'h3', 'h4', 'b', 'figcaption', 'summary', 'th'):
                skip += -1 if closing else (0 if part.endswith('/>') else 1)
                skip = max(skip, 0)
            elif tag == 'span' and 'class="tp' in part and not closing:
                skip += 1
            out.append(part)
        else:
            if skip or not part.strip():
                out.append(part); continue
            def rep(m):
                n = m.group(0)
                if n in seen: return n
                seen.add(n); used[n] = terms[n]
                return f'<span class="tp t2" role="button" tabindex="0" data-t="{e(n)}">{n}</span>'
            out.append(rx.sub(rep, part))
    return ''.join(out), used

def tipify(body, terms):
    used = {}
    def rep(m):
        t = m.group(1)
        if t not in terms: return m.group(0)
        used[t] = terms[t]
        return f'<b class="tp" role="button" tabindex="0" data-t="{e(t)}">{t}</b>'
    return re.sub(r'<b>([^<]*)</b>', rep, body), used

TIPJS = """<div id="tip" role="dialog" aria-live="polite"></div><script>(function(){var D=JSON.parse(document.getElementById('tipdata').textContent),T=document.getElementById('tip'),cur=null;
var SV={'徽章':'<svg viewBox="0 0 40 40"><path d="M20 4l4.6 9.4 10.4 1.5-7.5 7.3 1.8 10.3L20 27.6l-9.3 4.9 1.8-10.3L5 14.9l10.4-1.5z" fill="#d32f2f" stroke="#7a1519" stroke-width="2" stroke-linejoin="round"/><circle cx="20" cy="19" r="4" fill="#fff"/></svg>'};
SV['重要物品']='<svg viewBox="0 0 40 40"><circle cx="14" cy="20" r="7" fill="none" stroke="#7a1519" stroke-width="4"/><path d="M21 20h15M30 20v7M35 20v5" stroke="#7a1519" stroke-width="4" stroke-linecap="round"/></svg>';
function esc(x){return String(x).replace(/[&<>]/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;'}[c]})}
function hide(){T.classList.remove('on');cur=null}
function show(el){var k=el.getAttribute('data-t'),d=D[k];if(!d)return;if(cur===el){hide();return}cur=el;
var ic=d.i?'<img src="../img/'+d.i+'" alt="">':(SV[d.k]||'');
T.innerHTML='<button class="tx" aria-label="关闭">×</button><div class="th">'+ic+'<div><span class="tk">'+esc(d.k)+'</span><h4>'+esc(d.n||k.replace(/（.*/,''))+'</h4></div></div>'+(d.a?'<div class="ta">'+esc(d.a)+(d.b?' ｜ '+esc(d.b):'')+'</div>':'')+(d.d?'<div>'+esc(d.d)+'</div>':'');
T.classList.add('on');place();var b=T.getBoundingClientRect().bottom,lim=innerHeight-(innerWidth<=700?80:12);if(b>lim)scrollBy({top:b-lim,behavior:'smooth'})}
function place(){if(!cur)return;var r=cur.getBoundingClientRect(),w=T.offsetWidth,x=Math.min(Math.max(12,r.left),innerWidth-w-12);T.style.left=x+'px';T.style.top=(r.bottom+12)+'px';T.style.setProperty('--ax',Math.min(Math.max(20,r.left+r.width/2-x),w-20)+'px')}
addEventListener('scroll',function(){requestAnimationFrame(place)},{passive:true});addEventListener('resize',place);
document.addEventListener('click',function(ev){var b=ev.target.closest&&ev.target.closest('.tp,.ip');if(b){ev.preventDefault();show(b);return}if((ev.target.closest&&ev.target.closest('#tip .tx'))||!ev.target.closest('#tip'))hide()});
document.addEventListener('keydown',function(ev){if(ev.key==='Escape')hide();if((ev.key==='Enter'||ev.key===' ')&&ev.target.classList&&ev.target.classList.contains('tp')){ev.preventDefault();show(ev.target)}})})()</script>"""

def link_maps(body, cur=99):
    """Make map images non-linking, exit pins clickable, and add neighbour chips under each map."""
    body = re.sub(r'<a href="\.\./img/maps/[^"]*" target="_blank" rel="noopener">(<img[^>]*>)</a>', r'\1', body)

    def pin(m):
        h = place_href(m.group(4))
        if not h:
            return m.group(0)
        if h[1] > cur:
            return ''
        return f'<a class="pin exit {m.group(1)}" style="{m.group(2)}" href="{h[0]}" data-p="{h[1]}">{m.group(3)} {m.group(4)}</a>'
    body = re.sub(r'<span class="pin exit (\w)" style="([^"]*)">(.) (.*?)</span>', pin, body)

    def fig(m):
        inner, cap = m.group(0), m.group(1)
        n = NODEIDX['by'].get(norm_place(cap))
        if not n:
            return inner
        chips = ''
        for o in NODEIDX['nb'].get(n['k'], []):
            if o['p'] > cur:
                continue
            dx, dy = o['x'] - n['x'], o['y'] - n['y']
            ar = ('→' if dx > 0 else '←') if abs(dx) >= abs(dy) * 0.8 else ('↓' if dy > 0 else '↑')
            chips += f'<a href="part-{o["p"]}.html#{o["id"]}" data-p="{o["p"]}">{ar} {e(disp(o))}</a>'
        if not chips:
            return inner
        return inner.replace('</figure>', f'<p class="nbr"><b>相邻</b>{chips}</p></figure>')
    return re.sub(r'<figure class="map">(?:(?!</figure>).)*?<figcaption>([^<]*)</figcaption>.*?</figure>', fig, body, flags=re.S)


SPJS = "var SP={lock:function(){return false},off:function(){return true}};"


def spoiler_bar():
    return ''



def write_evo(folder, g, out):
    d = json.loads((folder / 'evolutions.json').read_text(encoding='utf-8'))
    h = '<p class="crumb"><a href="../">攻略大全</a> / <a href="./">' + e(g['game']) + '</a></p><h1>通讯进化改动一览</h1>'
    h += '<p class="chap">' + e(d['games']) + '</p>'
    for sec in d['sections']:
        h += f'<div class="cl evo"><h4 style="background:{sec["color"]}">{e(sec["title"])}</h4><ul class="il">'
        for r in sec['rows']:
            if len(r) == 2:
                h += f'<li><span class="n">{e(r[0])}</span><span class="d" style="padding-left:0">{e(r[1])}</span></li>'
            else:
                h += (f'<li><span class="n">{e(r[0])}<i class="ar">→</i>{e(r[1])}</span>'
                      f'<span class="d" style="padding-left:0">{r[2]}<em>{e(r[3])}</em></span></li>')
        h += '</ul></div>'
    h += '<div class="cl"><h4>说明</h4><ul class="il">' + ''.join(f'<li class="note">{e(x)}</li>' for x in d['notes']) + '</ul></div>'
    (out / 'evolutions.html').write_text(page_html('通讯进化改动一览 - ' + g['game'], h + '<style>.evo h4{color:#fff;padding:9px 14px;border-radius:10px;margin-bottom:6px}.ar{font-style:normal;color:#c62828;margin:0 8px}li.note{font-size:14px;color:#6f675c}</style>'), encoding='utf-8')


def write_map(folder, g, out, pages):
    wm = json.loads((folder / 'worldmap.json').read_text(encoding='utf-8'))
    by = {n['k']: n for n in wm['nodes']}
    titles = {slug: info['title'] for slug, info, _ in pages}
    sea = {tuple(x) for x in wm['sea']}
    svg = ''
    for a, b in wm['edges']:
        A, B = by[a], by[b]
        svg += f'<line x1="{A["x"]}" y1="{A["y"]}" x2="{B["x"]}" y2="{B["y"]}" data-p="{max(A["p"], B["p"])}" class="ed{" sea" if (a, b) in sea else ""}"/>'
    # long sea links drawn as curves dipping to the bottom
    for a, b in (('浅葱市', '海王丸号'), ('海王丸号', '枯叶市')):
        A, B = by[a], by[b]
        svg += f'<path d="M{A["x"]} {A["y"]} Q{(A["x"] + B["x"]) // 2} {max(A["y"], B["y"]) + 120} {B["x"]} {B["y"]}" class="ed sea" data-p="{max(A["p"], B["p"])}" fill="none"/>'
    x27 = next(m['x'] for m in wm['nodes'] if m['k'] == '27号')

    def catof(n):
        k = n['k']
        return ('市' if k.endswith('市') else '镇' if k.endswith('镇') else '路' if n['t'] == 'r' else
                '塔' if '塔' in k else '洞' if ('洞' in k or '之路' in k or '径' in k or k.endswith('林') and n['t'] == 'd' or '关口' in k) else
                '山' if k.endswith('山') else '水' if (k.endswith('湖') or k.endswith('岛') or k.endswith('号') and n['t'] == 'd') else '其')
    for n in wm['nodes']:
        h, w = 30, n['w']
        post = n['p'] > 16
        cls = f'nd {n["t"]}{" post" if post else ""}'
        href = f'part-{n["p"]}.html#{n["id"]}'
        k = n['k']
        cat = catof(n)
        reg = 'k' if n['x'] >= x27 else 'j'
        svg += (f'<a href="{href}" data-k="{e(k)}" data-c="{cat}" data-r="{reg}" data-ph="{2 if post else 1}" data-p="{n["p"]}"><g class="{cls}"><title>{e(n["k"])} · 第 {n["p"]} 节：{e(titles["part-" + str(n["p"])])}</title>'
                f'<rect x="{n["x"] - w // 2}" y="{n["y"] - h // 2}" width="{w}" height="{h}" rx="{15 if n["t"] != "r" else 8}"/>'
                f'<text x="{n["x"]}" y="{n["y"] + 5}" text-anchor="middle">{e(n["k"])}</text></g></a>')
    css = """<style>main{max-width:none;padding:8px 12px 40px}.mapwrap{overflow:auto;border:1px solid #ddd3be;border-radius:12px;background:#f4efe4;max-height:78vh;max-height:78dvh;cursor:grab;-webkit-overflow-scrolling:touch}.mapwrap.dr{cursor:grabbing;user-select:none}
.mapwrap svg{display:block;width:1900px}.ed{stroke:#9a9a9a;stroke-width:3}.ed.sea{stroke:#2f7fa6;stroke-dasharray:8 6}
.nd rect{fill:#e9e1cf;stroke:#d32f2f;stroke-width:2}.nd text{fill:#2a2623;font-size:15px;font-weight:700;font-family:-apple-system,'PingFang SC','Microsoft YaHei',sans-serif}
.nd.r rect{fill:#ffffff;stroke:#ddd3be;stroke-width:1.5}.nd.r text{font-size:13px;font-weight:500;fill:#444444}.nd.d rect{fill:#efe9f8;stroke:#8a6cc8}.nd.post rect{stroke:#2f8fc4}.nd.d.post rect{stroke:#2f8fc4}
.nd:hover rect{fill:#d32f2f}.nd:hover text{fill:#f4efe4}.leg{display:flex;flex-wrap:wrap;gap:6px 16px;font-size:13px;color:#6f675c;margin:6px 0 12px}.leg i{display:inline-block;width:14px;height:14px;border-radius:5px;vertical-align:-2px;margin-right:5px;border:2px solid}
.fl{margin:0 0 12px;display:grid;gap:8px}.fl input{width:100%;padding:9px 14px;border-radius:10px;border:1px solid #ddd3be;background:#ffffff;color:#2a2623;font-size:15px}.fl .row{display:flex;flex-wrap:wrap;gap:6px;align-items:center}.fl .row>b{font-size:12.5px;color:#6f675c;font-weight:600;margin-right:2px}.fl button{background:#ffffff;border:1px solid #ddd3be;color:#6f675c;border-radius:999px;padding:5px 12px;font-size:13.5px;cursor:pointer}.fl button.on{background:#d32f2f;color:#ffffff;border-color:#d32f2f;font-weight:700}.fc{font-size:13px;color:#6f675c}.nd.off{opacity:.13;pointer-events:none}.res{display:none;flex-wrap:wrap;gap:6px;margin:0 0 10px}.res a{font-size:13.5px;padding:4px 10px;border:1px solid #ddd3be;border-radius:999px;text-decoration:none;background:#ffffff}.vt{display:flex;gap:8px;align-items:center;margin:0 0 10px}.vt button{background:#ffffff;border:1px solid #ddd3be;color:#6f675c;border-radius:999px;padding:8px 18px;font-size:15px;cursor:pointer}.vt button.on{background:#d32f2f;color:#ffffff;border-color:#d32f2f;font-weight:700}.vt span{font-size:12.5px;color:#6f675c;margin-left:4px}.chips{display:flex;flex-wrap:wrap;gap:8px}.chip{display:inline-block;padding:10px 16px;border-radius:12px;border:1.5px solid #d32f2f;background:#e9e1cf;color:#2a2623;text-decoration:none;font-size:15px;font-weight:600}.chip.post{border-color:#2f8fc4}.chip.d{border-color:#8a6cc8;background:#efe9f8}.chip.r{border-color:#ddd3be;background:#ffffff;font-weight:500;color:#6f675c}.lst h2{font-size:16px;margin:18px 0 10px}svg.ov .nd.r{display:none}svg .nd{transform-box:fill-box;transform-origin:center;transform:scale(var(--ns,1))}.mapbox{position:relative}.zb{position:absolute;right:10px;bottom:10px;display:flex;flex-direction:column;gap:8px;z-index:3}.zb button{width:46px;height:46px;background:rgba(242,242,242,.94);border:1px solid #ddd3be;color:#2a2623;border-radius:12px;font-size:22px;line-height:1;padding:0;box-shadow:0 2px 8px rgba(0,0,0,.35)}.zb button.fit{font-size:13px;font-weight:700}
.mapwrap{touch-action:pan-x pan-y;overscroll-behavior:contain}.fdet>summary{cursor:pointer;list-style:none;display:flex;justify-content:space-between;align-items:center;padding:11px 14px;border:1px solid #ddd3be;border-radius:12px;background:#ffffff;font-weight:700;color:#c62828;margin:0 0 10px}.fdet>summary::-webkit-details-marker{display:none}.fdet>summary span{font-size:13px;color:#6f675c;font-weight:500}.fdet[open]>summary{margin-bottom:10px}
@media(max-width:720px){.zb{flex-direction:row;right:8px;bottom:8px}.zb button{width:42px;height:42px;font-size:20px}.mapwrap{max-height:none;min-height:320px}.fl button{padding:9px 14px;font-size:14.5px}.fl input{padding:12px 14px;font-size:16px}.res{flex-wrap:nowrap;overflow-x:auto;padding-bottom:4px}.res a{white-space:nowrap;padding:8px 14px;font-size:14.5px}.leg{font-size:12.5px;gap:4px 12px}h1{margin-bottom:2px}.chap{display:none}main{padding-bottom:40px!important}.vt span{display:none}}</style>"""
    legend = ('<div class="leg"><span><i style="border-color:#d32f2f;background:#e9e1cf"></i>城镇（主线 1–16 节）</span>'
              '<span><i style="border-color:#2f8fc4;background:#e9e1cf"></i>城镇（通关后 17–32 节）</span>'
              '<span><i style="border-color:#8a6cc8;background:#efe9f8"></i>洞窟 / 塔 / 特殊地点</span>'
              '<span><i style="border-color:#ddd3be;background:#ffffff"></i>道路</span>'
              '<span><i style="border:0;border-top:3px dashed #2f7fa6;height:0;width:18px;vertical-align:4px"></i>海路</span></div>')
    js = r"""<script>(function(){
var s=document.querySelector('.mapwrap svg'),m=document.querySelector('.mapwrap'),w=0,RA=960/1900,KEY='hgssMapState';
function ph(){return innerWidth<=720}
function fitW(){return Math.min(1900,Math.max(300,m.clientWidth-2))}
function hz(){if(w<=fitW()+2)m.style.height=Math.round(w*RA+2)+'px';else if(ph())m.style.height=Math.max(320,innerHeight-m.getBoundingClientRect().top-10)+'px';else m.style.height=''}
function apply(){var ns=Math.max(1,Math.min(3.2,1393/w));s.style.setProperty('--ns',ns);s.classList.toggle('ov',ns>=1.5);s.style.width=w+'px';hz()}
function set(v,cx,cy){var ox=(m.scrollLeft+cx)/w,oy=(m.scrollTop+cy)/(w*RA);w=Math.max(fitW(),Math.min(3200,v));apply();m.scrollLeft=ox*w-cx;m.scrollTop=oy*(w*RA)-cy}
function ctr(){return[m.clientWidth/2,m.clientHeight/2]}
function z(f){var c=ctr();set(w*f,c[0],c[1])}
function fit(){w=fitW();apply();m.scrollLeft=0;m.scrollTop=0}
var st=null;try{st=JSON.parse(sessionStorage.getItem(KEY))}catch(e){}
if(st&&st.w){w=Math.max(fitW(),st.w);apply();m.scrollLeft=st.l;m.scrollTop=st.t}else fit();
function save(){try{sessionStorage.setItem(KEY,JSON.stringify({w:w,l:m.scrollLeft,t:m.scrollTop}))}catch(e){}}
addEventListener('pagehide',save);
m.addEventListener('click',function(e){if(e.target.closest('a')){save();try{sessionStorage.setItem('hgssFromMap','1')}catch(x){}}});
document.getElementById('zi').onclick=function(){z(1.3)};document.getElementById('zo').onclick=function(){z(.77)};document.getElementById('zf').onclick=fit;
addEventListener('resize',function(){w=Math.max(fitW(),w);apply()});
function dist(t){return Math.hypot(t[0].clientX-t[1].clientX,t[0].clientY-t[1].clientY)}var P=null,lt=0,lx=0,ly=0;
m.addEventListener('touchstart',function(e){if(e.touches.length===2){P={d:dist(e.touches),w:w}}},{passive:true});
m.addEventListener('touchmove',function(e){if(e.touches.length===2&&P){e.preventDefault();var r=m.getBoundingClientRect(),t=e.touches;set(P.w*dist(t)/P.d,(t[0].clientX+t[1].clientX)/2-r.left,(t[0].clientY+t[1].clientY)/2-r.top)}},{passive:false});
m.addEventListener('touchend',function(e){if(e.touches.length<2)P=null;if(e.touches.length===0&&e.changedTouches.length===1&&!e.target.closest('a')){var c=e.changedTouches[0],n=Date.now();if(n-lt<320&&Math.hypot(c.clientX-lx,c.clientY-ly)<30){var r=m.getBoundingClientRect();if(w<=fitW()*1.3)set(Math.max(1500,fitW()*2.2),c.clientX-r.left,c.clientY-r.top);else fit();lt=0}else{lt=n;lx=c.clientX;ly=c.clientY}}});
['gesturestart','gesturechange','gestureend'].forEach(function(n){m.addEventListener(n,function(e){e.preventDefault()})});
var d=null;m.addEventListener('pointerdown',function(e){if(e.pointerType==='mouse'&&!e.target.closest('a'))d={x:e.clientX,y:e.clientY,l:m.scrollLeft,t:m.scrollTop}});
addEventListener('pointermove',function(e){if(!d)return;var dx=e.clientX-d.x,dy=e.clientY-d.y;if(Math.abs(dx)+Math.abs(dy)>3)m.classList.add('dr');m.scrollLeft=d.l-dx;m.scrollTop=d.t-dy});
addEventListener('pointerup',function(){d=null;m.classList.remove('dr')});
m.addEventListener('wheel',function(e){if(e.ctrlKey){e.preventDefault();var r=m.getBoundingClientRect();set(w*(e.deltaY<0?1.1:.91),e.clientX-r.left,e.clientY-r.top)}},{passive:false});
document.querySelectorAll('.vt button').forEach(function(b){b.onclick=function(){document.querySelectorAll('.vt button').forEach(function(x){x.classList.toggle('on',x===b)});var l=b.dataset.v==='list';document.querySelector('.mapbox').style.display=l?'none':'';document.querySelector('.lst').style.display=l?'block':'none';if(!l){apply()}}});
})()</script>"""
    ui = ('<div class="fl" style="margin:0 0 8px"><input id="fq" type="search" placeholder="搜索地点，如：月见山、3号、塔" autocomplete="off"></div><details class="fdet" id="fd"><summary>按类型 / 地区筛选 <span id="fs"></span></summary><div class="fl">'
          '<div class="row" data-g="c"><b>类型</b><button data-v="市">市</button><button data-v="镇">镇</button><button data-v="路">道路</button><button data-v="洞">洞窟·径·关口</button><button data-v="塔">塔</button><button data-v="山">山</button><button data-v="水">湖·岛·船</button></div>'
          '<div class="row" data-g="r"><b>地区</b><button data-v="j">城都</button><button data-v="k">关都</button></div>'
          '<div class="row" data-g="ph"><b>阶段</b><button data-v="1">主线（1–16 节）</button><button data-v="2">通关后（17–32 节）</button><button id="fx">清除筛选</button><span class="fc" id="fc"></span></div></div></details>'
          '<div class="res" id="rs"></div>')
    fjs = r"""<script>(function(){""" + SPJS + r"""var A=[].slice.call(document.querySelectorAll('.mapwrap a')),L=[].slice.call(document.querySelectorAll('.lst a')),F={c:[],r:[],ph:[]},q=document.getElementById('fq'),rs=document.getElementById('rs'),fc=document.getElementById('fc');
if(innerWidth>720)document.getElementById('fd').open=true;
function chk(d,t){return !SP.lock(+d.p)&&(!t||d.k.indexOf(t)>-1)&&(!F.c.length||F.c.indexOf(d.c)>-1)&&(!F.r.length||F.r.indexOf(d.r)>-1)&&(!F.ph.length||F.ph.indexOf(d.ph)>-1)}
function run(){document.querySelectorAll('.fl button[data-v="1"],.fl button[data-v="2"],.leg span:nth-child(2)').forEach(function(x){x.style.display=SP.off()?'':'none'});var t=q.value.trim(),act=t||F.c.length||F.r.length||F.ph.length,n=0,h='';
A.forEach(function(a){var ok=chk(a.dataset,t);a.style.display=SP.lock(+a.dataset.p)?'none':'';a.firstChild.classList.toggle('off',!ok);if(ok){n++;h+='<a href="'+a.getAttribute('href')+'">'+a.dataset.k+'</a>'}});
var ln=0;L.forEach(function(a){var ok=chk(a.dataset,t);a.style.display=ok?'':'none';if(ok)ln++});document.querySelectorAll('.lst h2').forEach(function(h){var c=h.nextElementSibling;h.style.display=c.querySelector('a:not([style*=none])')?'':'none'});if(!A.length){n=ln;var pl=document.getElementById('plc');if(pl)pl.style.display=act?'block':'none'}
document.querySelectorAll('.mapwrap line[data-p],.mapwrap path[data-p]').forEach(function(x){x.style.display=SP.lock(+x.dataset.p)?'none':''});
fc.textContent=act?'共 '+n+' 个地点':'';document.getElementById('fs').textContent=act?'· '+n+' 个地点':'';if(A.length){rs.style.display=act&&n<=40?'flex':'none';rs.innerHTML=h}}
document.querySelectorAll('.fl .row[data-g] button[data-v]').forEach(function(b){b.onclick=function(){var g=b.parentNode.dataset.g,v=b.dataset.v,i=F[g].indexOf(v);if(i<0)F[g].push(v);else F[g].splice(i,1);b.classList.toggle('on',i<0);run()}});
document.getElementById('fx').onclick=function(){F={c:[],r:[],ph:[]};q.value='';document.querySelectorAll('.fl button.on').forEach(function(b){b.classList.remove('on')});run()};q.oninput=run;run();
L.forEach(function(a){a.addEventListener('click',function(){try{sessionStorage.setItem('hgssFromMap','1')}catch(e){}})})})()</script>"""
    lst = '<div class="lst" style="display:none">'
    for rg, rl in (('j', '城都地区'), ('k', '关都地区')):
        lst += f'<h2>{rl}</h2><div class="chips">'
        for n in sorted([n for n in wm['nodes'] if (n['x'] >= x27) == (rg == 'k')], key=lambda n: (n['t'] == 'r', n['p'], n['k'])):
            k = n['k']; post = n['p'] > 16
            cat = catof(n)
            lst += (f'<a class="chip {n["t"]}{" post" if post else ""}" href="part-{n["p"]}.html#{n["id"]}" data-k="{e(k)}" data-c="{cat}" data-r="{rg}" data-ph="{2 if post else 1}" data-p="{n["p"]}">{e(k)}</a>')
        lst += '</div>'
    lst += '</div>'
    body = (f'<p class="crumb"><a href="../">攻略大全</a> / <a href="./">{e(g["game"])}</a></p><h1>地图总览</h1>'
            '<p class="chap">按城都和关都的地理位置排列，点任意地点跳到对应的攻略段落。左边是城都，右边是关都，两地由 27 号道路相连。</p>'
            f'{legend}{ui}'
            '<div class="vt"><button class="on" data-v="map">地图</button><button data-v="list">列表</button><span>双指缩放 · 双击放大 · 点地点跳转</span></div>'
            f'<div class="mapbox"><div class="mapwrap"><svg viewBox="0 0 1900 960" xmlns="http://www.w3.org/2000/svg">{svg}</svg></div>'
            f'<div class="zb"><button id="zi" aria-label="放大">＋</button><button id="zo" aria-label="缩小">－</button><button id="zf" class="fit">总览</button></div></div>{lst}{js}{fjs}')
    PLACES.update(css=css, ui=ui, lst=lst.replace('style="display:none"', ''), fjs=fjs)
    (out / 'map.html').write_text(page_html(f'地图总览 - {g["game"]}', css + body), encoding='utf-8')


def build(folder):
    g = json.loads((folder / 'guide.json').read_text(encoding='utf-8'))
    meta = json.loads((folder / 'source' / 'meta.json').read_text(encoding='utf-8'))
    imgs = json.loads((folder / 'source' / 'images.json').read_text(encoding='utf-8'))
    out = SITE / 'guides' / g['slug']
    out.mkdir(parents=True, exist_ok=True)
    wmf = folder / 'worldmap.json'
    if wmf.exists():
        wm0 = json.loads(wmf.read_text(encoding='utf-8'))
        NODEIDX['by'] = {n['k']: n for n in wm0['nodes']}
        NODEIDX['nb'] = {}
        for a_, b_ in wm0['edges']:
            NODEIDX['nb'].setdefault(a_, []).append(NODEIDX['by'][b_])
            NODEIDX['nb'].setdefault(b_, []).append(NODEIDX['by'][a_])
        for a_, b_ in (('浅葱市', '海王丸号'), ('海王丸号', '枯叶市')):
            NODEIDX['nb'].setdefault(a_, []).append(NODEIDX['by'][b_])
            NODEIDX['nb'].setdefault(b_, []).append(NODEIDX['by'][a_])
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
                f'配图来自原站，版权归原作者与游戏厂商；地图截图和人物图来自 <a href="https://archives.bulbagarden.net/wiki/Category:HeartGold_and_SoulSilver_maps" target="_blank" rel="noopener noreferrer">Bulbagarden Archives</a>，游戏画面版权归 Nintendo / Game Freak / The Pokémon Company。道具与属性图标来自 <a href="https://github.com/PokeAPI/sprites" target="_blank" rel="noopener noreferrer">PokeAPI sprites</a>。</p>')

    backjs = "<script>try{if(sessionStorage.getItem('hgssFromMap')){var a=document.createElement('a');a.className='backmap';a.href='map.html';a.textContent='\u2190 \u8fd4\u56de\u5730\u56fe';document.body.appendChild(a)}}catch(e){}</script>"
    tocs = {}
    for i, (slug, info, body) in enumerate(pages):
        body = re.sub(r'<figure data-img="([^"]+)">(.*?)</figure>', fig, body, flags=re.S)
        if NODEIDX['by']:
            body = link_maps(body, int(slug.split('-')[-1]))
        pins = json.loads((folder / 'item-pins.json').read_text(encoding='utf-8')) if (folder / 'item-pins.json').exists() else {}
        body, pextra = mappins(body, pins, json.loads((folder / 'terms.json').read_text(encoding='utf-8')) if (folder / 'terms.json').exists() else {})
        body = compact(body)
        body, cast = npcify(body)
        tdata = json.loads((folder / 'terms.json').read_text(encoding='utf-8')) if (folder / 'terms.json').exists() else {}
        body, tused = tipify(body, tdata)
        tused.update(pextra)
        body, aused = autoterm(body, tdata)
        tused.update(aused)
        tipblock = ('<script type="application/json" id="tipdata">' + json.dumps(tused, ensure_ascii=False).replace('</', '<\\/') + '</script>' + TIPJS) if tused else ''
        prev = pages[i - 1] if i else None
        nxt = pages[i + 1] if i + 1 < len(pages) else None
        pager = '<nav class="pager">'
        if prev:
            pager += f'<a href="{prev[0]}.html"><small>← 上一页</small>{e(prev[1]["title"])}</a>'
        if nxt:
            pager += f'<a class="next" href="{nxt[0]}.html"><small>下一页 →</small>继续</a>'
        else:
            pager += f'<a class="next" href="./"><small>本章完</small>回到目录</a>'
        pager += '</nav>'
        hasmap = (folder / 'worldmap.json').exists()
        dock = ('<nav class="dock">' + (f'<a href="{prev[0]}.html">← 上一页</a>' if prev else '<a class="dis">← 上一页</a>')
                + '<a href="./">目录</a>' + ('<a class="hl" href="map.html">地图</a>' if hasmap else '<a href="../">大全</a>')
                + (f'<a href="{nxt[0]}.html">下一页 →</a>' if nxt else '<a class="dis">下一页 →</a>') + '</nav>')
        crumb = f'<p class="crumb"><a href="../">攻略大全</a> / <a href="./">{e(g["game"])}</a>' + (' / <a href="map.html">地图总览</a>' if (folder / 'worldmap.json').exists() else '') + '</p>'
        tree = ''
        if g.get('tree'):
            body, items = treeify(body, nxt)
            tocs[slug] = items
        (out / f'{slug}.html').write_text(page_html(f'{short_title(info["title"])[0]} - {g["game"]}',
            f'{crumb}<h1>{e(short_title(info["title"])[0])}</h1><p class="chap">第 {slug.split("-")[-1]} 节 · {e(info["chapter"])}'+(f' · 途经 {e(short_title(info["title"])[1])}' if short_title(info["title"])[1] else '')+f'</p>{cast_strip(cast)}{tree}{body}{pager}{credit(slug)}{dock}{backjs if hasmap else ""}{tipblock}'), encoding='utf-8')

    toc, last = '', None
    for slug, info, _ in pages:
        if info['chapter'] != last:
            toc += ('</ul>' if last else '') + f'<h3>{e(info["chapter"])}</h3><ul class="toc">'
            last = info['chapter']
        if True:
            mt, sb = short_title(info["title"])
            toc += (f'<li><a href="{slug}.html"><em class="no">{slug.split("-")[-1]}</em><span class="tt"><i>{e(mt)}</i>'
                    + (f'<small>{e(sb)}</small>' if sb else '') + '</span><span>→</span></a></li>')
    toc += '</ul>'
    if (folder / 'worldmap.json').exists():
        toc = ('<p><a class="mapbtn" href="map.html">\U0001F5FA 打开地图总览（点地点跳到攻略）</a></p>' + toc)
        write_map(folder, g, out, pages)
        pl = (PLACES['ui']
              + '<div class="res" id="rs" style="display:none"></div>' + PLACES['lst'].replace('class="lst"', 'class="lst" id="plc" style="display:none"'))
        evo = ('<p><a class="mapbtn alt" href="evolutions.html">\U0001F501 通讯进化改动一览（3DS 关服后的替代进化方式）</a></p>'
               if (folder / 'evolutions.json').exists() else '')
        toc = PLACES['css'] + pl + PLACES['fjs'] + toc.replace('</p>', '</p>' + evo, 1)
        if (folder / 'evolutions.json').exists():
            write_evo(folder, g, out)
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
