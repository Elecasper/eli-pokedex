#!/usr/bin/env python3
"""Turn a Bulbapedia walkthrough (wikitext) into a Chinese guide.

  bulba-walkthrough-v1.py draft  <guide-slug> <part-json> <n>   -> prints a translation draft
  bulba-walkthrough-v1.py build  <guide-slug>                   -> writes fragments from drafts + translations

Source JSON (saved from the Bulbapedia API) lives in src/guides-tr/<slug>/source/part-<n>.json.
Translations live in src/guides-tr/<slug>/zh/part-<n>.txt as "KEY: 中文" lines.
Tables (wild Pokémon, items, shops, trainers, boss parties) are converted automatically
with names from data.json and PokeAPI slugs; prose, item locations and headings come
from the translation file. Untranslated keys fall back to the English text.
"""
import html, json, re, sys
from pathlib import Path

SITE = Path(__file__).resolve().parent.parent
e = html.escape
data = json.loads((SITE / 'data.json').read_text(encoding='utf-8'))
slugs = json.loads((SITE / 'src' / 'pokeapi-slugs-v1.json').read_text(encoding='utf-8'))
PM_EN = {p['en'].lower(): p for p in data['pokemon']}
PM_ID = {p['id']: p for p in data['pokemon']}
ITEM_ZH = {int(k): v for k, v in data['items'].items()}
ITEM_SLUG = slugs['item']
MOVE_ID = slugs['move']
ABIL_ID = slugs['ability']
AREA = {}
for a in data['areas'].values():
    AREA.setdefault(a[4], a[1])
TYPE_ZH = dict(zip('Normal Fighting Flying Poison Ground Rock Bug Ghost Steel Fire Water Grass Electric Psychic Ice Dragon Dark Fairy'.split(),
                   '一般 格斗 飞行 毒 地面 岩石 虫 幽灵 钢 火 水 草 电 超能力 冰 龙 恶 妖精'.split()))
STAT_ZH = {'HP': 'HP', 'Attack': '攻击', 'Defense': '防御', 'Sp. Atk': '特攻', 'Special Attack': '特攻', 'Sp. Def': '特防',
           'Special Defense': '特防', 'Speed': '速度', 'accuracy': '命中率', 'evasion': '闪避率', 'Accuracy': '命中率', 'Evasion': '闪避率'}
STATUS_ZH = {'sleep': '睡眠', 'paralysis': '麻痹', 'poison': '中毒', 'burn': '灼伤', 'freeze': '冰冻', 'confusion': '混乱',
             'badly poisoned': '剧毒', 'infatuation': '着迷', 'flinch': '畏缩'}
DOTW = {'Mo': '星期一', 'Tu': '星期二', 'We': '星期三', 'Th': '星期四', 'Fr': '星期五', 'Sa': '星期六', 'Su': '星期日'}
BADGE = {'Zephyr': '天空徽章', 'Hive': '昆虫徽章', 'Plain': '平原徽章', 'Fog': '迷雾徽章', 'Storm': '风暴徽章', 'Mineral': '矿物徽章',
         'Glacier': '冰河徽章', 'Rising': '升龙徽章', 'Boulder': '灰色徽章', 'Cascade': '蓝色徽章', 'Thunder': '橙色徽章',
         'Rainbow': '彩虹徽章', 'Soul': '粉红徽章', 'Marsh': '金色徽章', 'Volcano': '深红徽章', 'Earth': '绿色徽章'}
PEOPLE = json.loads((SITE / 'src' / 'bulba-names-v1.json').read_text(encoding='utf-8'))
METHOD = {'Grass': '草丛', 'Gift': '赠送', 'Surf': '冲浪', 'Old Rod': '破旧钓竿', 'Good Rod': '好钓竿', 'Super Rod': '厉害钓竿',
          'Rock Smash': '碎岩', 'Headbutt': '头锤', 'Trade': '交换', 'Swarm': '大量出现', 'Cave': '洞窟', 'Only One': '仅一只',
          'Event': '活动', 'Egg': '蛋', 'Hoenn Sound': '丰缘音乐', 'Sinnoh Sound': '神奥音乐', 'Safari Zone': '狩猎区',
          'Bug-Catching Contest': '捕虫大会', 'Fishing': '钓鱼', 'Rock': '岩石', 'Walking': '步行', 'Interact': '调查',
          'Headbutt (Low)': '头锤（低概率树）', 'Headbutt (High)': '头锤（高概率树）', 'Headbutt (Special)': '头锤（特殊树）'}
