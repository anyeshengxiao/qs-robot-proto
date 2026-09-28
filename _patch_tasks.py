# -*- coding: utf-8 -*-
import io
p = r'C:\Users\52560\Documents\Kimi\Workspaces\机器人\qs-robot-proto\index.html'
h = io.open(p, encoding='utf-8').read()

# ========== A1. 业务类型加「空间数据采集」 ==========
old = '<select class="input" id="teBiz" onchange="teBizChange()"><option value="patrol">巡检任务</option><option value="delivery">配送任务（两段式）</option><option value="guide">导览任务</option></select>'
new = '<select class="input" id="teBiz" onchange="teBizChange()"><option value="patrol">巡检任务</option><option value="delivery">配送任务（两段式）</option><option value="guide">导览任务</option><option value="scan">空间数据采集（点云扫图）</option></select>'
assert old in h; h = h.replace(old, new)

# ========== A2. 扫描参数块（插入 teDelivery 之后） ==========
anchor = '''          <div style="display:flex;gap:8px;margin-top:8px">
            <button class="btn" style="flex:1" onclick="saveTaskEdit()">💾 保存并下发</button>'''
scan_html = '''          <div id="teScan" style="display:none;border:1px dashed rgba(52,211,153,.4);border-radius:8px;padding:8px 10px;margin-bottom:4px">
            <div class="form-row"><label>扫描单体</label><span id="scBlds" style="display:flex;gap:6px;flex-wrap:wrap"></span></div>
            <div class="form-row"><label>扫描楼层</label><span id="scFls" style="display:flex;gap:6px;flex-wrap:wrap"></span></div>
            <div class="muted" style="font-size:10px;line-height:1.8">✅ 支持一次扫多层（勾选多个楼层）；⛔ 不支持跨建筑扫描（切换单体将清空已选楼层）<br>扫图任务<b>仅人工触发</b>：保存下发后狗启动前往目标楼层，自动跳转「远程接管」，由人控制完成扫图；点云按楼层回传归档。</div>
          </div>
''' + anchor
assert anchor in h; h = h.replace(anchor, scan_html, 1)

# ========== A3. teBizChange 处理 scan ==========
old = '''function teBizChange(){
  const b = document.getElementById('teBiz').value;
  document.getElementById('teDelivery').style.display = b==='delivery'?'block':'none';
  document.getElementById('tePatrolOpts').style.display = b==='delivery'?'none':'block';'''
new = '''function teBizChange(){
  const b = document.getElementById('teBiz').value;
  document.getElementById('teDelivery').style.display = b==='delivery'?'block':'none';
  document.getElementById('tePatrolOpts').style.display = (b==='delivery'||b==='scan')?'none':'block';
  const tt = document.getElementById('teType');
  document.getElementById('teScan').style.display = b==='scan'?'block':'none';
  if(b==='scan'){ tt.value='固定任务-人为触发'; tt.disabled=true; SC_BLD='主楼'; SC_FLS=[]; renderScanPanel();
    document.getElementById('teName').value='主楼 2F 空间数据采集（点云扫图）';
    document.getElementById('teDesc').value='人工触发扫图：狗启动后自动跳转远程接管，人控制狗完成扫描；点云按楼层回传归档。';
  } else tt.disabled=false;
  teTypeChange();'''
assert old in h; h = h.replace(old, new)

# ========== A4. renderTePlan 处理 scan 右侧 ==========
old = '''function renderTePlan(){
  const bizEl = document.getElementById('teBiz');
  const biz = bizEl ? bizEl.value : 'patrol';
  const hd = document.getElementById('tePlan').closest('.panel').querySelector('.panel-hd');'''
