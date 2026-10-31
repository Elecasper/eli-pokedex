// GPL-3.0. Node: original-fact preservation, grouping boundaries, exact lookup.
const fs=require('fs'),vm=require('vm'),assert=require('assert'),zlib=require('zlib'),path=require('path');
const R=__dirname,D=JSON.parse(fs.readFileSync(path.join(R,'eli-save-types-v2/data.json'))),base=JSON.parse(zlib.gunzipSync(fs.readFileSync(path.join(R,'eli-save-types-base-v1.json.gz'))));
let checks=0;function test(name,condition){assert(condition,name);checks++;}
for(const old of base.records){const n=D.records.find(g=>g.id===old.id);test('Original facts preserved '+old.id,JSON.stringify(Object.fromEntries(Object.keys(old).map(k=>[k,n[k]])))===JSON.stringify(old));}
const nodes=new Map(),document={getElementById(id){if(!nodes.has(id))nodes.set(id,{textContent:id==='save-data'?JSON.stringify(D):'',value:'',innerHTML:'',addEventListener(){}});return nodes.get(id);},querySelectorAll(){return[];}};
const hooks={},ctx={document,location:{hash:'',pathname:'/save-types/',search:''},history:{replaceState(){}},URLSearchParams,setTimeout,clearTimeout,__ELI_SAVE_TEST__:hooks};vm.createContext(ctx);vm.runInContext(fs.readFileSync(path.join(R,'eli-save-types-app-v2.js'),'utf8'),ctx);
const query=(q,platform='all',region='all')=>{Object.assign(hooks.state,{q,platform,region});return hooks.findMatches();};
let result=query('绿宝石');test('Emerald six codes collapse to one',result.length===1&&result[0].codes.length===6);test('All Emerald variants retained',result[0].variants.length===base.records.filter(g=>g.code.startsWith('BPE')).reduce((n,g)=>n+g.variants.length,0));test('Emerald remains Flash128 RTC',result[0].bytes===131072&&result[0].rtc===true);
for(const q of ['綠寶石','Pokemon Emerald','Pokémon Emerald','ポケットモンスター エメラルド']){const known=query(q).filter(g=>g.bytes!==null);test('Multilingual merged '+q,known.length===1&&known[0].codes.length===6);}
result=query('绿宝石','GBA','Japan');test('Regional filter restricts variant detail',result.length===1&&result[0].codes.join()==='BPEJ'&&result[0].variants.every(v=>v.region==='Japan'));
for(const q of ['BPEE','AGB-BPEE-USA','f3ae088181bf583e55daf962a92bb46f4f1d07b7'])test('Exact identity '+q,query(q)[0].codes.join()==='BPEE');
result=query('AXVE');test('Cross-platform code collision isolated',result.length===2&&new Set(result.map(g=>g.platform)).size===2);test('Never assign Disney Ruby capacity',result.find(g=>g.platform==='NDS').bytes===65536&&result.find(g=>g.platform==='GBA').bytes===131072);
for(const q of ['漆黑的魅影','水银','水銀','解放','Unbound','激进红'])test('Hack searchable '+q,query(q).filter(g=>g.kind==='hack').length===1&&query(q)[0].kind==='hack');
test('Mercury is not Liquid Crystal',query('水银')[0].family==='hack:azoth-fc'&&query('Liquid Crystal').every(g=>g.family!=='hack:azoth-fc'));
test('Unverified hacks do not inherit base game capacity',query('漆黑的魅影')[0].bytes===null&&query('水银')[0].bytes===null);
test('Unbound capacity and version are explicit',query('Unbound')[0].bytes===131072&&query('Unbound')[0].scope.includes('2.1.1.1'));
test('Radical Red RTC does not inherit FireRed',query('Radical Red')[0].rtc===null);
const h=query('Unbound')[0];test('Exact hack SHA256 supported',query(h.variants[0].sha256)[0].family===h.family);test('Original BPRE does not claim hack support',query('BPRE').every(g=>g.kind==='original'));
const sample={...D.records.find(g=>g.bytes!==null),id:90000,family:'synthetic',variants:[{name:'Test',region:'USA',sha1:'a'.repeat(40)}],warnings:[]};
const make=(overrides,id)=>({...sample,...overrides,id});
for(const [name,overrides] of Object.entries({capacity:{bytes:sample.bytes+512},protocol:{type:sample.type==='EEPROM'?'FLASH':'EEPROM'},clock:{rtc:sample.rtc===true?false:true},platform:{platform:sample.platform==='GBA'?'NDS':'GBA'},game:{family:'other'},kind:{kind:'hack'}}))test('Different '+name+' stays separate',hooks.makeCards([sample,make(overrides,90001)]).length===2);
test('Same known facts merge across code, source and vendor enum',hooks.makeCards([sample,make({code:'ZZZZ',match:'code',oaf:null},90002)]).length===1);
test('Unknown types never establish equivalence',hooks.makeCards([make({bytes:null},90003),make({bytes:null},90004)]).length===2);
for(const g of query('宝可梦'))for(const m of g.members)test('Every member shares summary facts '+m.id,g.type===m.type&&g.bytes===m.bytes&&g.rtc===m.rtc&&g.family===m.family&&g.platform===m.platform);
test('Unique hack profile references',D.records.filter(g=>g.kind==='hack').length===4);
const report={checks,passed:checks,originalRecords:base.records.length,sourceRecords:D.records.length,displayGroups:D.meta.displayGroups};fs.writeFileSync(path.join(R,'eli-save-types-data-checks-v2.json'),JSON.stringify(report,null,2));console.log(JSON.stringify(report));
