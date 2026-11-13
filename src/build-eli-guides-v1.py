#!/usr/bin/env python3
"""Build guides/index.html: per-game guide hub for games playable on 3DS.

Version exclusives come from data.json (same source as the pokedex).
External links were checked to return HTTP 200 on 2026-11-13.
Theme and top bar are copied from handheld/index.html so the pages match.
"""
import html, json, re
from pathlib import Path

SITE = Path(__file__).resolve().parent.parent
CHECKED = '2026-11-13'
WIKI = 'https://wiki.52poke.com/zh-hans/'
SEREBII = 'https://www.serebii.net'

# (title, platform, [version ids], 52poke page, serebii dir, {category: serebii page})
GAMES = [
    ('红宝石 / 蓝宝石', 'GBA', [7, 8], '寶可夢 紅寶石／藍寶石', 'rubysapphire',
     {'gym': 'gyms', 'e4': 'elitefour', 'legend': 'legendary', 'excl': 'exclusives', 'gift': 'gift', 'tm': 'tmhm'}),
    ('绿宝石', 'GBA', [9], '寶可夢 綠寶石', 'emerald',
     {'gym': 'gym', 'e4': 'elite', 'legend': 'legendary', 'gift': 'gift'}),
    ('火红 / 叶绿', 'GBA', [10, 11], '寶可夢 火紅／葉綠', 'fireredleafgreen',
     {'gym': 'gyms', 'e4': 'elitefour', 'legend': 'legendary', 'excl': 'exclusives', 'gift': 'gift', 'tm': 'tmhm'}),
    ('钻石 / 珍珠', 'NDS', [12, 13], '寶可夢 鑽石／珍珠', 'diamondpearl',
     {'legend': 'legendaries', 'excl': 'exclusives', 'tm': 'tmhm'}),
    ('白金', 'NDS', [14], '寶可夢 白金', 'platinum',
     {'e4': 'elitefour', 'legend': 'legends', 'gift': 'gift', 'tm': 'tmhm'}),
    ('心金 / 魂银', 'NDS', [15, 16], '寶可夢 心金／魂銀', 'heartgoldsoulsilver',
     {'gym': 'gym', 'e4': 'elitefour', 'legend': 'legends', 'excl': 'exclusives', 'gift': 'gift', 'tm': 'tmhm'}),
    ('黑 / 白', 'NDS', [17, 18], '寶可夢 黑／白', 'blackwhite',
     {'gym': 'gyms', 'e4': 'elitefour', 'legend': 'legendary', 'excl': 'exclusives', 'gift': 'gift', 'tm': 'tmhm'}),
    ('黑2 / 白2', 'NDS', [21, 22], '寶可夢 黑２／白２', 'black2white2',
     {'gym': 'gyms', 'e4': 'elitefour', 'legend': 'legendary', 'excl': 'exclusives', 'gift': 'gift', 'tm': 'tmhm'}),
    ('X / Y', '3DS', [23, 24], '寶可夢 Ｘ／Ｙ', 'xy',
     {'gym': 'gyms', 'e4': 'elitefour', 'legend': 'legendary', 'excl': 'exclusives', 'gift': 'gift', 'tm': 'tmhm'}),
    ('欧米伽红宝石 / 阿尔法蓝宝石', '3DS', [25, 26], '寶可夢 歐米加紅寶石／阿爾法藍寶石', 'omegarubyalphasapphire',
     {'gym': 'gyms', 'e4': 'elitefour', 'legend': 'legendary', 'excl': 'exclusives', 'gift': 'gift', 'tm': 'tmhm'}),
    ('太阳 / 月亮', '3DS', [27, 28], '精靈寶可夢 太陽／月亮', 'sunmoon',
     {'e4': 'elitefour', 'legend': 'legendary', 'excl': 'exclusives', 'gift': 'gift', 'tm': 'tm'}),
    ('究极之日 / 究极之月', '3DS', [29, 30], '精灵宝可梦 究极之日／究极之月', 'ultrasunultramoon',
     {'e4': 'elitefour', 'legend': 'legendary', 'excl': 'exclusives', 'gift': 'gift', 'tm': 'tm'}),
]
CAT = [('gym', '道馆'), ('e4', '四天王'), ('legend', '传说宝可梦'), ('excl', '版本限定'), ('gift', '赠送宝可梦'), ('tm', '招式学习器')]
PLAY = {'GBA': ('GBA放到桌面', 'vc'), 'NDS': ('NDS放到桌面', 'nds'), '3DS': ('备份存档', 'saves')}

