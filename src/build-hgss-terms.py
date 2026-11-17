# Builds src/guides-tr/pokemon-hgss-full/terms.json: popup data for bold item / move / TM / badge names.
# Source: PokeAPI CSV (zh-Hans names + flavor text, CC0-like data; text (c) Nintendo/Game Freak) + a few hand-written entries.
import csv, glob, json, re, sys, urllib.request, os
D = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'guides-tr', 'pokemon-hgss-full')
CACHE = '/tmp/pk'
os.makedirs(CACHE, exist_ok=True)
def load(f):
    p = f'{CACHE}/{f}'
    if not os.path.exists(p):
        urllib.request.urlretrieve('https://raw.githubusercontent.com/PokeAPI/pokeapi/master/data/v2/csv/' + f, p)
    return list(csv.DictReader(open(p, encoding='utf-8')))
def latest(rows, key):
    best = {}
    for r in rows:
        if r['language_id'] != '12': continue
        k = r[key]
        if k not in best or int(r['version_group_id']) >= int(best[k]['version_group_id']): best[k] = r
    return {k: re.sub(r'\s+', '', v['flavor_text']) for k, v in best.items()}
inm = {}
for r in load('item_names.csv'):
    if r['local_language_id'] == '12' and r['name'] not in inm: inm[r['name']] = r['item_id']
mnm = {r['name']: r['move_id'] for r in load('move_names.csv') if r['local_language_id'] == '12'}
for a, b in {'居合斩': '居合劈', '抢夺': '化为己用'}.items():
    if b in mnm: mnm[a] = mnm[b]
ift = latest(load('item_flavor_text.csv'), 'item_id')
mft = latest(load('move_flavor_text.csv'), 'move_id')
mv = {r['id']: r for r in load('moves.csv')}
tn = {r['type_id']: r['name'] for r in load('type_names.csv') if r['local_language_id'] == '12'}
cls = {'1': '变化', '2': '物理', '3': '特殊'}
def move_info(name):
    mid = mnm[name]; m = mv[mid]
    meta = [tn.get(m['type_id'], ''), cls.get(m['damage_class_id'], '')]
    s = ' · '.join(x for x in meta if x)
    st = []
    if m['power']: st.append('威力 ' + m['power'])
    st.append('命中 ' + (m['accuracy'] if m['accuracy'] else '—'))
    st.append('PP ' + m['pp'])
    return s, ' ｜ '.join(st), mft.get(mid, '')
HAND = {
 '自行车': ('重要物品', '骑上就能在道路上飞快移动，比步行和奔跑都快。'),
 '跑步鞋': ('重要物品', '穿上它，按住 B 键就能奔跑。'),
 '地图卡': ('重要物品', '装进宝可梦手表后，手表里的地图就能显示当前所在地区。'),
 '收音机卡': ('重要物品', '装进宝可梦手表后，就能收听各个广播节目。'),
 '扩充卡': ('重要物品', '宝可梦手表的扩展卡，装上后手表多一项功能。'),
 '宝可梦图鉴': ('重要物品', '记录见过和捕获的宝可梦的图鉴。'),
 '船票': ('重要物品', '海王丸号的登船凭证。'),
 '彩虹之羽': ('重要物品', '传说宝可梦凤王留下的羽毛，闪着七彩的光。'),
 '喷水壶': ('重要物品', '给树果和花浇水用的壶。'),
}
BADGES = {  # name: (leader, text)
 '天空徽章': ('阿速', '20 级以下的宝可梦都会听你的话，并且能在野外使用碎岩。'),
 '昆虫徽章': ('阿笔', '30 级以下的宝可梦都会听你的话，并且能在野外使用居合斩。'),
 '平原徽章': ('小茜', '可以在野外使用怪力。'),
 '迷雾徽章': ('松叶', '50 级以下的宝可梦都会听你的话，并且能在野外使用冲浪。'),
 '风暴徽章': ('阿四', '70 级以下的宝可梦都会听你的话，并且能在野外使用飞翔。'),
 '矿物徽章': ('阿蜜', ''),
 '冰河徽章': ('柳伯', '可以在野外使用潮旋。'),
 '升龙徽章': ('大长老', ''),
 '灰色徽章': ('小刚', ''), '蓝色徽章': ('小霞', ''), '橙色徽章': ('马志士', ''), '彩虹徽章': ('莉佳', ''),
 '粉红徽章': ('阿杏', ''), '金色徽章': ('娜姿', ''), '深红徽章': ('夏伯', ''), '绿色徽章': ('青绿', ''),
}
IDENT = {r['id']: r['identifier'] for r in load('items.csv')}
TYPES = ['normal','fighting','flying','poison','ground','rock','bug','ghost','steel','fire','water','grass','electric','psychic','ice','dragon','dark']
IMG = os.path.normpath(os.path.join(D, '..', '..', '..', 'guides', 'img'))
SP = 'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/'
def icon(rel, src):
    dst = os.path.normpath(os.path.join(IMG, rel))
    if not os.path.exists(dst):
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        try: urllib.request.urlretrieve(SP + src, dst)
        except Exception: return None
    return rel
