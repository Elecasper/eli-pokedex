#!/usr/bin/env python3
"""GPL-3.0 save-memory facts viewer. Parse data only; never read/download ROMs.
Sources pinned by commit. Type identity is SHA1 (GBA) / serial (NDS), never title similarity.
"""
import collections,datetime,hashlib,json,pathlib,re,struct,unicodedata,urllib.parse,urllib.request,xml.etree.ElementTree as ET
from opencc import OpenCC
R=pathlib.Path(__file__).resolve().parent;CACHE=pathlib.Path('/tmp/eli-save-types-source');OUT=R/'eli-save-types-v1';OUT.mkdir(exist_ok=True)
if(OUT/'index.html').exists():raise FileExistsError(OUT/'index.html')
PINS={'profi200/open_agb_firm':'401c3dff900f658d3edf77ababcfaf5dca54a0a8','profi200/libn3ds':'ccbb6a94d60bea2e6a1901263251636b192bad3f','melonDS-emu/melonDS':'1e654443e4c0a54b40709c0208aa0eeba41e6142','mgba-emu/mgba':'52de910807c0178d6cfb088aa350952569e8f08f','libretro/libretro-database':'2c93952f3cdf02837d2b34112aea5ee844d42b8b','SumavisionQ5/OfflineList.DAT':'4dec1d8543cca8f870beff5e6ad894bb669c88d7'}
FILES={'profi200/open_agb_firm':['resources/gba_db.bin','include/arm11/save_type.h','source/arm11/save_type.c','LICENSE.txt'],'profi200/libn3ds':['include/drivers/lgy_common.h','source/arm9/drivers/lgy9.c'],'melonDS-emu/melonDS':['src/ROMList.cpp','src/ROMList.h','src/NDSCart/CartRetail.cpp','LICENSE'],'mgba-emu/mgba':['src/gba/overrides.c','LICENSE'],'libretro/libretro-database':['metadat/no-intro/Nintendo - Game Boy Advance.dat','metadat/no-intro/Nintendo - Nintendo DS.dat','README.md'],'SumavisionQ5/OfflineList.DAT':['chsRoms - Nintendo - Game Boy Advance.xml','chsRoms - Nintendo - Nintendo DS.xml']}
manifest=[]
def read(repo,path):
 bundled=R.parent/'third-party/save-types'/repo/path;p=bundled if bundled.exists()else CACHE/repo/path
 if not p.exists():p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(urllib.request.urlopen(f'https://raw.githubusercontent.com/{repo}/{PINS[repo]}/'+urllib.parse.quote(path),timeout=45).read())
 b=p.read_bytes();manifest.append({'repo':repo,'commit':PINS[repo],'path':path,'url':f'https://github.com/{repo}/blob/{PINS[repo]}/'+urllib.parse.quote(path),'sha256':hashlib.sha256(b).hexdigest()});return b
inputs={(r,p):read(r,p)for r,paths in FILES.items()for p in paths}
t2s=OpenCC('t2s');s2t=OpenCC('s2t')
def norm(s):return re.sub(r'[^\w\u3040-\u30ff]','',unicodedata.normalize('NFKD',s).lower())
def stem(s):
 s=re.split(r'\(|\[',s)[0];s=re.sub(r'\bversion\b','',s,flags=re.I);return norm(s)
manual=json.loads((R/'eli-save-name-aliases-v1.json').read_text());curated={}
for plat,prefix,cn,jp,en in manual['pokemon']:
 aliases=[cn,jp,en,'Pokemon '+en,'Pocket Monsters '+en,'ポケットモンスター'+jp,'ポケモン'+jp]
 for pre in['宝可梦','口袋妖怪','口袋怪兽','神奇宝贝']:aliases.append(pre+cn)
 curated[(plat,prefix)]=['宝可梦 '+cn,aliases]
for plat,prefix,cn,jp,other in manual['games']:curated[(plat,prefix)]=[cn,[cn,jp]+other.split('|')]
cn_aliases=collections.defaultdict(set)
for plat,system in[('GBA','Game Boy Advance'),('NDS','Nintendo DS')]:
 root=ET.fromstring(inputs[('SumavisionQ5/OfflineList.DAT','chsRoms - Nintendo - '+system+'.xml')])
 for g in root.findall('./games/game'):
  name=g.findtext('title')or'';comment=re.split(r'[\[\(（]',g.findtext('comment')or'')[0].strip()
  if comment and re.search(r'[\u3400-\u9fff]',comment):cn_aliases[(plat,stem(name))].add(comment)
