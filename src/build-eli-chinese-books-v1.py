#!/usr/bin/env python3
"""构建中文书架。仅收录经核对的古腾堡中文公版底本，保留PG许可。
需 /tmp/eli-books-venv/bin/python3（opencc-python-reimplemented）。
不抓取付费小说，不提取平台正文。下载只做一次并缓存。
"""
import concurrent.futures,datetime,hashlib,io,json,pathlib,re,urllib.request,urllib.parse,xml.etree.ElementTree as ET,zipfile
from opencc import OpenCC
ROOT=pathlib.Path(__file__).resolve().parent;OUT=ROOT/'eli-chinese-books-v1';CACHE=pathlib.Path('/tmp/eli-chinese-books-source-v1');CC=OpenCC('t2s')
BOOKS=[
(24264,'红楼梦','曹雪芹','古典长篇','贾府兴衰与人物群像。'),(23962,'西游记','吴承恩','古典长篇','取经路上的神魔与世情。'),(23950,'三国演义','罗贯中','古典长篇','东汉末年至三国的历史演义。'),(23863,'水浒传','施耐庵','古典长篇','七十回底本，梁山群像与江湖命运。'),(24032,'儒林外史','吴敬梓','古典长篇','读书人与科举世相。'),(51828,'聊斋志异','蒲松龄','志怪短篇','狐鬼故事中的人情冷暖。'),(25377,'镜花缘','李汝珍','古典长篇','海外奇游与才女故事。'),(23850,'老残游记','刘鹗','近代小说','行医见闻中的晚清社会。'),(27166,'呐喊','鲁迅','现代小说','收有《狂人日记》《阿Q正传》等。'),(24042,'彷徨','鲁迅','现代小说','收有《祝福》《伤逝》等。'),(25271,'朝花夕拾','鲁迅','散文','回望童年、求学与旧人旧事。'),(25242,'野草','鲁迅','散文','鲁迅的散文诗集。')]
NS='http://www.w3.org/1999/xhtml';DC='http://purl.org/dc/elements/1.1/'
def fetch(url,path):
 if not path.exists():
  req=urllib.request.Request(url,headers={'User-Agent':'Eli-Chinese-Reading-Shelf/1.0 (small curated public-domain collection)'})
  path.write_bytes(urllib.request.urlopen(req,timeout=60).read())
 return path.read_bytes()