new = '''function renderTePlan(){
  const bizEl = document.getElementById('teBiz');
  const biz = bizEl ? bizEl.value : 'patrol';
  const hd = document.getElementById('tePlan').closest('.panel').querySelector('.panel-hd');
  if(biz==='scan'){
    hd.innerHTML = '<span class="dot"></span>扫图范围（空间数据采集 · 人工接管执行）<span class="extra" id="teCnt">已选 '+SC_FLS.length+' 层</span>';
    document.getElementById('tePlan').innerHTML = fpSvg() +
      '<div style="position:absolute;inset:0;display:flex;align-items:center;justify-content:center;pointer-events:none"><div style="background:rgba(7,12,24,.85);border:1px solid rgba(52,211,153,.4);border-radius:10px;padding:14px 18px;font-size:11.5px;line-height:2;color:#bfe6d8;text-align:center">🛰 扫图无需编排点位路线<br>保存下发 → 狗启动前往目标楼层 → 自动跳转<b style="color:#34d399">远程接管</b><br>人控制狗完成扫描 · 语音播报开始/结束</div></div>';
    document.getElementById('teRoute').innerHTML = SC_FLS.length
      ? SC_FLS.map(f=>'<div class="pt-item"><span class="badge b-ok">📄</span><span>'+SC_BLD+' · '+f+' 点云文件（扫描完成后回传 · 归属该楼层）</span><span class="muted" style="margin-left:auto">待采集</span></div>').join('')
      : '<div class="muted" style="font-size:11px">尚未选择楼层：请在左侧勾选本次扫描的楼层（可多选）</div>';
    return;
  }'''
assert old in h; h = h.replace(old, new)

# ========== A5. 扫描面板渲染 + saveTaskEdit 分支 ==========
old = '''let teSel = [];           /* 点位顺序路线：点位 id，按选择先后排序（可拖拽调整） */'''
new = '''let SC_BLD = '主楼', SC_FLS = [];
function renderScanPanel(){
  document.getElementById('scBlds').innerHTML = SP_BOX.map(b=>
    '<span class="fl-chip '+(SC_BLD===b.id?'on':'')+'" onclick="scPickBld(\\''+b.id+'\\')">'+b.name+'</span>').join('');
  const bObj = SP_BOX.find(x=>x.id===SC_BLD);
  document.getElementById('scFls').innerHTML = bObj.floors.map(f=>
    '<span class="fl-chip '+(SC_FLS.includes(f)?'on':'')+'" onclick="scPickFl(\\''+f+'\\')">'+f+'</span>').join('');
}
function scPickBld(id){
  if(id!==SC_BLD && SC_FLS.length) toast('扫图任务不支持跨建筑：已切换到「'+id+'」并清空已选楼层');
  SC_BLD=id; SC_FLS=[]; renderScanPanel(); renderTePlan();
}
function scPickFl(f){
  const i=SC_FLS.indexOf(f);
  if(i>=0) SC_FLS.splice(i,1); else SC_FLS.push(f);
  renderScanPanel(); renderTePlan();
}
let teSel = [];           /* 点位顺序路线：点位 id，按选择先后排序（可拖拽调整） */'''
assert old in h; h = h.replace(old, new)

old = '''function saveTaskEdit(){
  const biz = document.getElementById('teBiz').value;
  if(biz==='delivery'){'''
new = '''function saveTaskEdit(){
  const biz = document.getElementById('teBiz').value;
  if(biz==='scan'){
    if(!SC_FLS.length){ toast('请先勾选本次扫描的楼层（可多层，不可跨建筑）'); return; }
    const nm = document.getElementById('teName').value;
    toast('空间数据采集任务「'+nm+'」已下发 → 狗启动前往 '+SC_BLD+' '+SC_FLS.join('/'));
    aaEvent('🛰', '空间数据采集任务已下发（'+SC_BLD+' '+SC_FLS.join('/')+'）：狗到位后请通过远程接管控制扫图，点云将按楼层回传归档。');
    closeTeDrawer(); location.hash='#/monitor';
    mnBotSelect(teRobots[0]||'go2');
    setTimeout(()=>{ openTakeover(); },700);
    return;
  }
  if(biz==='delivery'){'''
assert old in h; h = h.replace(old, new)