raw=inputs[('profi200/open_agb_firm','resources/gba_db.bin')];assert len(raw)%28==0;gba={}
for i in range(0,len(raw),28):
 sha=raw[i:i+20].hex();serial=raw[i+20:i+24].decode('ascii');attr=struct.unpack_from('<I',raw,i+24)[0];assert attr<=15;assert sha not in gba;gba[sha]=(serial,attr)
# Hardware enum label EEPROM_8k is misleading: libn3ds shift=9 => 512 B, not 1KiB/8KiB.
shifts=[9,9,13,13,16,16,16,16,16,16,17,17,17,17,15,0]
lgy=inputs[('profi200/libn3ds','source/arm9/drivers/lgy9.c')].decode();match=re.search(r'sizeShiftLut\[16\]\s*=\s*\{([^}]+)',lgy);assert list(map(int,re.findall(r'\d+',match[1])))==shifts
mgba={}
for serial,save,hardware in re.findall(r'\{\s*"([A-Z0-9]{4})",\s*(GBA_SAVEDATA_\w+),\s*([^,]+),',inputs[('mgba-emu/mgba','src/gba/overrides.c')].decode()):mgba[serial]={'type':save,'rtc':'HW_RTC'in hardware,'hardware':hardware.strip()}
nds={}
for code,size,kind in re.findall(r'\{0x([0-9A-Fa-f]+),\s*0x([0-9A-Fa-f]+),\s*0x([0-9A-Fa-f]+)\}',inputs[('melonDS-emu/melonDS','src/ROMList.cpp')].decode()):
 serial=int(code,16).to_bytes(4,'little').decode('ascii');kind=int(kind,16)
 assert serial not in nds;nds[serial]=(int(size,16),kind)
nds_sizes=[0,512,8192,65536,131072,262144,524288,1048576,8388608,16777216,67108864]
retail=inputs[('melonDS-emu/melonDS','src/NDSCart/CartRetail.cpp')].decode();assert 'case 4: SRAMType = 2' in retail and'case 7: SRAMType = 3'in retail and'case 10: SRAMType = 4'in retail
rows=[];excluded=0;matched_curated=set()
for plat,system in[('GBA','Game Boy Advance'),('NDS','Nintendo DS')]:
 text=inputs[('libretro/libretro-database','metadat/no-intro/Nintendo - '+system+'.dat')].decode()
 for block in re.findall(r'^game \(\n(.*?)^\)',text,re.M|re.S):
  name=re.search(r'^\s*name "([^"]+)"',block,re.M)[1]
  if re.search(r'\((?:Pirate|Unl|Video|Save Data|Wi-Fi Kiosk|Kiosk|Promo|Proto[^)]*)\)',name,re.I):excluded+=1;continue
  h=re.search(r'\bsha1 ([0-9A-Fa-f]{40})\b',block);crc=re.search(r'\bcrc ([0-9A-Fa-f]{8})\b',block);serial=re.search(r'^\s*serial "([^"]+)"',block,re.M);serial=serial[1]if serial and re.fullmatch(r'[A-Z0-9]{4}',serial[1])else''
  if not h:continue
  sha=h[1].lower();region=re.search(r'\(([^()]+)\)',name);region=region[1]if region else'未标地区';kind=None;size=None;match_type='missing';family='未知';rtc=None;hw='';oaf=None;warnings=[]
  if plat=='GBA':
   if sha in gba:
    code,oaf=gba[sha]
    valid_code=bool(re.fullmatch(r'[A-Z0-9]{4}',code))
    if serial and valid_code and serial!=code:warnings.append('源表编号存在差异；类型按SHA1匹配，编号保留原版目录记录。')
    serial=serial or(code if valid_code else'');kind=oaf;match_type='sha1';size=(1<<shifts[kind])if kind!=15 else 0;family='EEPROM'if kind<4 else'FLASH'if kind<14 else'SRAM协议'if kind==14 else'无存档芯片'
   # Only fixed-size mGBA overrides may fill a missing SHA-based record. EEPROM is adaptive.
   override=mgba.get(serial)
   if override:
    rtc=override['rtc'];hw=override['hardware'];fixed={'GBA_SAVEDATA_FLASH512':('FLASH',65536),'GBA_SAVEDATA_FLASH1M':('FLASH',131072),'GBA_SAVEDATA_SRAM':('SRAM协议',32768),'GBA_SAVEDATA_SRAM512':('SRAM协议',65536),'GBA_SAVEDATA_FORCE_NONE':('无存档芯片',0)}
    if size is None and override['type']in fixed:family,size=fixed[override['type']];match_type='code';kind=None
    if rtc and family=='EEPROM':warnings.append('EEPROM与RTC是两回事；本作有额外硬件，不能为了RTC盲选Flash。')
    if any(t in hw for t in['HW_LIGHT_SENSOR','HW_GYRO','HW_TILT','HW_RUMBLE']):warnings.append('有光感、陀螺仪、倾斜或震动等额外硬件；存档类型不代表VC兼容性。')
  else:
   if serial in nds:
    source_size,kind=nds[serial]
    if 0<=kind<=10:
     size=nds_sizes[kind];family='无存档芯片'if kind==0 else'EEPROM'if kind<=4 else'FLASH'if kind<=7 else'NAND';match_type='code'
    else:warnings.append('源表记录为未定义类型；不当作无存档。')
  base=re.split(r'\s*\(',name,maxsplit=1)[0];aliases=set(cn_aliases.get((plat,stem(name)),[]));special=curated.get((plat,serial[:3]));display=base
  if special:display=special[0];aliases.update(special[1]);matched_curated.add((plat,serial[:3]))
  elif aliases:display=sorted(aliases,key=lambda a:(len(a),a))[0]
  aliases.update([base,serial]);aliases={x for a in aliases for x in[a,t2s.convert(a),s2t.convert(a)]if x}
  rows.append({'platform':plat,'code':serial,'name':name,'display':display,'aliases':sorted(aliases),'region':region,'sha1':sha,'crc32':crc[1].upper()if crc else'','type':family,'bytes':size,'rtc':rtc,'match':match_type,'oaf':oaf,'hardware':hw,'warnings':warnings})
