// Native workbench components; all external labels use textContent.
const e=(tag,cls='',text='')=>{const n=document.createElement(tag);n.className=cls;n.textContent=text;return n;};
const svg=(tag,attrs)=>{const n=document.createElementNS('http://www.w3.org/2000/svg',tag);for(const [k,v]of Object.entries(attrs))n.setAttribute(k,v);return n;};
const btn=(text,fn)=>{const b=e('button','button secondary',text);b.type='button';b.onclick=async()=>{b.disabled=true;try{await fn();}catch(x){alert(x.message);}finally{b.disabled=false;}};return b;};
const colors={bilibili:'#53bdb6',xiaoheihe:'#9b81e9',netease:'#e6b164'};
export function renderEventBoard(container,state,{name,accountName,time,open}){
 container.replaceChildren();const day=state.day_start,end=state.day_end,now=Date.now()/1000;
 const tasks=(state.tasks||[]).filter(t=>t.end>day&&t.start<end&&!['cancelled','skipped'].includes(t.state)).sort((a,b)=>a.start-b.start);
 const left=e('section','panel event-ring-panel'),right=e('section','panel today-events');left.append(e('h2','','24 小时时刻事件环'));
 const ring=svg('svg',{viewBox:'0 0 420 420',role:'img','aria-label':'今日各平台活动时段，环图旁列表可查看详情'});
 ring.append(svg('circle',{cx:210,cy:210,r:151,fill:'none',stroke:'#f0f1f6','stroke-width':13}));
 const point=(seconds,r)=>{const a=(seconds-day)/(end-day)*Math.PI*2-Math.PI/2;return [210+Math.cos(a)*r,210+Math.sin(a)*r];};
 for(let h=0;h<24;h++){const a=h/24*Math.PI*2-Math.PI/2;ring.append(svg('line',{x1:210+Math.cos(a)*178,y1:210+Math.sin(a)*178,x2:210+Math.cos(a)*(h%6?184:190),y2:210+Math.sin(a)*(h%6?184:190),stroke:'#cbd0df','stroke-width':h%6?1:2}));if(h%6===0){const p=[210+Math.cos(a)*200,210+Math.sin(a)*200];const text=svg('text',{x:p[0],y:p[1]+4,'text-anchor':'middle',fill:'#969db3','font-size':12});text.textContent=String(h).padStart(2,'0');ring.append(text);}}
 const lanes=[];
 for(const task of tasks){const a=Math.max(day,task.start),b=Math.min(end,task.end);let lane=lanes.findIndex(v=>v<=a);if(lane<0){lane=lanes.length;lanes.push(b);}else lanes[lane]=b;const r=Math.max(85,151-lane*16);const angle=Math.min(.999999,(b-a)/(end-day));const [x,y]=point(a,r),[u,v]=point(a+angle*(end-day),r);const path=svg('path',{d:`M ${x} ${y} A ${r} ${r} 0 ${angle>.5?1:0} 1 ${u} ${v}`,fill:'none',stroke:colors[task.provider]||'#8797bf','stroke-width':10,'stroke-linecap':'round',opacity:['succeeded','expired'].includes(task.state)?.5:1});const title=svg('title',{});title.textContent=name(task.provider)+' · '+time(task.start)+'–'+time(task.end);path.append(title);ring.append(path);}
 const [x,y]=point(now,172);ring.append(svg('circle',{cx:x,cy:y,r:5,fill:'#4e526e'}));const current=e('div','ring-center');current.append(e('small','','当前时间'),e('strong','',time(now,true)),e('span','',tasks.some(t=>t.state==='executing')?'自主活动正在进行':tasks.some(t=>t.state==='planned'&&t.end>now)?'等待下一场活动':'今日暂无后续事件'));
 const graphic=e('div','ring-graphic');graphic.append(ring,current);left.append(graphic);const legend=e('div','ring-legend');for(const [pid,color]of Object.entries(colors)){const label=e('span','',name(pid));label.style.setProperty('--swatch',color);legend.append(label);}left.append(legend);
 const head=e('div','section-heading'),intro=e('div');intro.append(e('h2','','今日事件'),e('p','muted',tasks.filter(t=>t.state==='succeeded').length+' 已完成 · '+tasks.filter(t=>t.state==='planned').length+' 待执行'));head.append(intro);right.append(head);
 if(!tasks.length)right.append(e('div','empty','今天尚无主动事件。规划器会按允许时间窗、账号权限和活跃度安排。'));
 for(const task of tasks){const row=e('button','event-row');row.type='button';row.style.setProperty('--swatch',colors[task.provider]||'#8797bf');row.append(e('strong','',time(task.start,true)+' — '+time(task.end,true)),e('span','',name(task.provider)+' · '+accountName(task.provider,task.account)),e('small','',task.state==='planned'?'待执行':task.state==='executing'?'正在活动':task.state==='succeeded'?'已完成':task.state==='failed'?'失败':task.state==='expired'?'已错过':'待核对'));row.onclick=()=>open(task.provider);right.append(row);}
 container.append(left,right);
}
const sourceDrafts=new Map();
const fallback=[['all','全部'],['pc_game','PC 游戏'],['mobile_game','手机游戏'],['console_game','主机游戏'],['community','盒友杂谈'],['daily','盒友日常'],['digital_tech','数码科技'],['anime','动漫二次元'],['film_tv','影视娱乐'],['esports','电竞赛事'],['guide','游戏攻略'],['deals','优惠资讯'],['indie_game','独立游戏']];
export function renderSources(container,state,aid,{action,reload,notify}){
 container.replaceChildren();const cfg=state.platforms?.xiaoheihe?.accounts?.[aid]?.browse||{},catalog=state.topic_catalogs?.[aid]||{};const draftKey=aid;let draft=sourceDrafts.get(draftKey);if(!draft){draft={selected:new Set(cfg.topic_ids||[]),fallback:new Set(cfg.fallback_sources||['all'])};sourceDrafts.set(draftKey,draft);}let selected=draft.selected,fallbackSelected=draft.fallback;
 const panel=e('section','panel'),head=e('div','section-heading'),intro=e('div');intro.append(e('h2','','主动浏览来源'),e('p','muted','真实分区优先；仅在未选择分区或所有分区请求失败时使用回退分类。'));head.append(intro,btn('探测 / 刷新真实分区',async()=>{await action({operation:'topics_probe',provider:'xiaoheihe',account:aid});await reload();notify('真实分区已刷新');}));panel.append(head);
 const lookup=new Map((catalog.topics||[]).map(t=>[t.id,t]));panel.append(e('p','source-summary',(cfg.topic_ids||[]).map(id=>lookup.get(id)?.name||id).join('、')||'尚未选择真实分区'),e('p','muted',(cfg.topic_ids||[]).length+' 个分区'));
 if(catalog.topic_count)panel.append(e('p','source-result','读取到 '+catalog.topic_count+' 个真实分区。'+(catalog.feed_verified?'已验证分区 '+catalog.verified_topic_id+' 的真实帖子流。':'帖子流暂未验证：'+(catalog.feed_error||'暂无可验证分区'))));
 const editor=e('details','topic-editor'),summary=e('summary','','修改选择'),search=e('input');search.placeholder='搜索分区名称、分组或编号';search.setAttribute('aria-label','搜索分区');const count=e('p','muted'),list=e('div','source-grid');
 const draw=()=>{count.textContent='已选 '+selected.size+' / 20';list.replaceChildren();for(const t of catalog.topics||[]){if(search.value&&!`${t.name} ${t.group} ${t.id}`.toLowerCase().includes(search.value.toLowerCase()))continue;const label=e('label','source-choice'),box=e('input');box.type='checkbox';box.checked=selected.has(t.id);box.onchange=()=>{if(box.checked&&selected.size>=20){box.checked=false;notify('最多选择20个真实分区',true);return;}box.checked?selected.add(t.id):selected.delete(t.id);count.textContent='已选 '+selected.size+' / 20';};label.append(box,e('span','',t.name+(t.group&&t.group!==t.name?' · '+t.group:'')));list.append(label);}};
 search.oninput=draw;draw();editor.append(summary,search,count,list,btn('保存真实分区选择',async()=>{await action({operation:'account_save',provider:'xiaoheihe',account:aid,values:{topic_id:'',topic_ids:[...selected]}});await reload();notify('真实分区选择已保存');}));if(!catalog.topics?.length)editor.append(e('p','muted','先探测真实分区；已保存的选择会保留。'));panel.append(editor);container.append(panel);
 const compatibility=e('section','panel');compatibility.append(e('h2','','兼容 / 回退推荐流分类'),e('p','muted','支持多选；“全部”与其他分类互斥。真实分区本轮全部请求失败时，会使用这里保存的分类回退。'));const grid=e('div','source-grid');const checks=[];
 for(const [key,title]of fallback){const label=e('label','source-choice'),box=e('input');box.type='checkbox';box.checked=fallbackSelected.has(key);box.onchange=()=>{if(box.checked){if(key==='all'){fallbackSelected.clear();fallbackSelected.add('all');}else{fallbackSelected.delete('all');fallbackSelected.add(key);}}else fallbackSelected.delete(key);for(const [id,input]of checks)input.checked=fallbackSelected.has(id);};checks.push([key,box]);label.append(box,e('span','',title));grid.append(label);}compatibility.append(grid,btn('保存回退分类',async()=>{if(!fallbackSelected.size)throw Error('至少选择一个分类');await action({operation:'account_save',provider:'xiaoheihe',account:aid,values:{fallback_sources:[...fallbackSelected]}});await reload();notify('回退分类已保存');}));container.append(compatibility);
}
export async function renderStorage(container,pid,{action,notify}){
 container.replaceChildren(e('p','muted','正在读取存储状态…'));const data=await action({operation:'storage_status',provider:pid});if(!container.isConnected)return;container.replaceChildren();const panel=e('section','panel');panel.append(e('h2','','存储管理'),e('p','muted','数据库大小为各平台共用的实际文件体积；记录数量仅统计当前平台。'));
 const metrics=e('div','metrics');for(const [title,value]of [['共用数据库',(data.database_bytes/1048576).toFixed(2)+' MB'],['日程',data.counts.tasks],['执行回执',data.counts.actions],['收件事件',data.counts.inbox]]){const c=e('div','metric');c.append(e('span','',title),e('strong','',String(value)));metrics.append(c);}panel.append(metrics,e('p','muted','保护保留：'+data.protected.join('、')));
 const label=e('label','field','已结束事件正文保留天数'),input=e('input');input.type='number';input.min=7;input.max=3650;input.value=data.retention_days;label.append(input);const result=e('p','muted');let preview=null;const run=btn('确认压缩到期正文',async()=>{if(!preview||preview.retention_days!==Number(input.value))throw Error('请先按当前保留天数预览清理范围');const r=await action({operation:'storage_cleanup',provider:pid,retention_days:Number(input.value),confirm:true});result.textContent='已压缩 '+r.pruned_bodies+' 条正文。'+r.note;run.disabled=true;notify('存储清理已完成');});run.hidden=true;input.oninput=()=>{preview=null;run.hidden=true;};panel.append(label,btn('预览清理范围',async()=>{preview=await action({operation:'storage_preview',provider:pid,retention_days:Number(input.value)});result.textContent='可压缩 '+preview.body_count+' 条正文。'+preview.note;run.hidden=false;}),result,run);container.append(panel);
}
let biliDecisionDraft;
function decisionDraft(review,save){
 const incoming=review||{revision:0,choices:{}};
 if(!biliDecisionDraft)biliDecisionDraft={revision:incoming.revision,choices:{...incoming.choices},dirty:false,saving:false,error:'',listeners:new Set(),timer:null};
 const draft=biliDecisionDraft;
 if(!draft.dirty&&!draft.saving&&incoming.revision>draft.revision){draft.revision=incoming.revision;draft.choices={...incoming.choices};}
 draft.save=save;return draft;
}
function decisionNotice(draft){for(const listener of draft.listeners){if(listener.alive())listener.update();else draft.listeners.delete(listener);}}
async function saveDecisions(draft){
 clearTimeout(draft.timer);if(draft.saving||!draft.dirty||!draft.save)return;
 draft.saving=true;draft.error='';decisionNotice(draft);
 try{while(draft.dirty){const choices={...draft.choices};draft.dirty=false;try{const result=await draft.save({revision:draft.revision,choices});draft.revision=result.revision;}catch(error){draft.dirty=true;draft.error=error.message||'保存未完成，请重试';break;}}}
 finally{draft.saving=false;decisionNotice(draft);}
}
function choicesChanged(draft){draft.dirty=true;draft.error='';decisionNotice(draft);clearTimeout(draft.timer);draft.timer=setTimeout(()=>saveDecisions(draft),400);}
export function renderBiliReference(container,rows,{review,save}={}){
 container.replaceChildren();const panel=e('section','panel'),draft=decisionDraft(review,save);
 panel.append(e('h2','','迁移状态与待判断功能'),e('p','muted','选择接入或不接入，系统会自动保存。这里只记录后续迁移决定，不会立即启用功能；你选完后我可以读取并继续修改。'));
 const pending=rows.filter(row=>row.status==='review');
 const progress=e('p','notice'),saved=e('p','muted');saved.setAttribute('role','status');saved.setAttribute('aria-live','polite');
 const saveButton=btn('立即保存选择',()=>saveDecisions(draft));
 const listener={alive:()=>panel.isConnected,update:()=>{if(!pending.length){const savedChoices=Object.values(review?.choices||{});progress.textContent=`本轮迁移已完成：接入 ${savedChoices.filter(x=>x==='integrate').length} 项，不接入 ${savedChoices.filter(x=>x==='skip').length} 项。以下可查阅当前能力和配置入口。`;saved.textContent='你的选择记录已保留。';saveButton.hidden=true;return;}const selected=pending.filter(row=>draft.choices[row.key]);const yes=selected.filter(row=>draft.choices[row.key]==='integrate').length;progress.textContent=`已选择 ${selected.length} / ${pending.length} 项：接入 ${yes} 项，不接入 ${selected.length-yes} 项${selected.length===pending.length?' · 全部选择完成':''}。另有 ${rows.length-pending.length} 项已接入或统一管理。`;saved.textContent=draft.error?'保存失败：'+draft.error:draft.saving?'正在自动保存…':draft.dirty?'有选择尚未保存':'选择已保存，可继续修改。';saved.className=draft.error?'notice warn':'muted';saveButton.disabled=draft.saving||!draft.dirty;for(const control of panel.querySelectorAll('[data-decision-key]'))control.value=draft.choices[control.dataset.decisionKey]||'';}};
 draft.listeners.add(listener);panel.append(progress,saved,saveButton);
 const search=e('input');search.placeholder='搜索功能、原配置项或迁移位置';search.setAttribute('aria-label','搜索迁移对照');
 const select=e('select');select.setAttribute('aria-label','筛选迁移状态');for(const [value,label]of [['review','需要你判断'],['all','全部保留项目'],['ported','已接入'],['shared','统一管理']]){const option=e('option','',label);option.value=value;select.append(option);}
 const controls=e('div','button-row');controls.append(search,select);const list=e('div');
 const draw=()=>{
  list.replaceChildren();const filtered=rows.filter(row=>(select.value==='all'||row.status===select.value)&&(!search.value||`${row.key} ${row.description} ${row.target}`.toLowerCase().includes(search.value.toLowerCase())));const groups=new Map();
  for(const row of filtered){const category=row.category||(row.status==='ported'?'已接入功能':'统一管理');if(!groups.has(category))groups.set(category,[]);groups.get(category).push(row);}
  for(const [category,items]of groups){
   const group=e('details','reference-group');group.open=select.value==='review'||Boolean(search.value);group.append(e('summary','',category+' · '+items.length+' 项'));
   const reviewRows=items.filter(row=>row.status==='review');
   if(reviewRows.length){const bulk=e('div','button-row reference-bulk');for(const [value,label]of [['integrate','本组全部接入'],['skip','本组全部不接入']])bulk.append(btn(label,()=>{for(const row of reviewRows)draft.choices[row.key]=value;choicesChanged(draft);}));group.append(bulk);}
   for(const row of items){const item=e('div','reference-row');item.append(e('strong','',row.description),e('small','muted',row.key),e('span','badge '+(row.status==='review'?'warn':'good'),row.status==='review'?'待你判断':row.status==='ported'?'已接入':'统一管理'),e('p','muted',row.target));
    if(row.status==='review'){
     const label=e('label','reference-choice','后续迁移选择'),choice=e('select');choice.dataset.decisionKey=row.key;choice.setAttribute('aria-label',row.description+'迁移选择');
     for(const [value,text]of [['','尚未选择'],['integrate','接入'],['skip','不接入']]){const option=e('option','',text);option.value=value;choice.append(option);}choice.value=draft.choices[row.key]||'';
     choice.onchange=()=>{if(choice.value)draft.choices[row.key]=choice.value;else delete draft.choices[row.key];choicesChanged(draft);};label.append(choice);item.append(label);
    }group.append(item);
   }list.append(group);
  }if(!filtered.length)list.append(e('p','muted','没有匹配项目。'));listener.update();
 };
 search.oninput=draw;select.onchange=draw;if(!pending.length)select.value='all';draw();panel.append(controls,list);container.append(panel);listener.update();
}
