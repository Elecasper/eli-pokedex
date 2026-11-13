"""Fetch StrategyWiki pages + image thumbs into <guide>/source. Usage: fetch_sw.py <guide dir> <game title> <page>..."""
import json,re,sys,urllib.request,urllib.parse
from pathlib import Path
d=Path(sys.argv[1]);T=sys.argv[2]+'/';src=d/'source';src.mkdir(exist_ok=True)
def api(p):
    u='https://strategywiki.org/w/api.php?'+urllib.parse.urlencode({'format':'json',**p})
    return json.load(urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'EliSiteGuideTranslate/1.0'})))
mf=src/'meta.json';meta=json.loads(mf.read_text()) if mf.exists() else {}
imf=src/'images.json';imgs=json.loads(imf.read_text()) if imf.exists() else {}
need=set()
for p in sys.argv[3:]:
    q=api({'action':'query','prop':'revisions','rvprop':'ids|timestamp|content','rvslots':'main','titles':T+p,'redirects':1})
    pg=next(iter(q['query']['pages'].values()));r=pg['revisions'][0];w=r['slots']['main']['*']
    fn=re.sub(r'[^A-Za-z0-9]+','-',p).strip('-').lower()
    (src/f'{fn}.wikitext').write_text(w)
    meta[fn]={'title':pg['title'],'revid':r['revid'],'timestamp':r['timestamp'],'bytes':len(w)}
    need|={x.strip() for x in re.findall(r'\[\[File:([^|\]]+)',w)}-set(imgs)
    print(fn,r['revid'],len(w))
need=sorted(need)
for i in range(0,len(need),40):
    q=api({'action':'query','prop':'imageinfo','iiprop':'url|size','iiurlwidth':640,'titles':'|'.join('File:'+x for x in need[i:i+40])})
    n={x['from']:x['to'] for x in q['query'].get('normalized',[])}
    info={p['title']:p.get('imageinfo',[{}])[0] for p in q['query']['pages'].values()}
    for x in need[i:i+40]:
        im=info.get(n.get('File:'+x,'File:'+x),{})
        imgs[x]={'thumb':im.get('thumburl'),'w':im.get('thumbwidth'),'h':im.get('thumbheight'),'page':im.get('descriptionurl')}
mf.write_text(json.dumps(meta,indent=1));imf.write_text(json.dumps(imgs,indent=1))
print('missing images:',[k for k,v in imgs.items() if not v['thumb']])