assert not(set(curated)-matched_curated),set(curated)-matched_curated
# Group only identical source conclusions. Distinct types, unknowns and confidence stay separate.
groups={}
for row in rows:
 key=(row['platform'],row['code']or row['sha1'],row['type'],row['bytes'],row['rtc'],row['match'],row['oaf'])
 if key not in groups:groups[key]={k:row[k]for k in['platform','code','display','type','bytes','rtc','match','oaf','hardware','warnings']};groups[key]['aliases']=set();groups[key]['variants']=[]
 g=groups[key];g['aliases'].update(row['aliases']);g['warnings']=sorted(set(g['warnings'])|set(row['warnings']));g['variants'].append({k:row[k]for k in['name','region','sha1','crc32']})
records=list(groups.values())
for i,g in enumerate(records):g['id']=i;g['aliases']=sorted(g['aliases']);g['variants'].sort(key=lambda x:x['name'])
chars=set(''.join(a for g in records for a in g['aliases']));charmap={c:t2s.convert(c)for c in chars if t2s.convert(c)!=c}
meta={'schema':'eli-save-types-v1','builtAt':datetime.date.today().isoformat(),'pins':PINS,'versions':len(rows),'groups':len(records),'knownVersions':sum(r['bytes']is not None for r in rows),'gbaKnownVersions':sum(r['platform']=='GBA'and r['bytes']is not None for r in rows),'ndsKnownVersions':sum(r['platform']=='NDS'and r['bytes']is not None for r in rows),'curatedFamilies':len(curated),'cjkAliasGroups':sum(any(re.search(r'[\u3400-\u9fff]',a)for a in g['aliases'])for g in records),'jpAliasGroups':sum(any(re.search(r'[\u3040-\u30ff]',a)for a in g['aliases'])for g in records),'excludedNonRetailRecords':excluded,'disclaimer':'原版参考；别名不代表汉化/改版实测。RTC仅在mGBA硬件覆盖表明确记录时下结论；缺记录不是不需要。','gbaSizeDefinition':'按libn3ds实际sizeShiftLut计算。源EEPROM_8k枚举对应512字节(4 Kbit)，不按名字猜容量。','ndsSizeDefinition':'按melonDS CartRetail sramlengths与SRAMType对应，未定义SaveMemType保持未知。'}
D={'meta':meta,'records':records,'charmap':charmap};data=json.dumps(D,ensure_ascii=False,separators=(',',':'));(OUT/'data.json').write_text(data+'\n');(OUT/'sources.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2));template=(R/'eli-save-types-template-v1.html').read_text();app=(R/'eli-save-types-app-v1.js').read_text();(OUT/'index.html').write_text(template.replace('__SAVE_DATA__',data.replace('<','\\u003c')).replace('/*__APP__*/',app));print(json.dumps(meta,ensure_ascii=False,indent=2))
