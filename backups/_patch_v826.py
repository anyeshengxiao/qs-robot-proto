# -*- coding: utf-8 -*-
import io, sys
p = r'C:\Users\52560\Documents\Kimi\Workspaces\机器人\qs-robot-proto\light\index.html'
s = io.open(p, encoding='utf-8').read()
n0 = 0
def rep(old, new, cnt=1):
    global s, n0
    c = s.count(old)
    assert c == cnt, 'anchor %r found %d times (expect %d)' % (old[:60], c, cnt)
    s = s.replace(old, new)
    n0 += 1

# ============ 1. 空间组织结构在线编辑 ============
# 1a. 面板头加编辑按钮
rep('''<div class="panel-hd"><span class="dot"></span>空间组织结构</div>
        <div class="panel-bd" style="overflow:auto">
          <div id="spcTree"></div>''',
'''<div class="panel-hd"><span class="dot"></span>空间组织结构<span class="extra" style="cursor:pointer;color:var(--cy)" id="spcEditBtn" onclick="spcEditToggle()">✏️ 编辑结构</span></div>
        <div class="panel-bd" style="overflow:auto">
          <div id="spcTree"></div>''')

# 1b. spcTreeHtml + renderSpcTrees 重写（编辑模式 + 项目根节点 + 上传按钮 + 模型计数）
rep('''function spcTreeHtml(nodes, selId, selFn, showCnt){
  return nodes.map(n=>{
    const kids = n.kids||[], hid = !!spcHidden[n.id];
    const cnt = showCnt ? nodePts(n.id).length : 0;
    return `<div>
      <div class="tree-row ${selId===n.id?'sel':''}" style="display:flex;align-items:center;gap:5px;${hid?'opacity:.45':''}" onclick="${selFn}('${n.id}')">
        <input type="checkbox" ${hid?'':'checked'} style="accent-color:#22d3ee" title="勾选加载 / 取消隐藏" onclick="event.stopPropagation();spcToggle('${n.id}')">
        <span class="badge b-dim" style="font-size:9px;padding:1px 5px;flex:none">${n.lv}</span>
        <span style="font-size:12px">${n.name}</span>
        ${showCnt&&cnt?`<span class="badge b-cy" style="font-size:9px;padding:1px 6px;margin-left:auto" title="该空间点位数">${cnt}</span>`:''}
      </div>
      ${kids.length?`<div style="margin-left:20px">${spcTreeHtml(kids, selId, selFn, showCnt)}</div>`:''}
    </div>`;
  }).join('');
}''',
'''let spcEdit = false;
const SP_LV_KIDS = { '项目':['园区'], '园区':['区块','单体'], '区块':['单体'], '单体':['楼层'], '楼宇':['楼层'], '楼层':['房间'], '房间':[], '区域':[] };
function spcEditToggle(){
  spcEdit = !spcEdit;
  const b = document.getElementById('spcEditBtn'); if(b) b.textContent = spcEdit ? '✔ 完成编辑' : '✏️ 编辑结构';
  renderSpcTrees();
  if(spcEdit) toast('结构编辑模式：＋ 新增子节点 · 点名称重命名 · ⬆ 上传该级空间模型（点云/实景/GIS/IFC）');
}
function spcTreeHtml(nodes, selId, selFn, showCnt){
  return nodes.map(n=>{
    const kids = n.kids||[], hid = !!spcHidden[n.id];
    const cnt = showCnt ? nodePts(n.id).length : 0;
    const ed = spcEdit && selFn==='spcSelNode';
    const canUp = ['园区','区块','单体','楼宇'].includes(n.lv);
    return `<div>
      <div class="tree-row ${selId===n.id?'sel':''}" style="display:flex;align-items:center;gap:5px;${hid?'opacity:.45':''}" onclick="${selFn}('${n.id}')">
        <input type="checkbox" ${hid?'':'checked'} style="accent-color:#22d3ee" title="勾选加载 / 取消隐藏" onclick="event.stopPropagation();spcToggle('${n.id}')">
        <span class="badge b-dim" style="font-size:9px;padding:1px 5px;flex:none">${n.lv}</span>
        <span style="font-size:12px;${ed?'cursor:text':''}" ${ed?`onclick="event.stopPropagation();spcRename('${n.id}')" title="点击重命名"`:''}>${n.name}</span>
        ${n.mdls&&n.mdls.length?`<span class="badge b-ok" style="font-size:9px;padding:1px 5px" title="${n.mdls.map(m=>m.t+'：'+m.f).join('&#10;')}">📦${n.mdls.length}</span>`:''}
        ${ed?`<span style="margin-left:auto;display:flex;gap:3px;flex:none" onclick="event.stopPropagation()">
          ${(SP_LV_KIDS[n.lv]||[]).length?`<button class="btn sm ghost" style="padding:0 6px;font-size:10px" title="新增子节点" onclick="spcAddNode('${n.id}')">＋</button>`:''}
          ${canUp?`<button class="btn sm ghost" style="padding:0 6px;font-size:10px" title="上传空间模型（点云 / 实景 / GIS / IFC）" onclick="nmOpen('${n.id}')">⬆</button>`:''}
          <button class="btn sm ghost" style="padding:0 6px;font-size:10px;color:#f87171" title="删除节点" onclick="spcDelNode('${n.id}')">✕</button>
        </span>`:(showCnt&&cnt?`<span class="badge b-cy" style="font-size:9px;padding:1px 6px;margin-left:auto" title="该空间点位数">${cnt}</span>`:'')}
      </div>
      ${kids.length?`<div style="margin-left:20px">${spcTreeHtml(kids, selId, selFn, showCnt)}</div>`:''}
    </div>`;
  }).join('');
}
let spcSeq = 1;
function spcAddNode(id){
  const par = id ? SP_NODES[id].n : null;
  const plv = par ? par.lv : '项目';
  const opts = SP_LV_KIDS[plv]||[];
  if(!opts.length){ toast('「'+plv+'」节点下不能再建子级（层级：园区-区块(可无)-单体-楼层-房间）'); return; }
  let lv = opts[0];
  if(opts.length>1){ const v = prompt('选择子节点类型：\\n1 = '+opts[0]+'（可无的中间层）\\n2 = '+opts[1], '2'); if(v===null) return; lv = opts[parseInt(v)-1]||opts[0]; }
  const name = prompt('请输入'+lv+'名称：', '新建'+lv); if(!name) return;
  const node = { id:'n'+(Date.now()%100000)+(spcSeq++), name, lv, kids:[] };
  if(par){ par.kids = par.kids||[]; par.kids.push(node); SP_NODES[node.id]={n:node, par:id}; }
  else { SP_TREE.push(node); SP_NODES[node.id]={n:node, par:null}; }
  renderSpcTrees();
  toast('已在「'+(par?par.name:'项目')+'」下新增'+lv+'「'+name+'」');
}
function spcDelNode(id){
  const m = SP_NODES[id]; if(!m) return;
  if(!confirm('确定删除节点「'+m.n.name+'」及其全部子级？\\n关联模型与点位引用将一并移除。')) return;
  const arr = m.par ? SP_NODES[m.par].n.kids : SP_TREE;
  const ix = arr.indexOf(m.n); if(ix>=0) arr.splice(ix,1);
  const wipe = n=>{ delete SP_NODES[n.id]; (n.kids||[]).forEach(wipe); }; wipe(m.n);
  if(spcSel===id) spcSel='main-1f';
  renderSpcTrees(); renderSpcView(); renderSpcInfo(); toast('节点「'+m.n.name+'」已删除');
}
function spcRename(id){
  const m = SP_NODES[id]; if(!m) return;
  const v = prompt('重命名节点（'+m.n.lv+'）：', m.n.name); if(!v) return;
  m.n.name = v; renderSpcTrees(); renderSpcInfo(); toast('已重命名为「'+v+'」');
}''')

