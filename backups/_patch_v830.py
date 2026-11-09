# -*- coding: utf-8 -*-
import io
p=r'C:\Users\52560\Documents\Kimi\Workspaces\机器人\qs-robot-proto\light\index.html'
s=io.open(p,encoding='utf-8').read()
n=0
def rep(a,b):
    global s,n
    assert s.count(a)==1,('anchor fail',a[:70],s.count(a))
    s=s.replace(a,b); n+=1

# ---------- 1) 面板头：编辑按钮旁增加 CityJSON 按钮 ----------
rep('<div class="panel-hd"><span class="dot"></span>空间组织结构<span class="extra" style="cursor:pointer;color:var(--cy)" id="spcEditBtn"',
    '<div class="panel-hd"><span class="dot"></span>空间组织结构<span class="extra" style="cursor:pointer;color:var(--cy);margin-right:8px" title="新增 CityJSON 数据" onclick="cjOpen()">🏙</span><span class="extra" style="cursor:pointer;color:var(--cy)" id="spcEditBtn"')

# ---------- 2) 树上方：双结构树切换 ----------
rep('          <div id="spcTree"></div>',
    '''          <div id="spcTreeTabs" style="display:none;gap:6px;padding:0 0 8px">
            <button class="chip" id="cjTabRobot" style="cursor:pointer" onclick="cjSetMode(false)">具身空间结构树</button>
            <button class="chip" id="cjTabCity" style="cursor:pointer" onclick="cjSetMode(true)">CityJSON 结构树</button>
          </div>
          <div id="spcTree"></div>''')

# ---------- 3) CityJSON 上传弹窗 ----------
rep('<div class="mask" id="timeMask">',
    '''<div class="mask" id="cjMask">
  <div class="modal" style="width:540px">
    <div class="modal-hd">🏙 新增 CityJSON 数据<button class="x" onclick="closeMask('cjMask')">✕</button></div>
    <div class="modal-bd" style="font-size:12px" id="cjBd"></div>
  </div>
</div>
<div class="mask" id="timeMask">''')

# ---------- 4) 渲染挂接 ----------
rep('''function renderSpcTrees(){
  /* 项目即最高级节点''',
    '''function renderSpcTrees(){
  if(typeof cjMode!=='undefined' && cjMode && cjData){ cjTreeRender(); return; }
  /* 项目即最高级节点''')
rep('''function renderSpcView(){
  const el = document.getElementById('spcView'); if(!el) return;''',
    '''function renderSpcView(){
  const el = document.getElementById('spcView'); if(!el) return;
  if(typeof cjMode!=='undefined' && cjMode && cjData){ cjViewRender(); return; }''')