e = html.escape
data = json.loads((SITE / 'data.json').read_text(encoding='utf-8'))
names = {p['id']: p['n'] for p in data['pokemon']}
vname = {v['id']: v['n'] for v in data['versions']}
seen = {}
for pid, rows in data['encounters'].items():
    for r in rows:
        seen.setdefault(r[0], set()).add(int(pid))


def chips(vid, ids):
    return ''.join(f'<a class="chip" href="../#v={vid}&amp;p={i}">{e(names[i])}</a>' for i in sorted(ids))


def exclusives(vids):
    if len(vids) < 2:
        return ''
    a, b = vids
    out = []
    for v, w in ((a, b), (b, a)):
        only = seen.get(v, set()) - seen.get(w, set())
        out.append(f'<div class="ex"><h4>只在{e(vname[v])} <span>{len(only)}</span></h4><div class="chips">{chips(v, only)}</div></div>')
    return f'<details class="block"><summary>版本限定宝可梦（野外与固定遭遇）</summary>{"".join(out)}<p class="note">点名字直接打开本站图鉴里这一作的记录。</p></details>'


cards = []
for title, plat, vids, wiki, sdir, pages in GAMES:
    q = ' '.join(vname[v] for v in vids)
    dex = ''.join(f'<a href="../#v={v}">图鉴：{e(vname[v])}</a>' for v in vids)
    play, tab = PLAY[plat]
    ext = ''.join(f'<a href="{SEREBII}/{sdir}/{pages[k]}.shtml" target="_blank" rel="noopener noreferrer">{lab}</a>'
                  for k, lab in CAT if k in pages)
    wurl = WIKI + wiki.replace(' ', '_')
    cards.append(f'''<article class="game" data-plat="{plat}" data-q="{e(title + ' ' + q)}">
<header><h3>{e(title)}</h3><span class="plat">{plat}</span></header>
<div class="row"><b>本站</b><div class="links">{dex}<a href="../save-types/index.html#q={e(vname[vids[0]])}">存档类型</a><a href="../handheld/">掌机指南·{play}</a></div></div>
<div class="row"><b>中文百科</b><div class="links"><a href="{e(wurl)}" target="_blank" rel="noopener noreferrer">神奇宝贝百科：剧情、地图、版本差异</a></div></div>
<div class="row"><b>英文资料</b><div class="links"><a href="{SEREBII}/{sdir}/" target="_blank" rel="noopener noreferrer">Serebii 总览</a>{ext}</div></div>
{exclusives(vids)}
</article>''')

hh = (SITE / 'handheld' / 'index.html').read_text(encoding='utf-8')
head = hh[:hh.index('<title>')]
theme = re.search(r'<style id="eli-theme">.*?</style>', hh, re.S).group(0)
bar = re.search(r'<header class="eli-bar">.*?</header>', hh, re.S).group(0)
bar = bar.replace(' aria-current="page"', '').replace('<a href="../guides/">', '<a href="../guides/" aria-current="page">')