# 1c. renderSpcTrees 加项目根节点
rep('''function renderSpcTrees(){
  const t1 = document.getElementById('spcTree'); if(t1) t1.innerHTML = spcTreeHtml(SP_TREE, spcSel, 'spcSelNode');
  const t2 = document.getElementById('spmTree'); if(t2) t2.innerHTML = spcTreeHtml(SP_TREE, spmSel, 'spmSelNode', true);
}''',
'''function renderSpcTrees(){
  const t1 = document.getElementById('spcTree');
  if(t1){
    const proj = (PROJECTS.find(p=>p.cur)||{}).name || '当前项目';
    const root = `<div class="tree-row" style="display:flex;align-items:center;gap:5px">
      <span style="width:12px;flex:none"></span><span class="badge b-cy" style="font-size:9px;padding:1px 5px;flex:none">项目</span><span style="font-size:12.5px;font-weight:600;color:var(--tx-hi)">🏗 ${proj}</span>
      ${spcEdit?`<span style="margin-left:auto;flex:none"><button class="btn sm ghost" style="padding:0 6px;font-size:10px" title="新增园区" onclick="event.stopPropagation();spcAddNode('')">＋</button></span>`:''}
    </div>`;
    t1.innerHTML = root + `<div style="margin-left:20px">${spcTreeHtml(SP_TREE, spcSel, 'spcSelNode')}</div>`;
  }
  const t2 = document.getElementById('spmTree'); if(t2) t2.innerHTML = spcTreeHtml(SP_TREE, spmSel, 'spmSelNode', true);
}''')

# 1d. 单体也走楼宇视图
rep("if(n.lv==='楼宇'){\n    const b = SP_BOX.find(x=>n.name.includes(x.id)) || SP_BOX[0];",
    "if(n.lv==='楼宇'||n.lv==='单体'){\n    const b = SP_BOX.find(x=>n.name.includes(x.id)) || SP_BOX[0];")

# 1e. 节点模型上传弹窗（HTML 加在 upMask 之后）
rep('''<!-- 新设备接入向导：新建设备 → 现场连接 → 模组测试 → 注册完成 -->''',
'''<!-- 空间组织 · 节点模型上传（园区 / 区块 / 单体 均可挂载：点云 / 实景 / GIS / IFC） -->
<div class="mask" id="nmMask">
  <div class="modal" style="width:520px">
    <div class="modal-hd">⬆ 上传空间模型 · <span id="nmNode">—</span><button class="x" onclick="closeMask('nmMask')">✕</button></div>
    <div class="modal-bd" style="font-size:12px">
      <div class="form-row"><label>挂载节点</label><span id="nmPath" style="font-size:12px;color:var(--tx-hi)"></span></div>
      <div class="form-row"><label>模型类型</label><span style="display:flex;gap:6px;flex-wrap:wrap;flex:1" id="nmTypes"></span></div>
      <div style="border:2px dashed rgba(34,211,238,.35);border-radius:12px;padding:22px;text-align:center;background:rgba(34,211,238,.04);margin-top:6px">
        <div style="font-size:22px;margin-bottom:4px">📦</div>
        <div style="color:var(--tx-hi);font-size:12.5px">拖拽文件到此处，或 <label style="color:var(--cy);cursor:pointer;text-decoration:underline">点击选择文件<input type="file" id="nmFile" style="display:none" onchange="nmFileSel=this.files[0]||null;document.getElementById('nmFname').textContent=this.files[0]?this.files[0].name:'未选择文件'"></label></div>
        <div class="muted" style="font-size:10.5px;margin-top:6px" id="nmFname">未选择文件</div>
      </div>
    </div>
    <div class="modal-ft"><button class="btn ghost" onclick="closeMask('nmMask')">取消</button><button class="btn" onclick="nmDo()">上传并挂载到节点</button></div>
  </div>
</div>

<!-- 新设备接入向导：新建设备 → 现场连接 → 模组测试 → 注册完成 -->''')

# 1f. 节点模型上传 JS（加在 spcRename 后 → 挂在 spcToggle 定义前）
rep('''function spcToggle(id){''',
'''/* 节点模型上传（园区 / 区块 / 单体：点云 / 实景 / GIS / IFC） */
let nmId = null, nmType = '点云模型', nmFileSel = null;
const NM_TYPES = ['点云模型','实景模型','GIS 模型','IFC 模型'];
function nmTypeSet(t){
  nmType = t;
  document.getElementById('nmTypes').innerHTML = NM_TYPES.map(x=>`<span class="badge ${x===t?'b-cy':'b-dim'}" style="cursor:pointer;padding:4px 10px" onclick="nmTypeSet('${x}')">${x}</span>`).join('');
}
function nmOpen(id){
  const m = SP_NODES[id]; if(!m) return;
  nmId = id; nmFileSel = null; nmType = '点云模型';
  document.getElementById('nmNode').textContent = m.n.name;
  document.getElementById('nmPath').textContent = spcPath(id);
  document.getElementById('nmFname').textContent = '未选择文件';
  nmTypeSet('点云模型');
  document.getElementById('nmMask').classList.add('on');
}
function nmDo(){
  if(!nmFileSel){ toast('请先选择模型文件'); return; }
  const m = SP_NODES[nmId]; if(!m) return;
  const n = m.n; n.mdls = n.mdls||[]; n.mdls.push({ t:nmType, f:nmFileSel.name, time:'刚刚' });
  closeMask('nmMask'); renderSpcTrees();
  toast(nmType+'「'+nmFileSel.name+'」已上传并挂载到「'+n.name+'」节点');
  aaEvent('📦', '空间模型已挂载：'+nmType+' → '+spcPath(nmId)+'（园区 / 区块 / 单体均可挂载模型，模型区将按新文件重新加载）。');
}
function spcToggle(id){''')

