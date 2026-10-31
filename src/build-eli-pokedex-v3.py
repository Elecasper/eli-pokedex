#!/usr/bin/env python3
"""v3: NS分类 + 真正的游戏物种支持名单。GPL-3.0；不运行上游代码。
名单和遭遇记录分离：有支持数据不等于有野生地点，不把缺记录当作未收录。
"""
import base64,collections,csv,datetime,gzip,io,json,pathlib,re,struct,urllib.request
from PIL import Image,ImageOps
R=pathlib.Path(__file__).resolve().parent;C=pathlib.Path('/tmp/eli-pokedex-source');PK=(R.parent/'third-party/pkhex')if(R.parent/'third-party/pkhex').exists()else pathlib.Path('/tmp/eli-pokedex-v3-source');SHA='6b8db7f3cb31cfaa37cb74e5c3edff124bcba5ce';PKSHA='61da5c6f68fbc0f8fa5b09212dc8329169a830db'
base=R/'eli-pokedex-data-v2.json';D=json.loads(base.read_text()if base.exists()else gzip.decompress((R/'dex-base-v2.json.gz').read_bytes()).decode())
def get(url,p):
 if not p.exists():p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(urllib.request.urlopen(url,timeout=40).read())
 return p.read_bytes()
def pk(path):return get(f'https://raw.githubusercontent.com/kwsch/PKHeX/{PKSHA}/{path}',PK/path)
def rows(name):
 p=C/'csv'/(name+'.csv');get(f'https://raw.githubusercontent.com/PokeAPI/pokeapi/{SHA}/data/v2/csv/{name}.csv',p)
 with p.open(encoding='utf-8',newline='')as f:return list(csv.DictReader(f))
NS=[(31,'去吧！皮卡丘',7,19,'gg'),(32,'去吧！伊布',7,19,'gg'),(33,'剑',8,20,'swsh'),(34,'盾',8,20,'swsh'),(37,'晶灿钻石',8,23,'bdsp'),(38,'明亮珍珠',8,23,'bdsp'),(39,'传说 阿尔宙斯',8,24,'la'),(40,'朱',9,25,'sv'),(41,'紫',9,25,'sv'),(47,'传说 Z-A',9,30,'za')]
D['rosters']={};D['rosterRegionalOnly']={};max_old={3:386,4:493,5:649,6:721}
for v in D['versions']:
 vid=v['id'];limit=1025 if vid==0 else max_old.get(v['gen'],802 if vid in [27,28]else 807)
 D['rosters'][str(vid)]=list(range(1,limit+1));v['rosterCount']=limit
