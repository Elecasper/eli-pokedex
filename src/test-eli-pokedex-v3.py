#!/usr/bin/env python3
"""离线回归检查；不下载、不运行游戏文件、不改浏览器存档。"""
import base64,gzip,io,json,pathlib,re
from PIL import Image
R=pathlib.Path(__file__).resolve().parent;D=json.loads((R/'eli-pokedex-data-v3.json').read_text());B=json.loads((R/'eli-pokedex-data-v2.json').read_text()if(R/'eli-pokedex-data-v2.json').exists()else gzip.decompress((R/'dex-base-v2.json.gz').read_bytes()).decode());checks=[]
def test(name,result):
 checks.append({'name':name,'pass':bool(result)})
 if not result:raise AssertionError(name)
roster=lambda v:set(D['rosters'][str(v)])
test('1025个唯一物种',[p['id']for p in D['pokemon']]==list(range(1,1026)))
test('32个作品版本加全国百科',len(D['versions'])==33)
test('10个NS版本',len([v for v in D['versions']if v['platform']=='NS'])==10)
for v,count in[(7,386),(12,493),(17,649),(23,721),(27,802),(28,802),(29,807),(30,807),(31,153),(32,153),(33,664),(34,664),(37,493),(38,493),(39,242),(40,733),(41,733),(47,364)]:test('版本'+str(v)+'支持名单数量',len(roster(v))==count)
test('无地点的小火龙仍在钻石名单',4 in roster(12)and not any(r[0]==12 for r in D['encounters'].get('4',[])))
test('无野生地点的美录坦仍在剑名单',808 in roster(33)and not any(r[0]==33 for r in D['encounters'].get('808',[])))
test('剑不收录小拉达、达克莱伊',19 not in roster(33)and 491 not in roster(33))
test('LetsGo仅关都151种和美录坦家族',roster(31)==set(range(1,152))|{808,809})
test('太阳不混入究极日月新物种',802 in roster(27)and 803 not in roster(27)and 807 in roster(29))
test('ZA不把表尾形态记录误当1001至1025物种',max(roster(47))<=1000 and not(roster(47)&set(range(1001,1026))))
test('阿尔宙斯包含仅地区形态可用的卡蒂狗',58 in roster(39)and 58 in D['rosterRegionalOnly']['39'])
test('全部名单合法编号',all(0<i<=1025 for rs in D['rosters'].values()for i in rs))
test('全部名单无重复',all(len(rs)==len(set(rs))for rs in D['rosters'].values()))
old_ids={v['id']for v in B['versions']};oldrows=lambda d:{sid:[r for r in rs if r[0]in old_ids]for sid,rs in d['encounters'].items()if any(r[0]in old_ids for r in rs)}
test('原22版本地点概率条件完整保留',oldrows(B)==oldrows(D))
test('原地点中文与分区不回退',all(D['areas'][aid]==a for aid,a in B['areas'].items()))
test('所有遭遇记录有合法地点和方式',all(str(r[1])in D['areas']and str(r[2])in D['methods']for rs in D['encounters'].values()for r in rs))
test('所有条件有中文标签',all(str(c)in D['conditions']for rs in D['encounters'].values()for r in rs for c in r[6]))
test('新增NS地点只属于所选游戏支持物种',all(int(sid)in roster(r[0])for sid,rs in D['encounters'].items()for r in rs if r[0]in[31,32,33,34]))
test('NS新表不制造未经换算的百分比',all(r[5]is None for rs in D['encounters'].values()for r in rs if r[0]in[31,32,33,34]))
test('无待翻译NS地点与条件',not D['meta']['nsMissingLocations']and not D['meta']['nsUntranslatedConditions'])
r=D['encounters']['280'];test('绿宝石拉鲁拉丝102道路4级4%',any(x[0]==9 and D['areas'][str(x[1])][1]=='102号道路'and x[3]==4 and x[4]==4 and x[5]==4 for x in r))
test('ORAS保留群战与普通区域补充',any(x[0]==25 and x[3]==2 for x in r)and any(x[0]==25 and x[2]==91 and x[3]==3 for x in r))
test('耿鬼历史特性保留',D['pokemon'][93]['g']['6']['a']!=D['pokemon'][93]['g']['7']['a'])
test('钻石迁移说明保留NDS硬件限制','3DS'in D['obtainNotes']['4']['12']['text']and'NDS'in D['obtainNotes']['4']['12']['text'])
# 裁透明边界不能替换精灵、补不存在的形态图或改变像素。
count=0
for a,b in zip(D['pokemon'],B['pokemon']):
 for x,y in zip([a]+a['forms'],[b]+b['forms']):
  if x.get('imageMissing'):test('缺失形态图仍明确标出 '+str(x['pid']),x.get('imageMissing')==y.get('imageMissing'));continue
  ims=[]
  for item in[x,y]:
   im=Image.open(io.BytesIO(base64.b64decode(item['img'].split(',',1)[1]))).convert('RGBA');ims.append(im.crop(im.getchannel('A').getbbox()))
  assert ims[0].size==ims[1].size and ims[0].tobytes()==ims[1].tobytes(),x.get('id',x.get('pid'))
  count+=1
test('全部'+str(count)+'张有效精灵图仅裁透明边界',count>1250)
html=(R/'eli-pokedex-v3.html').read_text();js=(R/'eli-pokedex-app-v3.js').read_text();guide=((R/'eli-handheld-v3/index.html')if(R/'eli-handheld-v3/index.html').exists()else R.parent/'handheld/index.html').read_text();books=((R/'eli-books-withdrawn-v3/index.html')if(R/'eli-books-withdrawn-v3/index.html').exists()else R.parent/'books/index.html').read_text()
test('旧收集筛选及地点记录筛选文案已移除','本作已收集'not in html and'本作有地点记录'not in html)
test('不改写或删除用户旧浏览器记录',not re.search(r'localStorage\.(?:setItem|removeItem|clear)',js))
test('保留原格式的可选旧记录导出',"schema:'eli-pokedex-catches-v1'"in js)
test('网页不调用网络API',"connect-src 'none'"in html and not re.search(r'\bfetch\s*\(|XMLHttpRequest|WebSocket',js))
test('新增VC中文菜单与安装步骤',all(s in guide for s in['Load ROM','Export CIA','FBI','HOME','128KiB','RTC']))
test('NDS明确是入口而非转换游戏',all(s in guide for s in['快捷入口','不能删除或移动','并非把NDS转换为原生3DS游戏','NDS Forwarder Generator']))
test('引导工具为Wiki所链Beta28作者包','hxvfg8cwrebi5gxeikokr/Debug.zip'in guide)
test('撤下页无EPUB、ZIP、假站登录外链',not re.search(r'href=[\"\'][^\"\']*(?:z-lib\.id|\.epub|\.zip)',books))
report={'checks':len(checks),'passed':sum(c['pass']for c in checks),'spritePixelChecks':count,'tests':checks,'method':'本地数据与文件检查；不代表掌机实测。'}
print(json.dumps(report,ensure_ascii=False,indent=2))
