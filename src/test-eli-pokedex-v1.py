#!/usr/bin/env python3
"""本地图鉴数据与成品一致性测试；不联网、不改收集记录。"""
import base64,json,pathlib,re
P=pathlib.Path(__file__).resolve().parent
D=json.loads((P/'eli-pokedex-data-v1.json').read_text());mons={p['id']:p for p in D['pokemon']};versions={v['id']:v for v in D['versions']};tests=[]
def check(name,value):
    tests.append({'name':name,'passed':bool(value)})
    assert value,name
check('807个连续全国编号',sorted(mons)==list(range(1,808)))
check('22个指定作品版本',len(versions)==22 and set(v['platform'] for v in versions.values())=={'GBA','NDS','3DS'})
check('主地点、分区与条件无未翻译项',all(not x for x in D['meta']['untranslated'].values()))
check('图像全部内嵌PNG',all(p['img'].startswith('data:image/png;base64,') and base64.b64decode(p['img'].split(',')[1]).startswith(b'\x89PNG') for p in mons.values()))
check('中文名称齐全',all(p['n'] for p in mons.values()))
check('所有遭遇引用有效',all(r[0] in versions and str(r[1]) in D['areas'] and str(r[2]) in D['methods'] and all(str(c) in D['conditions'] for c in r[6]) for rs in D['encounters'].values() for r in rs))
check('所有等级范围有效',all(1<=r[3]<=r[4]<=100 for rs in D['encounters'].values() for r in rs))
check('不发布超100%的概率',all(r[5] is None or 0<r[5]<=100 for rs in D['encounters'].values() for r in rs))
check('复杂机制不强行相加',all(r[5] is None for rs in D['encounters'].values() for r in rs if r[2] in [33,44,54,55]))
ralts=[r for r in D['encounters']['280'] if r[0]==9]
check('绿宝石拉鲁拉丝102号道路Lv4且4%',any(D['areas'][str(r[1])][0]==450 and r[3:6]==[4,4,4] for r in ralts))
gible=[r for r in D['encounters']['443'] if r[0]==14]
check('白金圆陆鲨默认非双插正确合并20%',any(r[5]==20 and r[6]==[8] for r in gible))
check('拉鲁拉丝第3世代没有妖精属性',mons[280]['g']['3']['t']==[14])
check('拉鲁拉丝第6世代有妖精属性',mons[280]['g']['6']['t']==[14,18])
check('耿鬼第6世代飘浮',mons[94]['g']['6']['a']==[[26,0]])
check('耿鬼第7世代诅咒之躯',mons[94]['g']['7']['a']==[[130,0]])
check('皮卡丘旧世代防御30、新世代40',mons[25]['g']['5']['s'][2]==30 and mons[25]['g']['6']['s'][2]==40)
check('ORAS不冒充完整地点库',all(versions[v]['note'] for v in [25,26]))
check('历史基础资料数据完整',all(len(p['g'][str(g)]['s'])==6 and p['g'][str(g)]['t'] for p in mons.values() for g in range(3,8)))
page=(P/'eli-pokedex-v1.html').read_text();data_match=re.search(r'<script id="pokedex-data" type="application/json">(.*?)</script>',page,re.S)
check('HTML内嵌数据与JSON一致',json.loads(data_match[1])==D)
check('HTML使用最新应用代码',(P/'eli-pokedex-app-v1.js').read_text() in page)
check('禁止运行时联网',"connect-src 'none'" in page and not re.search(r'fetch\(|XMLHttpRequest|WebSocket\(', (P/'eli-pokedex-app-v1.js').read_text()))
check('没有远程脚本或外部样式',not re.search(r'<script[^>]+src=|<link[^>]+stylesheet',page))
check('存在免责声明和许可',all(x in page for x in ['没有记录 ≠ 本作不能获得','All rights reserved.','All image contents within are Copyright The Pokémon Company.']))
print(json.dumps({'passed':len(tests),'total':len(tests),'tests':tests},ensure_ascii=False,indent=2))
