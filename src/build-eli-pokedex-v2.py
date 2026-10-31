#!/usr/bin/env python3
"""图鉴v2：扩展百科、招式、常见形态；以PKHeX区域级表补3DS缺口。
补充解析器/派生资料按GPL-3.0发布；保留原应用MIT与PokéAPI许可。
.pkl 是PKHeX自定义平坦字节表，仅struct读取；绝不pickle.load或运行上游代码。
"""
import base64,collections,concurrent.futures,csv,datetime,hashlib,json,pathlib,re,struct,urllib.request
ROOT=pathlib.Path(__file__).resolve().parent;CACHE=pathlib.Path('/tmp/eli-pokedex-source');PK=pathlib.Path('/tmp/eli-pokedex-v2-research')
SHA='6b8db7f3cb31cfaa37cb74e5c3edff124bcba5ce';SPRITE='1dd55c0436d2a5b6e324c0b780e1b1b416fbfb64';PKSHA='61da5c6f68fbc0f8fa5b09212dc8329169a830db'
D=json.loads((ROOT/'eli-pokedex-data-v1.json').read_text())
def rows(n):
 path=CACHE/'csv'/(n+'.csv')
 fetch(f'https://raw.githubusercontent.com/PokeAPI/pokeapi/{SHA}/data/v2/csv/{n}.csv',path)
 with path.open(newline='',encoding='utf-8') as f:return list(csv.DictReader(f))
def index(n):return {int(r['id']):r for r in rows(n)}
def names(n,key,col='name',lang=12):
 out={}
 for lg in [9,4,lang]:
  for r in rows(n):
   if int(r['local_language_id'])==lg and r[col]:out[int(r[key])]=r[col]
 return out
def fetch(url,path):
 if not path.exists():
  path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(urllib.request.urlopen(url,timeout=40).read())
 return path.read_bytes()
S=index('pokemon_species');P=index('pokemon');VG=index('version_groups');N=names('pokemon_species_names','pokemon_species_id');EN=names('pokemon_species_names','pokemon_species_id',lang=9);TW=names('pokemon_species_names','pokemon_species_id',lang=4);GENUS=names('pokemon_species_names','pokemon_species_id','genus');AN=names('ability_names','ability_id');MN=names('move_names','move_id');IN=names('item_names','item_id');FN=names('pokemon_form_names','pokemon_form_id','form_name')
by_species=collections.defaultdict(list);forms=[]
for f in rows('pokemon_forms'):
 pid=int(f['pokemon_id']);sid=int(P[pid]['species_id']);vg=int(f['introduced_in_version_group_id']);gen=int(VG[vg]['generation_id'])
 if pid!=sid and sid<=1025 and int(f['id']) in FN and gen<=9 and pid not in {x['pid'] for x in forms}:forms.append({'pid':pid,'sid':sid,'n':FN[int(f['id'])],'gen':gen,'vg':vg})
sprite_ids=list(range(808,1026))+[f['pid'] for f in forms]
def sprite(pid):
 try:
  b=fetch(f'https://raw.githubusercontent.com/PokeAPI/sprites/{SPRITE}/sprites/pokemon/{pid}.png',CACHE/'sprites'/f'{pid}.png');assert b.startswith(b'\x89PNG');return pid,'data:image/png;base64,'+base64.b64encode(b).decode()
 except Exception:return pid,None
with concurrent.futures.ThreadPoolExecutor(max_workers=12) as ex:images=dict(ex.map(sprite,sprite_ids))
ST=collections.defaultdict(dict);TY=collections.defaultdict(list);AB=collections.defaultdict(dict);PA=collections.defaultdict(list);PT=collections.defaultdict(list);PS=collections.defaultdict(list)
for r in rows('pokemon_stats'):
 if int(r['stat_id'])<=6:ST[int(r['pokemon_id'])][int(r['stat_id'])]=int(r['base_stat'])
for r in rows('pokemon_types'):TY[int(r['pokemon_id'])].append((int(r['slot']),int(r['type_id'])))
for r in rows('pokemon_abilities'):AB[int(r['pokemon_id'])][int(r['slot'])]=(int(r['ability_id']),int(r['is_hidden']))
for name,out in [('pokemon_abilities_past',PA),('pokemon_types_past',PT),('pokemon_stats_past',PS)]:
 for r in rows(name):out[int(r['pokemon_id'])].append(r)
