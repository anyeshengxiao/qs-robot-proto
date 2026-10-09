# -*- coding: utf-8 -*-
import io
p = r'C:\Users\52560\Documents\Kimi\Workspaces\机器人\qs-robot-proto\light\index.html'
s = io.open(p, encoding='utf-8').read()
n = 0
def rep(old, new, cnt=1):
    global s, n
    c = s.count(old)
    assert c == cnt, 'anchor %r found %d (expect %d)' % (old[:60], c, cnt)
    s = s.replace(old, new); n += 1

# 1. 编辑按钮只留图标
rep('''<span class="extra" style="cursor:pointer;color:var(--cy)" id="spcEditBtn" onclick="spcEditToggle()">✏️ 编辑结构</span>''',
'''<span class="extra" style="cursor:pointer;color:var(--cy)" id="spcEditBtn" title="编辑空间结构" onclick="spcEditToggle()">✏️</span>''')
rep('''  const b = document.getElementById('spcEditBtn'); if(b) b.textContent = spcEdit ? '✔ 完成编辑' : '✏️ 编辑结构';''',
'''  const b = document.getElementById('spcEditBtn'); if(b){ b.textContent = spcEdit ? '✔' : '✏️'; b.title = spcEdit ? '完成编辑' : '编辑空间结构'; }''')
rep('''  if(spcEdit) toast('结构编辑模式：＋ 新增子节点 · 点名称重命名 · ⬆ 上传该级空间模型（点云/实景/GIS/IFC）');''',
'''  if(spcEdit) toast('结构编辑模式：＋ 新增子节点（弹框选类型/可传模型）· 点名称重命名 · 点根节点类型徽标切换 园区/区块/楼宇 · 节点可拖拽移动');''')

# 2. 层级表：项目即根（类型可设），楼宇归一为单体
rep('''const SP_LV_KIDS = { '项目':['园区'], '园区':['区块','单体'], '区块':['单体'], '单体':['楼层'], '楼宇':['楼层'], '楼层':['房间'], '房间':[], '区域':[] };''',
'''const SP_LV_KIDS = { '园区':['区块','单体'], '区块':['单体'], '单体':['楼层'], '楼层':['房间'], '房间':[], '区域':[] };
function lvK(lv){ return lv==='楼宇'?'单体':lv; }''')

# 3. spcTreeHtml：根节点样式 + 弹框式操作 + 拖拽
rep('''    const ed = spcEdit && selFn==='spcSelNode';
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
      </div>''',
'''    const ed = spcEdit && selFn==='spcSelNode';
    const isRoot = !SP_NODES[n.id].par;
    const canUp = ['园区','区块','单体','楼宇'].includes(n.lv);
    return `<div>
      <div class="tree-row ${selId===n.id?'sel':''}" style="display:flex;align-items:center;gap:5px;${hid?'opacity:.45':''}" onclick="${selFn}('${n.id}')" ${ed?`draggable="true" ondragstart="spcDragStart(event,'${n.id}')" ondragover="spcDragOver(event)" ondragleave="spcDragLeave(event)" ondrop="spcDrop(event,'${n.id}')" title="拖拽可移动节点"`:''}>
        <input type="checkbox" ${hid?'':'checked'} style="accent-color:#22d3ee" title="勾选加载 / 取消隐藏" onclick="event.stopPropagation();spcToggle('${n.id}')">
        ${isRoot&&ed?`<span class="badge b-cy" style="font-size:9px;padding:1px 5px;flex:none;cursor:pointer" title="项目节点类型（点击设置：园区 / 区块 / 楼宇）" onclick="event.stopPropagation();ndRootType()">${n.lv}</span>`:`<span class="badge ${isRoot?'b-cy':'b-dim'}" style="font-size:9px;padding:1px 5px;flex:none">${n.lv}</span>`}
        <span style="font-size:12px;${isRoot?'font-weight:600;color:var(--tx-hi);':''}${ed?'cursor:text':''}" ${ed?`onclick="event.stopPropagation();ndRename('${n.id}')" title="点击重命名"`:''}>${isRoot?'🏗 ':''}${n.name}</span>
        ${n.mdls&&n.mdls.length?`<span class="badge b-ok" style="font-size:9px;padding:1px 5px" title="${n.mdls.map(m=>m.t+'：'+m.f).join('&#10;')}">📦${n.mdls.length}</span>`:''}
        ${ed?`<span style="margin-left:auto;display:flex;gap:3px;flex:none" onclick="event.stopPropagation()">
          ${(SP_LV_KIDS[lvK(n.lv)]||[]).length?`<button class="btn sm ghost" style="padding:0 6px;font-size:10px" title="新增子节点（弹框选类型 · 可上传模型）" onclick="ndOpen('${n.id}')">＋</button>`:''}
          ${canUp?`<button class="btn sm ghost" style="padding:0 6px;font-size:10px" title="上传空间模型（点云 / 实景 / GIS / IFC）" onclick="nmOpen('${n.id}')">⬆</button>`:''}
          ${isRoot?'':`<button class="btn sm ghost" style="padding:0 6px;font-size:10px;color:#f87171" title="删除节点" onclick="spcDelNode('${n.id}')">✕</button>`}
        </span>`:(showCnt&&cnt?`<span class="badge b-cy" style="font-size:9px;padding:1px 6px;margin-left:auto" title="该空间点位数">${cnt}</span>`:'')}
      </div>''')

