#!/usr/bin/env python3
"""构建无需联网的图鉴。仅标准库；上游固定提交，禁止覆盖成品。
python3 outputs/build-eli-pokedex-v1.py --cache /tmp/eli-pokedex-source
原始 CSV 与图像来自 PokéAPI，不抓取商业 App，不运行上游代码。
"""
import argparse, base64, collections, csv, datetime, html, itertools, json, pathlib, re, runpy, urllib.request
ROOT=pathlib.Path(__file__).resolve().parent
L=runpy.run_path(str(ROOT/'eli-pokedex-localization-v1.py'))
SHA='6b8db7f3cb31cfaa37cb74e5c3edff124bcba5ce'
SPRITE_SHA='1dd55c0436d2a5b6e324c0b780e1b1b416fbfb64'
VERSION_IDS=set(L['VERSIONS'])

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--cache',default='/tmp/eli-pokedex-source');args=ap.parse_args();cache=pathlib.Path(args.cache);(cache/'csv').mkdir(parents=True,exist_ok=True);(cache/'sprites').mkdir(exist_ok=True)
    for meta,expected in [('commit.json',SHA),('sprites-commit.json',SPRITE_SHA)]:
        if (cache/meta).exists() and json.loads((cache/meta).read_text()).get('sha')!=expected:raise ValueError('Source cache revision mismatch: '+meta)
    def fetch(url,path):
        if not path.exists():path.write_bytes(urllib.request.urlopen(url,timeout=60).read())
        return path
    def rows(n):
        p=fetch(f'https://raw.githubusercontent.com/PokeAPI/pokeapi/{SHA}/data/v2/csv/{n}.csv',cache/'csv'/(n+'.csv'))
        with p.open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f))
    def ix(n,key='id'):return {int(r[key]):r for r in rows(n)}
    def names(n,key,lang=12,col='name'):
        result={}
        for language in [9,4,lang]:
            for r in rows(n):
                if int(r['local_language_id'])==language and r[col]:result[int(r[key])]=r[col]
        return result
    species=ix('pokemon_species');pokemon=ix('pokemon');s_names=names('pokemon_species_names','pokemon_species_id');traditional=names('pokemon_species_names','pokemon_species_id',4);english=names('pokemon_species_names','pokemon_species_id',9);genus=names('pokemon_species_names','pokemon_species_id',12,'genus');t_names=names('type_names','type_id');a_names=names('ability_names','ability_id');item_names=names('item_names','item_id');move_names=names('move_names','move_id');loc=ix('locations');areas=ix('location_areas');loc_zh={int(r['location_id']):r['name'] for r in rows('location_names') if r['local_language_id']=='12'}
    version_groups=ix('version_groups');versions_raw=ix('versions');ability_defs=ix('abilities');type_defs=ix('types');items=ix('items');item_slug={r['identifier']:item_names.get(i,r['identifier']) for i,r in items.items()};species_slug={r['identifier']:s_names.get(i,r['identifier']) for i,r in species.items()};forms=rows('pokemon_forms');f_names=names('pokemon_form_names','pokemon_form_id',12,'form_name');form_names={int(f['pokemon_id']):f_names[int(f['id'])] for f in forms if int(f['id']) in f_names and f_names[int(f['id'])]}
    # 中文名称优先，不确定的地方保留原始标识，绝不杜撰地点。
    unknown_locs=set();unknown_areas=set();unknown_conditions=set()
    def location_name(i):
        r=loc[i];slug=r['identifier'];region=int(r['region_id'] or 0)
        if slug in L['LOCATIONS']:return L['LOCATIONS'][slug]
        m=re.search(r'(?:sea-)?route-(\d+)$',slug)
        if m:return m[1]+'号道路'
        if 'victory-road' in slug:return '冠军之路'
        if 'safari-zone' in slug:return '狩猎地带'
        if 'altering-cave' in slug:return '变化洞穴'
        if 'pokemon-league' in slug:return '宝可梦联盟'
        if slug.startswith('roaming-'):return L['REGIONS'].get(region,'地区')+'游走（非固定地点）'
        if 'pokecenter' in slug:return '宝可梦中心'
        if 'pokemart' in slug:return '友好商店'
        if slug.endswith('-chamber') and i in range(491,498):return '阿斯卡纳遗迹·石室（'+slug.split('-')[0].capitalize()+'）'
        if i in loc_zh:return loc_zh[i].translate(str.maketrans('０１２３４５６７８９','0123456789'))
        unknown_locs.add(slug);return '地点待译（'+slug+'）'
    direction={'north':'北侧','south':'南侧','east':'东侧','west':'西侧','north-east':'东北侧','south-east':'东南侧','north-west':'西北侧','south-west':'西南侧'}
    def area_name(slug):
        if not slug:return '主区域'
        if slug in L['AREAS']:return L['AREAS'][slug]
        if re.fullmatch(r'[a-i]',slug):return '分区'+slug.upper()
        if re.fullmatch(r'\d+f',slug):return slug[:-1]+'层'
        if re.fullmatch(r'b\d+f',slug):return '地下'+slug[1:-1]+'层'
        if re.fullmatch(r'(?:area|room|pillar)-\d+',slug):
            a,b=slug.split('-');return {'area':'分区','room':'房间','pillar':'柱子'}[a]+b
        if slug.startswith('unknown-area-'):return '分区未确定（源编号'+slug.split('-')[-1]+'）'
        if slug in ['0-9-different-unown-caught','10-25-different-unown-caught','26-plus-different-unown-caught']:return {'0':'已捕获0–9种未知图腾','10':'已捕获10–25种未知图腾','26':'已捕获26种以上未知图腾'}[slug.split('-')[0]]
        if slug.startswith('hidden-grotto-'):return '隐藏洞穴·'+area_name(slug[14:])
        if slug in ['grass','bug','dark','dragon','electric','fairy','fighting','fire','flying','ghost','ground','ice','normal','poison','psychic','rock','steel']:
            ids={r['identifier']:i for i,r in type_defs.items()};return t_names[ids[slug]]+'属性区'
        m=re.match(r'route-(\d+)$',slug)
        if m:return m[1]+'号道路侧'
        for prefix,label in [('north-towards-','北侧往'),('south-towards-','南侧往'),('east-towards-','东侧往'),('west-towards-','西侧往')]:
            if slug.startswith(prefix):return label+L['LOCATIONS'].get(slug[len(prefix):],slug[len(prefix):])
        for dr,label in sorted(direction.items(),key=lambda x:-len(x[0])):
            prefix=dr+'-of-'
            if slug.startswith(prefix):
                target=slug[len(prefix):];rm=re.match(r'route-(\d+)$',target)
                cn=rm[1]+'号道路' if rm else L['LOCATIONS'].get(target)
                if cn:return cn+label
        replacements={'leftmost-room':'最左房间','rightmost-room':'最右房间','left-room':'左侧房间','right-room':'右侧房间','middle-room':'中间房间','private-room':'独立房间','small-room':'小房间','unknown-room':'房间未确定','from-exterior':'室外入口侧','cave-behind-team-rocket':'火箭队后方洞穴','top':'上部','left':'左侧','right':'右侧','cave':'洞穴','gate':'入口','pond':'池塘','shrine':'神社','stairs':'台阶','dark-grass':'深色草丛','inner-area':'内侧区域','outer-area':'外侧区域','near-youngster':'短裤小子附近','near-pokemon-breeder':'宝可梦培育家附近','upper-cave':'上层洞窟','lower-cave':'下层洞窟','east-cave':'东侧洞窟','cave-gate':'洞穴入口','forest-cave':'林中洞穴','farthest-hollow':'最深处洞穴','dining-room':'餐厅','department-store-5f':'百货商店5层','silph-co':'西尔佛公司','silph-co-7f':'西尔佛公司7层','game-freak-hq-1f':'GAME FREAK办公室1层','pwt-entrance':'宝可梦世界锦标赛入口','lighthouse-basement':'灯塔地下','before-pillar-1':'第1根柱子前','between-pillars-1-and-2':'第1、2根柱子之间','between-pillars-2-and-3':'第2、3根柱子之间','after-pillar-3':'第3根柱子后','poni-island-reached':'已抵达波尼岛','ulaula-island-reached':'已抵达乌拉乌拉岛','huntail-boat':'猎斑鱼船','se':'东南部','sw':'西南部','backsmall-room':'后方小房间','southwest-house':'西南方小屋','north-west-house':'西北方小屋'}
        if slug in replacements:return replacements[slug]
        m=re.match(r'((?:b)?\d+f)-(.*)',slug)
        if m:
            rest=m[2];return area_name(m[1])+'·'+(replacements.get(rest) or area_name(rest))
        m=re.match(r'interior-([a-d])$',slug)
        if m:return '内部'+m[1].upper()+'区'
        if slug=='b1f-3f':return '地下1层至3层'
        if slug in ['1fsmall-room','1f-unknown-room']:return '1层小房间' if slug.startswith('1fsmall') else '1层未定房间'
        for prefix in ['inside-','north-','south-','east-','west-']:
            if slug.startswith(prefix):return {'inside-':'内部·','north-':'北侧·','south-':'南侧·','east-':'东侧·','west-':'西侧·'}[prefix]+area_name(slug[len(prefix):])
        if slug in L['LOCATIONS']:return L['LOCATIONS'][slug]+'侧'
        unknown_areas.add(slug);return '分区（'+slug+'）'
    conditions_raw=ix('encounter_condition_values');condition_map=collections.defaultdict(list)
    for r in rows('encounter_condition_value_map'):condition_map[int(r['encounter_id'])].append(int(r['encounter_condition_value_id']))
    def condition_name(slug):
        if slug in L['CONDITIONS']:return L['CONDITIONS'][slug]
        if slug.startswith('coins-'):return '需'+slug[6:]+'枚游戏币'
        if slug.startswith('trade-') and slug[6:] in species_slug:return '用'+species_slug[slug[6:]]+'交换'
        if slug.startswith('starter-') and slug[8:] in species_slug:return '最初选择'+species_slug[slug[8:]]
        if slug.startswith('item-') and slug[5:] in item_slug:return '需要'+item_slug[slug[5:]]
        if slug.startswith('slot2-'):
            cn={'ruby':'红宝石','sapphire':'蓝宝石','emerald':'绿宝石','firered':'火红','leafgreen':'叶绿'}[slug[6:]];return '双插《'+cn+'》（3DS无GBA卡槽）'
        if slug.startswith('weekday-'):return '星期'+{'sunday':'日','monday':'一','tuesday':'二','wednesday':'三','thursday':'四','friday':'五','saturday':'六'}[slug[8:]]
        if slug.startswith('season-'):return {'spring':'春季','summer':'夏季','autumn':'秋季','winter':'冬季'}[slug[7:]]
        if slug.startswith('time-'):
            t=slug[5:];time_map={'morning':'清晨','day':'白天','night':'夜晚','minute-00-to-19':'当前小时第00–19分钟','minute-20-to-39':'当前小时第20–39分钟','minute-40-to-59':'当前小时第40–59分钟','04-00-to-19-59':'游戏时间04:00–19:59','20-00-to-21-59':'游戏时间20:00–21:59','21-00-to-03-59':'游戏时间21:00–03:59'}
            if t in time_map:return time_map[t]
        m=re.fullmatch(r'johto-safari-blocks-(plains|forest|peak|water)-min-(\d+)',slug)
        if m:return '狩猎区'+{'plains':'草原','forest':'森林','peak':'岩山','water':'水边'}[m[1]]+'类有效点数≥'+m[2]+'（含天数加成）'
        m=re.fullmatch(r'great-marsh-daily-slot-(\d+)-of-32',slug)
        if m:return '每日更换抽选（'+m[1]+'/32名额）'
        unknown_conditions.add(slug);return '条件待译（'+slug+'）'
    stats=collections.defaultdict(dict);types=collections.defaultdict(list);abilities=collections.defaultdict(dict)
    for r in rows('pokemon_stats'):
        if int(r['stat_id'])<=6:stats[int(r['pokemon_id'])][int(r['stat_id'])]=int(r['base_stat'])
    for r in rows('pokemon_types'):types[int(r['pokemon_id'])].append((int(r['slot']),int(r['type_id'])))
    for r in rows('pokemon_abilities'):abilities[int(r['pokemon_id'])][int(r['slot'])]=(int(r['ability_id']),bool(int(r['is_hidden'])))
    past_stats=collections.defaultdict(list);past_types=collections.defaultdict(list);past_abilities=collections.defaultdict(list)
    for table,out in [('pokemon_stats_past',past_stats),('pokemon_types_past',past_types),('pokemon_abilities_past',past_abilities)]:
        for r in rows(table):out[int(r['pokemon_id'])].append(r)
    def by_generation(pid,g):
        st=stats[pid].copy()
        for stat in range(1,7):
            candidates=[r for r in past_stats[pid] if int(r['stat_id'])==stat and int(r['generation_id'])>=g and r['base_stat']]
            if candidates:st[stat]=int(min(candidates,key=lambda r:int(r['generation_id']))['base_stat'])
        ty=types[pid]
        candidates=[r for r in past_types[pid] if int(r['generation_id'])>=g]
        if candidates:
            pg=min(int(r['generation_id']) for r in candidates);ty=[(int(r['slot']),int(r['type_id'])) for r in candidates if int(r['generation_id'])==pg]
        ab=abilities[pid].copy()
        for slot in [1,2,3]:
            candidates=[r for r in past_abilities[pid] if int(r['slot'])==slot and int(r['generation_id'])>=g]
            if candidates:
                r=min(candidates,key=lambda r:int(r['generation_id']));ab[slot]=(int(r['ability_id'] or 0),bool(int(r['is_hidden'])))
        return {'s':[st.get(i,0) for i in range(1,7)],'t':[x[1] for x in sorted(ty)],'a':[[a,int(h)] for slot,(a,h) in sorted(ab.items()) if a and int(ability_defs[a]['generation_id'])<=g]}
    descriptions={}
    for r in rows('pokemon_species_flavor_text'):
        if r['language_id']=='12' and int(r['species_id'])<=807:descriptions[int(r['species_id'])]=' '.join(r['flavor_text'].replace('\f',' ').split())
    evo=collections.defaultdict(set)
    for r in rows('pokemon_evolution'):
        child=int(r['evolved_species_id']);vg=version_groups.get(int(r['version_group_id'] or 0));ef=int(r['evolved_pokemon_form_id'] or 0)
        if child>807 or (vg and int(vg['generation_id'])>7) or ef>=10000:continue
        trigger=int(r['evolution_trigger_id']);pieces=[]
        if r['minimum_level']:pieces.append('Lv.'+r['minimum_level'])
        if trigger==2:pieces.append('通信交换')
        if r['trigger_item_id']:pieces.append('使用'+item_names[int(r['trigger_item_id'])])
        if r['held_item_id']:pieces.append('携带'+item_names[int(r['held_item_id'])])
        if r['gender_id']:pieces.append({'1':'雌性','2':'雄性','3':'无性别'}.get(r['gender_id'],'性别条件'))
        if r['minimum_happiness']:pieces.append('高亲密度')
        if r['minimum_affection']:pieces.append('友好度达标')
        if r['minimum_beauty']:pieces.append('美丽度达标')
        if r['time_of_day']:pieces.append({'day':'白天','night':'夜晚','dusk':'黄昏'}.get(r['time_of_day'],'特定时段'))
        if r['known_move_id']:pieces.append('学会'+move_names.get(int(r['known_move_id']),'指定招式'))
        if r['known_move_type_id']:pieces.append('学会'+t_names[int(r['known_move_type_id'])]+'属性招式')
        if r['near_special_rock']=='1':pieces.append('特殊岩石附近')
        elif r['location_id']:pieces.append('特定地点')
        if r['relative_physical_stats']:pieces.append({'-1':'攻击＜防御','0':'攻击＝防御','1':'攻击＞防御'}[r['relative_physical_stats']])
        if r['party_species_id']:pieces.append('同行有'+s_names[int(r['party_species_id'])])
        if r['party_type_id']:pieces.append('同行有'+t_names[int(r['party_type_id'])]+'属性宝可梦')
        if r['trade_species_id']:pieces.append('与'+s_names[int(r['trade_species_id'])]+'互换')
        if r['needs_overworld_rain']=='1':pieces.append('地图下雨')
        if r['turn_upside_down']=='1':pieces.append('倒置主机')
        if r['region_id']:pieces.append('特定地区形态')
        if trigger==1:pieces.append('升级')
        if trigger not in [1,2,3]:pieces.append('特殊进化，按作品核对')
        evo[child].add('＋'.join(pieces) or '特殊条件')
    mons=[]
    for i in range(1,808):
        s=species[i];p=pokemon[i];gen=int(s['generation_id']);blob=fetch(f'https://raw.githubusercontent.com/PokeAPI/sprites/{SPRITE_SHA}/sprites/pokemon/{i}.png',cache/'sprites'/f'{i}.png').read_bytes();assert blob.startswith(b'\x89PNG')
        mons.append({'id':i,'n':s_names[i],'en':english[i],'slug':s['identifier'],'gen':gen,'genus':genus.get(i,''),'desc':descriptions.get(i,''),'h':int(p['height'])/10,'w':int(p['weight'])/10,'parent':int(s['evolves_from_species_id'] or 0),'chain':int(s['evolution_chain_id']),'evo':sorted(evo[i]),'alias':L['ALIASES'].get(i,[])+([traditional[i]] if traditional.get(i)!=s_names[i] else []),'g':{str(g):by_generation(i,max(gen,g)) for g in range(3,8)},'img':'data:image/png;base64,'+base64.b64encode(blob).decode()})
    slots=ix('encounter_slots');raw=[r for r in rows('encounters') if int(r['version_id']) in VERSION_IDS and int(pokemon[int(r['pokemon_id'])]['species_id'])<=807]
    groups={};used_conditions=set();used_areas=set();raw_count_by_version=collections.Counter()
    for r in raw:
        pid=int(r['pokemon_id']);sid=int(pokemon[pid]['species_id']);v=int(r['version_id']);aid=int(r['location_area_id']);slotid=int(r['encounter_slot_id']);slot=slots[slotid];mid=int(slot['encounter_method_id']);cond=tuple(sorted(set(condition_map[int(r['id'])])));key=(sid,v,aid,mid,cond,pid);raw_count_by_version[v]+=1;used_conditions.update(cond);used_areas.add(aid)
        if key not in groups:groups[key]={'min':int(r['min_level']),'max':int(r['max_level']),'slots':{}}
        group=groups[key];group['min']=min(group['min'],int(r['min_level']));group['max']=max(group['max'],int(r['max_level']));group['slots'][slotid]=int(slot['rarity'] or 0)
    encounters=collections.defaultdict(list);used_methods=set();uncertain_pools=0
    # 常规遇敌先重建条件下的槽位，再消去不影响结果的条件。
    # 复杂机制与冲突数据不换算概率，不发布伪百分比。
    probability_methods=set(range(1,18))|{22,23,24,27,31}
    pools=collections.defaultdict(list)
    for r in raw:
        pid=int(r['pokemon_id']);sid=int(pokemon[pid]['species_id']);slotid=int(r['encounter_slot_id']);mid=int(slots[slotid]['encounter_method_id']);cond=frozenset(condition_map[int(r['id'])]);pools[(int(r['version_id']),int(r['location_area_id']),mid)].append((sid,pid,slotid,int(r['min_level']),int(r['max_level']),cond))
    def emit(sid,pid,v,aid,mid,low,high,chance,cond):
        form='' if pid==sid else form_names.get(pid) or ('阿罗拉的样子' if 'alola' in pokemon[pid]['identifier'] else '特殊形态：'+pokemon[pid]['identifier'])
        encounters[sid].append([v,aid,mid,low,high,chance,sorted(cond),form]);used_methods.add(mid)
    def simplify(contexts,domains,droppable):
        cubes=set(contexts)
        while True:
            before=cubes.copy()
            for axis,domain in enumerate(domains):
                if axis not in droppable:continue
                grouped=collections.defaultdict(set)
                for cube in cubes:
                    key=list(cube);key[axis]=None;grouped[tuple(key)].add(cube[axis])
                new=set()
                for key,values in grouped.items():
                    if None in values or values==set(domain):new.add(key)
                    else:
                        for value in values:
                            cube=list(key);cube[axis]=value;new.add(tuple(cube))
                cubes=new
            if cubes==before:return cubes
    for (v,aid,mid),pool in pools.items():
        axes=collections.defaultdict(set);safe=mid in probability_methods
        for _,_,_,_,_,cond in pool:
            for c in cond:
                if c>20:safe=False
                axes[int(conditions_raw[c]['encounter_condition_id'])].add(c)
        axis_ids=sorted(axes);domains=[tuple(sorted(axes[a])) for a in axis_ids]
        droppable={i for i,a in enumerate(axis_ids) if axes[a]=={c for c,r in conditions_raw.items() if c<=20 and int(r['encounter_condition_id'])==a}}
        contexts=list(itertools.product(*domains)) if safe else []
        if len(contexts)>128:safe=False
        outcomes=collections.defaultdict(lambda:collections.defaultdict(set))
        if safe:
            for context in contexts:
                active=[r for r in pool if r[5].issubset(context)];occupied=collections.defaultdict(set)
                for sid,pid,slotid,low,high,cond in active:occupied[slotid].add(pid)
                if any(len(ids)>1 for ids in occupied.values()) or sum(int(slots[i]['rarity'] or 0) for i in occupied)>100:
                    safe=False;break
                by_mon=collections.defaultdict(list)
                for r in active:by_mon[(r[0],r[1])].append(r)
                for (sid,pid),rr in by_mon.items():
                    unique={r[2] for r in rr};chance=sum(int(slots[i]['rarity'] or 0) for i in unique) or None
                    outcomes[(sid,pid)][(min(r[3] for r in rr),max(r[4] for r in rr),chance)].add(context)
        if safe:
            for (sid,pid),variants in outcomes.items():
                for (low,high,chance),contexts_for_result in variants.items():
                    for cube in simplify(contexts_for_result,domains,droppable):emit(sid,pid,v,aid,mid,low,high,chance,[c for c in cube if c is not None])
        else:
            uncertain_pools+=1
            per_mon=collections.defaultdict(list)
            for sid,pid,slotid,low,high,cond in pool:per_mon[(sid,pid,tuple(sorted(cond)))].append((low,high))
            for (sid,pid,cond),rr in per_mon.items():emit(sid,pid,v,aid,mid,min(x[0] for x in rr),max(x[1] for x in rr),None,cond)
    for sid in encounters:encounters[sid].sort(key=lambda x:(x[0],x[1],x[2],x[6]))
    area_data={}
    for aid in sorted(used_areas):
        a=areas[aid];lid=int(a['location_id']);region=int(loc[lid]['region_id'] or 0);area_data[aid]=[lid,location_name(lid),area_name(a['identifier']),region,loc[lid]['identifier'],a['identifier']]
    condition_data={i:condition_name(conditions_raw[i]['identifier']) for i in sorted(used_conditions)}
    version_data=[]
    for vid in L['VERSIONS']:
        vg=version_groups[int(versions_raw[vid]['version_group_id'])];generation=int(vg['generation_id']);records=[r for sid,rr in encounters.items() for r in rr if r[0]==vid];species_with={sid for sid,rr in encounters.items() if any(r[0]==vid for r in rr)}
        version_data.append({'id':vid,'n':L['VERSIONS'][vid],'gen':generation,'vg':int(vg['id']),'platform':{3:'GBA',4:'NDS',5:'NDS',6:'3DS',7:'3DS'}[generation],'species':len(species_with),'locations':len({area_data[r[1]][0] for r in records}),'rows':len(records),'note':'地点资料明显不全：主要收录定点、赠送等，普通野外地点仍待补。' if vid in [25,26] else ('部分特殊区域与条件可能尚未完整收录。' if generation>=6 else '')})
    licence=fetch(f'https://raw.githubusercontent.com/PokeAPI/pokeapi/{SHA}/LICENSE.md',cache/'POKEAPI-LICENSE.txt').read_text()
    sprite_licence=fetch(f'https://raw.githubusercontent.com/PokeAPI/sprites/{SPRITE_SHA}/LICENCE.txt',cache/'SPRITES-LICENCE.txt').read_text()
    data={'meta':{'builtAt':datetime.datetime.now(datetime.timezone.utc).date().isoformat(),'commit':SHA,'spritesCommit':SPRITE_SHA,'rawEncounters':len(raw),'groupedEncounters':sum(len(rr) for rr in encounters.values()),'uncertainPools':uncertain_pools,'scope':'前7世代807种；GBA／NDS／3DS共22版本。基础资料为默认形态；地点另注地区形态。非完整活动与联机攻略。','license':licence,'spriteLicense':sprite_licence,'probabilityNote':'概率仅指满足所列条件、触发对应遇敌方式后的占比，不是每走一步的概率。不同条件不能相加。复杂机制（如SOS、群聚、隐藏洞穴、涂蜜树）不强行合并概率，以「—」表示未可靠换算，不是0%。赠送、定点和交换不代表自动获得。','nameNote':'采用现行中文名。地点中文做了人工对照；旧汉化名称可能不同，未确定的分区明确注明。','untranslated':{'locations':sorted(unknown_locs),'areas':sorted(unknown_areas),'conditions':sorted(unknown_conditions)}},'pokemon':mons,'versions':version_data,'areas':area_data,'conditions':condition_data,'methods':{i:L['METHODS'].get(i,'方式待补（'+str(i)+'）') for i in used_methods},'encounters':encounters,'types':{i:{'n':t_names[i],'gen':int(r['generation_id'])} for i,r in type_defs.items() if 1<=i<=18},'abilities':a_names,'regions':L['REGIONS'],'efficacy':[[int(r['damage_type_id']),int(r['target_type_id']),int(r['damage_factor'])] for r in rows('type_efficacy')],'efficacyPast':[[int(r['damage_type_id']),int(r['target_type_id']),int(r['damage_factor']),int(r['generation_id'])] for r in rows('type_efficacy_past')]}
    for name in ['eli-pokedex-data-v1.json','eli-pokedex-v1.html','eli-pokedex-sources-v1.txt']:
        if (ROOT/name).exists():raise FileExistsError('Refusing to overwrite '+name)
    compact=json.dumps(data,ensure_ascii=False,separators=(',',':'))
    (ROOT/'eli-pokedex-data-v1.json').write_text(compact+'\n')
    template=(ROOT/'eli-pokedex-template-v1.html').read_text();js=(ROOT/'eli-pokedex-app-v1.js').read_text();page=template.replace('/*__APP__*/',js).replace('__DATA_JSON__',compact.replace('<','\\u003c'))
    assert '__DATA_JSON__' not in page and '/*__APP__*/' not in page
    (ROOT/'eli-pokedex-v1.html').write_text(page)
    (ROOT/'eli-pokedex-sources-v1.txt').write_text(f'Eli 宝可梦图鉴\n构建：{data["meta"]["builtAt"]}\n\n功能参考而非复制：口袋图鉴 App Store https://apps.apple.com/cn/app/id6755204960\n数据：PokéAPI，固定提交 {SHA}\nhttps://github.com/PokeAPI/pokeapi/tree/{SHA}/data/v2/csv\n精灵图：PokéAPI sprites，固定提交 {SPRITE_SHA}\nhttps://github.com/PokeAPI/sprites/tree/{SPRITE_SHA}\n图像版权归 The Pokémon Company；并非官方产品。\n中文地点与条件用语：本项目人工整理；未确定部分保留源标识，不杜撰。\n数据不足≠本作无法获得；ORAS资料尤不完整。\n本作不能泛化“刷新点”为地图坐标；仅为主系列的遭遇地点与条件，不含 Pokémon GO。\n\n'+licence+'\n\nSPRITES LICENSE\n'+sprite_licence)
    print(json.dumps({'species':len(mons),'versions':len(version_data),'rawEncounters':len(raw),'groupedEncounters':sum(len(rr) for rr in encounters.values()),'uncertainPools':uncertain_pools,'htmlBytes':(ROOT/'eli-pokedex-v1.html').stat().st_size,'untranslated':data['meta']['untranslated'],'versionCoverage':version_data},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