# ============ 2. 监控中心：当前使用地图 + 去恢复/叫停 ============
rep('''      <button class="btn sm ghost" onclick="toast('恢复导航：POST /navigation:resume')">▶ 恢复</button>
      <button class="btn sm ghost" onclick="openInterrupt()">⏯ 叫停·插临时任务</button>
      <button class="btn sm ghost" onclick="openTrack()">🛤 轨迹回放</button>''',
'''      <button class="btn sm ghost" onclick="openTrack()">🛤 轨迹回放</button>''')

rep('''    <div class="td-sec" style="margin-top:10px">网络模式 <span class="muted" style="font-weight:400;font-size:10px">逐机设置 · 「自动」按信号阈值切换</span></div>''',
'''    ${(()=>{ const ms=(pcMaps(id)||[]).filter(m=>m.on); const m=ms[0]; const ix=m?pcMaps(id).indexOf(m):-1;
      return `<div class="td-sec" style="margin-top:10px">当前使用地图</div>
      <div class="pt-item" style="margin-bottom:4px"><span>🧊</span><span style="font-size:11.5px;min-width:0">${m?`<b style="color:var(--cy);font-family:var(--mono)">PC-${String(ix+1).padStart(2,'0')}</b> · ${m.name}<div class="muted" style="font-size:10px">${m.space} · ${m.reg?'已配准':'未配准'} · ${m.size}</div>`:'未启用点云地图（接入中心 · 导航 页签配置）'}</span></div>`; })()}
    <div class="td-sec" style="margin-top:10px">网络模式 <span class="muted" style="font-weight:400;font-size:10px">逐机设置 · 「自动」按信号阈值切换</span></div>''')

# ============ 3. 任务详情缩略图压字修复 ============
rep('''<div class="avatar" style="width:44px;height:44px;border-radius:8px">${r.icon?`<img src="../assets/${r.icon}">`:r.emoji}</div>''',
'''<div class="avatar" style="width:44px;height:44px;border-radius:8px;overflow:hidden;flex:none;background:var(--inset2);border:1px solid var(--border);display:flex;align-items:center;justify-content:center;font-size:22px">${r.icon?`<img src="../assets/${r.icon}" style="width:100%;height:100%;object-fit:cover">`:r.emoji}</div>''')

# ============ 4. 通行控制列表过滤 ============
rep('''<span class="extra">${DOORS.length} 个门点 · 自动门 ${DOORS.filter(d=>d.type==='auto').length}</span>''',
'''<span class="extra">自动门 ${DOORS.filter(d=>d.type==='auto').length} 个（非自动门在空间组织构件上设置）</span>''')
rep('''      ${DOORS.map(d=>{
        const noApi = doorNoApi(d);''',
'''      ${DOORS.filter(d=>d.type==='auto').map(d=>{
        const noApi = doorNoApi(d);''')

# ============ 5+6. LIFTS 数据重构（底楼层配置 + xy 坐标 + 多接口 API） ============
rep('''const LIFTS = [
  { id:'L-01', name:'客梯 L1', space:'主楼 · 电梯厅', fl:'main-1f', floors:'B1 - 3F', api:'POST /lift/call · /lift/select · /lift/status', loc:'轿厢局部图 + 激光重定位', x:70, y:22, vx:47, vy:50, usable:true },
  { id:'L-02', name:'客梯 L2', space:'主楼 · 电梯厅', fl:'main-1f', floors:'B1 - 3F', api:'POST /lift/call · /lift/select · /lift/status', loc:'轿厢局部图 + 激光重定位', x:75, y:22, vx:50, vy:50, usable:false },
];''',
'''/* 电梯：fl/base = 最底楼层（仅在该层选中可配置）；mks = 标记显示楼层；cx/cy = 电梯间中心点（仅 XY，轿厢定位坐标与其一致）；apis = 梯控多接口 */
const LIFTS = [
  { id:'L-01', name:'客梯 L1', space:'主楼 · 电梯厅', fl:'main-b1', base:'main-b1', mks:['main-b1','main-1f','main-2f','main-3f'], floors:'B1、1F、2F、3F', api:'POST /lift/call · /lift/select · /lift/status', apis:{call:'POST /lift/call',open:'POST /lift/door/open',close:'POST /lift/door/close',select:'POST /lift/select',status:'GET /lift/status'}, cx:'12430.0', cy:'3382.5', x:70, y:22, vx:47, vy:50, usable:true },
  { id:'L-02', name:'客梯 L2', space:'主楼 · 电梯厅', fl:'main-b1', base:'main-b1', mks:['main-b1','main-1f','main-2f','main-3f'], floors:'B1、1F、2F、3F', api:'', apis:{call:'',open:'',close:'',select:'',status:''}, cx:'12439.5', cy:'3382.5', x:75, y:22, vx:50, vy:50, usable:true },
];''')

# 5b. 空间组织地图电梯标记：mks 多楼层显示
rep("}).join('') + (spcGateF.lift?LIFTS.filter(l=>l.fl===flKey):[]).map(l=>`<div class=\"gate-mk lift",
    "}).join('') + (spcGateF.lift?LIFTS.filter(l=>(l.mks||[l.fl]).includes(flKey)):[]).map(l=>`<div class=\"gate-mk lift")

