#!/usr/bin/env python3
import hashlib,json,pathlib,re,struct,collections
R=pathlib.Path(__file__).resolve().parent;P=R/'eli-save-types-v1';C=(R.parent/'third-party/save-types')if(R.parent/'third-party/save-types').exists()else pathlib.Path('/tmp/eli-save-types-source');D=json.loads((P/'data.json').read_text());checks=[]
def test(name,value):
 checks.append({'name':name,'pass':bool(value)})
 if not value:raise AssertionError(name)
gs=D['records'];test('大于一万条版本元数据',D['meta']['versions']>10000);test('两平台均有明确来源',D['meta']['gbaKnownVersions']>2700 and D['meta']['ndsKnownVersions']>6500);test('所有分组ID唯一',len({g['id']for g in gs})==len(gs));test('版本数量可追溯',sum(len(g['variants'])for g in gs)==D['meta']['versions'])
lookup=lambda code,platform='GBA':[g for g in gs if g['code']==code and g['platform']==platform]
for code in['BPEE','BPEJ','AXVE','AXPE','BPRE','BPGE']:
 r=lookup(code);test(code+'类型为128KiBFlash',r and all(g['type']=='FLASH'and g['bytes']==131072 for g in r if g['bytes']is not None))
for code in['BPEE','BPEJ','AXVE','AXPE']:test(code+'明确需要RTC',all(g['rtc']is True for g in lookup(code)))
for code in['BPRE','BPGE']:test(code+'明确不需RTC',all(g['rtc']is False for g in lookup(code)))
for code in['ADAE','CPUE','IPKE','IPGE','IRBO','IREO']:
 r=lookup(code,'NDS');test(code+'NDS为512KiBFlash',any(g['platform']=='NDS'and g['type']=='FLASH'and g['bytes']==524288 for g in r))
test('同编号跨平台不混用',any(g['bytes']==131072 for g in lookup('AXVE','GBA'))and any(g['bytes']==65536 for g in lookup('AXVE','NDS')))
test('空之探险队为128KiBEEPROM',any(g['code']=='C2SE'and g['bytes']==131072 and g['type']=='EEPROM'for g in gs))
test('Boktai的EEPROM与RTC分别记录',any(g['code']=='U3IE'and g['type']=='EEPROM'and g['rtc']is True and g['warnings']for g in gs))
test('EEPROM小容量不是8KiB',all(g['bytes']==512 for g in gs if g['platform']=='GBA'and g['oaf']in[0,1]))
test('EEPROM大容量为8KiB',all(g['bytes']==8192 for g in gs if g['platform']=='GBA'and g['oaf']in[2,3]))
test('0容量不与未知混淆',any(g['bytes']==0 and g['type']=='无存档芯片'for g in gs)and any(g['bytes']is None and g['type']=='未知'for g in gs))
test('原版地区与修订保留',any('Rev'in v['name']for g in lookup('AXVE')for v in g['variants']))
test('编号差异不覆盖NoIntro编号',any(g['code']=='AXVE'and g['warnings']for g in gs))
for q in['绿宝石','綠寶石','エメラルド','Pokemon Emerald','口袋妖怪绿宝石','ポケットモンスターエメラルド']:test('绿宝石别名 '+q,any(q in a for g in lookup('BPEE')for a in g['aliases']))
for q in['心金','ハートゴールド','HeartGold']:test('心金别名 '+q,any(q in a for g in lookup('IPKE','NDS')for a in g['aliases']))
test('无记录未推断为无存档',all(g['bytes']is None for g in gs if g['match']=='missing'))
test('SHA1与CRC字段合法',all(re.fullmatch('[0-9a-f]{40}',v['sha1'])and re.fullmatch('[0-9A-F]{8}',v['crc32'])for g in gs for v in g['variants']))
raw=(C/'profi200/open_agb_firm/resources/gba_db.bin').read_bytes();db={raw[i:i+20].hex():struct.unpack_from('<I',raw,i+24)[0]for i in range(0,len(raw),28)};shifts=[9,9,13,13,16,16,16,16,16,16,17,17,17,17,15,0]
test('每个SHA1匹配都可回溯相同原始编码',all(db[v['sha1']]==g['oaf']for g in gs if g['match']=='sha1'for v in g['variants']))
test('每个GBA实际容量来自移位表',all(g['bytes']==(0 if g['oaf']==15 else 1<<shifts[g['oaf']])for g in gs if g['oaf']is not None))
text=(C/'melonDS-emu/melonDS/src/ROMList.cpp').read_text();nd={int(a,16).to_bytes(4,'little').decode():int(c,16)for a,b,c in re.findall(r'\{0x([0-9A-Fa-f]+),\s*0x([0-9A-Fa-f]+),\s*0x([0-9A-Fa-f]+)\}',text)};sizes=[0,512,8192,65536,131072,262144,524288,1048576,8388608,16777216,67108864]
test('所有NDS类型按编号回溯源表',all(g['bytes']==sizes[nd[g['code']]]for g in gs if g['platform']=='NDS'and g['bytes']is not None))
test('NDS未定义类型保持未知',all(g['bytes']is None for g in gs if g['platform']=='NDS'and g['code']in nd and nd[g['code']]>10))
for source in json.loads((P/'sources.json').read_text()):test('来源完整SHA256 '+source['repo']+'/'+source['path'],hashlib.sha256(((C/source['repo']/source['path'])if(C/source['repo']/source['path']).exists()else pathlib.Path('/tmp/eli-save-types-source')/source['repo']/source['path']).read_bytes()).hexdigest()==source['sha256'])
html=(P/'index.html').read_text();js=(R/'eli-save-types-app-v1.js').read_text();test('零运行时API调用',"connect-src 'none'"in html and not re.search(r'\bfetch\s*\(|XMLHttpRequest|WebSocket',js));test('没有上传或存档写入',not re.search(r'<form|type=[\"\']file|localStorage\.(?:setItem|removeItem)|showSaveFilePicker',html));test('数据完整内嵌','__SAVE_DATA__'not in html and'/*__APP__*/'not in html);test('说明多语言别名非全覆盖','别名非全覆盖'in html)
print(json.dumps({'checks':len(checks),'passed':sum(c['pass']for c in checks),'tests':checks,'meta':D['meta']},ensure_ascii=False,indent=2))
