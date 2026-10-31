async () => {
 const $=id=>document.getElementById(id),rows=[],sleep=()=>new Promise(r=>setTimeout(r,40)),record=(stage,extra={})=>{const ok=document.documentElement.scrollWidth<=innerWidth;rows.push({stage,viewport:innerWidth,document:document.documentElement.scrollWidth,pass:ok,...extra});if(!ok||extra.pass===false)throw Error('溢出或控件过小: '+stage+' '+JSON.stringify(rows.at(-1)));};
 if($('pokedex-data')){
  if($('info-dialog').open)$('info-dialog').close();if(document.body.classList.contains('show-detail'))$('mobile-back').click();$('reset').click();record('图鉴列表');
  const controls=[...document.querySelectorAll('.controls button,.controls select,.controls input,.appbar button,.pager button')].filter(e=>e.getBoundingClientRect().width>0);record('主要触控区',{minHeight:Math.min(...controls.map(e=>e.getBoundingClientRect().height)),pass:controls.every(e=>e.getBoundingClientRect().height>=44)});
  document.querySelector('[data-mon]').click();for(const t of['where','stats','moves','family']){document.querySelector('[data-tab="'+t+'"]').click();await sleep();record('详情-'+t,{contentWidth:$('tab-content').clientWidth,contentScroll:$('tab-content').scrollWidth,pass:$('tab-content').scrollWidth<=$('tab-content').clientWidth+1});}
  if(document.body.classList.contains('show-detail'))$('mobile-back').click();$('filters-open').click();record('展开筛选');$('filters-open').click();$('info-open').click();document.querySelectorAll('#info-dialog details').forEach(d=>d.open=true);record('完整资料说明',{client:$('info-dialog').clientWidth,scroll:$('info-dialog').scrollWidth,pass:$('info-dialog').scrollWidth<=$('info-dialog').clientWidth+1});$('info-close').click();
 }else if(document.querySelector('[data-tab="vc"]')){
  for(const t of['vc','nds','gba','saves']){document.querySelector('[data-tab="'+t+'"]').click();await sleep();record('教程-'+t);document.querySelector('#content details').open=true;record('教程展开说明-'+t);}
  const controls=[...document.querySelectorAll('button,.actions a,summary')].filter(e=>e.getBoundingClientRect().width>0);record('教程触控区',{minHeight:Math.min(...controls.map(e=>e.getBoundingClientRect().height)),pass:controls.every(e=>e.getBoundingClientRect().height>=44)});
 }else record('图书入口撤下页');
 return {width:innerWidth,height:innerHeight,rows,pass:rows.every(r=>r.pass),method:'Chrome视口模拟，非真机测试'};
}