CSS = '''<style>
*{box-sizing:border-box}body{margin:0;font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','Microsoft YaHei',sans-serif;background:#1f2a24;color:#f1f0e6}
main{max-width:960px;margin:auto;padding:8px 16px max(28px,env(safe-area-inset-bottom))}
h1{font-size:26px;margin:18px 0 6px}.intro{color:#a9b5a6;font-size:14px;line-height:1.8;margin:0 0 14px}
.bar{display:flex;flex-wrap:wrap;gap:8px;align-items:center;margin:0 0 16px}
.bar input{flex:1 1 220px;min-height:42px;border-radius:999px;border:1px solid #44574b;background:#2a372f;color:#f1f0e6;padding:0 16px;font:inherit;font-size:15px}
.bar button{min-height:40px;border-radius:999px;border:1px solid #44574b;background:transparent;color:#f1f0e6;padding:0 14px;font:inherit;font-size:14px;cursor:pointer}
.bar button[aria-pressed=true]{background:#c9e265;color:#1f2a24;border-color:#c9e265;font-weight:700}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(420px,1fr));gap:12px}
.game{background:#2a372f;border:1px solid #44574b;border-radius:14px;padding:14px 16px}
.game header{display:flex;align-items:center;gap:10px;margin-bottom:6px}.game h3{margin:0;font-size:19px}
.plat{font-size:12px;font-weight:700;color:#1f2a24;background:#a9b5a6;border-radius:999px;padding:2px 9px}
.row{display:grid;grid-template-columns:64px 1fr;gap:8px;padding:7px 0;border-top:1px solid #36463c;font-size:14px}
.row b{color:#a9b5a6;font-weight:600;font-size:13px;padding-top:7px}
.links{display:flex;flex-wrap:wrap;gap:6px}
.links a{display:inline-flex;align-items:center;min-height:34px;padding:0 11px;border-radius:999px;background:#1f2a24;border:1px solid #44574b;color:#f1f0e6;text-decoration:none;font-size:13px}
.links a:hover,.chip:hover{border-color:#c9e265;color:#c9e265}
.block{border-top:1px solid #36463c;margin-top:2px}.block summary{min-height:42px;display:flex;align-items:center;cursor:pointer;font-size:14px;color:#c9e265}
.ex h4{margin:6px 0;font-size:13px;color:#a9b5a6;font-weight:600}.ex h4 span{color:#f1f0e6}
.chips{display:flex;flex-wrap:wrap;gap:5px;margin-bottom:8px}
.chip{font-size:12px;padding:4px 9px;border-radius:999px;border:1px solid #44574b;color:#f1f0e6;text-decoration:none}
.note,.foot{font-size:12px;color:#a9b5a6;line-height:1.8}.foot{margin:18px 0 0}.foot a{color:#c9e265}
.empty{color:#a9b5a6;padding:20px 0}
a:focus-visible,button:focus-visible,input:focus-visible,summary:focus-visible{outline:3px solid #c9e265;outline-offset:2px}
@media(max-width:560px){.grid{grid-template-columns:1fr}h1{font-size:22px;margin-top:12px}.game{padding:12px}.row{grid-template-columns:1fr;gap:4px}.row b{padding-top:0}}
[hidden]{display:none!important}
</style>'''

JS = '''<script>
(()=>{const q=document.getElementById('q'),bs=[...document.querySelectorAll('[data-p]')],gs=[...document.querySelectorAll('.game')],em=document.getElementById('empty');let p='all';
function run(){const t=q.value.trim().toLowerCase();let n=0;for(const g of gs){const ok=(p==='all'||g.dataset.plat===p)&&(!t||g.dataset.q.toLowerCase().includes(t)||g.textContent.toLowerCase().includes(t));g.hidden=!ok;if(ok)n++}em.hidden=n>0}
bs.forEach(b=>b.onclick=()=>{p=b.dataset.p;bs.forEach(x=>x.setAttribute('aria-pressed',x===b));run()});q.oninput=run;})();
</script>'''

page = f'''{head}<title>宝可梦攻略导航 · Eli</title>{CSS}{theme}</head><body>{bar}<main>
<h1>宝可梦攻略导航</h1>
<p class="intro">3DS 能玩的 12 组宝可梦正作（GBA / NDS / 3DS），每作汇总本站资料和靠谱的外部攻略。搜索框可以搜游戏名，也可以搜宝可梦名字，查它是哪个版本限定。</p>
<div class="bar"><input id="q" type="search" placeholder="搜游戏或宝可梦，例如：心金、六尾" aria-label="搜索"><button data-p="all" aria-pressed="true">全部</button><button data-p="GBA" aria-pressed="false">GBA</button><button data-p="NDS" aria-pressed="false">NDS</button><button data-p="3DS" aria-pressed="false">3DS</button></div>
<div class="grid">{''.join(cards)}</div>
<p class="empty" id="empty" hidden>没有匹配的游戏。</p>
<p class="foot">版本限定名单来自本站图鉴数据（PokéAPI 等），只算野外和固定遭遇，不含配信活动和交换。外部链接于 {CHECKED} 逐个核对可访问，内容版权归各站点所有。中文资料来自 <a href="https://wiki.52poke.com/" target="_blank" rel="noopener noreferrer">神奇宝贝百科</a>，英文资料来自 <a href="https://www.serebii.net/" target="_blank" rel="noopener noreferrer">Serebii</a>。</p>
</main>{JS}</body></html>
'''
out = SITE / 'guides' / 'index.html'
out.parent.mkdir(exist_ok=True)
out.write_text(page, encoding='utf-8')
print('wrote', out, len(page))
