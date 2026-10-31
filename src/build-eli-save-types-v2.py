#!/usr/bin/env python3
"""GPL-3.0. Extend fixed v1 metadata; never read/download game or save files.
Hardware facts in the original records remain unchanged. Grouping is presentation only.
"""
import collections, datetime, gzip, hashlib, json, pathlib, re, unicodedata
R=pathlib.Path(__file__).resolve().parent
OUT=R/'eli-save-types-v2'
OUT.mkdir(exist_ok=True)
if (OUT/'index.html').exists(): raise FileExistsError(OUT/'index.html')
base=R/'eli-save-types-base-v1.json.gz'
D=json.loads(gzip.decompress(base.read_bytes()))
base_meta=dict(D['meta'])
manual=json.loads((R/'eli-save-name-aliases-v1.json').read_text())
curated={(p,k) for p,k,*_ in manual['pokemon']+manual['games']}
def canonical(name):
    name=name.split(' (',1)[0]
    return ''.join(c for c in unicodedata.normalize('NFKD',name).casefold() if c.isalnum())
for g in D['records']:
    # Only explicitly curated game identities can bridge different localized titles.
    g['family']='curated:'+g['code'][:3] if (g['platform'],g['code'][:3]) in curated else 'title:'+canonical(g['variants'][0]['name'])
    g['kind']='original'
hacks=json.loads((R/'eli-save-hacks-v2.json').read_text())
evidence=json.loads((R/'eli-save-hack-profile-evidence-v2.json').read_text())
profiles={p['game']:p for p in evidence}
for h in hacks['records']:
    assert all(s['url'].startswith('https://') for s in h['sources'])
    profile=profiles.get(h.get('profile'))
    if h['bytes'] is not None:
        assert h['type']=='FLASH' and h['bytes']==131072
        assert (profile and profile['flashSize']==h['bytes']) or h.get('basis'), h['key']
    hashes=profile['identity'].get('rom_sha256',[]) if profile else []
    g={'id':len(D['records']),'kind':'hack','family':'hack:'+h['key'],'platform':'GBA','code':'',
       'display':h['display'],'aliases':sorted(set(h['aliases']+[h['display']])),'scope':h['scope'],
       'type':h['type'],'bytes':h['bytes'],'rtc':h['rtc'],'match':'reference','oaf':None,'hardware':'',
       'warnings':h['warnings'],'sources':h['sources'],
       'variants':[{'name':h['display']+' · '+h['scope'],'region':'World','sha1':'','crc32':'','sha256':s} for s in hashes or ['']]}
    D['records'].append(g)
# Expand the existing standalone traditional->simplified map for new hack names.
D['charmap'].update({'銀':'银','進':'进','紅':'红','釋':'释','夢':'梦','寶':'宝','國':'国','際':'际','體':'体','靈':'灵','獸':'兽'})
keys=[]
for g in D['records']:
    keys.append(('unknown',g['id']) if g['bytes'] is None else (g['kind'],g['platform'],g['family'],g['type'],g['bytes'],g['rtc']))
D['meta'].update({'schema':'eli-save-types-v2','builtAt':datetime.date.today().isoformat(),
    'originalVersions':base_meta['versions'],'originalGroups':base_meta['groups'],'originalKnownVersions':base_meta['knownVersions'],
    'versions':sum(len(g['variants']) for g in D['records']),'groups':len(D['records']),
    'knownVersions':sum(len(g['variants']) for g in D['records'] if g['bytes'] is not None),
    'gbaKnownVersions':sum(len(g['variants']) for g in D['records'] if g['platform']=='GBA' and g['bytes'] is not None),
    'cjkAliasGroups':base_meta['cjkAliasGroups']+len(hacks['records']),
    'hackEntries':len(hacks['records']),'hackKnownCapacity':sum(h['bytes'] is not None for h in hacks['records']),
    'sourceRecordGroups':len(D['records']),'displayGroups':len(set(keys)),
    'baseDataGzipSHA256':hashlib.sha256(base.read_bytes()).hexdigest(),
    'grouping':'Same explicit game identity + known protocol/capacity + identical RTC label; unknown type/capacity never merged. Sources/identifiers stay per variant.',
    'disclaimer':'原版配置与标明版本的改版资料参考；待核验不代表不需要，配置相同不代表存档互通。'})
manifest=json.loads((R/'eli-save-types-base-sources-v1.json').read_text())
manifest += [{'kind':'hack-profile-evidence',**p} for p in evidence]
manifest += [{'kind':'hack-reference','game':h['display'],'scope':h['scope'],'sources':h['sources']} for h in hacks['records']]
def dump(name,value): (OUT/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
data=json.dumps(D,ensure_ascii=False,separators=(',',':'))
(OUT/'data.json').write_text(data+'\n')
dump('hacks.json',hacks);dump('sources.json',manifest)
template=(R/'eli-save-types-template-v2.html').read_text()
app=(R/'eli-save-types-app-v2.js').read_text()
(OUT/'index.html').write_text(template.replace('__SAVE_DATA__',data.replace('<','\\u003c')).replace('/*__APP__*/',app))
print(json.dumps(D['meta'],ensure_ascii=False,indent=2))