# 5c. 电梯构件信息面板重写（仅底楼层可配 + 中心点拾取 xy + 轿厢定位一致）
rep('''      <div class="td-sec">梯控配置</div>
      <div class="form-row"><label>梯控状态</label><select class="input" id="sgLiftUsable"><option value="1" ${gl.usable?'selected':''}>可乘 · 已接梯控</option><option value="0" ${gl.usable?'':'selected'}>不可乘 · 未接梯控</option></select></div>
      <div class="form-row"><label>服务单体</label><span style="font-size:12px;color:var(--tx-hi)">${(SP_FL_MAP[gl.fl]||['主楼'])[0]}（当前所在单体）</span></div>
      <div class="form-row"><label>服务楼层</label><span style="display:flex;gap:6px;flex-wrap:wrap;flex:1">${(SP_BOX.find(x=>x.id===(SP_FL_MAP[gl.fl]||['主楼'])[0])||SP_BOX[0]).floors.map(f=>`<span class="sgLf2 ${gl.floors.includes(f)?'on':''}" data-v="${f}" onclick="this.classList.toggle('on')">${f}</span>`).join('')}</span></div>
      <div class="form-row"><label>梯控 API</label><input class="input" id="sgLiftApi" style="font-size:11px;opacity:.65;cursor:not-allowed" value="${gl.api||''}" placeholder="未配置" readonly></div>
      <div class="muted" style="font-size:10px;margin:-4px 0 8px">只读 · 在「智能通行控制」中配置</div>
      <div class="form-row"><label>轿厢定位</label><span style="font-size:11px;color:var(--tx-dim)">${gl.loc}</span></div>`}''',
'''      <div class="td-sec">梯控配置</div>
      ${spcSel!==(gl.base||gl.fl)?`
      <div class="muted" style="font-size:11px;line-height:1.9;padding:4px 0 8px">电梯配置统一在<b style="color:var(--cy)">最底楼层（${(SP_FL_MAP[gl.base||gl.fl]||['主楼','B1'])[1]}）</b>进行：请在空间树选中「${(SP_FL_MAP[gl.base||gl.fl]||['主楼','B1'])[0]} · ${(SP_FL_MAP[gl.base||gl.fl]||['主楼','B1'])[1]}」后点击电梯标记。</div>
      <div class="form-row"><label>梯控状态</label><span style="font-size:12px">${gl.usable?'可乘 · 已接梯控':'不可乘 · 未接梯控'}</span></div>
      <div class="form-row"><label>服务楼层</label><span style="font-size:12px">${gl.floors}</span></div>`:`
      <div class="form-row"><label>梯控状态</label><select class="input" id="sgLiftUsable"><option value="1" ${gl.usable?'selected':''}>可乘 · 已接梯控</option><option value="0" ${gl.usable?'':'selected'}>不可乘 · 未接梯控</option></select></div>
      <div class="form-row"><label>服务单体</label><span style="font-size:12px;color:var(--tx-hi)">${(SP_FL_MAP[gl.fl]||['主楼'])[0]}（当前所在单体）</span></div>
      <div class="form-row"><label>服务楼层</label><span style="display:flex;gap:6px;flex-wrap:wrap;flex:1">${(SP_BOX.find(x=>x.id===(SP_FL_MAP[gl.fl]||['主楼'])[0])||SP_BOX[0]).floors.map(f=>`<span class="sgLf2 ${gl.floors.includes(f)?'on':''}" data-v="${f}" onclick="this.classList.toggle('on')">${f}</span>`).join('')}</span></div>
      <div class="form-row"><label>中心点坐标</label><span style="display:flex;gap:4px;align-items:center;flex:1"><span style="font-size:10px;color:var(--tx-dim)">X</span><input class="input" id="sgLiftX" style="width:72px;padding:3px 6px;font-size:11px;font-family:var(--mono)" value="${gl.cx}"><span style="font-size:10px;color:var(--tx-dim)">Y</span><input class="input" id="sgLiftY" style="width:72px;padding:3px 6px;font-size:11px;font-family:var(--mono)" value="${gl.cy}"><button class="btn sm ghost" style="padding:3px 8px;font-size:10px" onclick="sgLiftPickStart()">🎯 拾取</button></span></div>
      <div class="muted" style="font-size:10px;margin:-4px 0 8px">拾取电梯间中心点，仅 X / Y（不需要 Z）；轿厢定位坐标与该点一致</div>
      <div class="form-row"><label>轿厢定位</label><span style="font-family:var(--mono);font-size:11px;color:var(--cy)">X ${gl.cx}, Y ${gl.cy}</span><span class="muted" style="font-size:10px">（与中心点一致）</span></div>
      <div class="form-row"><label>梯控 API</label><input class="input" id="sgLiftApi" style="font-size:11px;opacity:.65;cursor:not-allowed" value="${gl.api||''}" placeholder="未配置" readonly></div>
      <div class="muted" style="font-size:10px;margin:-4px 0 8px">只读 · 在「智能通行控制 · 梯控 · 设置」中配置</div>`}`}''')

# 5d. spcSelGate：电梯中心点用 l.cx/l.cy（无 Z）
rep('''  spcComp = { n:g.name, coord:'X '+(12340+g.vx*1.9).toFixed(1)+', Y '+(3330+g.vy*1.05).toFixed(1)+', Z 1.2（构件中心点）' };''',
'''  spcComp = d ? { n:g.name, coord:'X '+(12340+g.vx*1.9).toFixed(1)+', Y '+(3330+g.vy*1.05).toFixed(1)+', Z 1.2（构件中心点）' }
              : { n:g.name, coord:'X '+g.cx+', Y '+g.cy+'（电梯间中心点）' };''')

# 5e. sgGateSave 保存 xy
rep('''    const fls=[...document.querySelectorAll('.sgLf2.on')].map(c=>c.dataset.v); if(fls.length) l.floors = fls.join('、');
    l.api = document.getElementById('sgLiftApi').value.trim();''',
'''    const fls=[...document.querySelectorAll('.sgLf2.on')].map(c=>c.dataset.v); if(fls.length) l.floors = fls.join('、');
    const ex=document.getElementById('sgLiftX'), ey=document.getElementById('sgLiftY');
    if(ex&&ex.value.trim()) l.cx=ex.value.trim();
    if(ey&&ey.value.trim()) l.cy=ey.value.trim();
    spcComp.coord='X '+l.cx+', Y '+l.cy+'（电梯间中心点）';''')

# 5f. 拾取模式 JS（加在 spcSelDev 前）
rep('''function spcSelDev(name){''',
'''/* 电梯间中心点拾取：点击空间地图返回 XY（不需要 Z），轿厢定位坐标与其一致 */
let liftPicking = false;
function sgLiftPickStart(){
  if(!spcGate || spcGate.kind!=='lift') return;
  liftPicking = true;
  const v = document.getElementById('spcView'); if(v) v.style.cursor='crosshair';
  toast('🎯 拾取模式：在空间地图上点击电梯间中心点（返回 X / Y 坐标）');
}
function spcViewClick(ev){
  if(!liftPicking || !spcGate || spcGate.kind!=='lift') return;
  liftPicking = false;
  const v = document.getElementById('spcView'); if(v) v.style.cursor='';
  const r = ev.currentTarget.getBoundingClientRect();
  const px = (ev.clientX-r.left)/r.width*100, py = (ev.clientY-r.top)/r.height*100;
  const l = LIFTS.find(x=>x.id===spcGate.id); if(!l) return;
  l.cx = (12340+px*1.9).toFixed(1); l.cy = (3330+py*1.05).toFixed(1);
  spcComp.coord = 'X '+l.cx+', Y '+l.cy+'（电梯间中心点）';
  renderSpcInfo();
  toast('已拾取电梯间中心点：X '+l.cx+', Y '+l.cy+'（轿厢定位坐标已同步）');
}
function spcSelDev(name){''')

# 5g. 空间组织楼层视图容器加点击拾取
rep('''  el.innerHTML = gateChips + `<div style="position:relative;flex:1;min-height:0;display:flex;flex-direction:column">${fpSvg(true)}''',
'''  el.innerHTML = gateChips + `<div style="position:relative;flex:1;min-height:0;display:flex;flex-direction:column" onclick="spcViewClick(event)">${fpSvg(true)}''')

