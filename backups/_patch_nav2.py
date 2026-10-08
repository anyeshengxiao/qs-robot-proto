# -*- coding: utf-8 -*-
import io

NEW_NAV = '''/* ---- 导航：点云地图管理（批量导入 · 搜索 / 排序 / 导出 / 删除 / 启用禁用 / 选 BIM 配准 · 查看配准合模）+ 跨图通行（按图指定楼梯 / 电梯） ---- */
const PC_MAPS = {};
function bimFiles(){
  const out = [];
  SP_BOX.forEach(b => b.floors.forEach(f => out.push(b.id + '-' + f + ' 空间结构.ifc')));
  return out;
}
function pcMaps(id){
  if(!PC_MAPS[id]){
    const n = ROBOTS[id] ? ROBOTS[id].name : '机器人';
    const bf = bimFiles();
    const bi = k => bf.findIndex(x => x.indexOf(k) === 0);
    PC_MAPS[id] = [
      { name:n+' · 主楼-1F 扫描点云.ply', space:'主楼 · 1F', size:'1.2 GB', time:'2026-08-20 10:32', on:true,  reg:id==='go1', bim:bi('主楼-1F'), cross:'both',  liftId:'L-01' },
      { name:n+' · 主楼-2F 扫描点云.ply', space:'主楼 · 2F', size:'0.9 GB', time:'2026-08-15 16:20', on:true,  reg:false, bim:bi('主楼-2F'), cross:'lift',  liftId:'L-01' },
      { name:n+' · 主楼-3F 扫描点云.ply', space:'主楼 · 3F', size:'1.1 GB', time:'2026-08-12 09:48', on:false, reg:false, bim:bi('主楼-3F'), cross:'stair', liftId:'L-01' },
    ];
  }
  return PC_MAPS[id];
}
let navQ = '', navRegIdx = -1, navSort = 'time';
function pcTimeKey(t){ return t === '刚刚' ? 9e15 : (Date.parse(t.replace(' ', 'T')) || 0); }
function pcFloorKey(space){
  const m = space.match(/(.+) · (B\\d+|\\d+F)/);
  if(!m) return [999, 999];
  const bi = SP_BOX.findIndex(b => b.id === m[1]);
  const f = m[2].charAt(0) === 'B' ? -parseInt(m[2].slice(1)) : parseInt(m[2]);
  return [bi < 0 ? 999 : bi, f];
}
function pcSortedRows(id){
  const maps = pcMaps(id), q = navQ.trim();
  let rows = maps.map((m, i) => ({ m, i })).filter(x => !q || x.m.name.includes(q) || x.m.space.includes(q));
  if(navSort === 'st') rows.sort((a, b) => (b.m.reg - a.m.reg) || (pcTimeKey(b.m.time) - pcTimeKey(a.m.time)));
  else if(navSort === 'fl') rows.sort((a, b) => { const ka = pcFloorKey(a.m.space), kb = pcFloorKey(b.m.space); return ka[0] - kb[0] || ka[1] - kb[1]; });
  else rows.sort((a, b) => pcTimeKey(b.m.time) - pcTimeKey(a.m.time));
  return rows;
}
function pcListHtml(id){
  const rows = pcSortedRows(id), bims = bimFiles();
  if(!rows.length) return '<div class="muted" style="font-size:11px;padding:18px 0;text-align:center">未找到匹配的点云地图</div>';
  return rows.map(({ m, i }) => `<div class="pt-item" style="${m.on ? '' : 'opacity:.55'}">
      <span style="font-size:14px">🧊</span>
      <span style="min-width:0;flex:1"><b style="font-size:12px;color:var(--tx-hi)">${m.name}</b> <span class="badge ${m.reg ? 'b-ok' : 'b-dim'}" style="font-size:9px">${m.reg ? '已配准' : '未配准'}</span>${m.on ? '' : ' <span class="badge b-dim" style="font-size:9px">已禁用</span>'}<br>
      <span class="muted" style="font-size:10px">${m.space} · ${m.size} · 上传时间 ${m.time}</span></span>
      <select class="input" style="width:168px;padding:3px 6px;font-size:10px;flex:none" onchange="pcMaps(curCfg)[${i}].bim=parseInt(this.value)">
        <option value="-1" ${m.bim < 0 ? 'selected' : ''}>（选择 BIM 模型）</option>
        ${bims.map((b, bi) => `<option value="${bi}" ${m.bim === bi ? 'selected' : ''}>BIM：${b}</option>`).join('')}
      </select>
      <span style="display:flex;gap:5px;flex:none">
        <button class="btn sm" style="padding:3px 10px;font-size:10px" onclick="pcRegOpen(${i})">配准</button>
        <button class="btn sm ghost" style="padding:3px 8px;font-size:10px" onclick="pcExport(${i})">导出</button>
        <button class="btn sm ghost" style="padding:3px 8px;font-size:10px" onclick="pcToggle(${i})">${m.on ? '禁用' : '启用'}</button>
        <button class="btn sm ghost" style="padding:3px 8px;font-size:10px;color:#f87171" onclick="pcDel(${i})">删除</button>
      </span>
    </div>`).join('');
}
function crossBtn(m, i, v, tx){
  return `<button class="btn sm ghost" style="padding:3px 9px;font-size:10px;${m.cross === v ? 'border-color:var(--cy);color:var(--cy);background:rgba(34,211,238,.08)' : ''}" onclick="pcCrossSet(${i},'${v}')">${tx}</button>`;
}
function cfgNavHtml(r){
  if(navRegIdx >= 0){
    const m = pcMaps(curCfg)[navRegIdx];
    return `<div style="display:flex;align-items:center;gap:10px;margin-bottom:12px">
      <button class="btn sm ghost" onclick="navRegBack()">← 返回点云地图列表</button>
      <span style="font-size:12px;color:var(--tx-hi)">正在配准：<b>${m ? m.name : ''}</b></span></div>` + cfgRegHtml(r);
  }
  const maps = pcMaps(curCfg);
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
      <div class="muted" style="font-size:11px;margin-bottom:10px;line-height:1.7">设备接入时导入或手动批量导入的扫描点云地图，用于导航定位；支持搜索、排序、导出、删除与启用 / 禁用。每张地图选择对应 BIM 模型后可进行配准，<b style="color:var(--cy)">配准完成后该楼层才能按坐标执行任务</b>。</div>
      <div style="display:flex;gap:8px;align-items:center;margin-bottom:10px;flex-wrap:wrap">
        <input class="input" style="width:230px;font-size:11px" placeholder="🔍 搜索点云地图（名称 / 空间）" value="${navQ}" oninput="navSearch(this.value)">
        <select class="input" style="width:210px;font-size:11px" onchange="navSort=this.value;renderCfgDetail()">
          <option value="time" ${navSort === 'time' ? 'selected' : ''}>排序：按时间（新 → 旧）</option>
          <option value="st" ${navSort === 'st' ? 'selected' : ''}>排序：按状态（已配准优先）</option>
          <option value="fl" ${navSort === 'fl' ? 'selected' : ''}>排序：按楼层（单体 · 地下 → 地上）</option>
        </select>
      </div>
      <input type="file" id="pcImport" style="display:none" multiple accept=".ply,.pcd,.las,.laz,.zip" onchange="pcImportFiles(this)">
      <div id="pcList">${pcListHtml(curCfg)}</div>
    </div>
  </div>`;
}
function navSearch(v){ navQ = v; const el = document.getElementById('pcList'); if(el) el.innerHTML = pcListHtml(curCfg); }
function pcCrossSet(i, v){ pcMaps(curCfg)[i].cross = v; renderCfgDetail(); }
function pcLiftSet(i, v){ pcMaps(curCfg)[i].liftId = v; renderCfgDetail(); }
function navLiftTest(i){ const m = pcMaps(curCfg)[i]; const l = LIFTS.find(x => x.id === m.liftId); toast('测试连接 ' + (l ? l.name : '') + ' 梯控 API：✓ 呼叫响应 320ms'); const st = document.getElementById('navLiftSt-' + i); if(st){ st.className = 'badge b-ok'; st.textContent = '梯控已连接'; st.style.fontSize = '9px'; } }
function pcToggle(i){ const m = pcMaps(curCfg)[i]; m.on = !m.on; renderCfgDetail(); toast(m.on ? '已启用「' + m.name + '」' : '已禁用「' + m.name + '」：任务调度将不再使用该图'); }
function pcExport(i){ toast('正在导出「' + pcMaps(curCfg)[i].name + '」，完成后将提示下载'); }
function pcDel(i){ const m = pcMaps(curCfg)[i]; if(confirm('确定删除点云地图「' + m.name + '」？\\n删除后该楼层的导航与配准结果将一并移除。')){ pcMaps(curCfg).splice(i, 1); if(navRegIdx === i) navRegIdx = -1; renderCfgDetail(); toast('点云地图已删除'); } }
function pcImportFiles(inp){
  const fs = Array.prototype.slice.call(inp.files || []); if(!fs.length) return;
  fs.forEach(f => pcMaps(curCfg).push({ name:f.name, space:'待分配', size:(f.size / 1048576).toFixed(1) + ' MB', time:'刚刚', on:true, reg:false, bim:-1, cross:'stair', liftId:'L-01' }));
  inp.value = ''; renderCfgDetail();
  toast('已导入 ' + fs.length + ' 个点云文件：请为其选择 BIM 模型并完成配准');
}
function pcRegOpen(i){ navRegIdx = i; regUI.pcFile = 0; regUI.pcLoaded = true; regUI.mode = 'idle'; regUI.step = 1; regUI.bim = []; regUI.pc = []; renderCfgDetail(); toast('已加载「' + pcMaps(curCfg)[i].name + '」，请使用手动配准'); }
function navRegBack(){ navRegIdx = -1; regUI.mode = 'idle'; renderCfgDetail(); }
/* 查看配准：全部点云 ↔ BIM 配对与合模情况 */
const PCV_DOTS = [[-40,-20],[-25,-38],[-8,-30],[12,-40],[30,-25],[40,-5],[28,12],[10,26],[-12,20],[-32,8],[-45,28],[0,0],[18,-8],[-20,42],[35,32]];
function pcvOv(m){
  const off = m.reg ? 0 : 14;
  return `<svg viewBox="0 0 380 240" style="width:100%;display:block;background:rgba(4,8,16,.5);border-radius:6px">
    <rect x="60" y="40" width="120" height="70" rx="4" fill="rgba(56,189,248,.08)" stroke="#0284c7" stroke-opacity=".55" stroke-dasharray="5 4"/>
    <rect x="200" y="40" width="120" height="70" rx="4" fill="rgba(56,189,248,.08)" stroke="#0284c7" stroke-opacity=".55" stroke-dasharray="5 4"/>
    <rect x="60" y="130" width="260" height="70" rx="4" fill="rgba(56,189,248,.08)" stroke="#0284c7" stroke-opacity=".55" stroke-dasharray="5 4"/>
    ${PCV_DOTS.map(([x, y]) => `<circle cx="${190 + x + off}" cy="${120 + y + off / 2}" r="2.2" fill="#e879f9" opacity=".85"/>`).join('')}
    ${m.reg ? '' : '<text x="190" y="228" text-anchor="middle" font-size="10" fill="#fbbf24">未配准 · 点云与模型存在偏移</text>'}
  </svg>`;
}
function pcvHtml(){
  const maps = pcMaps(curCfg), bims = bimFiles();
  const pairs = maps.filter(m => m.bim >= 0);
  const unPc = maps.filter(m => m.bim < 0);
  const used = {}; pairs.forEach(m => used[m.bim] = 1);
  const unBim = bims.filter((b, bi) => !used[bi]);
  const res = REG_RES[curCfg] || { rmse:1.86, overlap:97.8 };
  return `<div style="display:grid;grid-template-columns:300px 1fr;gap:14px;align-items:start">
    <div>
      <div class="muted" style="font-size:11px;margin-bottom:6px">配对列表（${pairs.length}）· 点击右侧查看合模</div>
      ${pairs.map((m, i) => `<div class="queue-item" style="cursor:pointer" onclick="pcvFocus(${i})"><span style="min-width:0"><b style="font-size:11px;color:var(--tx-hi)">${m.space}</b><br><span class="muted" style="font-size:10px">${m.name}<br>↔ ${bims[m.bim]}</span></span><span class="badge ${m.reg ? 'b-ok' : 'b-warn'}" style="font-size:9px">${m.reg ? '已配准' : '未配准'}</span></div>`).join('') || '<div class="muted" style="font-size:11px">暂无配对</div>'}
      ${(unPc.length || unBim.length) ? `<div class="muted" style="font-size:11px;margin:12px 0 6px">未配对</div>
        ${unPc.map(m => `<div class="queue-item"><span style="min-width:0;font-size:10px">🧊 ${m.name}</span><span class="badge b-warn" style="font-size:9px">点云 · 未选 BIM</span></div>`).join('')}
        ${unBim.map(b => `<div class="queue-item"><span style="min-width:0;font-size:10px">🏗 ${b}</span><span class="badge b-dim" style="font-size:9px">BIM · 无点云</span></div>`).join('')}` : ''}
    </div>
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px">
      ${pairs.map((m, i) => `<div class="panel" id="pcvCard${i}" style="margin:0;transition:box-shadow .3s"><div class="panel-hd"><span class="dot"></span><span style="font-size:11px">${m.space} 合模</span><span class="extra"><span class="badge ${m.reg ? 'b-ok' : 'b-warn'}" style="font-size:9px">${m.reg ? '已配准' : '未配准'}</span></span></div><div class="panel-bd">${pcvOv(m)}<div class="muted" style="margin-top:4px;font-size:10px">${m.name} ↔ ${bims[m.bim]}</div>${m.reg ? `<div style="margin-top:2px;color:var(--tx-dim);font-size:10px">RMSE ${res.rmse} mm · 重叠率 ${res.overlap}%</div>` : ''}</div></div>`).join('') || '<div class="muted" style="font-size:11px">暂无配对：请先在点云地图列表为点云选择 BIM 模型</div>'}
    </div>
  </div>`;
}
function pcvOpen(){ document.getElementById('pcvBd').innerHTML = pcvHtml(); document.getElementById('pcvMask').classList.add('on'); }
function pcvFocus(i){ const c = document.getElementById('pcvCard' + i); if(!c) return; c.scrollIntoView({ block:'nearest' }); c.style.boxShadow = '0 0 0 2px var(--cy)'; setTimeout(() => { c.style.boxShadow = ''; }, 1600); }
'''

PCV_MASK = '''<!-- 查看配准（点云 ↔ BIM 合模情况） -->
<div class="mask" id="pcvMask">
  <div class="modal" style="width:960px;max-width:94vw">
    <div class="modal-hd">🧩 点云 · BIM 合模情况<button class="x" onclick="closeMask('pcvMask')">✕</button></div>
    <div class="modal-bd" id="pcvBd" style="max-height:72vh;overflow:auto"></div>
  </div>
</div>

<!-- 时光盒子详情 -->'''

for path in ['index.html', 'light/index.html']:
    s = io.open(path, encoding='utf-8').read()
    # 1. 替换整个导航代码块
    start = s.index('/* ---- 导航：')
    end = s.index('function cfgRegHtml(r){', start)
    s = s[:start] + NEW_NAV + s[end:]
    # 2. 插入查看配准弹窗
    anchor = '<!-- 时光盒子详情 -->'
    assert s.count(anchor) == 1, (path, 'mask anchor')
    s = s.replace(anchor, PCV_MASK)
    io.open(path, 'w', encoding='utf-8').write(s)
    print(path, 'nav block replaced + pcvMask added')
