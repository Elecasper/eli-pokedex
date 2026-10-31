#!/usr/bin/env python3
"""v2百科及中文EPUB的离线检查。只读，不改浏览器记录。"""
import base64,hashlib,json,pathlib,posixpath,re,urllib.parse,xml.etree.ElementTree as E,zipfile
R=pathlib.Path(__file__).resolve().parent;D=json.loads((R/'eli-pokedex-data-v2.json').read_text());B=json.loads((R/'eli-chinese-books-v1/sources.json').read_text());OLD=json.loads((R/'eli-pokedex-data-v1.json').read_text());tests=[]
def check(n,v):
 tests.append({'name':n,'passed':bool(v)})
 assert v,n
M={p['id']:p for p in D['pokemon']};V={v['id']:v for v in D['versions']}
check('1025个连续编号',sorted(M)==list(range(1,1026)))
check('22个游戏版本加百科模式',len(V)==23 and 0 in V)
check('所有默认种类有中文名',all(re.search('[\u4e00-\u9fff]',p['n'])for p in M.values()))
check('1025张默认图全部内嵌有效PNG',all(base64.b64decode(p['img'].split(',')[1]).startswith(b'\x89PNG')for p in M.values()))
check('310条特殊形态资料',sum(len(p['forms'])for p in M.values())==310)
check('缺图明确区分',all(bool(f['img'])!=bool(f['imageMissing'])for p in M.values()for f in p['forms']))
check('基本资料都有3至9世代字段',all(all(str(g)in p['g']and len(p['g'][str(g)]['s'])==6 for g in range(3,10))for p in M.values()))
check('属性引用都存在',all(str(t)in D['types']for p in M.values()for d in p['g'].values()for t in d['t']))
check('努力值引用有效',all(1<=int(k)<=6 for p in M.values()for k in p['effort']))
check('原有地点未丢失',all(all(r in D['encounters'][sid]for r in rs)for sid,rs in OLD['encounters'].items()))
check('4117条区域补充',sum(10000 in r[6]for rs in D['encounters'].values()for r in rs)==4117)
check('区域补充不伪造概率',all(r[5]is None for rs in D['encounters'].values()for r in rs if 10000 in r[6]))
check('所有遭遇引用有效',all(r[0]in V and str(r[1])in D['areas']and str(r[2])in D['methods']and all(str(c)in D['conditions']for c in r[6])for rs in D['encounters'].values()for r in rs))
check('等级合法',all(1<=r[3]<=r[4]<=100 for rs in D['encounters'].values()for r in rs))
check('绿宝石拉鲁拉丝4%',any(r[0]==9 and r[3:6]==[4,4,4]for r in D['encounters']['280']))
check('ORAS普通拉鲁拉丝未被群聚记录覆盖',any(r[0]==25 and r[2]==91 and r[3]==3 and 10000 in r[6]for r in D['encounters']['280']))
check('钻石小火龙有迁移说明',all('伙伴公园'in D['obtainNotes']['4'][str(v)]['text']and'3DS'in D['obtainNotes']['4'][str(v)]['text']for v in [12,13,14]))
check('较新中文特性作用267条',len(D['abilityDescriptions'])>=267)
check('较新中文招式作用826条',len(D['moveDescriptions'])>=826)
check('招式引用有效',all(str(r[1])in D['moves']for vs in D['learnsets'].values()for rs in vs.values()for r in rs))
check('桃歹郎招式可查',bool(D['learnsets'].get('1025',{}).get('25')))
check('超级喷火龙X为火龙',next(f for f in M[6]['forms']if f['pid']==10034)['g']['9']['t']==[10,16])
check('耿鬼第六代飘浮第七代诅咒之躯',M[94]['g']['6']['a']==[[26,0]]and M[94]['g']['7']['a']==[[130,0]])
check('12本中文文学',len(B['books'])==12 and all(re.search('[\u4e00-\u9fff]',b['title']+b['author'])for b in B['books']))
check('水浒标明70回本',next(b for b in B['books']if b['id']==23863)['chapterCount']==70)
check('红楼梦120回与西游100回',next(b for b in B['books']if b['id']==24264)['chapterCount']==120 and next(b for b in B['books']if b['id']==23962)['chapterCount']==100)
anchors_ok=0;local_refs_checked=0
for b in B['books']:
 path=R/'eli-chinese-books-v1'/b['file']
 check(b['title']+'文件指纹一致',hashlib.sha256(path.read_bytes()).hexdigest()==b['simplifiedSHA256'])
 with zipfile.ZipFile(path)as z:
  check(b['title']+'有效EPUB容器',z.namelist()[0]=='mimetype'and z.read('mimetype')==b'application/epub+zip'and z.getinfo('mimetype').compress_type==zipfile.ZIP_STORED)
  text=[];docs={}
  for file in z.namelist():
   if file.endswith(('.html','.xhtml','.opf','.ncx')):
    root=E.fromstring(z.read(file));docs[file]=root
    if file.endswith(('.html','.xhtml')):text.extend(root.itertext())
  alltext=''.join(text)
  check(b['title']+'许可与原文保留','PROJECT GUTENBERG'in alltext.upper()and len(re.findall('[\u4e00-\u9fff]',alltext))>8000)
  for file,root in docs.items():
   for node in root.iter():
    href=node.get('href')
    if not href or href.startswith(('http:','https:','mailto:','data:')):continue
    parsed=urllib.parse.urlsplit(href);target=posixpath.normpath(posixpath.join(posixpath.dirname(file),urllib.parse.unquote(parsed.path)))if parsed.path else file
    if not parsed.path or target in z.namelist():
     local_refs_checked+=1
     if parsed.fragment and target in docs:
      ids={n.get('id')or n.get('{http://www.w3.org/XML/1998/namespace}id')for n in docs[target].iter()}
      assert urllib.parse.unquote(parsed.fragment)in ids,(b['title'],file,href)
      anchors_ok+=1
check('EPUB原有目录与内部链接可解析',local_refs_checked>10)
page=(R/'eli-pokedex-v2.html').read_text();data=re.search(r'<script id="pokedex-data" type="application/json">(.*?)</script>',page,re.S)
check('内嵌百科数据一致',json.loads(data[1])==D)
check('内嵌最新应用代码',(R/'eli-pokedex-app-v2.js').read_text().replace('/*__DETAILS__*/',(R/'eli-pokedex-details-v2.js').read_text())in page)
check('禁止运行时联网',"connect-src 'none'"in page and not re.search('fetch\\(|XMLHttpRequest|WebSocket\\(', (R/'eli-pokedex-app-v2.js').read_text()))
print(json.dumps({'passed':len(tests),'total':len(tests),'epubAnchorsChecked':anchors_ok,'epubInternalLinksChecked':local_refs_checked,'tests':tests},ensure_ascii=False,indent=2))