# 6b. 梯控列表：仅已接梯控 + 轿厢 xy + 设置按钮
rep('''  <div class="panel" style="margin-bottom:10px"><div class="panel-hd"><span class="dot"></span>梯控配置</div>
    <div class="panel-bd" style="font-size:12px">
      ${LIFTS.map(l=>`<div class="pt-item"><span style="font-size:14px">🛗</span><span style="min-width:0"><b style="font-size:12px;color:var(--tx-hi)">${l.name}</b> <span class="badge b-dim" style="font-size:9px">${l.id}</span><br><span class="muted" style="font-size:10px">${l.space} · 服务楼层 ${l.floors} · 轿厢定位：${l.loc}</span></span><span style="margin-left:auto;text-align:right"><span class="badge ${l.usable?'b-ok':'b-danger'}" style="font-size:9px">${l.usable?'可乘 · 已接梯控':'不可乘 · 未接梯控'}</span><br><span style="font-family:var(--mono);font-size:10px">${l.api}</span></span><button class="btn sm btn-test" onclick="toast('测试连接 ${l.name} 梯控 API：✓ 呼叫响应 320ms')">测试</button></div>`).join('')}
    </div>
  </div>''',
'''  <div class="panel" style="margin-bottom:10px"><div class="panel-hd"><span class="dot"></span>梯控配置<span class="extra">仅显示已接梯控的电梯（含未配 API）</span></div>
    <div class="panel-bd" style="font-size:12px">
      ${LIFTS.filter(l=>l.usable).map(l=>`<div class="pt-item"><span style="font-size:14px">🛗</span><span style="min-width:0"><b style="font-size:12px;color:var(--tx-hi)">${l.name}</b> <span class="badge b-dim" style="font-size:9px">${l.id}</span><br><span class="muted" style="font-size:10px">${l.space} · 服务楼层 ${l.floors} · 轿厢定位 X ${l.cx}, Y ${l.cy}</span></span><span style="margin-left:auto;text-align:right"><span class="badge ${l.api?'b-ok':'b-danger'}" style="font-size:9px">${l.api?'可乘 · 已接梯控':'可乘 · 未配置 API ⚠'}</span><br><span style="font-family:var(--mono);font-size:10px">${l.api||'—'}</span></span><button class="btn sm btn-test" onclick="toast('测试连接 ${l.name} 梯控 API：✓ 呼叫响应 320ms')">测试</button><button class="btn sm ghost" onclick="liftSetOpen('${l.id}')">设置</button></div>`).join('')||'<div class="muted" style="padding:8px;font-size:12px">暂无已接梯控的电梯</div>'}
    </div>
  </div>''')

# 6c. 电梯设置弹窗 HTML（加在 nmMask 前）
rep('''<!-- 空间组织 · 节点模型上传（园区 / 区块 / 单体 均可挂载：点云 / 实景 / GIS / IFC） -->''',
'''<!-- 智能通行控制 · 电梯设置（梯控多接口 API） -->
<div class="mask" id="lsMask">
  <div class="modal" style="width:560px">
    <div class="modal-hd">🛗 电梯设置 · <span id="lsName">—</span><button class="x" onclick="closeMask('lsMask')">✕</button></div>
    <div class="modal-bd" style="font-size:12px">
      <div class="td-sec" style="margin-top:0">梯控接口 API（逐项配置）</div>
      <div class="form-row"><label>呼梯 API</label><input class="input" id="lsApiCall" placeholder="POST /lift/call"></div>
      <div class="form-row"><label>开门 API</label><input class="input" id="lsApiOpen" placeholder="POST /lift/door/open"></div>
      <div class="form-row"><label>关门 API</label><input class="input" id="lsApiClose" placeholder="POST /lift/door/close"></div>
      <div class="form-row"><label>选层（按键楼层）API</label><input class="input" id="lsApiSel" placeholder="POST /lift/select"></div>
      <div class="form-row"><label>状态查询 API</label><input class="input" id="lsApiSt" placeholder="GET /lift/status"></div>
      <div class="td-sec">电梯间中心点（与空间组织一致 · 仅 X / Y）</div>
      <div class="form-row"><label>中心点坐标</label><span style="font-family:var(--mono);font-size:11px;color:var(--cy)" id="lsCoord"></span></div>
    </div>
    <div class="modal-ft"><button class="btn ghost" onclick="closeMask('lsMask')">取消</button><button class="btn" onclick="liftSetSave()">保存设置</button></div>
  </div>
</div>

<!-- 空间组织 · 节点模型上传（园区 / 区块 / 单体 均可挂载：点云 / 实景 / GIS / IFC） -->''')

# 6d. 电梯设置 JS（加在 doorSetOpen 前）
rep('''/* 门点设置弹窗（空间管理 / 门控页签 / 监控地图共用） */
let doorSetId = null;''',
'''/* 电梯设置弹窗（梯控多接口 API · 智能通行控制） */
let liftSetId = null;
function lsV(id){ const e=document.getElementById(id); return e ? (e.value||'').trim() : ''; }
function liftSetOpen(id){
  liftSetId = id;
  const l = LIFTS.find(x=>x.id===id); if(!l) return;
  l.apis = l.apis || {call:'',open:'',close:'',select:'',status:''};
  document.getElementById('lsName').textContent = l.name;
  document.getElementById('lsApiCall').value = l.apis.call||'';
  document.getElementById('lsApiOpen').value = l.apis.open||'';
  document.getElementById('lsApiClose').value = l.apis.close||'';
  document.getElementById('lsApiSel').value = l.apis.select||'';
  document.getElementById('lsApiSt').value = l.apis.status||'';
  document.getElementById('lsCoord').textContent = 'X '+l.cx+', Y '+l.cy+'（轿厢定位坐标一致）';
  document.getElementById('lsMask').classList.add('on');
}
function liftSetSave(){
  const l = LIFTS.find(x=>x.id===liftSetId); if(!l) return;
  l.apis = { call:lsV('lsApiCall'), open:lsV('lsApiOpen'), close:lsV('lsApiClose'), select:lsV('lsApiSel'), status:lsV('lsApiSt') };
  const filled = Object.values(l.apis).filter(Boolean);
  l.api = filled.join(' · ');
  closeMask('lsMask');
  if(curSpaceTab==='pass') spPassRender();
  renderSpcView(); if(spcGate&&spcGate.id===l.id) renderSpcInfo();
  toast('电梯「'+l.name+'」设置已保存：梯控接口 '+filled.length+' 项'+(filled.length?'':'（未配置 API · 列表标红）'));
}
/* 门点设置弹窗（空间管理 / 门控页签 / 监控地图共用） */
let doorSetId = null;''')