DIV = {'First partner Pokémon': '最初的伙伴', 'Fishing': '钓鱼', 'Special': '特殊', 'Surfing': '冲浪', 'Later visit': '之后再来',
       'Headbutt Group A': '头锤（A 组树）', 'Headbutt Group B': '头锤（B 组树）', 'Swarm': '大量出现', 'Rock Smash': '碎岩',
       'Gift Pokémon': '赠送的宝可梦', 'Special Pokémon': '特殊的宝可梦', 'West side': '西侧', 'East side': '东侧', 'Requires Surf': '需要冲浪',
       'Entrance': '入口', 'Second room': '第二个房间', 'Third room': '第三个房间'}
METHOD.update({'Fish Old': '破旧钓竿', 'Fish Good': '好钓竿', 'Fish Super': '厉害钓竿', 'Hoenn': '丰缘音乐', 'Sinnoh': '神奥音乐',
               'Helix': '贝壳化石', 'Dome': '甲壳化石', 'Amber': '秘密琥珀', 'Root': '根状化石', 'Claw': '爪子化石', 'Skull': '头盖化石', 'Armor': '盾甲化石'})
RATE_KEY = {'all': '', 'morning': '早', 'day': '日', 'night': '夜'}


def slugify(s):
    s = s.lower().replace('é', 'e').replace('♀', '-f').replace('♂', '-m')
    s = re.sub(r"[.'’:]", '', s)
    return re.sub(r'[^a-z0-9]+', '-', s).strip('-')


def pm(name, show_icon=True):
    p = PM_EN.get(name.strip().lower())
    if not p:
        return e(name)
    icon = f'<img class="pm" src="../img/pm/{p["id"]}.png" alt="" width="40" height="30">' if show_icon else ''
    USED_PM.add(p['id'])
    return icon + e(p['n'])


ITEM_FIX = {'Grn Apricorn': 'Green Apricorn', 'Blu Apricorn': 'Blue Apricorn', 'Ylw Apricorn': 'Yellow Apricorn',
            'Red Apricorn': 'Red Apricorn', 'Wht Apricorn': 'White Apricorn', 'Blk Apricorn': 'Black Apricorn', 'Pnk Apricorn': 'Pink Apricorn',
            'Dowsing MCHN': 'Dowsing Machine'}
ITEM_ZH_EXTRA = {'Pokégear': '宝可装置', 'Running Shoes': '跑步鞋', 'Sticker Case': '贴纸盒', 'Dowsing Machine': '探宝器',
                 'Basement Key': '地下钥匙', 'Lost Item': '遗失物', 'Flower Mail': '花朵邮件', 'Apricorn Box': '球果盒'}


def item(name):
    n = re.sub(r'\[\[|\]\]', '', name).strip()
    n = re.sub(r'\s*\((item)\)$|\s+(III|IV)$', '', n)
    n = ITEM_FIX.get(n, n)
    if n in ITEM_ZH_EXTRA:
        return e(ITEM_ZH_EXTRA[n])
    sid = ITEM_SLUG.get(slugify(n))
    if sid and sid in ITEM_ZH:
        USED_ITEM.add(slugify(n))
        return f'<img class="icon" src="../img/items/{slugify(n)}.png" alt="" width="30" height="30" loading="lazy">' + e(ITEM_ZH[sid])
    m = re.match(r'(TM|HM)(\d+)', n)
    if m:
        return ('招式学习器' if m.group(1) == 'TM' else '秘传学习器') + m.group(2)
    return e(n)


def move(n):
    mid = MOVE_ID.get(slugify(n))
    return data['moves'][str(mid)]['n'] if mid and str(mid) in data['moves'] else n


def place(n):
    s = slugify(n)
    for k in (s, 'johto-' + s, 'kanto-' + s):
        if k in AREA:
            return AREA[k]
    return n


USED_PM, USED_ITEM = set(), set()


def split_params(body):
    out, depth, cur = [], 0, ''
    for ch in body:
        if ch in '{[':
            depth += 1
        elif ch in '}]':
            depth -= 1
        if ch == '|' and depth == 0:
            out.append(cur); cur = ''
        else:
            cur += ch
    out.append(cur)
    pos, kw = [], {}
    for x in out:
        m = re.match(r'\s*([\w ]+?)\s*=(.*)$', x, re.S)
        if m and not m.group(1).isdigit():
            kw[m.group(1).strip()] = m.group(2).strip()
        elif m and m.group(1).isdigit() and int(m.group(1)) > 9:
            kw[m.group(1)] = m.group(2).strip()
        else:
            pos.append(x.strip())
    return pos, kw