AD=index('abilities')
def generation(pid,g):
 stats=ST[pid].copy();types=TY[pid];abilities=AB[pid].copy()
 for k in range(1,7):
  old=[r for r in PS[pid] if int(r['stat_id'])==k and int(r['generation_id'])>=g and r['base_stat']]
  if old:stats[k]=int(min(old,key=lambda r:int(r['generation_id']))['base_stat'])
 old=[r for r in PT[pid] if int(r['generation_id'])>=g]
 if old:
  end=min(int(r['generation_id'])for r in old);types=[(int(r['slot']),int(r['type_id']))for r in old if int(r['generation_id'])==end]
 for slot in [1,2,3]:
  old=[r for r in PA[pid] if int(r['slot'])==slot and int(r['generation_id'])>=g]
  if old:
   r=min(old,key=lambda r:int(r['generation_id']));abilities[slot]=(int(r['ability_id'] or 0),int(r['is_hidden']))
 return {'s':[stats.get(i,0)for i in range(1,7)],'t':[v for _,v in sorted(types)],'a':[[a,h] for _,(a,h) in sorted(abilities.items()) if a and int(AD[a]['generation_id'])<=g]}
DESC={}
for r in rows('pokemon_species_flavor_text'):
 if r['language_id']=='12':DESC[int(r['species_id'])]=' '.join(r['flavor_text'].split())
EG=collections.defaultdict(list)
for r in rows('pokemon_egg_groups'):EG[int(r['species_id'])].append(int(r['egg_group_id']))
efforts=collections.defaultdict(dict)
for r in rows('pokemon_stats'):
 if int(r['effort']):efforts[int(r['pokemon_id'])][int(r['stat_id'])]=int(r['effort'])
M={p['id']:p for p in D['pokemon']}
for i in range(1,1026):
 s=S[i];p=P[i];gen=int(s['generation_id'])
 if i not in M:
  if not images.get(i):raise ValueError('Missing default sprite '+str(i))
  mon={'id':i,'n':N[i],'en':EN[i],'slug':s['identifier'],'gen':gen,'genus':GENUS.get(i,''),'desc':DESC.get(i,''),'h':int(p['height'])/10,'w':int(p['weight'])/10,'parent':int(s['evolves_from_species_id'] or 0),'chain':int(s['evolution_chain_id']),'evo':[],'alias':[TW[i]] if TW.get(i)!=N[i] else [],'g':{},'img':images[i]};M[i]=mon
 mon=M[i]
 for g in range(3,10):
  if str(g) not in mon['g']:mon['g'][str(g)]=generation(i,max(gen,g))
 mon.update({'captureRate':int(s['capture_rate']),'genderRate':int(s['gender_rate']),'hatchCycles':int(s['hatch_counter'] or 0),'eggGroups':EG[i],'effort':efforts[i],'forms':[]})
for f in forms:
 pid=f['pid'];sid=f['sid'];p=P[pid]
 M[sid]['forms'].append({'pid':pid,'n':f['n'],'gen':f['gen'],'vg':f['vg'],'h':int(p['height'])/10,'w':int(p['weight'])/10,'g':{str(g):generation(pid,max(g,f['gen']))for g in range(3,10)},'img':images.get(pid),'imageMissing':not bool(images.get(pid))})
D['pokemon']=[M[i]for i in range(1,1026)];D['abilities']=AN;D['eggGroups']={1:'怪兽',2:'水中1',3:'虫',4:'飞行',5:'陆上',6:'妖精',7:'植物',8:'人型',9:'水中3',10:'矿物',11:'不定形',12:'水中2',13:'百变怪',14:'龙',15:'未发现'}
# 作用说明明确标为较新中文描述，不伪称已经逐代验证机制。
for table,key,label in [('ability_flavor_text','ability_id','abilityDescriptions'),('move_flavor_text','move_id','moveDescriptions')]:
 out={}
 for r in rows(table):
  if r['language_id']=='12':out[int(r[key])]=' '.join(r['flavor_text'].split())
 D[label]=out
MOVES=index('moves');D['moves']={i:{'n':MN[i],'t':int(m['type_id']),'p':int(m['power']) if m['power'] else None,'a':int(m['accuracy']) if m['accuracy'] else None,'pp':int(m['pp'])if m['pp'] else None,'class':int(m['damage_class_id'])}for i,m in MOVES.items()if i in MN}
D['learnsets']=collections.defaultdict(lambda:collections.defaultdict(list));allowed_vg={v['vg']for v in D['versions']}|{25,26,27}
for r in rows('pokemon_moves'):
 pid=int(r['pokemon_id']);vg=int(r['version_group_id']);method=int(r['pokemon_move_method_id'])
 if int(P.get(pid,{}).get('species_id',9999))<=1025 and vg in allowed_vg and method in [1,2,3,4]:D['learnsets'][pid][vg].append((int(r['level']),int(r['move_id']),method))
D['learnsets']={p:{v:sorted(set(rs),key=lambda x:(x[2],x[0],x[1]))for v,rs in vs.items()}for p,vs in D['learnsets'].items()}
# 保留机器可读的进化条件，可显示数字与例外，不只写“特殊条件”。
D['evolutionRules']=collections.defaultdict(list)
for r in rows('pokemon_evolution'):
 if int(r['evolved_species_id'])<=1025:D['evolutionRules'][int(r['evolved_species_id'])].append({k:v for k,v in r.items()if v not in ['', '0'] or k=='relative_physical_stats' and v=='0'})