# ---------- 5) CityJSON 全部逻辑 ----------
CJ_JS = r'''
/* ================= CityJSON 数据与结构树 ================= */
let cjData = null;          /* {title,file,time,layers,nodes,fallback} */
let cjMode = false;         /* 当前是否 CityJSON 结构树视图 */
let cjHidden = {};          /* 显式隐藏节点（含子级联动） */
let cjLayersOff = {};       /* 图层（MLLX）未勾选 */
let cjExpanded = {};        /* 展开节点 */
let cjFile = null;          /* 待上传文件 */
let cjFilterOpen = false;
const CJ_MLLX_C = {'米方':'#7fa8d9','米格':'#7fb77e','米粒':'#e0c07a','微观细分':'#b08ad9','房米料':'#e08a8a','条米料':'#8ac6c6'};
const CJ_GREEN = ['场地','绿地','广场','树池','看台','码头','护岸','防汛墙','防汛门','下船平台'];
const CJ_RED = ['建筑','棚房','简房','筒房','构筑物','悬空廊道'];
function cjStColor(st){
  if(CJ_GREEN.includes(st)) return '#7fb77e';
  if(CJ_RED.includes(st)) return '#e08a8a';
  return '#7fa8d9';
}
function cjOpen(){ cjFile=null; cjBdRender(); document.getElementById('cjMask').classList.add('on'); }
function cjBdRender(){
  const el=document.getElementById('cjBd');
  el.innerHTML = `
    ${cjData?`<div style="padding:10px 12px;border:1px solid var(--border);border-radius:8px;margin-bottom:12px;line-height:1.9">
      <b>已有数据</b>：${cjData.file}<br><span class="muted">上传于 ${cjData.time} · ${cjData.title}</span></div>`:''}
    <div class="form-row"><label>CityJSON 文件</label><input type="file" id="cjFileInp" accept=".json" style="flex:1" onchange="cjFile=this.files[0]"></div>
    <div class="muted" style="font-size:11px;line-height:1.8;margin:6px 0 2px">上传后按 <b>[宏观]规划单元 → [中观]地块 → [微观]功能空间</b> 层级真实解析构建结构树；无法识别层级属性时按对象类型分组。结构树可与「具身空间结构树」随时切换，互不影响机器人空间数据组织与导航。</div>
    ${cjData?`<div style="margin-top:10px;padding:9px 12px;border-radius:8px;background:rgba(251,191,36,.10);color:var(--warn);font-size:11.5px">⚠ 已存在 CityJSON 数据，上传新文件将<b>替换</b>现有数据；取消则保留当前数据。</div>`:''}
    <div style="display:flex;gap:10px;margin-top:16px">
      <button class="btn" onclick="cjUpload()">${cjData?'替换并上传':'上传并解析'}</button>
      <button class="btn ghost" onclick="closeMask('cjMask')">取消</button>
      ${cjData?`<button class="btn ghost" style="color:var(--danger);margin-left:auto" onclick="cjDel()">删除数据</button>`:''}
    </div>
    <div style="margin-top:12px;font-size:11px"><span style="color:var(--cy);cursor:pointer" onclick="cjExample()">没有文件？使用示例数据（复兴岛多尺度模型）</span></div>`;
}
function cjNow(){ const d=new Date(); const p=x=>String(x).padStart(2,'0'); return d.getFullYear()+'-'+p(d.getMonth()+1)+'-'+p(d.getDate())+' '+p(d.getHours())+':'+p(d.getMinutes()); }
function cjUpload(){
  if(!cjFile){ toast('请先选择 CityJSON 文件'); return; }
  const fr = new FileReader();
  fr.onload = e => {
    try{
      const j = JSON.parse(e.target.result);
      cjLoad(j, cjFile.name);
      closeMask('cjMask');
    }catch(err){ toast('解析失败：'+err.message); }
  };
  fr.readAsText(cjFile);
}
function cjExample(){
  fetch('../assets/cityjson_tree.json').then(r=>r.json()).then(j=>{
    cjData = Object.assign({}, j, {time:cjNow()});
    cjAfterLoad();
    closeMask('cjMask');
    toast('已加载示例 CityJSON：复兴岛多尺度模型');
  }).catch(()=>toast('示例数据加载失败'));
}
function cjLoad(j, file){
  const co = j.CityObjects||{};
  const hasLv = Object.values(co).some(v=>v.attributes && v.attributes['级别']);
  if(!hasLv){
    /* 降级：按对象类型分组 */
    const groups={};
    for(const id in co){
      const t=co[id].type||'Object';
      (groups[t]=groups[t]||[]).push({id:id,name:id,lv:3,color:'#7fa8d9',st:t});
    }
    cjData={title:(j.metadata&&j.metadata.title)||file, file:file, time:cjNow(), fallback:true, layers:[],
      nodes:[{id:'root',name:file,lv:1,color:'#5b6b8c',ch:Object.keys(groups).map(t=>({id:'g_'+t,name:t,lv:2,mllx:'默认',color:'#7fa8d9',ch:groups[t]}))}]};
    cjAfterLoad();
    toast('未识别宏观/中观/微观层级属性，已按对象类型分组');
    return;
  }
  const nodes=[];
  const layers={};
  for(const k1 in co){
    const v1=co[k1], a1=v1.attributes||{};
    if(a1['级别']!==1) continue;
    const n1={id:k1,name:'规划单元 '+String(a1['细分类型']||k1),lv:1,color:'#5b6b8c',ch:[]};
    for(const k2 of (v1.children||[])){
      const v2=co[k2]; if(!v2) continue;
      const a2=v2.attributes||{};
      if(a2['级别']!==2) continue;
      const mllx=a2['MLLX']||'默认'; layers[mllx]=true;
      const n2={id:k2,name:'地块 '+String(a2['PLOTNUMBER']||a2['细分类型']||k2),lv:2,mllx:mllx,color:CJ_MLLX_C[mllx]||'#7fa8d9',ch:[]};
      for(const k3 of (v2.children||[])){
        const v3=co[k3]; if(!v3) continue;
        const a3=v3.attributes||{};
        if(a3['级别']!==3) continue;
        const st=a3['STMC']||a3['细分类型']||'空间';
        n2.ch.push({id:k3,name:st+'-'+k3.split('_').pop(),lv:3,st:st,color:cjStColor(st)});
      }
      n1.ch.push(n2);
    }
    nodes.push(n1);
  }
  cjData={title:(j.metadata&&j.metadata.title)||file, file:file, time:cjNow(), layers:Object.keys(layers), nodes:nodes};
  cjAfterLoad();
  toast('CityJSON 解析完成：宏观 '+nodes.length+' · 已构建结构树');
}
function cjAfterLoad(){
  cjHidden={}; cjLayersOff={}; cjExpanded={}; cjFilterOpen=false;
  for(const n of cjData.nodes) cjExpanded[n.id]=true;
  cjMode=true;
  document.getElementById('spcTreeTabs').style.display='flex';
  cjTabSync(); cjTreeRender(); cjViewRender();
}
function cjDel(){
  cjData=null; cjMode=false;
  document.getElementById('spcTreeTabs').style.display='none';
  closeMask('cjMask');
  renderSpcTrees(); renderSpcView();
  toast('已删除 CityJSON 数据，恢复具身空间结构树');
}
function cjSetMode(city){
  if(city && !cjData) return;
  cjMode=city; cjTabSync();
  if(!city) document.getElementById('spcViewTip').textContent='按勾选分级加载 · 点选设备构件可打标';
  renderSpcTrees(); renderSpcView();
}
function cjTabSync(){
  const a=document.getElementById('cjTabRobot'), b=document.getElementById('cjTabCity');
  if(!a||!b) return;
  a.style.background=cjMode?'':'var(--cy-dim)'; a.style.color=cjMode?'':'var(--cy)'; a.style.border=cjMode?'':'1px solid var(--cy)';
  b.style.background=cjMode?'var(--cy-dim)':''; b.style.color=cjMode?'var(--cy)':''; b.style.border=cjMode?'1px solid var(--cy)':'';
}
function cjExpandToggle(id){ cjExpanded[id]=!cjExpanded[id]; cjTreeRender(); }
function cjToggleNode(id, on){
  const set=ns=>{ for(const n of ns){ if(on) delete cjHidden[n.id]; else cjHidden[n.id]=true; set(n.ch||[]); } };
  (function find(ns){ for(const n of ns){ if(n.id===id){ set([n]); return true; } if(find(n.ch||[])) return true; } return false; })(cjData.nodes);
  cjTreeRender(); cjViewRender();
}
function cjTreeRender(){
  const t=document.getElementById('spcTree'); if(!t||!cjData) return;
  let total=0, hidden=0;
  function walk(ns, depth, ancHid){
    let h='';
    for(const n of ns){
      const hid=!!(cjHidden[n.id]||ancHid);
      total++; if(hid) hidden++;
      const kids=n.ch||[];
      const open=!!cjExpanded[n.id];
      const tag=n.lv===1?'[宏观]':n.lv===2?'[中观]':'[微观]功能空间 ';
      h+=`<div style="display:flex;align-items:center;gap:6px;padding:3px 4px 3px ${depth*16+4}px;font-size:12px;${hid?'opacity:.45':''}">
        ${kids.length?`<span style="cursor:pointer;width:12px;flex:none;color:var(--tx-dim)" onclick="cjExpandToggle('${n.id}')">${open?'▾':'▸'}</span>`:'<span style="width:12px;flex:none"></span>'}
        <input type="checkbox" ${hid?'':'checked'} onchange="cjToggleNode('${n.id}',this.checked)" style="cursor:pointer;flex:none">
        <span style="width:8px;height:8px;border-radius:50%;background:${n.color};flex:none"></span>
        <span style="cursor:pointer;${hid?'text-decoration:line-through':''}" onclick="${kids.length?`cjExpandToggle('${n.id}')`:''}">${tag}${n.name}</span>
      </div>`;
      if(kids.length && open) h+=walk(kids, depth+1, hid);
    }
    return h;
  }
  t.innerHTML=`<div style="display:flex;gap:16px;padding:2px 6px 10px;font-size:12px;color:var(--tx-hi)"><span>🏙 空间: <b>${total}</b></span><span>隐藏: <b>${hidden}</b></span></div>`+walk(cjData.nodes,0,false);
}
/* 模型区覆盖块位置（示意） */
const CJ_SLOTS=[[30,60,10,7],[45,42,12,8],[55,28,10,7],[38,75,9,6],[62,16,9,6],[25,82,8,5],[52,55,10,7],[66,38,8,6],[40,20,9,6],[58,70,9,6]];
function cjViewRender(){
  const el=document.getElementById('spcView'); if(!el||!cjData) return;
  document.getElementById('spcViewTip').textContent='CityJSON 模型 · 树节点勾选 / 图层过滤控制显隐';
  const plots=[];
  for(const n1 of cjData.nodes){
    const h1=!!cjHidden[n1.id];
    for(const n2 of (n1.ch||[])) plots.push({n:n2, ancHid:h1});
  }
  const blocks=plots.slice(0,CJ_SLOTS.length).map((p,i)=>{
    const sl=CJ_SLOTS[i];
    const show=!(cjHidden[p.n.id]||p.ancHid) && !(p.n.mllx && cjLayersOff[p.n.mllx]);
    return `<div style="position:absolute;left:${sl[0]}%;top:${sl[1]}%;width:${sl[2]}%;height:${sl[3]}%;background:${p.n.color}55;border:1px solid ${p.n.color};border-radius:4px;display:${show?'flex':'none'};align-items:center;justify-content:center;font-size:10px;color:#334">${p.n.name.replace('地块 ','')}</div>`;
  }).join('');
  const layers=cjData.layers||[];
  const allOn=layers.every(x=>!cjLayersOff[x]);
  el.innerHTML=`
    <div style="position:relative;flex:1;min-height:0;overflow:auto">
      <div style="position:relative;min-width:520px">
        <img src="../assets/cityjson_model.png" style="width:100%;display:block">
        ${blocks}
      </div>
      <div style="position:absolute;left:12px;top:12px;background:var(--panel);border:1px solid var(--border);border-radius:8px;padding:8px 12px;font-size:11px;line-height:1.8">
        🏙 <b>${cjData.title}</b><br><span class="muted">${cjData.file} · ${cjData.time}</span>
      </div>
      <button title="CityJSON 过滤显示" onclick="cjFilterToggle()" style="position:absolute;right:14px;bottom:14px;width:36px;height:36px;border-radius:8px;border:1px solid var(--border);background:var(--panel-solid);color:var(--cy);cursor:pointer;font-size:16px">▽</button>
      <div style="position:absolute;right:14px;bottom:58px;display:${cjFilterOpen?'block':'none'};background:var(--panel-solid);border:1px solid var(--border);border-radius:10px;padding:10px 16px;z-index:5;box-shadow:0 8px 30px rgba(0,0,0,.18)">
        <label style="display:flex;gap:8px;align-items:center;padding:5px 2px;font-size:12px;cursor:pointer;color:var(--cy)"><input type="checkbox" ${allOn?'checked':''} onchange="cjLayerToggle('默认',this.checked)">默认</label>
        ${layers.map(l=>`<label style="display:flex;gap:8px;align-items:center;padding:5px 2px;font-size:12px;cursor:pointer"><input type="checkbox" ${cjLayersOff[l]?'':'checked'} onchange="cjLayerToggle('${l}',this.checked)">${l}</label>`).join('')}
      </div>
    </div>`;
}
function cjFilterToggle(){ cjFilterOpen=!cjFilterOpen; cjViewRender(); }
function cjLayerToggle(l, on){
  if(l==='默认'){
    if(on) cjLayersOff={};
    else for(const x of (cjData.layers||[])) cjLayersOff[x]=true;
  }else{
    if(on) delete cjLayersOff[l]; else cjLayersOff[l]=true;
  }
  cjViewRender();
}
'''
rep('function spcEditToggle(){', CJ_JS + '\nfunction spcEditToggle(){')

io.open(p,'w',encoding='utf-8').write(s)
print('patched',n)