def inline(s):
    """Convert inline wikitext to HTML, translating names where possible."""
    def tpl(m):
        body = m.group(1)
        name, _, rest = body.partition('|')
        name = name.strip()
        pos, kw = split_params(rest) if rest else ([], {})
        n = name.lower()
        if n in ('p', 'pkmn', 'pokemon') and pos:
            if n == 'pkmn':
                return {'trainer': '训练家', 'gym leader': '道馆馆主', 'elite four': '四天王'}.get(pos[0].lower(), pos[-1])
            return pm(pos[0], False) if len(pos) == 1 else pos[-1]
        if n == 'm' and pos:
            return move(pos[0])
        if n in ('t', 'type') and pos:
            return TYPE_ZH.get(pos[0], pos[0])
        if n in ('rt', 'rtn') and pos:
            return f'{pos[0]}号道路'
        if n == 'tm' and len(pos) >= 2:
            return f'招式学习器{pos[0]}（{move(pos[1])}）'
        if n == 'hm' and len(pos) >= 2:
            return f'秘传学习器{pos[0]}（{move(pos[1])}）'
        if n == 'bag' and pos:
            return item(pos[0])
        if n == 'badge' and pos:
            return BADGE.get(pos[0], pos[0] + ' Badge')
        if n in ('pdollar', 'pokedollar'):
            return '₽'
        if n == 'color2' and pos:
            return pos[-1]
        if n == 'stat' and pos:
            return STAT_ZH.get(pos[-1], pos[-1])
        if n == 'status' and pos:
            return STATUS_ZH.get(pos[0].lower(), pos[-1])
        if n == 'dotw' and pos:
            return DOTW.get(pos[0], pos[0])
        if n == 'dl' and len(pos) >= 2:
            return {'Shock Ribbon': '震惊缎带', 'Smile Ribbon': '笑容缎带', 'Gorgeous Ribbon': '华丽缎带', 'Royal Ribbon': '皇家缎带',
                    'Careless Ribbon': '粗心缎带', 'Downcast Ribbon': '沮丧缎带', 'Relax Ribbon': '放松缎带', 'Snooze Ribbon': '瞌睡缎带',
                    'Alert Ribbon': '警觉缎带', 'Footprint Ribbon': '足迹缎带', 'Record Ribbon': '纪录缎带', 'Legend Ribbon': '传说缎带'}.get(pos[-1], pos[-1])
        if n in ('dl', 'ga', 'jo', 'tc', 'ka', 'mga', 'an', 'cat', 'pcp', 'g', 'ab', 'ability'):
            if n in ('ab', 'ability') and pos:
                aid = ABIL_ID.get(slugify(pos[0]))
                return data['abilities'].get(str(aid), pos[0]) if aid else pos[0]
            key = pos[-1] if pos else ''
            if n in ('ga', 'jo', 'tc', 'ka', 'mga'):
                return PEOPLE.get(pos[0], key) if len(pos) == 1 else key
            return key
        if n in ('msp/3', 'msp') and len(pos) >= 2:
            return pm(pos[1])
        if n == 'playerchoice' and len(pos) >= 2:
            return f'如果你选了{pm(pos[1], False)}'
        if n == 'tt' and len(pos) >= 2:
            return f'{pos[0]}（{pos[1]}）'
        if n in ('sup/4', 'sup/3', 'sup', '-', 'roundy', 'shop', 'clear', 'tt', 'wp'):
            return ''
        if n == 'game' and pos:
            return pos[0]
        if n in ('i', 'item') and pos:
            return item(pos[0])
        return pos[-1] if pos else ''
    prev = None
    while prev != s:
        prev = s
        s = re.sub(r'\{\{([^{}]*)\}\}', tpl, s)
    def link(m):
        target, _, text = m.group(1).partition('|')
        if target.startswith(('File:', 'Image:', 'Category:')):
            return ''
        t = text or target
        if not text:
            p = PM_EN.get(t.lower())
            if p:
                return p['n']
            pl = place(t)
            if pl != t:
                return pl
            sid = ITEM_SLUG.get(slugify(t))
            if sid and sid in ITEM_ZH:
                return ITEM_ZH[sid]
        return t
    s = re.sub(r'\[\[([^\[\]]*)\]\]', link, s)
    s = re.sub(r"'''(.*?)'''", r'<b>\1</b>', s)
    s = re.sub(r"''(.*?)''", r'<i>\1</i>', s)
    s = re.sub(r'<sc>(.*?)</sc>', r'\1', s)
    s = re.sub(r'<ref[^>]*>.*?</ref>|<ref[^>]*/>', '', s, flags=re.S)
    return s.strip()