def build_book(b):
 num,title,author,genre,desc=b;p=CACHE/f'{num}.html';raw=fetch(f'https://www.gutenberg.org/ebooks/{num}',p).decode();assert 'Public domain in the USA' in raw,num
 m=re.search(r'href="([^"]+\.epub3\.images)"',raw)
 if not m:raise ValueError('EPUB3 link missing: '+str(num))
 url=urllib.parse.urljoin('https://www.gutenberg.org',m[1]);original=fetch(url,CACHE/f'{num}.epub');source=zipfile.ZipFile(io.BytesIO(original));assert sum(i.file_size for i in source.infolist())<25000000
 name=f'pg-{num}-zh-hans.epub';dest=OUT/'files'/name;processed=[];alltext=[];changed=False;note_added=False
 for info in source.infolist():
  body=source.read(info.filename)
  if info.filename.lower().endswith(('.xhtml','.html','.htm','.opf','.ncx')):
   try:doc=ET.fromstring(body)
   except ET.ParseError as e:raise ValueError(f'{num}/{info.filename}: invalid XML {e}')
   for n in doc.iter():
    if n.text:n.text=CC.convert(n.text)
    if n.tail:n.tail=CC.convert(n.tail)
    for key in ['title','alt']:
     if key in n.attrib:n.set(key,CC.convert(n.get(key)))
    if n.tag in [f'{{{DC}}}language']:n.text='zh-Hans'
    if 'lang' in n.attrib:n.set('lang','zh-Hans')
    if '{http://www.w3.org/XML/1998/namespace}lang' in n.attrib:n.set('{http://www.w3.org/XML/1998/namespace}lang','zh-Hans')
   # 只改可见文字，不改锚点ID、href、文件名，保留目录链接。
   alltext.append(''.join(doc.itertext()))
   body=ET.tostring(doc,encoding='utf-8',xml_declaration=True);changed=True
  processed.append((info.filename,body))
 # 保留原PG正文、许可与制作人员信息；新增独立修改说明，不冒称官方简体校勘版。
 readme=f'《{title}》简体阅读版\n作者：{author}\n底本：https://www.gutenberg.org/ebooks/{num}\n\n由Eli书架使用OpenCC做繁简转换，未做校勘。正文、章节与完整PG许可保留。原版可能含底本错误、古字、异体字及版本差异；本文件不是现代校注版，也不是古腾堡官方新版本。\n美国公版状态已核对，其他地区请确认当地版权期限。\n'
 with zipfile.ZipFile(dest,'x',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
  z.writestr('mimetype',source.read('mimetype'),compress_type=zipfile.ZIP_STORED)
  for n,body in processed:
   if n!='mimetype':z.writestr(n,body)
  z.writestr('META-INF/ELI-READING-NOTE.txt',readme)
 plain='\n'.join(alltext)
 assert 'PROJECT GUTENBERG' in plain.upper(),num
 assert len(plain)>5000,num
 # EPUB内部许可完整保留，不把现代校注/封面混入本项目。
 return {'id':num,'title':title,'author':author,'genre':genre,'desc':desc,'file':'files/'+name,'bytes':dest.stat().st_size,'source':f'https://www.gutenberg.org/ebooks/{num}','sourceEpub':url,'originalSHA256':hashlib.sha256(original).hexdigest(),'simplifiedSHA256':hashlib.sha256(dest.read_bytes()).hexdigest(),'characters':len(plain),'version':'按古腾堡收录底本全文；繁简转换，未校勘','chapterCount':{24264:120,23962:100,23950:120,23863:70,24032:56,25377:100,23850:20}.get(num),'extent':str({24264:120,23962:100,23950:120,23863:70,24032:56,25377:100,23850:20}[num])+'回底本' if num in {24264,23962,23950,23863,24032,25377,23850} else '作品集底本'}
if OUT.exists():raise FileExistsError(OUT)
OUT.mkdir();(OUT/'files').mkdir();CACHE.mkdir(exist_ok=True)
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:books=list(ex.map(build_book,BOOKS))
(OUT/'sources.json').write_text(json.dumps({'builtAt':datetime.date.today().isoformat(),'notice':'中文公版底本，繁简转换，不含现代校注。版权以所在地为准。','books':books},ensure_ascii=False,indent=2)+'\n')
page='''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="color-scheme" content="light"><meta http-equiv="Content-Security-Policy" content="default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; img-src data:; connect-src 'none'; form-action 'none'"><title>Eli的中文书架</title><style>
*{box-sizing:border-box}body{margin:0;background:#f5f3eb;color:#253f36;font:16px/1.6 -apple-system,BlinkMacSystemFont,'PingFang SC','Microsoft YaHei',sans-serif}main{max-width:1040px;margin:auto;padding:28px 24px 50px}header{display:flex;justify-content:space-between;align-items:center;gap:14px}h1{margin:0;font-size:30px}p{margin:8px 0}a{color:#285c43}button,a,input{font:inherit}button{cursor:pointer}a.action,button{min-height:44px;border:1px solid #cbd6c4;border-radius:9px;padding:9px 14px;background:#fff;color:#285c43;text-decoration:none;display:inline-flex;align-items:center;justify-content:center}a.primary{background:#315e47;color:white;border-color:#315e47}a:focus-visible,button:focus-visible,input:focus-visible{outline:3px solid #c58a35;outline-offset:3px}.sub{color:#647665;font-size:14px}.search{margin:20px 0 10px;display:flex;gap:10px}input{border:1px solid #cbd6c4;border-radius:10px;background:#fff;padding:12px;width:100%;min-height:46px;color:#253f36}.filters{display:flex;gap:7px;flex-wrap:wrap}.filters button{font-size:13px;min-height:44px;padding:7px 11px}.filters button[aria-pressed=true]{background:#e2ead8;border-color:#71916a}.status{font-size:12px;color:#66745e;margin:15px 0 10px}.grid{display:grid;grid-template-columns:1fr 1fr;gap:13px}.book{background:#fff;border:1px solid #dce2d4;border-radius:13px;padding:17px;display:grid;grid-template-columns:52px 1fr;gap:13px;min-width:0}.cover{background:var(--cover);border-radius:3px 7px 7px 3px;box-shadow:inset 5px 0 #0002;min-height:76px;color:#fff;display:flex;align-items:center;justify-content:center;writing-mode:vertical-rl;letter-spacing:3px;font-size:14px;padding:9px 8px;text-align:center;align-self:start}.book h2{font-size:21px;margin:0;line-height:1.4}.meta{color:#79816f;font-size:12px;margin:3px 0}.desc{font-size:13px;margin:5px 0 10px}.actions{display:flex;gap:10px;align-items:center;flex-wrap:wrap}.actions a{font-size:12px}.source{padding:10px 0;min-height:44px;display:inline-flex;align-items:center}.pager{display:flex;gap:12px;justify-content:center;align-items:center;margin-top:20px}.pager span{font-size:13px}button:disabled{opacity:.4;cursor:default}details{margin-top:22px;color:#68765f;font-size:12px}summary{cursor:pointer;min-height:44px;display:flex;align-items:center;font-size:13px}details p{line-height:1.8}.new-books{margin-top:20px;border-top:1px solid #d8dece;padding-top:18px}.new-books h2{font-size:18px;margin:0 0 6px}.new-books p{font-size:13px}.new-links{display:flex;gap:9px;flex-wrap:wrap;margin-top:10px}.toplinks{display:flex;gap:8px}.toplinks a{font-size:12px;white-space:nowrap}.empty{grid-column:1/-1;padding:40px;text-align:center;font-size:14px}@media(max-width:640px){main{padding:18px 14px 32px}header{align-items:flex-start}h1{font-size:25px}.toplinks{flex-direction:column;gap:5px}.toplinks a{padding:7px 10px;min-height:44px}.sub{font-size:13px;max-width:260px}.grid{grid-template-columns:1fr;gap:10px}.book{padding:14px;gap:12px}.book h2{font-size:20px}.search{margin-top:15px}.actions a{font-size:13px}.filters button{font-size:12px}.new-links a{font-size:13px}input{font-size:16px}}
</style></head><body><main><header><div><h1>Eli的中文书架</h1><p class="sub">中文小说、散文与古典文学。选一本，下载简体EPUB。</p></div><nav class="toplinks"><a class="action" href="https://elecasper.github.io/eli-pokedex/">宝可梦图鉴</a><a class="action" href="https://www.amazon.com/sendtokindle" target="_blank" rel="noopener">发送到Kindle</a></nav></header><div class="search"><input id="q" type="search" aria-label="搜索书名或作者" placeholder="搜索书名或作者，例如：鲁迅"></div><div id="filters" class="filters" aria-label="文学分类"></div><p id="status" class="status" aria-live="polite"></p><section class="grid" id="grid" aria-label="可下载的中文文学"></section><nav class="pager"><button id="prev">← 上一页</button><span id="page"></span><button id="next">下一页 →</button></nav><section class="new-books"><h2>想看较新的中文小说？</h2><p>去正版中文平台找。免费、完结和下载权限以平台为准，在线免费阅读不等于可下载EPUB。</p><div class="new-links"><a class="action" href="https://m.qidian.com/" target="_blank" rel="noopener">起点中文网</a><a class="action" href="https://weread.qq.com/" target="_blank" rel="noopener">微信读书</a></div></section><details><summary>底本、版权与Kindle导入说明</summary><p>这些文件来自Project Gutenberg明确标为美国公版的中文原文底本，已做繁简转换，未做校勘，保留原有完整许可。不是现代校注本，其他地区请按所在地版权期限判断。各书的“底本信息”可查原始版本，不把残篇冒充补全本。</p><p>EPUB先保存在手机“文件”或电脑里，再上传Send to Kindle，掌机联网同步。同一亚马逊账号；不要把EPUB直接用USB拷进Kindle。古籍中的异体字可能因设备字体而显示不同。</p><p>近年商业小说只提供正版平台入口，不提供盗版整本、网盘资源或DRM绕过。</p></details></main><script id="book-data" type="application/json">__DATA__</script><script>
const B=JSON.parse(document.getElementById('book-data').textContent),$=id=>document.getElementById(id);let cat='全部',page=0;const colors=['#586b4b','#8b5a44','#565f77','#8d7047','#496e67','#74566c'],escape=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));function draw(){const q=$('q').value.trim().toLowerCase(),list=B.filter(b=>(cat==='全部'||b.genre===cat)&&(!q||(b.title+b.author+b.genre+b.desc+b.extent).toLowerCase().includes(q))),pages=Math.max(1,Math.ceil(list.length/6));page=Math.min(page,pages-1);$('filters').innerHTML=['全部',...new Set(B.map(b=>b.genre))].map(c=>`<button data-cat="${c}" aria-pressed="${cat===c}">${c}</button>`).join('');$('status').textContent=`${list.length} 本 · 按收录底本全文 · 简体阅读版`; $('grid').innerHTML=list.slice(page*6,page*6+6).map((b,i)=>`<article class="book"><div class="cover" style="--cover:${colors[(page*6+i)%colors.length]}" aria-hidden="true">中文文学</div><div><h2>${escape(b.title)}</h2><p class="meta">${escape(b.author)} · ${escape(b.genre)} · ${escape(b.extent)}</p><p class="desc">${escape(b.desc)}</p><div class="actions"><a class="action primary" href="${b.file}" download="${escape(b.title)}-简体.epub">简体EPUB · ${b.bytes<1048576?Math.round(b.bytes/1024)+' KB':(b.bytes/1048576).toFixed(1)+' MB'}</a><a class="source" href="${b.source}" target="_blank" rel="noopener">底本信息 ↗</a></div></div></article>`).join('')||'<p class="empty">没有匹配的书，试试作者名或清空搜索。</p>';$('prev').disabled=page===0;$('next').disabled=page>=pages-1;$('page').textContent=`${page+1} / ${pages}`;}$('q').addEventListener('input',()=>{page=0;draw()});$('filters').addEventListener('click',e=>{const b=e.target.closest('[data-cat]');if(b){cat=b.dataset.cat;page=0;draw()}});$('prev').onclick=()=>{page--;draw();$('grid').scrollIntoView({block:'start'})};$('next').onclick=()=>{page++;draw();$('grid').scrollIntoView({block:'start'})};draw();
</script></body></html>'''
(OUT/'index.html').write_text(page.replace('__DATA__',json.dumps(books,ensure_ascii=False).replace('<','\\u003c')))
print(json.dumps({'books':len(books),'bytes':sum(b['bytes'] for b in books),'files':[{'title':b['title'],'id':b['id'],'characters':b['characters'],'chapter120':b['chapter120'],'chapter100':b['chapter100']} for b in books]},ensure_ascii=False,indent=2))