params={'swsh':(176,33,64,898,30,32),'la':(176,33,64,905,30,32),'sv':(80,28,255,1025,24,26),'za':(80,28,255,1000,24,26)}
roster_cache={};regional_cache={}
for name,(size,flag,mask,maximum,indexoff,countoff)in params.items():
 b=pk('PKHeX.Core/Resources/byte/personal/personal_'+name);assert len(b)%size==0
 def present(i):return bool(b[i*size+flag]&mask)
 result=[];regional=[]
 for sid in range(1,maximum+1):
  data=b[sid*size:(sid+1)*size];fc=data[countoff];fi=struct.unpack_from('<H',data,indexoff)[0]
  alternatives=range(fi,fi+fc-1)if fi>0 and fc>1 else[]
  assert all(i<len(b)//size for i in alternatives)
  included=present(sid)or any(present(i)for i in alternatives)
  if included:result.append(sid)
  if included and not present(sid):regional.append(sid)
 roster_cache[name]=result;regional_cache[name]=regional
roster_cache['gg']=list(range(1,152))+[808,809];roster_cache['bdsp']=list(range(1,494))
for vid,name,gen,vg,table in NS:
 roster=roster_cache[table];D['rosters'][str(vid)]=roster;D['rosterRegionalOnly'][str(vid)]=regional_cache.get(table,[])
 D['versions'].append({'id':vid,'n':name,'gen':gen,'vg':vg,'platform':'NS','species':0,'locations':0,'rows':0,'rosterCount':len(roster),'abilitiesSupported':table not in ['gg','la','za'],'breedingSupported':table not in ['gg','la','za'],'rosterSource':'PKHeX PersonalTable '+table,'note':'名单按当前快照的物种支持判断，含交换、迁入或DLC兼容；不等于本版可野生捕捉清单。'})
D['regions'].update({'8':'伽勒尔','9':'洗翠','10':'帕底亚'})
# NS现有公开遭遇表（LGPE及剑盾含DLC）；其余游戏不造地图。
versions={x['id']:x for x in D['versions']};vr={int(x['id']):x for x in rows('versions')};loc={int(x['id']):x for x in rows('locations')};areas={int(x['id']):x for x in rows('location_areas')};slots={int(x['id']):x for x in rows('encounter_slots')};pokemon={int(x['id']):x for x in rows('pokemon')};cnold={a[0]:a[1]for a in D['areas'].values()};cnmanual={'indigo-plateau':'石英高原','lavender-town':'紫苑镇','galar-wild-area-max-dens':'旷野地带（极巨巢穴）','isle-of-armor-caves':'铠之孤岛（洞窟，区域级）','roaming-crown-tundra':'王冠雪原（游走，区域级）','roaming-galar-wild-area':'旷野地带（游走，区域级）','roaming-isle-of-armor':'铠之孤岛（游走，区域级）'};enloc={int(x['location_id']):x['name']for x in rows('location_names')if x['local_language_id']=='9'}
def norm(s):return re.sub(r'[^a-z0-9]','',re.sub(r'\([^)]*\)|（[^）]*）','',s).lower())
ns_names={}
for gen,prefix in [('gen8','swsh'),('gen8a','la'),('gen8b','bdsp'),('gen9','sv'),('gen9a','za')]:
 path=f'PKHeX.Core/Resources/text/locations/{gen}/text_{prefix}_00000_'
 en=pk(path+'en.txt').decode().splitlines();zh=pk(path+'zh-Hans.txt').decode().splitlines()
 for e,z in zip(en,zh):
  if e.strip()and z.strip():ns_names[norm(e)]=z.strip()
methods={38:'可见野生',39:'水面可见野生',40:'空中可见野生',41:'特殊可见野生',42:'空中特殊',43:'水面特殊',56:'地面潜伏',57:'游走野生',58:'水面游走',59:'水面追逐',60:'极巨大冒险',61:'极巨团体战'};D['methods'].update({str(k):v for k,v in methods.items()})
condition_source={int(r['id']):r['identifier']for r in rows('encounter_condition_values')};condition_map=collections.defaultdict(list)
for r in rows('encounter_condition_value_map'):condition_map[int(r['encounter_id'])].append(int(r['encounter_condition_value_id']))
cnconditions={106:'已捕获急冻鸟',107:'已捕获闪电鸟',108:'已捕获火焰鸟',206:'有去吧皮卡丘存档',207:'有去吧伊布存档',208:'需要化石鸟',209:'需要化石龙',210:'需要化石海兽',211:'需要化石鱼',212:'完成道场第一项修行',213:'完成道场第三项修行',226:'完成雪暴马／灵幽马相关救村事件',227:'已捕获5只究极异兽',247:'晴天',248:'阴天',249:'雨天',250:'雷雨',251:'下雪',252:'暴风雪',253:'沙暴',254:'烈日',255:'雾天',256:'进入名人堂之前',324:'找到50个洞窟足迹',325:'找到50个草原足迹',326:'找到50个铁心足迹',327:'队伍有五种雷吉系宝可梦',328:'选择雷吉艾勒奇图案',329:'选择雷吉铎拉戈图案',330:'种出冰萝卜',331:'种出黑萝卜',332:'与32人交谈过',333:'与三圣剑同吃咖喱相关条件',334:'需要牵绊缰绳',335:'已目击伽勒尔三圣鸟争斗',336:'普通光柱',337:'稀有光柱',343:'特殊极巨巢穴'}
slugnames={p['slug']:p['n']for p in D['pokemon']};unknown_conditions=set();unknown_locations=set()
def condcn(i):
 if str(i)in D['conditions']:return D['conditions'][str(i)]
 if i in cnconditions:return cnconditions[i]
 s=condition_source[i]
 if s.startswith('alolan-diglett-found-'):return '找到'+s.split('-')[-1]+'只阿罗拉地鼠'
 if s.startswith('max-den-rating-'):return s.split('-')[-2]+'星极巨巢穴'
 for prefix,label in [('starter-','最初选择'),('trade-','用以下宝可梦交换：')]:
  if s.startswith(prefix):
   species=s[len(prefix):];region='（伽勒尔）'if species.endswith('-galar')else'';species=species.removesuffix('-galar')
   if species in slugnames:return label+slugnames[species]+region
 unknown_conditions.add(s);return '条件待校对（'+s+'）'
def loccn(i):
 if i in cnold:return cnold[i]
 r=loc[i];name=enloc.get(i,r['identifier']);slug=r['identifier']
 if slug in cnmanual:return cnmanual[slug]
 match=re.search(r'(?:sea-)?route-(\d+)$',slug)
 if match:return match[1]+'号道路'
 key=norm(name)
 if key in ns_names:return ns_names[key]
 if key.endswith('area')and key[:-4]in ns_names:return ns_names[key[:-4]]
 unknown_locations.add(slug);return '地名待校对（'+name+'）'
area_labels={'':'主区域','area':'主区域','overworld':'地面','unknown-area':'分区未定','whole-area':'全区域','water':'水面','1f':'1层','2f':'2层','3f':'3层','b1f':'地下1层','b2f':'地下2层','b3f':'地下3层','main-area':'主区域','outside':'外部','inside':'内部'}
ns_version_map={31:31,32:32,33:33,34:34,35:33,36:33,50:34,51:34};groups={};new_raw=0
for r in rows('encounters'):
 source_v=int(r['version_id'])
 if source_v not in ns_version_map:continue
 v=ns_version_map[source_v];pid=int(r['pokemon_id']);sid=int(pokemon[pid]['species_id'])
 if sid not in D['rosters'][str(v)]:continue
 aid=int(r['location_area_id']);method=int(slots[int(r['encounter_slot_id'])]['encounter_method_id']);conditions=tuple(sorted(set(condition_map[int(r['id'])])));key=(sid,v,aid,method,conditions,pid)
 if key not in groups:groups[key]=[int(r['min_level']),int(r['max_level'])]
 else:groups[key]=[min(groups[key][0],int(r['min_level'])),max(groups[key][1],int(r['max_level']))]
 new_raw+=1
for(sid,v,aid,method,conditions,pid),(low,high)in groups.items():
 a=areas[aid];lid=int(a['location_id']);region=int(loc[lid]['region_id'] or 0);area=a['identifier'];label=area_labels.get(area)
 if label is None:
  m=re.fullmatch(r'(b?)(\d+)f',area)
  label=('地下'if m[1]else'')+m[2]+'层'if m else'分区条件需核对'
 D['areas'].setdefault(str(aid),[lid,loccn(lid),label,region,loc[lid]['identifier'],area])
 for c in conditions:D['conditions'][str(c)]=condcn(c)
 form=''if pid==sid else next((f['n']for f in D['pokemon'][sid-1]['forms']if f['pid']==pid),'特殊形态（需核对）')
 D['encounters'].setdefault(str(sid),[]).append([v,aid,method,low,high,None,list(conditions),form])
# 给新增NS作品补学习表，不能因为没有地点就判定不属于游戏。
D['learnsets']=collections.defaultdict(dict,D['learnsets']);vgs={x[3]for x in NS};temp=collections.defaultdict(lambda:collections.defaultdict(list))
for r in rows('pokemon_moves'):
 vg=int(r['version_group_id']);pid=int(r['pokemon_id']);method=int(r['pokemon_move_method_id'])
 if vg in vgs and method in[1,2,3,4]and int(pokemon.get(pid,{}).get('species_id',9999))<=1025:temp[str(pid)][str(vg)].append((int(r['level']),int(r['move_id']),method))
for pid,vv in temp.items():
 for vg,rs in vv.items():D['learnsets'][pid][vg]=sorted(set(rs),key=lambda r:(r[2],r[0],r[1]))
for v in D['versions']:
 if v['id']==0:continue
 rs=[(sid,r)for sid,records in D['encounters'].items()for r in records if r[0]==v['id']];v['species']=len({sid for sid,r in rs});v['locations']=len({D['areas'][str(r[1])][0]for sid,r in rs});v['rows']=len(rs)
# 只裁透明边缘，让手机列表里的小型像素图可读；来源原图不改写。
for p in D['pokemon']:
 for item in[p]+p.get('forms',[]):
  image=item.get('img')
  if not image or item.get('imageMissing'):continue
  assert image.startswith('data:image/png;base64,')
  im=Image.open(io.BytesIO(base64.b64decode(image.split(',',1)[1])));rgba=im.convert('RGBA');box=rgba.getchannel('A').getbbox()
  if box:
   transparency=im.info.get('transparency')
   if im.mode=='P' and isinstance(transparency,(int,bytes)) and (isinstance(transparency,int) or 0 in transparency):
    clear=transparency if isinstance(transparency,int)else next(i for i,a in enumerate(transparency)if a==0)
    cropped=im.crop(box);processed=Image.new('P',(cropped.width+8,cropped.height+8),clear);processed.putpalette(im.getpalette());processed.paste(cropped,(4,4));processed.info['transparency']=transparency
   else:processed=ImageOps.expand(rgba.crop(box),border=4,fill=(0,0,0,0))
   output=io.BytesIO();processed.save(output,format='PNG',optimize=True);item['img']='data:image/png;base64,'+base64.b64encode(output.getvalue()).decode()
D['meta'].update({'imageProcessing':'仅裁切PNG透明边缘并留4px边距；来源、角色和像素内容不替换。','revision':3,'builtAt':datetime.date.today().isoformat(),'scope':'1025种；32个GBA/NDS/3DS/NS作品版本。物种支持名单与地点记录分开。','rosterDefinition':'本作收录指快照中的物种支持名单，含交换/迁入/DLC兼容；不是地区图鉴编号表，也不保证当下可野生捕捉或获得。','nsRawEncounterRows':new_raw,'nsGroupedEncounterRows':len(groups),'rosterPKHeXCommit':PKSHA,'totalEncounterRecords':sum(map(len,D['encounters'].values())),'nsMissingLocations':sorted(unknown_locations),'nsUntranslatedConditions':sorted(unknown_conditions),'bookShelfWithdrawn':True})
for name in['eli-pokedex-data-v3.json','eli-pokedex-v3.html']:
 if(R/name).exists():raise FileExistsError(name)
text=json.dumps(D,ensure_ascii=False,separators=(',',':'));(R/'eli-pokedex-data-v3.json').write_text(text+'\n');js=(R/'eli-pokedex-app-v3.js').read_text().replace('/*__DETAILS__*/',(R/'eli-pokedex-details-v3.js').read_text());html=(R/'eli-pokedex-template-v3.html').read_text().replace('/*__APP__*/',js).replace('__DATA_JSON__',text.replace('<','\\u003c'));(R/'eli-pokedex-v3.html').write_text(html)
print(json.dumps({'rosters':[(v['n'],v['rosterCount'],v['species'])for v in D['versions']],'nsEncounterRows':len(groups),'unknownLocations':sorted(unknown_locations),'unknownConditions':sorted(unknown_conditions),'bytes':(R/'eli-pokedex-v3.html').stat().st_size},ensure_ascii=False,indent=2))