def take_block(w, i):
    """Return end index of a {| ... |} or {{ ... }} block starting at i."""
    if w.startswith('{|', i):
        depth = 0
        for m in re.finditer(r'(?m)^[ \t]*(\{\||\|\})', w[i:]):
            depth += 1 if m.group(1) == '{|' else -1
            if depth == 0:
                return i + m.end()
        return len(w)
    depth, j = 0, i
    while j < len(w):
        if w.startswith('{{', j):
            depth += 1; j += 2; continue
        if w.startswith('}}', j):
            depth -= 1; j += 2
            if depth == 0:
                return j
            continue
        j += 1
    return len(w)


def ver(hg, ss):
    hg, ss = hg == 'yes', ss == 'yes'
    return '心金 / 魂银' if hg and ss else '心金' if hg else '魂银' if ss else ''


def catch_table(block, keys):
    rows, cur = [], ''
    def tr(t):
        t = DIV.get(t, METHOD.get(t, t))
        if re.search(r'[A-Za-z]{3,}', re.sub(r'<[^>]+>', '', t)):
            k = nk(keys, 'M'); keys[k] = t
            return '{{' + k + '}}'
        return e(t)
    for m in re.finditer(r'\{\{[Cc]atch/(div|entryhs)\|([^{}]*(?:\{\{[^{}]*\}\}[^{}]*)*)\}\}', block):
        pos, kw = split_params(m.group(2))
        if m.group(1) == 'div':
            cur = re.sub(r'<br\s*/?>', ' ', inline(pos[-1])) if pos else ''
            cur = re.sub(r'<[^>]+>', '', cur).strip()
            rows.append(f'<tr class="div"><th colspan="5">{tr(cur)}</th></tr>')
            continue
        if len(pos) < 6:
            continue
        if 'all' in kw:
            rates = kw['all']
        elif len(pos) >= 9:
            rates = f'早 {pos[6]} · 日 {pos[7]} · 夜 {pos[8]}'
        else:
            rates = ''
        meth = pos[4]
        rt = re.sub(r'<[^>]+>', '', inline(rates)).replace('One', '1 只')
        rows.append(f'<tr><td>{pm(pos[1])}</td><td>{ver(pos[2], pos[3])}</td><td>{tr(re.sub(r"<[^>]+>", "", inline(meth)))}</td>'
                    f'<td>{tr(pos[5]) if re.search(r"[A-Za-z]{3,}", pos[5]) else "Lv." + e(pos[5])}</td><td>{tr(rt) if re.search(r"[A-Za-z]{3,}", rt) else e(rt)}</td></tr>')
    if not rows:
        return None
    return ('<table class="grid"><caption>可遇到的宝可梦</caption><tr><th>宝可梦</th><th>版本</th><th>方式</th><th>等级</th><th>出现率</th></tr>'
            + ''.join(rows) + '</table>')


def item_table(block, keys, prefix):
    rows = []
    for m in re.finditer(r'\{\{([Ii]temlist|[Cc]atch/div)\|((?:[^{}]|\{\{[^{}]*\}\})*)\}\}', block):
        pos, kw = split_params(m.group(2))
        if m.group(1).lower() == 'catch/div':
            label = pos[-1] if pos else ''
            k = nk(keys, prefix); keys[k] = label
            rows.append(f'<tr class="div"><th colspan="3">{{{{{k}}}}}</th></tr>')
            continue
        name = pos[0] if pos else ''
        disp = kw.get('display', '')
        if disp and re.match(r'(TM|HM) |None|unknown', name):
            k0 = None
            label = re.sub(r'×\s*\d+', '', inline(disp)).strip()
            qty = re.search(r'×\s*(\d+)', disp)
            desc = pos[1] if len(pos) > 1 else ''
            k = nk(keys, prefix); keys[k] = inline(desc)
            rows.append(f'<tr><td>{label}{" ×" + qty.group(1) if qty else ""}</td><td>{ver(kw.get("HG", ""), kw.get("SS", ""))}</td>'
                        f'<td>{{{{{k}}}}}</td></tr>')
            continue
        qty = re.search(r'×\s*(\d+)', disp)
        desc = pos[1] if len(pos) > 1 else ''
        k = nk(keys, prefix); keys[k] = inline(desc)
        rows.append(f'<tr><td>{item(name)}{" ×" + qty.group(1) if qty else ""}</td><td>{ver(kw.get("HG", ""), kw.get("SS", ""))}</td>'
                    f'<td>{{{{{k}}}}}</td></tr>')
    if not rows:
        return None
    return ('<table class="grid"><caption>道具</caption><tr><th>道具</th><th>版本</th><th>位置 / 获得方法</th></tr>' + ''.join(rows) + '</table>')