# ========== B1. NL 解析确认卡弹窗（插入坐标拾取弹窗前） ==========
anchor = '<!-- 坐标拾取弹窗（空间地图：单体 → 楼层 → 点击拾取 · XYZ 可手工微调） -->'
nl_html = '''<!-- NL 任务解析确认卡（小舆 / 任务设置 🎙 入口共用） -->
<div class="mask" id="nlMask" style="z-index:155" onclick="if(event.target===this)this.classList.remove('on')">
  <div class="modal" style="width:560px;max-width:94vw">
    <div class="modal-hd">🧠 AI 任务识别 · 解析确认<span class="muted" style="font-size:11px;font-weight:400;margin-left:10px">先推理 → 缺项高亮补填 → 确认后进入路径规划</span><button class="x" onclick="document.getElementById('nlMask').classList.remove('on')">✕</button></div>
    <div class="modal-bd">
      <div class="form-row"><label>任务描述</label><input class="input" id="nlInp" placeholder="说人话：每个工作日 9 点巡检 3F / 送杯咖啡到 301 / 扫描 2F…" onkeydown="if(event.key==='Enter')nlParse()"></div>
      <div id="nlStep1" style="text-align:center;padding:16px 0;display:none">
        <div style="font-size:22px;animation:aaspin 1.2s linear infinite;display:inline-block">⚙️</div>
        <div class="muted" style="font-size:11px;margin-top:6px">AI 推理中：语义解析 → 空间匹配 → 岗位能力校验 → 模板命中…</div>
      </div>
      <div id="nlCard" style="display:none">
        <div class="panel" style="margin-bottom:0"><div class="panel-bd" id="nlRows" style="font-size:12px"></div></div>
      </div>
    </div>
    <div class="modal-ft">
      <button class="btn ghost" onclick="nlRe()">🔄 重新描述</button>
      <button class="btn" id="nlOk" onclick="nlConfirm()">确认并规划路径 →</button>
    </div>
  </div>
</div>

''' + anchor
assert anchor in h; h = h.replace(anchor, nl_html, 1)

# ========== B2. NL 解析 JS（插到 sendCmd 前） ==========
anchor = 'function sendCmd(txt){'
nl_js = '''/* ---- NL 任务解析确认卡（小舆 / 任务设置 🎙 入口共用） ---- */
let NL_TXT='', NL_MISS=false;
function nlOpen(t){
  NL_TXT=(t||'').trim();
  document.getElementById('nlInp').value=NL_TXT;
  document.getElementById('nlCard').style.display='none';
  document.getElementById('nlStep1').style.display='none';
  document.getElementById('nlMask').classList.add('on');
  if(NL_TXT) nlParse();
}
function nlParse(){
  NL_TXT=document.getElementById('nlInp').value.trim();
  if(!NL_TXT){ toast('请先描述任务'); return; }
  document.getElementById('nlCard').style.display='none';
  document.getElementById('nlStep1').style.display='block';
  setTimeout(nlBuildCard, 1200);
}
function nlBuildCard(){
  const t=NL_TXT;
  let biz='巡检任务';
  if(/送|配送|咖啡|奶茶|取/.test(t)) biz='配送任务';
  else if(/扫描|点云|扫图/.test(t)) biz='空间数据采集';
  else if(/导览|讲解|参观/.test(t)) biz='导览任务';
  const hasDest=/去|到|送往|送至|扫描/.test(t);
  const sp=mnInferSpace(t);
  NL_MISS=!hasDest;
  const cyc=/每天|每日|工作日|每周|周末/.test(t)?'固定任务-周期（已识别周期语义）':'临时任务（单次）';
  const rows=[
    ['任务类型', biz, ''],
    ['目标位置', hasDest? sp.space+' · '+sp.bld+' '+sp.fl : '⚠ 未识别到目的地，请补充（如"去 3F 办公区"）', hasDest?'':'miss'],
    ['点位要求', biz==='空间数据采集'?'整层全覆盖扫描（人工接管执行）':'按任务模板带出必覆盖点位，可在下一步调整', ''],
    ['返回结果要求', biz==='配送'?'取货/送达双确认照片':'照片 ×4 方位 + 录像 30s + 传感器快照', ''],
    ['执行路径规则', '避让禁行区/低速区 · 优先主路线（导航策略默认）', ''],
    ['任务形式', cyc, '']
  ];
  document.getElementById('nlRows').innerHTML=rows.map(r=>
    '<div style="display:flex;justify-content:space-between;gap:12px;padding:7px 0;border-bottom:1px dashed var(--border)"><span class="muted">'+r[0]+'</span><b style="text-align:right;font-weight:600;'+(r[2]==='miss'?'color:#fbbf24':'color:var(--tx-hi)')+'">'+r[1]+'</b></div>').join('');
  document.getElementById('nlStep1').style.display='none';
  document.getElementById('nlCard').style.display='block';
}
function nlRe(){
  document.getElementById('nlCard').style.display='none';
  document.getElementById('nlStep1').style.display='none';
  document.getElementById('nlInp').focus();
}
function nlConfirm(){
  if(NL_MISS){ toast('请先补充目的地（目标位置标黄项）'); return; }
  document.getElementById('nlMask').classList.remove('on');
  if(!curRobotId){
    const firstOnline=Object.keys(ROBOTS).find(id=>ROBOTS[id].st==='online'||ROBOTS[id].st==='executing')||'go1';
    mnBotSelect(firstOnline);
  }
  aaSay('解析已确认，为 '+curRobot.name+' 生成 3 条推荐路径，请比选后下发。');
  location.hash='#/monitor';
  setTimeout(()=>sendCmd(NL_TXT),500);
}
''' + anchor
assert anchor in h; h = h.replace(anchor, nl_js, 1)