# 6e. spPassMapRender：梯控 tab 楼层只显示有电梯的 + 标记随 tab
rep('''  const bd = bdSel.value;
  const seen = {}, fls = [];
  Object.keys(SP_FL_MAP).forEach(k=>{ const bf = SP_FL_MAP[k]; if(bf[0]===bd && !seen[bf[1]]){ seen[bf[1]]=1; fls.push(k); } });
  const oldFl = sel.value;
  sel.innerHTML = fls.map(k=>`<option value="${k}">${SP_FL_MAP[k][1]}</option>`).join('');
  sel.value = fls.includes(oldFl) ? oldFl : (fls.find(k=>DOORS.some(d=>d.fl===k)||LIFTS.some(l=>l.fl===k)) || fls[0]);
  const flKey = sel.value;
  const empty = (DOORS.some(d=>d.fl===flKey)||LIFTS.some(l=>l.fl===flKey)) ? '' :
    `<div class="muted" style="position:absolute;left:0;right:0;top:46%;text-align:center;font-size:11px">本层未识别到门 / 电梯构件</div>`;
  box.innerHTML = fpSvg(true) + empty +
    DOORS.filter(d=>d.fl===flKey).map(d=>{''',
'''  const bd = bdSel.value;
  const seen = {}, fls0 = [];
  Object.keys(SP_FL_MAP).forEach(k=>{ const bf = SP_FL_MAP[k]; if(bf[0]===bd && !seen[bf[1]]){ seen[bf[1]]=1; fls0.push(k); } });
  /* 梯控 tab：楼层只显示有配电梯的楼层 */
  const fls = passTab==='lift' ? fls0.filter(k=>LIFTS.some(l=>(l.mks||[l.fl]).includes(k))) : fls0;
  const oldFl = sel.value;
  sel.innerHTML = fls.map(k=>`<option value="${k}">${SP_FL_MAP[k][1]}</option>`).join('');
  sel.value = fls.includes(oldFl) ? oldFl : (fls.find(k=>passTab==='lift' ? LIFTS.some(l=>(l.mks||[l.fl]).includes(k)) : DOORS.some(d=>d.fl===k)) || fls[0]);
  const flKey = sel.value;
  const hasMk = passTab==='lift' ? LIFTS.some(l=>(l.mks||[l.fl]).includes(flKey)) : DOORS.some(d=>d.fl===flKey);
  const empty = hasMk ? '' :
    `<div class="muted" style="position:absolute;left:0;right:0;top:46%;text-align:center;font-size:11px">${passTab==='lift'?'本层未配置电梯':'本层未识别到门构件'}</div>`;
  box.innerHTML = fpSvg(true) + empty +
    (passTab==='gate'?DOORS.filter(d=>d.fl===flKey):[]).map(d=>{''')

rep('''    }).join('') +
    LIFTS.filter(l=>l.fl===flKey).map(l=>`<div class="gate-mk lift ${l.usable?'':'noapi'}" style="left:${l.x}%;top:${l.y}%" title="${l.name} · ${l.usable?'可乘 · 已接梯控':'不可乘 · 未接梯控'}（点击定位到梯控列表）" onclick="passTab='lift';spPassRender();toast('已定位到梯控列表 · ${l.name}')">🛗</div>`).join('');
}''',
'''    }).join('') +
    (passTab==='lift'?LIFTS.filter(l=>(l.mks||[l.fl]).includes(flKey)):[]).map(l=>`<div class="gate-mk lift ${l.usable?'':'noapi'}" style="left:${l.x}%;top:${l.y}%" title="${l.name} · ${l.usable?'可乘 · 已接梯控':'不可乘 · 未接梯控'} · 中心点 X ${l.cx}, Y ${l.cy}（点击设置）" onclick="liftSetOpen('${l.id}')">🛗</div>`).join('');
}''')

# ============ 7. 提示文字清理 ============
rep('''    <span class="muted" style="font-size:10px;margin-left:auto;align-self:center">门 / 电梯构件由空间管理语义识别自动提取（空间组织模型区「门 / 电梯」过滤查看）</span>
  </div>
  ${passTab==='gate'?cfgGateHtml(r):cfgLiftHtml(r)}`;''',
'''  </div>
  ${passTab==='gate'?cfgGateHtml(r):cfgLiftHtml(r)}`;''')
rep('''      <span class="muted" style="font-size:10px;margin-left:auto;align-self:center">门 / 电梯构件由空间语义识别自动提取（空间组织模型区「门 / 电梯」过滤查看 · 点标记看构件信息）</span>
    </div>` + (passTab==='gate' ? cfgGateHtml() : cfgLiftHtml());''',
'''    </div>` + (passTab==='gate' ? cfgGateHtml() : cfgLiftHtml());''')
rep('''<span class="muted" style="font-size:9.5px">语义识别自 BIM · 点击标记可设置（自动门未配 API 红色显示）</span></div>`;''',
'''</div>`;''')
rep('''<div class="form-row"><label>构件类型</label><span style="font-size:12px;color:var(--tx-hi)">${gd?'门':'电梯'}（空间语义识别自 BIM）</span></div>''',
'''<div class="form-row"><label>构件类型</label><span style="font-size:12px;color:var(--tx-hi)">${gd?'门':'电梯'}</span></div>''')

# ============ 8. 导航页签：顺序 / 单体切换 / 乘梯 xyz / 点云地图精简 ============
# 8a. pcListHtml：单体+楼层双选、去导出/禁用按钮
rep('''      <select class="input" style="width:168px;padding:3px 6px;font-size:10px;flex:none" onchange="pcMaps(curCfg)[${i}].bim=parseInt(this.value)">
        <option value="-1" ${m.bim < 0 ? 'selected' : ''}>（选择 BIM 模型）</option>
        ${bims.map((b, bi) => `<option value="${bi}" ${m.bim === bi ? 'selected' : ''}>BIM：${b}</option>`).join('')}
      </select>
      <span style="display:flex;gap:5px;flex:none">
        <button class="btn sm" style="padding:3px 10px;font-size:10px" onclick="pcRegOpen(${i})">配准</button>
        <button class="btn sm ghost" style="padding:3px 8px;font-size:10px" onclick="pcExport(${i})">导出</button>
        <button class="btn sm ghost" style="padding:3px 8px;font-size:10px" onclick="pcToggle(${i})">${m.on ? '禁用' : '启用'}</button>
        <button class="btn sm ghost" style="padding:3px 8px;font-size:10px;color:#f87171" onclick="pcDel(${i})">删除</button>
      </span>''',
'''      ${(()=>{ const pr = pcBimParts(m); const bxs = SP_BOX.map(b=>`<option value="${b.id}" ${pr[0]===b.id?'selected':''}>${b.id}</option>`).join('');
        const fls = pr[0] ? (SP_BOX.find(x=>x.id===pr[0])||{floors:[]}).floors.map(f=>`<option ${pr[1]===f?'selected':''}>${f}</option>`).join('') : '';
        return `<select class="input" id="pcB${i}" style="width:86px;padding:3px 6px;font-size:10px;flex:none" onchange="pcBimSet(${i})"><option value="">（选择单体）</option>${bxs}</select>
        <select class="input" id="pcF${i}" style="width:86px;padding:3px 6px;font-size:10px;flex:none" onchange="pcBimSet(${i})"><option value="">（选择楼层）</option>${fls}</select>`; })()}
      <span style="display:flex;gap:5px;flex:none">
        <button class="btn sm" style="padding:3px 10px;font-size:10px" onclick="pcRegOpen(${i})">配准</button>
        <button class="btn sm ghost" style="padding:3px 8px;font-size:10px;color:#f87171" onclick="pcDel(${i})">删除</button>
      </span>''')