D['items']=IN;D['versionGroups']={i:{'gen':int(v['generation_id']),'order':int(v['order'] or 0)}for i,v in VG.items()}
D['versions'].insert(0,{'id':0,'n':'全国百科（不查地点）','gen':9,'vg':25,'platform':'百科','species':1025,'locations':0,'rows':0,'note':'百科招式按朱／紫及已收录DLC资料展示；不代表该宝可梦在朱／紫一定可获得。'})
# 区域表补充：不覆盖已有的更细楼层/时段记录，不从“合法性表”推造概率。
def key_name(s):
 s=re.sub(r'[（(].*?[）)]','',s);return s.replace('水道','道路').replace('绿茵','绿荫').replace('号水路','号道路').replace(' ','')
place_lookup={}
for a in D['areas'].values():place_lookup[(a[3],key_name(a[1]))]=a[0]
have=set();have_any=set()
for sid,rs in D['encounters'].items():
 for r in rs:
  loc=D['areas'][str(r[1])][0]
  if r[2]not in [18,19,20,21,25,26,30,36]:have_any.add((int(sid),r[0],loc));have.add((int(sid),r[0],loc,r[2]))
D['methods'].update({'91':'常规野外（区域级补充）'})
condition_id=10000;D['conditions'][str(condition_id)]='区域级补充，仅确认区域与等级；概率、时段、剧情解锁待核对。图鉴导航与特殊区域可能另有前置条件。'
source_files=[];supp_raw=0;supp_added=0;added_seen=set()
for gen,game,vid,region in [(6,'x',23,6),(6,'y',24,6),(6,'or',25,3),(6,'as',26,3),(7,'sn',27,7),(7,'mn',28,7),(7,'us',29,7),(7,'um',30,7)]:
 file=PK/f'PKHeX.Core/Resources/legality/wild/Gen{gen}/encounter_{game}.pkl';b=fetch(f'https://raw.githubusercontent.com/kwsch/PKHeX/{PKSHA}/'+str(file.relative_to(PK)),file);source_files.append(str(file.relative_to(PK)));count=struct.unpack_from('<H',b,2)[0];offsets=struct.unpack_from('<'+'I'*(count+1),b,4);assert offsets[-1]==len(b)
 bank_path=PK/f'PKHeX.Core/Resources/text/locations/gen{gen}/text_{"xy"if gen==6 else"sm"}_00000_zh-Hans.txt'
 bank=fetch(f'https://raw.githubusercontent.com/kwsch/PKHeX/{PKSHA}/'+str(bank_path.relative_to(PK)),bank_path).decode().splitlines()
 for i in range(count):
  part=b[offsets[i]:offsets[i+1]];locid=struct.unpack_from('<H',part)[0];ty=part[2];assert (len(part)-4)%4==0
  current_bank=bank;bankbase=0
  if locid>=10000:
   bankbase=(locid//10000)*10000;extra_path=PK/f'PKHeX.Core/Resources/text/locations/gen{gen}/text_{"xy"if gen==6 else"sm"}_{bankbase}_zh-Hans.txt';current_bank=fetch(f'https://raw.githubusercontent.com/kwsch/PKHeX/{PKSHA}/'+str(extra_path.relative_to(PK)),extra_path).decode().splitlines()
  local_index=locid-bankbase
  if local_index>=len(current_bank)or not current_bank[local_index].strip():raise ValueError(f'Unlabelled location {game}: {locid}')
  cn=current_bank[local_index].strip();loc=place_lookup.get((region,key_name(cn)),900000+gen*1000+locid);aid=200000+gen*10000+locid*10+ty;method={0:91,1:1,2:5,3:2,4:3,5:4,6:6,7:44,8:91}.get(ty,91)if gen==6 else (33 if ty==1 else 91)
  D['areas'][str(aid)]=[loc,cn,'区域级补充（未细分楼层）',region,f'pkhex-gen{gen}-{locid}','region-level']
  grouped=collections.defaultdict(list)
  for off in range(4,len(part),4):
   bits,low,high=struct.unpack_from('<HBB',part,off);sid=bits&0x3ff;form=bits>>11
   if sid==0:continue
   assert 1<=sid<=1025 and 1<=low<=high<=100
   supp_raw+=1;grouped[(sid,form)].append((low,high))
  for (sid,form),levels in grouped.items():
   if (sid,vid,loc,method,form)in added_seen:continue
   detailed=[r for r in D['encounters'].get(str(sid),[]) if r[0]==vid and D['areas'][str(r[1])][0]==loc and 10000 not in r[6]]
   # Horde/SOS不能冒充常规遇敌：不能因已有群聚记录就丢掉普通野生记录。
   low=min(v[0]for v in levels);high=max(v[1]for v in levels)
   compatible=lambda r:(not form and not r[7])or(bool(form)and bool(r[7]))
   if method!=91 and any(r[2]==method and compatible(r)for r in detailed):continue
   if method==91 and any(r[2]in [1,2,3,4,5,14,15,16,17]and r[3]<=low and r[4]>=high and compatible(r)for r in detailed):continue
   alola={19,20,26,27,28,37,38,50,51,52,53,74,75,76,88,89,103,105}
   form_name='阿罗拉的样子' if gen==7 and sid in alola and form==1 else ('游戏内形态编号'+str(form)if form else '')
   D['encounters'].setdefault(str(sid),[]).append([vid,aid,method,min(v[0]for v in levels),max(v[1]for v in levels),None,[condition_id],form_name]);supp_added+=1
   added_seen.add((sid,vid,loc,method,form))
for v in D['versions']:
 if v['id']==0:continue
 records=[(sid,r)for sid,rs in D['encounters'].items()for r in rs if r[0]==v['id']];v['species']=len({sid for sid,r in records});v['rows']=len(records);v['locations']=len({D['areas'][str(r[1])][0]for sid,r in records})
 if v['gen']>=6:v['note']='已补充PKHeX野外区域表；区域级补充不含精确概率、全部解锁条件及坐标。仍非完整活动或联机攻略。'
for rs in D['encounters'].values():rs.sort(key=lambda r:(10000 in r[6],r[0],r[1],r[2]))
D['obtainNotes']={str(sid):{str(v):{'text':'本作没有该御三家的通常野生刷新点。可交换已有个体，或从GBA正作经伙伴公园迁移；伙伴公园需全国图鉴。GBA迁移要用有GBA卡槽的NDS／NDS Lite，3DS不能直接双插迁移。','source':'https://bulbapedia.bulbagarden.net/wiki/Pal_Park'}for v in [12,13,14]}for sid in [1,4,7]}
fetch(f'https://raw.githubusercontent.com/kwsch/PKHeX/{PKSHA}/LICENSE',PK/'LICENSE')
D['meta'].update({'builtAt':datetime.date.today().isoformat(),'revision':2,'scope':'1–9世代1025种及常见特殊形态；GBA／NDS／3DS共22游戏版本地点＋全国百科模式。','pkhexCommit':PKSHA,'pkhexLicense':(PK/'LICENSE').read_text(),'supplementRawSlots':supp_raw,'supplementAddedRecords':supp_added,'species':1025,'formRecords':len(forms),'groupedEncounters':sum(len(x)for x in D['encounters'].values()),'dataNotes':['补充地点是区域级资料，未伪造缺失的概率或精细刷新条件。','基础属性、种族值与特性名称按世代；作用描述与招式威力等为较新中文资料，部分历代效果不同。','百科模式不是朱紫捕捉清单。']})
for f in ['eli-pokedex-data-v2.json','eli-pokedex-v2.html','eli-pokedex-sources-v2.txt']:
 if (ROOT/f).exists():raise FileExistsError(f)
compact=json.dumps(D,ensure_ascii=False,separators=(',',':'));(ROOT/'eli-pokedex-data-v2.json').write_text(compact+'\n')
page=(ROOT/'eli-pokedex-template-v2.html').read_text().replace('/*__APP__*/',(ROOT/'eli-pokedex-app-v2.js').read_text().replace('/*__DETAILS__*/',(ROOT/'eli-pokedex-details-v2.js').read_text())).replace('__DATA_JSON__',compact.replace('<','\\u003c'));(ROOT/'eli-pokedex-v2.html').write_text(page)
(ROOT/'eli-pokedex-sources-v2.txt').write_text((ROOT/'eli-pokedex-sources-v1.txt').read_text()+f'\n\nV2补充：PKHeX，固定提交{PKSHA}\nhttps://github.com/kwsch/PKHeX/tree/{PKSHA}\n补充表是区域与等级事实，不提供概率；不冒充完整游戏攻略。二进制表用struct读取，未运行PKHeX或任何游戏。\n解析器、补充数据与整体v2组合发布遵守GPL-3.0，原应用MIT声明保留。输入表、相关格式源码、转换脚本和完整许可随仓库提供。\n\n'+(PK/'LICENSE').read_text())
print(json.dumps({'species':len(D['pokemon']),'forms':len(forms),'learnsetPokemon':len(D['learnsets']),'supplementSlots':supp_raw,'supplementAdded':supp_added,'htmlBytes':(ROOT/'eli-pokedex-v2.html').stat().st_size,'coverage':[{k:v[k]for k in ['id','n','species','locations','rows']}for v in D['versions']if v['gen']>=6]},ensure_ascii=False,indent=2))