# 4. renderSpcTrees：去掉独立项目行，根节点名 = 当前项目名
rep('''function renderSpcTrees(){
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
}''',
'''function renderSpcTrees(){
  /* 项目即最高级节点：根节点名随当前项目，类型可设（默认园区） */
  const proj = (PROJECTS.find(p=>p.cur)||{}).name || '';
  if(proj && SP_TREE[0] && SP_TREE[0].id==='park') SP_TREE[0].name = proj;
  const t1 = document.getElementById('spcTree'); if(t1) t1.innerHTML = spcTreeHtml(SP_TREE, spcSel, 'spcSelNode');
  const t2 = document.getElementById('spmTree'); if(t2) t2.innerHTML = spcTreeHtml(SP_TREE, spmSel, 'spmSelNode', true);
}''')

# 5. spcAddNode/spcRename → 平台弹框（ndMask）+ 拖拽函数
rep('''let spcSeq = 1;
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
}''',
'''let spcSeq = 1;
/* 新建 / 重命名 / 项目类型：平台内弹框（不调浏览器 prompt）；新建可同时上传模型 */
let ndMode = 'add', ndParId = '', ndType = '', ndMType = '点云模型', ndFileSel = null, ndOpts = [];
function ndChips(elId, arr, cur, fn){
  document.getElementById(elId).innerHTML = arr.map(t=>`<span class="badge ${t===cur?'b-cy':'b-dim'}" style="cursor:pointer;padding:4px 10px" onclick="${fn}('${t}')">${t}</span>`).join('');
}
function ndTypeSet(t){ ndType = t; ndChips('ndTypes', ndOpts, ndType, 'ndTypeSet'); }
function ndMTypeSet(t){ ndMType = t; ndChips('ndMTypes', NM_TYPES, ndMType, 'ndMTypeSet'); }
function ndOpen(parId){
  const par = parId ? SP_NODES[parId].n : null;
  const plv = par ? lvK(par.lv) : '园区';
  ndOpts = (SP_LV_KIDS[plv]||[]).slice();
  if(!ndOpts.length){ toast('「'+plv+'」节点下不能再建子级（层级：园区-区块(可无)-单体-楼层-房间）'); return; }
  ndMode = 'add'; ndParId = parId; ndFileSel = null; ndType = ndOpts[ndOpts.length-1]; ndMType = '点云模型';
  document.getElementById('ndTtl').textContent = '＋ 新建节点';
  document.getElementById('ndParRow').style.display = '';
  document.getElementById('ndPar').textContent = par ? spcPath(parId) : '（项目根）';
  document.getElementById('ndNameRow').style.display = '';
  document.getElementById('ndTypeRow').style.display = '';
  document.getElementById('ndUpRow').style.display = '';
  document.getElementById('ndName').value = '';
  document.getElementById('ndFname').textContent = '未选择（也可稍后用节点 ⬆ 上传）';
  ndChips('ndTypes', ndOpts, ndType, 'ndTypeSet');
  ndChips('ndMTypes', NM_TYPES, ndMType, 'ndMTypeSet');
  document.getElementById('ndMask').classList.add('on');
}
function ndRename(id){
  const m = SP_NODES[id]; if(!m) return;
  ndMode = 'rename'; ndParId = id;
  document.getElementById('ndTtl').textContent = '✏️ 重命名节点（'+m.n.lv+'）';
  document.getElementById('ndParRow').style.display = 'none';
  document.getElementById('ndNameRow').style.display = '';
  document.getElementById('ndTypeRow').style.display = 'none';
  document.getElementById('ndUpRow').style.display = 'none';
  document.getElementById('ndName').value = m.n.name;
  document.getElementById('ndMask').classList.add('on');
}
function ndRootType(){
  ndMode = 'rootType'; ndOpts = ['园区','区块','单体']; ndType = lvK(SP_TREE[0].lv);
  document.getElementById('ndTtl').textContent = '🏗 项目节点类型';
  document.getElementById('ndParRow').style.display = 'none';
  document.getElementById('ndNameRow').style.display = 'none';
  document.getElementById('ndTypeRow').style.display = '';
  document.getElementById('ndUpRow').style.display = 'none';
  ndChips('ndTypes', ndOpts, ndType, 'ndTypeSet');
  document.getElementById('ndMask').classList.add('on');
}
function ndDo(){
  if(ndMode==='rename'){
    const m = SP_NODES[ndParId]; const v = document.getElementById('ndName').value.trim();
    if(!v){ toast('请输入名称'); return; }
    m.n.name = v; closeMask('ndMask'); renderSpcTrees(); renderSpcInfo(); toast('已重命名为「'+v+'」'); return;
  }
  if(ndMode==='rootType'){
    SP_TREE[0].lv = ndType==='单体' ? '楼宇' : ndType;
    closeMask('ndMask'); renderSpcTrees(); renderSpcView(); toast('项目节点类型已设为「'+ndType+'」'); return;
  }
  const v = document.getElementById('ndName').value.trim();
  if(!v){ toast('请输入节点名称'); return; }
  const node = { id:'n'+(Date.now()%100000)+(spcSeq++), name:v, lv:ndType, kids:[] };
  if(ndFileSel) node.mdls = [{ t:ndMType, f:ndFileSel.name, time:'刚刚' }];
  const par = ndParId ? SP_NODES[ndParId].n : null;
  if(par){ par.kids = par.kids||[]; par.kids.push(node); SP_NODES[node.id] = { n:node, par:ndParId }; }
  else { SP_TREE.push(node); SP_NODES[node.id] = { n:node, par:null }; }
  closeMask('ndMask'); renderSpcTrees();
  toast('已在「'+(par?par.name:'项目')+'」下新增'+ndType+'「'+v+'」'+(ndFileSel?'，'+ndMType+'「'+ndFileSel.name+'」已挂载':''));
}
/* 节点拖拽移动（层级校验：园区-区块(可无)-单体-楼层-房间） */
let spcDragId = null;
function spcDragStart(ev, id){ spcDragId = id; ev.dataTransfer.effectAllowed = 'move'; }
function spcDragOver(ev){ ev.preventDefault(); ev.currentTarget.classList.add('drop'); }
function spcDragLeave(ev){ ev.currentTarget.classList.remove('drop'); }
function spcDrop(ev, id){
  ev.preventDefault(); ev.currentTarget.classList.remove('drop');
  const sid = spcDragId; spcDragId = null;
  if(!sid || sid===id) return;
  const sm = SP_NODES[sid], tm = SP_NODES[id]; if(!sm || !tm) return;
  if(!sm.par){ toast('项目根节点不可移动'); return; }
  let cur = id; while(cur){ if(cur===sid){ toast('不能移动到自身的子级下'); return; } cur = SP_NODES[cur].par; }
  if(!(SP_LV_KIDS[lvK(tm.n.lv)]||[]).includes(lvK(sm.n.lv))){ toast('层级不符：「'+tm.n.lv+'」下不能放「'+sm.n.lv+'」（园区-区块(可无)-单体-楼层-房间）'); return; }
  const arr = SP_NODES[sm.par].n.kids; const ix = arr.indexOf(sm.n); if(ix>=0) arr.splice(ix,1);
  tm.n.kids = tm.n.kids||[]; tm.n.kids.push(sm.n); sm.par = id;
  renderSpcTrees(); toast('已将「'+sm.n.name+'」移动到「'+tm.n.name+'」下');
}''')