SHOP_LABEL = {'Upper cashier': '上方收银台', 'Lower cashier': '下方收银台', 'Left cashier': '左侧收银台', 'Right cashier': '右侧收银台',
              'Left Gentleman': '左边的绅士', 'Right Gentleman - TMs': '右边的绅士（招式学习器）', 'Right Gentleman - Held items': '右边的绅士（携带道具）'}


def shop_table(block):
    cap = re.search(r'SHOP:(.*)', block)
    label = re.sub(r'<[^>]+>', '', inline(cap.group(1))).strip() if cap else ''
    rows = []
    for m in re.finditer(r'\{\{shop(item|mon)\|((?:[^{}]|\{\{[^{}]*\}\})*)\}\}', block):
        pos, kw = split_params(m.group(2))
        if m.group(1) == 'mon':
            if len(pos) >= 3:
                rows.append(f'<tr><td>{pm(pos[0])} Lv.{e(kw.get("lv", ""))}</td><td>{e(pos[2])} 代币</td></tr>')
            continue
        if len(pos) < 2:
            continue
        name, price = pos[0], pos[1]
        cur = '代币' if len(pos) > 2 and pos[2] == 'C' else ''
        tm = re.match(r'(TM|HM)(\d+)', name)
        label_ = f'{"招式学习器" if tm.group(1) == "TM" else "秘传学习器"}{tm.group(2)}（{move(pos[-1])}）' if tm else item(kw.get('display') or name)
        rows.append(f'<tr><td>{label_}</td><td>{"₽" if not cur else ""}{e(price)}{" " + cur if cur else ""}</td></tr>')
    if not rows:
        return None
    cap_ = SHOP_LABEL.get(label, label) or '商店'
    return f'<table class="grid"><caption>{e(cap_)}</caption><tr><th>商品</th><th>价格</th></tr>{"".join(rows)}</table>'


CLASS = PEOPLE.get('_classes', {})


def trainer_table(block, keys):
    rows = []
    for m in re.finditer(r'\{\{[Tt]rainer(entry|div)\|([^{}]*)\}\}', block):
        pos, kw = split_params(m.group(2))
        if m.group(1) == 'div':
            if len(pos) > 1 and pos[1]:
                rows.append(f'<tr class="div"><th colspan="3">{e(inline(pos[1]))}</th></tr>')
            continue
        if len(pos) < 6:
            continue
        cls, name, prize, n = pos[1], pos[2], pos[3], pos[4]
        mons = []
        rest = pos[5:]
        for i in range(0, len(rest) - 4, 5):
            mons.append(f'{pm(rest[i + 1])} Lv.{e(rest[i + 3])}')
        pz = re.sub(r'<[^>]+>|-{4}', ' ', inline(prize)).split()
        money = pz[0] if pz else ''
        note = ' '.join(pz[1:])
        if note:
            k = nk(keys, 'M'); keys[k] = note
            note = '<br><small>{{' + k + '}}</small>'
        rows.append(f'<tr><td><b>{e(CLASS.get(cls, cls))}</b><br><small>{e(PEOPLE.get(name, name))}</small></td>'
                    f'<td>{"<br>".join(mons)}</td><td>₽{e(money)}{note}</td></tr>')
    if not rows:
        return None
    return '<table class="grid"><caption>训练家</caption><tr><th>训练家</th><th>宝可梦</th><th>奖金</th></tr>' + ''.join(rows) + '</table>'


def party_table(block):
    head = re.search(r'\{\{Party\s*\|((?:[^{}]|\{\{[^{}]*\}\})*)\}\}', block)
    if not head:
        return None
    _, kw = split_params(head.group(1))
    cls = inline(kw.get('class', '')); name = inline(kw.get('name', '')); prize = inline(kw.get('prize', ''))
    cards = []
    for m in re.finditer(r'\{\{Pokémon\s*\|((?:[^{}]|\{\{[^{}]*\}\})*)\}\}', block):
        _, k = split_params(m.group(1))
        moves = '、'.join(move(k[f'move{i}']) for i in range(1, 5) if k.get(f'move{i}'))
        held = item(k['held']) if k.get('held') and k['held'] != 'None' else ''
        aid = ABIL_ID.get(slugify(k.get('ability', '')))
        ab = data['abilities'].get(str(aid), k.get('ability', '')) if aid else k.get('ability', '')
        typ = ' / '.join(TYPE_ZH.get(k[t], k[t]) for t in ('type1', 'type2') if k.get(t))
        cards.append(f'<tr><td>{pm(k.get("pokemon", ""))}<br><small>Lv.{e(k.get("level", ""))} · {e(typ)}</small></td>'
                     f'<td>特性：{e(ab)}{"<br>携带：" + held if held else ""}<br>招式：{e(moves)}</td></tr>')
    if not cards:
        return None
    who = f'{CLASS.get(cls, cls)} {PEOPLE.get(name, name)}'.strip()
    if 'Silver' in kw.get('classlink', '') or 'Silver' in kw.get('name', ''):
        who = '劲敌（西尔弗）'
    if kw.get('caption'):
        who += f'（{re.sub(r"<[^>]+>", "", inline(kw["caption"]))}）'
    cap = f'<caption>{e(who)}{"　奖金 " + e(prize) if prize else ""}</caption>' if who else ''
    return (f'<table class="grid party">{cap}'
            f'<tr><th>宝可梦</th><th>详情</th></tr>{"".join(cards)}</table>')