terms = {}
used = set()
for f in glob.glob(D + '/zh/part-*.txt'):
    used |= set(re.findall(r'<b>([^<]*)</b>', open(f, encoding='utf-8').read()))
BLACK = {'大葱', '要害攻击'}
HMS = ['冲浪', '怪力', '碎岩', '飞翔', '闪光', '潮旋', '攀瀑', '攀岩', '居合斩']
alltxt = ''.join(open(f, encoding='utf-8').read() for f in glob.glob(D + '/zh/part-*.txt') + glob.glob(D + '/source/part-*.body.html'))
alltxt = re.sub(r'<[^>]+>', '', alltxt)
names = sorted({n for n in inm if len(n) >= 2 and n not in BLACK}, key=len, reverse=True)
used |= set(re.findall('|'.join(map(re.escape, names)), alltxt))
used |= {h for h in HMS if h in alltxt}
used |= set(re.findall(r'(?:招式|秘传)学习器\d+（[^）]+）', alltxt))
pp = os.path.join(D, 'item-pins.json')
if os.path.exists(pp):
    for lst in json.load(open(pp, encoding='utf-8')).values():
        used |= {x['n'] for x in lst}
HAND.setdefault('Pokédex', ('重要物品', '记录见过和捕获的宝可梦的图鉴。'))
for t in sorted(used):
    m = re.match(r'^(招式|秘传)学习器(\d+)（(.+)）$', t)
    if m and m.group(3) in mnm:
        a, b, c = move_info(m.group(3))
        ty = int(mv[mnm[m.group(3)]]['type_id'])
        ic = icon('tip/hm-normal.png', 'items/hm-normal.png') if m.group(1) == '秘传' else icon(f'tip/tm-{TYPES[ty-1]}.png', f'items/tm-{TYPES[ty-1]}.png') if ty <= 17 else None
        terms[t] = {'k': m.group(1) + '学习器', 'a': a, 'b': b, 'd': c, 'n': f'{m.group(1)}学习器{m.group(2)} · 教会宝可梦「{m.group(3)}」', 'i': ic}
    elif t in BADGES:
        ld, tx = BADGES[t]
        terms[t] = {'k': '徽章', 'd': ('道馆徽章，由' + ('馆主' if ld != '大长老' else '') + ld + '授予。') + tx}
    elif t in HAND:
        terms[t] = {'k': HAND[t][0], 'd': HAND[t][1]}
    elif t in inm and inm[t] in ift:
        idn = IDENT.get(inm[t], '')
        terms[t] = {'k': '道具', 'd': ift[inm[t]], 'i': icon(f'items/{idn}.png', f'items/{idn}.png') if idn else None}
    elif t in mnm:
        a, b, c = move_info(t)
        ty = int(mv[mnm[t]]['type_id'])
        terms[t] = {'k': '招式', 'a': a, 'b': b, 'd': c, 'i': icon(f'tip/type-{ty}.png', f'types/generation-viii/sword-shield/{ty}.png')}
SPN = {r['name'] for r in load('pokemon_species_names.csv') if r['local_language_id'] == '12'}
for t, v in terms.items():
    if v['k'] == '道具' and (t in mnm or t in SPN or any(sp.startswith(t) for sp in SPN if len(t) <= 3)):
        v['amb'] = 1
for v in terms.values():
    if not v.get('i'): v.pop('i', None)
json.dump(terms, open(D + '/terms.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
print(len(terms), 'terms;', len(used - set(terms)), 'unmatched')
if '-v' in sys.argv: print(sorted(used - set(terms)))
