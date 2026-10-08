# -*- coding: utf-8 -*-
import io

NAV_FUNCS = '''/* ---- 导航：点云地图管理（接入导入 · 搜索 / 导出 / 删除 / 启用禁用 / 选 BIM 配准）+ 跨图通行（楼梯 / 电梯） ---- */
const PC_MAPS = {};
function pcMaps(id){
  if(!PC_MAPS[id]){
    const n = ROBOTS[id] ? ROBOTS[id].name : '机器人';
    PC_MAPS[id] = [
      { name:n+' · 主楼-1F 扫描点云.ply', space:'主楼 · 1F', size:'1.2 GB', time:'2026-08-20 10:32', on:true,  reg:id==='go1', bim:0 },
      { name:n+' · 主楼-2F 扫描点云.ply', space:'主楼 · 2F', size:'0.9 GB', time:'2026-08-15 16:20', on:true,  reg:false, bim:0 },
      { name:n+' · 主楼-3F 扫描点云.ply', space:'主楼 · 3F', size:'1.1 GB', time:'2026-08-12 09:48', on:false, reg:false, bim:0 },
    ];
  }
  return PC_MAPS[id];
}
const NAV_CFG = {};
function navCfg(id){ if(!NAV_CFG[id]) NAV_CFG[id] = { stair:true, lift:true, liftId:(LIFTS[0]||{}).id }; return NAV_CFG[id]; }
let navQ = '', navRegIdx = -1;
function pcListHtml(id){
  const maps = pcMaps(id), q = navQ.trim();
  const rows = maps.map((m,i)=>({m,i})).filter(x=>!q || x.m.name.includes(q) || x.m.space.includes(q));
  if(!rows.length) return '<div class="muted" style="font-size:11px;padding:18px 0;text-align:center">未找到匹配的点云地图</div>';
  return rows.map(({m,i})=>{
    const bs = m.space.replace(' · ','-');
    return `<div class="pt-item" style="${m.on?'':'opacity:.55'}">
      <span style="font-size:14px">🧊</span>
      <span style="min-width:0;flex:1"><b style="font-size:12px;color:var(--tx-hi)">${m.name}</b> <span class="badge ${m.reg?'b-ok':'b-dim'}" style="font-size:9px">${m.reg?'已配准':'未配准'}</span>${m.on?'':' <span class="badge b-dim" style="font-size:9px">已禁用</span>'}<br>
      <span class="muted" style="font-size:10px">${m.space} · ${m.size} · 上传时间 ${m.time}</span></span>
      <select class="input" style="width:158px;padding:3px 6px;font-size:10px;flex:none" onchange="pcMaps(curCfg)[${i}].bim=parseInt(this.value)">
        <option value="0" ${m.bim===0?'selected':''}>BIM：${bs} 空间结构.ifc</option>
        <option value="1" ${m.bim===1?'selected':''}>BIM：${bs} 空间结构.glb</option>
      </select>
      <span style="display:flex;gap:5px;flex:none">
        <button class="btn sm" style="padding:3px 10px;font-size:10px" onclick="pcRegOpen(${i})">配准</button>
        <button class="btn sm ghost" style="padding:3px 8px;font-size:10px" onclick="pcExport(${i})">导出</button>
        <button class="btn sm ghost" style="padding:3px 8px;font-size:10px" onclick="pcToggle(${i})">${m.on?'禁用':'启用'}</button>
        <button class="btn sm ghost" style="padding:3px 8px;font-size:10px;color:#f87171" onclick="pcDel(${i})">删除</button>
      </span>
    </div>`;
  }).join('');
}
function cfgNavHtml(r){
  if(navRegIdx >= 0){
    const m = pcMaps(curCfg)[navRegIdx];
    return `<div style="display:flex;align-items:center;gap:10px;margin-bottom:12px">
      <button class="btn sm ghost" onclick="navRegBack()">← 返回点云地图列表</button>
      <span style="font-size:12px;color:var(--tx-hi)">正在配准：<b>${m?m.name:''}</b></span></div>` + cfgRegHtml(r);
  }
  const nc = navCfg(curCfg);
  const liftObj = LIFTS.find(l=>l.id===nc.liftId) || LIFTS[0] || {usable:false};
  const maps = pcMaps(curCfg);
  return `
  <div class="panel" style="margin-bottom:12px"><div class="panel-hd"><span class="dot"></span>跨图通行<span class="extra">跨楼层导航的通行方式</span></div>
    <div class="panel-bd" style="font-size:12px;display:flex;gap:20px;flex-wrap:wrap;align-items:center">
      <label style="display:flex;align-items:center;gap:6px;cursor:pointer"><input type="checkbox" ${nc.stair?'checked':''} style="accent-color:#22d3ee" onchange="navSet('stair',this.checked)"> <span>支持<b style="color:var(--tx-hi)">楼梯</b>跨图</span></label>
      <label style="display:flex;align-items:center;gap:6px;cursor:pointer"><input type="checkbox" ${nc.lift?'checked':''} style="accent-color:#22d3ee" onchange="navSet('lift',this.checked)"> <span>支持<b style="color:var(--tx-hi)">电梯</b>跨图</span></label>
      ${nc.lift?`<span style="display:flex;align-items:center;gap:8px;flex-wrap:wrap">乘梯
        <select class="input" style="padding:4px 8px;font-size:11px;width:auto" onchange="navSet('liftId',this.value)">${LIFTS.map(l=>`<option value="${l.id}" ${l.id===nc.liftId?'selected':''}>${l.name}（${l.space}）</option>`).join('')}</select>
        <span class="badge ${liftObj.usable?'b-ok':'b-danger'}" style="font-size:9px" id="navLiftSt">${liftObj.usable?'梯控已连接':'梯控未连接'}</span>
        <button class="btn sm btn-test" onclick="navLiftTest()">测试连接</button></span>`:''}
    </div>
  </div>
  <div class="panel"><div class="panel-hd"><span class="dot"></span>点云地图<span class="extra">${maps.length} 个文件 · 启用 ${maps.filter(m=>m.on).length}</span></div>
    <div class="panel-bd" style="font-size:12px">
      <div class="muted" style="font-size:11px;margin-bottom:10px;line-height:1.7">设备接入时导入的扫描点云地图，用于导航定位；支持搜索、导出、删除与启用 / 禁用。每张地图选择对应 BIM 模型后可进行配准，<b style="color:var(--cy)">配准完成后该楼层才能按坐标执行任务</b>。</div>
      <input class="input" style="width:260px;margin-bottom:10px;font-size:11px" placeholder="🔍 搜索点云地图（名称 / 空间）" value="${navQ}" oninput="navSearch(this.value)">
      <div id="pcList">${pcListHtml(curCfg)}</div>
    </div>
  </div>`;
}
function navSearch(v){ navQ = v; const el = document.getElementById('pcList'); if(el) el.innerHTML = pcListHtml(curCfg); }
function navSet(k, v){ navCfg(curCfg)[k] = v; renderCfgDetail(); }
function navLiftTest(){ const nc = navCfg(curCfg); const l = LIFTS.find(x=>x.id===nc.liftId); toast('测试连接 '+(l?l.name:'')+' 梯控 API：✓ 呼叫响应 320ms'); const st = document.getElementById('navLiftSt'); if(st){ st.className='badge b-ok'; st.textContent='梯控已连接'; st.style.fontSize='9px'; } }
function pcToggle(i){ const m = pcMaps(curCfg)[i]; m.on = !m.on; renderCfgDetail(); toast(m.on ? '已启用「'+m.name+'」' : '已禁用「'+m.name+'」：任务调度将不再使用该图'); }
function pcExport(i){ toast('正在导出「'+pcMaps(curCfg)[i].name+'」，完成后将提示下载'); }
function pcDel(i){ const m = pcMaps(curCfg)[i]; if(confirm('确定删除点云地图「'+m.name+'」？\\n删除后该楼层的导航与配准结果将一并移除。')){ pcMaps(curCfg).splice(i,1); if(navRegIdx===i) navRegIdx=-1; renderCfgDetail(); toast('点云地图已删除'); } }
function pcRegOpen(i){ navRegIdx = i; regUI.pcFile = 0; regUI.pcLoaded = true; regUI.mode = 'idle'; regUI.step = 1; regUI.bim = []; regUI.pc = []; renderCfgDetail(); toast('已加载「'+pcMaps(curCfg)[i].name+'」，请使用手动配准'); }
function navRegBack(){ navRegIdx = -1; regUI.mode = 'idle'; renderCfgDetail(); }
function cfgRegHtml(r){'''