def gym_table(block, keys):
    out = []
    t = trainer_table(block, keys)
    if t:
        out.append(t)
    p = party_table(block)
    if p:
        out.append(p)
    return '\n'.join(out) or None


def parse(w):
    """Yield ('h', level, text) / ('p', text) / ('t', html, kind) blocks."""
    w = re.sub(r'<!--.*?-->', '', w, flags=re.S)
    blocks, i, para = [], 0, []
    def flush():
        if para:
            txt = ' '.join(x.strip() for x in para).strip()
            if re.sub(r'\s', '', re.sub(r'<[^>]+>', '', txt)):
                blocks.append(('p', txt))
            para.clear()
    lines_buf = ''
    while i < len(w):
        if w.startswith('{|', i) or w.startswith('{{', i):
            j = take_block(w, i)
            blk = w[i:j]
            head = blk[:60].lower()
            if re.match(r'\{\{party\s*\n?\|', head):
                end = re.search(r'\{\{Party/end\}\}', w[j:], re.I)
                if end:
                    j = j + end.end()
                    blk = w[i:j]
            if blk.startswith('{|') or re.match(r'\{\{(party|walkthroughgym|walkthroughboss|pokémon\s*\n)', head):
                flush()
                blocks.append(('raw', blk))
                i = j
                continue
            if re.match(r'\{\{(walkthroughnotice|walkthroughprevnext|project walkthroughs notice|-)', head):
                i = j
                continue
            para.append(blk)
            i = j
            continue
        nl = w.find('\n', i)
        nl = len(w) if nl < 0 else nl
        line = w[i:nl]
        i = nl + 1
        m = re.match(r'^(={2,5})\s*(.*?)\s*\1\s*$', line)
        if m:
            flush(); blocks.append(('h', len(m.group(1)), m.group(2))); continue
        if not line.strip():
            flush(); continue
        if line.startswith(('*', '#', ':')):
            flush(); blocks.append(('li', line.lstrip('*#: ').strip())); continue
        para.append(line)
    flush()
    return blocks


def nk(keys, prefix):
    return f'{prefix}{1 + sum(1 for k in keys if re.match(prefix + r"\d+$", k))}'


def split_top(s, sep):
    out, depth, cur, i = [], 0, '', 0
    while i < len(s):
        if s.startswith('{{', i) or s.startswith('[[', i):
            depth += 1; cur += s[i:i + 2]; i += 2; continue
        if s.startswith('}}', i) or s.startswith(']]', i):
            depth -= 1; cur += s[i:i + 2]; i += 2; continue
        if depth == 0 and s.startswith(sep, i):
            out.append(cur); cur = ''; i += len(sep); continue
        cur += s[i]; i += 1
    out.append(cur)
    return out