# 8b. pcBimParts / pcBimSet（加在 pcListHtml 前）
rep('''function pcListHtml(id){''',
'''function pcBimParts(m){
  const s = m.bim >= 0 ? bimFiles()[m.bim] : '';
  const mm = (s||'').match(/^(.+)-(\\S+) 空间结构\\.ifc$/);
  return mm ? [mm[1], mm[2]] : ['', ''];
}
function pcBimSet(i){
  const b = document.getElementById('pcB'+i).value, f = document.getElementById('pcF'+i).value;
  const m = pcMaps(curCfg)[i];
  m.bim = (b && f) ? bimFiles().indexOf(b+'-'+f+' 空间结构.ifc') : -1;
  renderCfgDetail();
}
function pcListHtml(id){''')

# 8c. cfgNavHtml 重排：点云地图在上、跨图通行在下 + 单体切换 + 乘梯位置 xyz + 去提示句
rep('''  const maps = pcMaps(curCfg);
  return `
  <div class="panel" style="margin-bottom:12px"><div class="panel-hd"><span class="dot"></span>跨图通行<span class="extra">各点云地图跨楼层切图的通行方式</span></div>
    <div class="panel-bd" style="font-size:12px">
      ${maps.map((m, i) => {
        const liftObj = LIFTS.find(l => l.id === m.liftId) || LIFTS[0] || { usable:false };
        return `<div class="pt-item" style="${m.on ? '' : 'opacity:.55'}">
        <span style="min-width:0;flex:1"><b style="font-size:12px;color:var(--tx-hi)">${m.space}</b><br><span class="muted" style="font-size:10px">${m.name}</span></span>
        <span style="display:flex;gap:4px;flex:none;align-items:center;flex-wrap:wrap">
          ${crossBtn(m, i, 'stair', '楼梯')}${crossBtn(m, i, 'both', '楼梯+电梯')}${crossBtn(m, i, 'lift', '电梯')}
          ${m.cross !== 'stair' ? `<select class="input" style="padding:3px 6px;font-size:10px;width:auto" onchange="pcLiftSet(${i},this.value)">${LIFTS.map(l => `<option value="${l.id}" ${l.id === m.liftId ? 'selected' : ''}>${l.name}</option>`).join('')}</select>
          <span class="badge ${liftObj.usable ? 'b-ok' : 'b-danger'}" style="font-size:9px" id="navLiftSt-${i}">${liftObj.usable ? '梯控已连接' : '梯控未连接'}</span>
          <button class="btn sm btn-test" style="padding:3px 8px;font-size:10px" onclick="navLiftTest(${i})">测试连接</button>` : ''}
        </span>
      </div>`; }).join('')}
    </div>
  </div>
  <div class="panel"><div class="panel-hd"><span class="dot"></span>点云地图<span class="extra" style="display:flex;align-items:center;gap:8px"><span>${maps.length} 个文件 · 启用 ${maps.filter(m => m.on).length}</span><button class="btn sm ghost" onclick="pcvOpen()">🧩 查看配准</button><button class="btn sm" onclick="document.getElementById('pcImport').click()">⬆ 导入点云</button></span></div>
    <div class="panel-bd" style="font-size:12px">
      <div class="muted" style="font-size:11px;margin-bottom:10px;line-height:1.7">设备接入时导入或手动批量导入的扫描点云地图，用于导航定位；支持搜索、排序、导出、删除与启用 / 禁用。每张地图选择对应 BIM 模型后可进行配准，<b style="color:var(--cy)">配准完成后该楼层才能按坐标执行任务</b>。</div>''',
'''  const maps = pcMaps(curCfg);
  const cblds = [...new Set(maps.map(m => (m.space.match(/^(.+?) ·/) || [,''])[1]).filter(Boolean))];
  if(!cblds.includes(navCrossBld)) navCrossBld = cblds[0] || '';
  const crossRows = maps.map((m, i) => ({ m, i })).filter(({ m }) => !navCrossBld || m.space.indexOf(navCrossBld + ' ·') === 0);
  return `
  <div class="panel" style="margin-bottom:12px"><div class="panel-hd"><span class="dot"></span>点云地图<span class="extra" style="display:flex;align-items:center;gap:8px"><span>${maps.length} 个文件 · 启用 ${maps.filter(m => m.on).length}</span><button class="btn sm ghost" onclick="pcvOpen()">🧩 查看配准</button><button class="btn sm" onclick="document.getElementById('pcImport').click()">⬆ 导入点云</button></span></div>
    <div class="panel-bd" style="font-size:12px">
      <div class="muted" style="font-size:11px;margin-bottom:10px;line-height:1.7">设备接入时导入或手动批量导入的扫描点云地图，用于导航定位。每张地图选择对应单体与楼层后可进行配准，<b style="color:var(--cy)">配准完成后该楼层才能按坐标执行任务</b>。</div>''')

rep('''      <input type="file" id="pcImport" style="display:none" multiple accept=".ply,.pcd,.las,.laz,.zip" onchange="pcImportFiles(this)">
      <div id="pcList">${pcListHtml(curCfg)}</div>
    </div>
  </div>`;
}''',
'''      <input type="file" id="pcImport" style="display:none" multiple accept=".ply,.pcd,.las,.laz,.zip" onchange="pcImportFiles(this)">
      <div id="pcList">${pcListHtml(curCfg)}</div>
    </div>
  </div>
  <div class="panel"><div class="panel-hd"><span class="dot"></span>跨图通行<span class="extra">各点云地图跨楼层切图的通行方式</span></div>
    <div class="panel-bd" style="font-size:12px">
      <div style="display:flex;gap:6px;align-items:center;margin-bottom:10px;flex-wrap:wrap"><span class="muted" style="font-size:10px">单体</span>${cblds.map(b => `<button class="btn sm ghost" style="padding:3px 12px;font-size:10px;${navCrossBld === b ? 'border-color:var(--cy);color:var(--cy);background:rgba(34,211,238,.08)' : ''}" onclick="navCrossBld='${b}';renderCfgDetail()">${b}</button>`).join('')}</div>
      ${crossRows.map(({ m, i }) => {
        const liftObj = LIFTS.find(l => l.id === m.liftId) || LIFTS[0] || { usable:false };
        const fz = (m.space.match(/· (B\\d+|\\d+F|室外)$/) || [,'1F'])[1];
        return `<div class="pt-item" style="${m.on ? '' : 'opacity:.55'}">
        <span style="min-width:0;flex:1"><b style="font-size:12px;color:var(--tx-hi)">${m.space}</b><br><span class="muted" style="font-size:10px">${m.name}</span>${m.cross !== 'stair' ? `<br><span class="muted" style="font-size:10px;font-family:var(--mono)">乘梯位置：X ${liftObj.cx||'—'}, Y ${liftObj.cy||'—'}, Z ${pmZ(fz)}（电梯厅候梯点）</span>` : ''}</span>
        <span style="display:flex;gap:4px;flex:none;align-items:center;flex-wrap:wrap">
          ${crossBtn(m, i, 'stair', '楼梯')}${crossBtn(m, i, 'both', '楼梯+电梯')}${crossBtn(m, i, 'lift', '电梯')}
          ${m.cross !== 'stair' ? `<select class="input" style="padding:3px 6px;font-size:10px;width:auto" onchange="pcLiftSet(${i},this.value)">${LIFTS.map(l => `<option value="${l.id}" ${l.id === m.liftId ? 'selected' : ''}>${l.name}</option>`).join('')}</select>
          <span class="badge ${liftObj.usable ? 'b-ok' : 'b-danger'}" style="font-size:9px" id="navLiftSt-${i}">${liftObj.usable ? '梯控已连接' : '梯控未连接'}</span>
          <button class="btn sm btn-test" style="padding:3px 8px;font-size:10px" onclick="navLiftTest(${i})">测试连接</button>` : ''}
        </span>
      </div>`; }).join('') || '<div class="muted" style="padding:8px">该单体下暂无点云地图</div>'}
    </div>
  </div>`;
}''')