# ========== B3. aaDispatch 走解析卡 ==========
old = '''function aaDispatch(t){
  AA_CTX.lastText=t;
  if(!curRobotId){
    const firstOnline = Object.keys(ROBOTS).find(id=>ROBOTS[id].st==='online'||ROBOTS[id].st==='executing') || 'go1';
    mnBotSelect(firstOnline);
  }
  aaSay(`收到！已为 ${curRobot.name} 做 AI 任务识别：语义解析「${t.slice(0,14)}」→ 空间规则与岗位校验 → 3 条路径推荐，请在监控中心确认后下发。`);
  setTimeout(()=>{ location.hash='#/monitor'; sendCmd(t); },900);
}'''
new = '''function aaDispatch(t){
  AA_CTX.lastText=t;
  aaSay('收到！先做 AI 任务识别，请在解析确认卡中核对五要素，确认后我再生成推荐路径。');
  setTimeout(()=>nlOpen(t),600);
}'''
assert old in h; h = h.replace(old, new)

# ========== B4. 任务设置页加 🎙 入口 ==========
old = '<button class="btn" style="margin-left:auto;background:linear-gradient(90deg,#0e7490,#7c3aed);border:none;font-size:13px;padding:9px 20px;border-radius:10px;box-shadow:0 4px 18px rgba(56,140,255,.35),0 0 0 1px rgba(167,139,250,.35);letter-spacing:.5px" onclick="openTeDrawer()">➕ 新建任务</button>'
new = '<button class="btn ghost" style="margin-left:auto;font-size:13px;padding:9px 16px;border-radius:10px" onclick="nlOpen()">🎙 语音/文字建任务</button>' + old.replace('margin-left:auto','margin-left:8px')
assert old in h; h = h.replace(old, new)

# ========== C. 路径弹窗子模型标注 + 重点设备标记 ==========
old = '② 路径规划 · 楼层平面图（<span id="planFloor">1F 共青130寓</span>）· 代价因子：空间规则 + 历史执行经验 + 实时环境'
new = '② 路径规划 · <b style="color:var(--cy)">路径子模型</b>（子模型提取：仅空间 + 重点系统/设备 + 重点位置，不加载全量模型）· <span id="planFloor">1F 共青130寓</span> · 代价因子：空间规则 + 历史执行经验 + 实时环境'
assert old in h; h = h.replace(old, new)
old = '''            <!-- 路径 B（备选·受阻） -->'''
new = '''            <text x="330" y="172" text-anchor="middle" font-size="12">🧯</text>
            <text x="480" y="122" text-anchor="middle" font-size="12">🛗</text>
            <text x="95" y="40" text-anchor="middle" font-size="9" fill="#22d3ee" opacity=".8">🔥 烟感</text>
            <!-- 路径 B（备选·受阻） -->'''
assert old in h; h = h.replace(old, new)

io.open(p, 'w', encoding='utf-8').write(h)
print('task patch ok')