def render_wikitable(block, keys, cprefix='C'):
    """Render plain wikitables (innermost ones) as HTML; English cells become C-keys."""
    inner = []
    def grab(b):
        body = b[2:-2] if b.startswith('{|') else b
        if re.search(r'(?m)^[ \t]*\{\|', body):
            i = 0
            while True:
                m = re.search(r'(?m)^[ \t]*\{\|', body[i:])
                if not m:
                    break
                st = i + m.start() + (len(m.group(0)) - 2)
                en = take_block(body, st)
                grab(body[st:en]); i = en
        else:
            inner.append(b)
    grab(block)
    html_out = []
    m = re.match(r'\{\|[^\n]*\n\|-[^\n]*\n!([^\n]*)\n\|-[^\n]*\n\|(.*)\n\|\}\s*$', block, re.S)
    if m and not re.search(r'(?m)^\s*\{\|', m.group(2)) and re.search(r'==|\n\n|----|\{\{Pokémon', m.group(2)):
        head = re.sub(r'<[^>]+>', '', inline(split_top(m.group(1), '|')[-1])).strip()
        body = m.group(2)
        parts = split_top(body.split('\n', 1)[0], '|')
        if len(parts) > 1 and '=' in parts[0]:
            body = '|'.join(parts[1:]) + ('\n' + body.split('\n', 1)[1] if '\n' in body else '')
        body = body.replace('----', '\n\n')
        k = nk(keys, 'X'); keys[k] = head
        return f'<div class="box"><h4>{{{{{k}}}}}</h4>' + convert(body, keys, nested=True) + '</div>'
    for t in inner:
        rows, cur = [], []
        lines = t[2:-2].split('\n')[1:]
        for line in lines:
            ls = line.strip()
            if ls.startswith('|-'):
                if cur:
                    rows.append(cur)
                cur = []
                continue
            if ls.startswith('|+'):
                continue
            if ls.startswith('!') or ls.startswith('|'):
                tag = 'th' if ls.startswith('!') else 'td'
                for c in split_top(ls[1:], '!!' if tag == 'th' else '||'):
                    parts = split_top(c, '|')
                    attrs, content = (parts[0], '|'.join(parts[1:])) if len(parts) > 1 and '=' in parts[0] else ('', c)
                    span = ''.join(f' {k}="{v}"' for k, v in re.findall(r'(colspan|rowspan)="?(\d+)', attrs))
                    cur.append((tag, span, content.strip()))
            elif cur:
                tag, span, content = cur[-1]
                cur[-1] = (tag, span, content + ' ' + ls)
        if cur:
            rows.append(cur)
        trs = []
        for r in rows:
            cells = []
            for tag, span, content in r:
                txt = inline(content)
                plain = re.sub(r'<[^>]+>', '', txt).strip()
                if plain.lower() in PM_EN:
                    txt = pm(plain)
                elif plain in TYPE_ZH:
                    txt = TYPE_ZH[plain]
                elif re.search(r'[A-Za-z]{3,}', plain):
                    k = nk(keys, cprefix)
                    keys[k] = txt
                    txt = '{{' + k + '}}'
                cells.append(f'<{tag}{span}>{txt}</{tag}>')
            if any(re.sub(r'<[^>]+>', '', c) for c in cells):
                trs.append('<tr>' + ''.join(cells) + '</tr>')
        if trs:
            html_out.append('<table class="grid">' + ''.join(trs) + '</table>')
    return '\n'.join(html_out) or None


def convert(w, keys, nested=False):
    w = re.sub(r'</?div[^>]*>', '', w)
    w = re.sub(r'\{\{shop\|((?:[^{}]|\{\{(?:[^{}]|\{\{[^{}]*\}\})*\}\})*)\}\}(.*?)\{\{shopfooter[^{}]*\}\}',
               lambda m: '\n{|\n! SHOP:' + m.group(1) + '\n' + m.group(2) + '\n|}\n', w, flags=re.S)
    out = []
    HP, PP = ('X', 'X') if nested else ('H', 'P')
    for b in parse(w):
        if b[0] == 'h':
            t = inline(b[2])
            k = nk(keys, HP); keys[k] = t
            out.append(f'<h{2 if b[1] <= 2 else 3}>{{{{{k}}}}}</h{2 if b[1] <= 2 else 3}>')
        elif b[0] in ('p', 'li'):
            t = inline(b[1])
            if not re.sub(r'<[^>]+>|\s', '', t):
                continue
            k = nk(keys, PP); keys[k] = t
            out.append(f'<p>{{{{{k}}}}}</p>' if b[0] == 'p' else f'<ul><li>{{{{{k}}}}}</li></ul>')
        else:
            blk = b[1]
            low = blk.lower()
            html_ = None
            if 'catch/entryhs' in low:
                html_ = catch_table(blk, keys)
            elif 'itemlist' in low:
                html_ = item_table(blk, keys, 'X' if nested else 'D')
            elif 'shopitem' in low or 'shopmon' in low:
                html_ = shop_table(blk)
            elif 'walkthroughgym' in low or 'walkthroughboss' in low:
                html_ = gym_table(blk, keys)
            elif 'trainerentry' in low:
                html_ = trainer_table(blk, keys)
            elif low.startswith('{{party'):
                html_ = party_table(blk)
            elif low.startswith('{{pokémon'):
                html_ = party_table('{{Party|class=|name=|prize=}}\n' + blk)
            if html_:
                out.append(html_)
            elif blk.startswith('{|') and (html_ := render_wikitable(blk, keys, 'X' if nested else 'C')):
                out.append(html_)
            elif blk.startswith('{|'):
                txt = inline(re.sub(r'^\{\||\|\}$|^[!|].*?\|(?=[^|])', '', blk, flags=re.M))
                txt = re.sub(r'\n\s*\|-.*', '', txt)
                cells = [c.strip() for c in re.split(r'\n\s*[!|]+\s*', txt) if c.strip() and not c.strip().startswith(('style=', 'class='))]
                if cells:
                    k = nk(keys, PP); keys[k] = ' / '.join(cells)
                    out.append(f'<p class="note">{{{{{k}}}}}</p>')
    return '\n'.join(out)