# 6. 去掉旧 spcRename
rep('''function spcRename(id){
  const m = SP_NODES[id]; if(!m) return;
  const v = prompt('重命名节点（'+m.n.lv+'）：', m.n.name); if(!v) return;
  m.n.name = v; renderSpcTrees(); renderSpcInfo(); toast('已重命名为「'+v+'」');
}
''','''''')

# 7. ndMask 弹窗 HTML
rep('''<!-- 智能通行控制 · 电梯设置（梯控多接口 API） -->''',
'''<!-- 空间组织 · 新建 / 重命名节点（类型选择 + 可选上传模型） -->
<div class="mask" id="ndMask">
  <div class="modal" style="width:480px">
    <div class="modal-hd"><span id="ndTtl">＋ 新建节点</span><button class="x" onclick="closeMask('ndMask')">✕</button></div>
    <div class="modal-bd" style="font-size:12px">
      <div class="form-row" id="ndParRow"><label>上级节点</label><span id="ndPar" style="font-size:12px;color:var(--tx-hi)"></span></div>
      <div class="form-row" id="ndNameRow"><label>节点名称</label><input class="input" id="ndName" placeholder="请输入名称"></div>
      <div class="form-row" id="ndTypeRow"><label>节点类型</label><span style="display:flex;gap:6px;flex-wrap:wrap;flex:1" id="ndTypes"></span></div>
      <div id="ndUpRow">
        <div class="td-sec">上传空间模型（可选）</div>
        <div class="form-row"><label>模型类型</label><span style="display:flex;gap:6px;flex-wrap:wrap;flex:1" id="ndMTypes"></span></div>
        <div class="form-row"><label>模型文件</label><span style="display:flex;gap:8px;align-items:center;flex:1"><label style="color:var(--cy);cursor:pointer;font-size:12px;text-decoration:underline">点击选择文件<input type="file" id="ndFile" style="display:none" onchange="ndFileSel=this.files[0]||null;document.getElementById('ndFname').textContent=this.files[0]?this.files[0].name:'未选择（也可稍后用节点 ⬆ 上传）'"></label><span class="muted" style="font-size:10.5px" id="ndFname">未选择（也可稍后用节点 ⬆ 上传）</span></span></div>
      </div>
    </div>
    <div class="modal-ft"><button class="btn ghost" onclick="closeMask('ndMask')">取消</button><button class="btn" onclick="ndDo()">确定</button></div>
  </div>
</div>

<!-- 智能通行控制 · 电梯设置（梯控多接口 API） -->''')

# 8. 拖拽高亮样式
rep('''.tree-row .lv{font-size:10px;padding:0 5px;border-radius:3px;flex:none}''',
'''.tree-row .lv{font-size:10px;padding:0 5px;border-radius:3px;flex:none}
.tree-row.drop{outline:1.5px dashed var(--cy);background:var(--cy-dim)}''')

io.open(p, 'w', encoding='utf-8').write(s)
print('patched', n)