PATCHES = [
    ("config:[['base','基础信息',null],['reg','配准',null],['api','能力模组',null],['dispatch','工作分配',null]],",
     "config:[['base','基础信息',null],['api','能力模组',null],['nav','导航',null],['dispatch','工作分配',null]],"),
    ("if(!l2ok('config',curCfgTab)) curCfgTab = ['base','reg','api','dispatch'].find(x=>l2ok('config',x))||'base';",
     "if(!l2ok('config',curCfgTab)) curCfgTab = ['base','api','nav','dispatch'].find(x=>l2ok('config',x))||'base';"),
    ("if(curCfgTab==='reg') body = cfgRegHtml(r);",
     "if(curCfgTab==='nav') body = cfgNavHtml(r);"),
    ('''      ${l2ok('config','reg')?`<button class="ptab ${curCfgTab==='reg'?'on':''}" onclick="cfgTab('reg')"><span class="pi">🎯</span>配准</button>`:''}
      ${l2ok('config','api')?`<button class="ptab ${curCfgTab==='api'?'on':''}" onclick="cfgTab('api')"><span class="pi">🧩</span>能力模组</button>`:''}''',
     '''      ${l2ok('config','api')?`<button class="ptab ${curCfgTab==='api'?'on':''}" onclick="cfgTab('api')"><span class="pi">🧩</span>能力模组</button>`:''}
      ${l2ok('config','nav')?`<button class="ptab ${curCfgTab==='nav'?'on':''}" onclick="cfgTab('nav')"><span class="pi">🗺</span>导航</button>`:''}'''),
    ("if(curCfgTab==='reg') regBindVp();",
     "if(curCfgTab==='nav' && navRegIdx>=0) regBindVp();"),
    ("function cfgRegHtml(r){", NAV_FUNCS, 1),
    ("  regUI.mode = 'idle'; regUI.step = 1; regUI.bim = []; regUI.pc = [];",
     "  regUI.mode = 'idle'; regUI.step = 1; regUI.bim = []; regUI.pc = [];\n  if(navRegIdx>=0){ const mm = pcMaps(curCfg)[navRegIdx]; if(mm) mm.reg = true; }", 1),
    ('<button class="btn" style="width:100%" ${inOp?\'disabled\':\'\'} onclick="regAuto()">🤖 自动配准</button>',
     '<button class="btn" style="width:100%;opacity:.45" onclick="toast(\'自动配准开发中，请使用手动配准\')">🤖 自动配准</button>'),
    ("接下来：在「基础信息」配置岗位能力集 →「配准」完成点云与空间地图配准 →「工作分配」指派任务",
     "接下来：在「基础信息」配置岗位能力集 →「导航」完成点云地图配准 →「工作分配」指派任务"),
    ('<label style="display:flex;align-items:center;gap:8px;font-size:12px;margin-bottom:8px;opacity:.55;cursor:not-allowed" title="暂不可修改 · 后续版本放开"><input type="checkbox" ${GATE_UNIFIED?\'checked\':\'\'} disabled style="accent-color:#22d3ee;cursor:not-allowed"> <span><b style="color:var(--tx-hi)">统一网关（GW-01）</b> <span class="badge b-dim" style="font-size:9px">暂不可改</span> —— 勾选后全部自动门默认共用该网关、视为已配置；单门仍可单独覆盖（兼容「商铺各自网关」与「整楼统一网关」两种形态）</span></label>',
     '<label style="display:flex;align-items:center;gap:8px;font-size:12px;margin-bottom:8px;cursor:pointer"><input type="checkbox" ${GATE_UNIFIED?\'checked\':\'\'} style="accent-color:#22d3ee" onchange="gateUnified(this.checked)"> <span><b style="color:var(--tx-hi)">统一网关（GW-01）</b> —— 勾选后全部自动门默认共用该网关、视为已配置；单门仍可单独覆盖</span></label>'),
    ("分支：已开 → 直接通过；未开 → 发开门请求；超时（默认 20s）→ 重试 ×2 → 人工兜底（小舆推送 → 远程开门 / 改路线 / 终止任务）。",
     "分支：已开 → 直接通过；未开 → 发开门请求；超时（默认 20s）→ 重试 ×2"),
    ('<div class="panel-hd"><span class="dot"></span>梯控配置<span class="extra"><span class="badge b-warn" style="font-weight:400">云际 · 联调中</span></span></div>',
     '<div class="panel-hd"><span class="dot"></span>梯控配置</div>'),
    ('      <div class="muted" style="font-size:10.5px;margin-top:6px">选层指令按「支持 API」设计；<b style="color:#fbbf24">降级说明</b>：电梯不支持选层 API 时，由人工 / 机械按层，平台仅下发呼梯与到层检测。</div>\n', ''),
    ("'API · 降级人工/机械'", "'API 选层'"),
    ('      <p class="muted" style="font-size:11px;margin-top:6px">异常分支：呼梯无响应 → 重试 → 转人工；轿厢内断网 → 到站自动恢复定位；跨层任务在任务详情与地图上显示「乘梯中」节点。</p>\n', ''),
    ('        <tr><td>跟踪视角</td><td>规划中（tracking_view_plan）：2D 局部关系图，与 robotApiStore 同频刷新</td></tr>\n', ''),
    ('单版发布；版本管理 / 历史追溯 / 多机同步规划中。', '单版发布。'),
    ('📍 跟踪视角（规划中 · 2D 局部关系图）', '📍 跟踪视角（2D 局部关系图）'),
    ("toast('离线急停：经边缘单元近场通道（LoRa/蓝牙兜底链路）下发安全停机')",
     "toast('离线急停：经近场通道下发安全停机')"),
    ('<span class="muted" style="font-size:10px">需实测校准</span>', ''),
    ('<span class="muted">（双刻度见电量条 · 阈值需实测校准）</span>', ''),
    ('低于回充阈值自动回桩充电；低于禁派阈值标黄「暂停派单」并拦截任务下发。<b style="color:#fbbf24">阈值需实测校准</b>，接入后可在「基础信息」随时修改。',
     '低于回充阈值自动回桩充电；低于禁派阈值标黄「暂停派单」并拦截任务下发，接入后可在「基础信息」随时修改。'),
    ("空间规则：可配置限速 / 禁行时段 / 优先避让等（规划中）", "空间规则：可配置限速 / 禁行时段 / 优先避让等"),
    ('<button class="btn sm" style="margin-left:10px" onclick="document.getElementById(\'upMask\').classList.add(\'on\')">⬆ 上传空间数据</button>',
     '<button class="btn sm" id="upSpcBtn" style="margin-left:10px" onclick="document.getElementById(\'upMask\').classList.add(\'on\')">⬆ 上传空间数据</button>'),
    ("  if(t==='org'){ renderSpcTrees(); renderSpcView(); renderSpcInfo(); }",
     "  document.getElementById('upSpcBtn').style.display = t==='org'?'':'none';\n  if(t==='org'){ renderSpcTrees(); renderSpcView(); renderSpcInfo(); }"),
]

for path in ['index.html', 'light/index.html']:
    s = io.open(path, encoding='utf-8').read()
    for p in PATCHES:
        old, new = p[0], p[1]
        expect = p[2] if len(p) > 2 else 1
        c = s.count(old)
        assert c == expect, (path, old[:60], c, expect)
        s = s.replace(old, new)
    n = s.count('跨楼层物品配送（两段式 POC）')
    assert n == 2, (path, 'POC', n)
    s = s.replace('跨楼层物品配送（两段式 POC）', '跨楼层物品配送')
    io.open(path, 'w', encoding='utf-8').write(s)
    print(path, 'patched', len(PATCHES), '+ POC x2')