# 8d. navCrossBld 状态变量
rep("let navQ = '', navRegIdx = -1, navSort = 'time';",
    "let navQ = '', navRegIdx = -1, navSort = 'time', navCrossBld = '';")

# ============ 9. 配送动作设置 ============
rep('''/* 配送动作设置：四节点（取货 → 取货成功 → 开始送货 → 送货成功），语音 + 位姿（朝向/距离/云台） + 动作（类型/等待时长），配置同步小舆语音库；置物架承载，不涉及开关舱门 */''',
'''/* 配送动作设置：四节点（取货 → 取货成功 → 开始送货 → 送货成功），语音 + 位姿（朝向/距离） + 动作（类型/等待时长），配置同步小舆语音库；货箱承载 · 人工放置/取走 · 使用全景相机（无云台） */''')
rep('''  { id:'a1', name:'① 取货动作', icon:'🤏', trigger:'到达目标点位', pose:{face:'正对柜台', dist:'1.2 m', gimbal:'云台水平 0°'}, act:{type:'伸展置物架托盘 · 等待放货', wait:'等待放货 · 超时 5 分钟'}, say:'您好，我是配送机器人，我来取货，请将物品放置在托盘上。' },
  { id:'a2', name:'② 触发取货成功', icon:'✅', trigger:'店员语音：「货物已放好，可以去送货了」', pose:{face:'保持取货位姿', dist:'停稳不动', gimbal:'云台水平 0°'}, act:{type:'收回置物架托盘 · 语音复述物品清单', wait:'识别到店员语音后立即触发'}, say:'已收到：咖啡 2 杯、文件袋 1 个，确认无误我将出发配送。' },
  { id:'a3', name:'③ 开始送货', icon:'🚀', trigger:'路径下发至机器人', pose:{face:'导航姿态 · 靠右行驶', dist:'低速 0.8 m/s', gimbal:'云台前视'}, act:{type:'自动规划送达路径（门控/梯控联动）· 礼让行人', wait:'全程自主导航'}, say:'出发啦，预计 4 分钟后送达 3F 办公区 301。' },
  { id:'a4', name:'④ 送货成功', icon:'🎉', trigger:'到达目的地坐标', pose:{face:'面向收件人 · 停稳', dist:'距离 1.0 m', gimbal:'云台微俯 -10°'}, act:{type:'伸展置物架托盘 · 等待取货 · 完成后自动返程充电桩', wait:'等待取货 · 超时 5 分钟'}, say:'您好，您的配送已送达，请及时取走托盘上的物品，谢谢。' },''',
'''  { id:'a1', name:'① 取货动作', icon:'🤏', trigger:'到达目标点位', pose:{face:'正对柜台', dist:'1.2 m'}, act:{type:'停靠等待 · 店员人工将物品放置到货箱', wait:'等待放货 · 超时 5 分钟'}, say:'您好，我是配送机器人，我来取货，请将【平台】【订单号】物品放置在货箱中。' },
  { id:'a2', name:'② 触发取货成功', icon:'✅', trigger:'店员语音：「货物已放好，可以去送货了」', pose:{face:'保持取货位姿', dist:'停稳不动'}, act:{type:'语音复述物品清单 · 确认物品已放置', wait:'识别到店员语音后立即触发'}, say:'已收到【平台】【订单号】物品，确认无误我将出发配送。' },
  { id:'a3', name:'③ 开始送货', icon:'🚀', trigger:'路径下发至机器人', pose:{face:'导航姿态 · 靠右行驶', dist:'低速 0.8 m/s'}, act:{type:'自动规划送达路径（门控/梯控联动）· 礼让行人', wait:'全程自主导航'}, say:'出发啦，预计 4 分钟后送达 3F 办公区 301。' },
  { id:'a4', name:'④ 送货成功', icon:'🎉', trigger:'到达目的地坐标', pose:{face:'面向收件人 · 停稳', dist:'距离 1.0 m'}, act:{type:'停靠等待 · 收件人人工取走货箱物品 · 完成后自动返程充电桩', wait:'等待取货 · 超时 5 分钟'}, say:'您好，您的配送已送达，请及时取走货箱中的物品，谢谢。' },''')

# 9b. 去掉云台表单行
rep('''          <div class="form-row"><label>云台</label><select class="input" style="font-size:11px" onchange="DL_ACTS[${i}].pose.gimbal=this.value">${['云台水平 0°','云台微俯 -10°','云台俯角 -20°','云台前视','云台仰角 +30°'].map(o=>`<option ${o===a.pose.gimbal?'selected':''}>${o}</option>`).join('')}</select></div>
''','''''')

# 9c. 面板标题
rep('''<span class="dot"></span>动作设置（四节点流程：语音播报 + 位姿 + 动作）''',
'''<span class="dot"></span>动作设置（四节点流程：触发 + 语音播报 + 位姿 + 动作）''')

io.open(p, 'w', encoding='utf-8').write(s)
print('light patched', n0)

# ============ 小程序：去相机/定位图标 ============
q = r'C:\Users\52560\Documents\Kimi\Workspaces\机器人\qs-robot-proto\miniapp.html'
m = io.open(q, encoding='utf-8').read()
a = '<div class="inp"><input id="fOrderNo" placeholder="输入取餐码 / 小票订单号"><span class="ic" onclick="toast(\'调起扫码\')">📷</span></div>'
b = '<div class="inp"><input id="fOrderNo" placeholder="输入取餐码 / 小票订单号"></div>'
assert m.count(a) == 1; m = m.replace(a, b)
c = 'oninput="matchDest(this.value)"><span class="ic">📍</span></div>'
d = 'oninput="matchDest(this.value)"></div>'
assert m.count(c) == 1; m = m.replace(c, d)
io.open(q, 'w', encoding='utf-8').write(m)
print('miniapp patched 2')