def folder(slug):
    return SITE / 'src' / 'guides-tr' / slug


def draft(slug, n):
    src = json.loads((folder(slug) / 'source' / f'part-{n}.json').read_text(encoding='utf-8'))
    keys = {}
    body = convert(src['parse']['wikitext']['*'], keys)
    (folder(slug) / 'source' / f'part-{n}.body.html').write_text(body, encoding='utf-8')
    zh = folder(slug) / 'zh' / f'part-{n}.txt'
    done = {}
    if zh.exists():
        for line in zh.read_text(encoding='utf-8').splitlines():
            m = re.match(r'^([A-Z]\d+):\s?(.*)$', line)
            if m:
                done[m.group(1)] = m.group(2)
    for k, v in keys.items():
        if k not in done:
            print(f'{k}: {re.sub(r"<[^>]+>", "", v)}')


def build(slug, titles):
    g = json.loads((folder(slug) / 'guide.json').read_text(encoding='utf-8'))
    meta, pages = {}, []
    for n in range(1, len(titles) + 1):
        src = json.loads((folder(slug) / 'source' / f'part-{n}.json').read_text(encoding='utf-8'))
        keys = {}
        body = convert(src['parse']['wikitext']['*'], keys)
        zh = {}
        zf = folder(slug) / 'zh' / f'part-{n}.txt'
        if not zf.exists():
            continue
        for line in zf.read_text(encoding='utf-8').splitlines():
            m = re.match(r'^([A-Z]\d+):\s?(.*)$', line)
            if m:
                zh[m.group(1)] = m.group(2)
        kf = folder(slug) / 'source' / f'part-{n}.keys.json'
        if kf.exists():
            prev = json.loads(kf.read_text(encoding='utf-8'))
            moved = [k for k in keys if k in prev and prev[k] != keys[k]]
            if moved:
                print(f'part {n}: WARNING source text changed for {moved[:5]} - check translations still line up')
        kf.write_text(json.dumps(keys, ensure_ascii=False, indent=0), encoding='utf-8')
        missing = [k for k in keys if k not in zh]
        if missing:
            print(f'part {n}: {len(missing)} untranslated keys, e.g. {missing[:5]}')
        body = re.sub(r'\{\{([A-Z]\d+)\}\}', lambda m: zh.get(m.group(1), keys.get(m.group(1), '')), body)
        body = re.sub(r'<h([23])></h\1>|<p></p>|<ul><li></li></ul>|<th colspan="3"></th>', '', body)
        info = {'title': titles[n - 1][0], 'chapter': titles[n - 1][1]}
        (folder(slug) / f'part-{n}.html').write_text(f'<!--{json.dumps(info, ensure_ascii=False)}-->\n{body}\n', encoding='utf-8')
        pages.append(f'part-{n}')
        p = src['parse']
        meta[f'part-{n}'] = {'title': p['title'], 'revid': p['revid'], 'timestamp': src.get('timestamp', '')}
    g['pages'] = pages
    g['total'] = f'已翻译 {len(pages)} / {len(titles)} 节' if len(pages) < len(titles) else f'全部 {len(titles)} 节'
    (folder(slug) / 'guide.json').write_text(json.dumps(g, ensure_ascii=False, indent=1), encoding='utf-8')
    (folder(slug) / 'source' / 'meta.json').write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding='utf-8')
    (folder(slug) / 'source' / 'images.json').write_text('{}', encoding='utf-8')
    (folder(slug) / 'source' / 'used.json').write_text(json.dumps({'pm': sorted(USED_PM), 'items': sorted(USED_ITEM)}), encoding='utf-8')
    print('built', len(pages), 'parts; sprites', len(USED_PM), 'items', len(USED_ITEM))


if __name__ == '__main__':
    if sys.argv[1] == 'draft':
        draft(sys.argv[2], int(sys.argv[3]))
    else:
        titles = json.loads((folder(sys.argv[2]) / 'titles.json').read_text(encoding='utf-8'))
        build(sys.argv[2], titles)
