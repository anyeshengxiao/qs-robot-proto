# -*- coding: utf-8 -*-
import io

NEW_PCV = '''/* 查看配准：右侧单一合模视口（默认整单体多层合模，可切单体；点左侧配对看 1v1） */
const PCV_DOTS = [[-40,-20],[-25,-38],[-8,-30],[12,-40],[30,-25],[40,-5],[28,12],[10,26],[-12,20],[-32,8],[-45,28],[0,0],[18,-8],[-20,42],[35,32]];
let pcvSel = -1, pcvBld = '';
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
function pcvWholeSvg(bId){
  const b = SP_BOX.find(x => x.id === bId) || SP_BOX[0];
  const maps = pcMaps(curCfg).filter(m => m.bim >= 0 && m.space.indexOf(b.id + ' · ') === 0);
  const fk = s => s.charAt(0) === 'B' ? -parseInt(s.slice(1)) : parseInt(s);
  const fls = b.floors.slice().sort((a, c) => fk(a) - fk(c));
  const H = 260, gap = Math.min(52, (H - 70) / Math.max(fls.length, 1));
  let g = '';
  fls.forEach((f, i) => {
    const y = H - 36 - i * gap, x = 74 + i * 10;
    g += `<rect x="${x}" y="${y - 26}" width="240" height="26" rx="3" fill="rgba(56,189,248,.07)" stroke="#0284c7" stroke-opacity=".55"/>
      <text x="${x - 8}" y="${y - 7}" text-anchor="end" font-size="10" fill="#6b7a90">${f}</text>`;
    maps.filter(m => m.space === b.id + ' · ' + f).forEach(m => {
      const off = m.reg ? 0 : 16;
      g += PCV_DOTS.slice(0, 10).map(([dx, dy]) => `<circle cx="${(x + 120 + dx * 2.2 + off).toFixed(1)}" cy="${(y - 13 + dy * 0.28).toFixed(1)}" r="1.8" fill="#e879f9" opacity=".85"/>`).join('');
      if(!m.reg) g += `<text x="${x + 236}" y="${y - 7}" text-anchor="end" font-size="8" fill="#fbbf24">未配准</text>`;
    });
  });
  if(!maps.length) g += '<text x="200" y="130" text-anchor="middle" font-size="11" fill="#6b7a90">该单体暂无已配对的点云地图</text>';
  return `<svg viewBox="0 0 400 260" style="width:100%;display:block;background:rgba(4,8,16,.5);border-radius:6px">${g}</svg>`;
}
function pcvHtml(){
  const maps = pcMaps(curCfg), bims = bimFiles();
  const pairs = maps.filter(m => m.bim >= 0);
  const unPc = maps.filter(m => m.bim < 0);
  const used = {}; pairs.forEach(m => used[m.bim] = 1);
  const unBim = bims.filter((b, bi) => !used[bi]);
  const res = REG_RES[curCfg] || { rmse:1.86, overlap:97.8 };
  if(!pcvBld) pcvBld = SP_BOX[0].id;
  const bTabs = SP_BOX.map(b => `<button class="btn sm ghost" style="padding:3px 10px;font-size:10px;${pcvBld === b.id && pcvSel < 0 ? 'border-color:var(--cy);color:var(--cy);background:rgba(34,211,238,.08)' : ''}" onclick="pcvBldSet('${b.id}')">${b.name || b.id}</button>`).join('');
  let right;
  if(pcvSel < 0){
    right = `<div class="panel" style="margin:0"><div class="panel-hd"><span class="dot"></span>${pcvBld} · 整体合模<span class="extra" style="display:flex;gap:4px">${bTabs}</span></div>
      <div class="panel-bd">${pcvWholeSvg(pcvBld)}<div class="muted" style="font-size:10px;margin-top:4px">多层 BIM 与全部点云同窗叠加；青色为 BIM、品红为点云，偏移层标注「未配准」</div></div></div>`;
  } else {
    const m = pairs[pcvSel];
    right = m ? `<div class="panel" style="margin:0"><div class="panel-hd"><span class="dot"></span>${m.space} · 1v1 合模<span class="extra" style="display:flex;gap:6px;align-items:center"><span class="badge ${m.reg ? 'b-ok' : 'b-warn'}" style="font-size:9px">${m.reg ? '已配准' : '未配准'}</span><button class="btn sm ghost" style="padding:2px 8px;font-size:10px" onclick="pcvBack()">返回整体视图</button></span></div>
      <div class="panel-bd">${pcvOv(m)}<div class="muted" style="margin-top:4px;font-size:10px">${m.name} ↔ ${bims[m.bim]}</div>${m.reg ? `<div style="margin-top:2px;color:var(--tx-dim);font-size:10px">RMSE ${res.rmse} mm · 重叠率 ${res.overlap}%</div>` : ''}</div></div>` : '';
  }
  return `<div style="display:grid;grid-template-columns:300px 1fr;gap:14px;align-items:start">
    <div>
      <div class="queue-item" style="cursor:pointer;${pcvSel < 0 ? 'border-left:2px solid var(--cy)' : ''}" onclick="pcvBack()"><span style="min-width:0"><b style="font-size:11px;color:var(--tx-hi)">🏢 整体合模视图</b><br><span class="muted" style="font-size:10px">整单体 · 多层 BIM + 全部点云</span></span></div>
      <div class="muted" style="font-size:11px;margin:10px 0 6px">配对列表（${pairs.length}）· 点击看 1v1 合模</div>
      ${pairs.map((m, i) => `<div class="queue-item" style="cursor:pointer;${pcvSel === i ? 'border-left:2px solid var(--cy)' : ''}" onclick="pcvFocus(${i})"><span style="min-width:0"><b style="font-size:11px;color:var(--tx-hi)">${m.space}</b><br><span class="muted" style="font-size:10px">${m.name}<br>↔ ${bims[m.bim]}</span></span><span class="badge ${m.reg ? 'b-ok' : 'b-warn'}" style="font-size:9px">${m.reg ? '已配准' : '未配准'}</span></div>`).join('') || '<div class="muted" style="font-size:11px">暂无配对</div>'}
      ${(unPc.length || unBim.length) ? `<div class="muted" style="font-size:11px;margin:12px 0 6px">未配对</div>
        ${unPc.map(m => `<div class="queue-item"><span style="min-width:0;font-size:10px">🧊 ${m.name}</span><span class="badge b-warn" style="font-size:9px">点云 · 未选 BIM</span></div>`).join('')}
        ${unBim.map(b => `<div class="queue-item"><span style="min-width:0;font-size:10px">🏗 ${b}</span><span class="badge b-dim" style="font-size:9px">BIM · 无点云</span></div>`).join('')}` : ''}
    </div>
    <div>${right}</div>
  </div>`;
}
function pcvOpen(){ document.getElementById('pcvBd').innerHTML = pcvHtml(); document.getElementById('pcvMask').classList.add('on'); }
function pcvFocus(i){ pcvSel = i; document.getElementById('pcvBd').innerHTML = pcvHtml(); }
function pcvBack(){ pcvSel = -1; document.getElementById('pcvBd').innerHTML = pcvHtml(); }
function pcvBldSet(id){ pcvBld = id; pcvSel = -1; document.getElementById('pcvBd').innerHTML = pcvHtml(); }
'''

SORT_OLD = '''        <select class="input" style="width:210px;font-size:11px" onchange="navSort=this.value;renderCfgDetail()">
          <option value="time" ${navSort === 'time' ? 'selected' : ''}>排序：按时间（新 → 旧）</option>
          <option value="st" ${navSort === 'st' ? 'selected' : ''}>排序：按状态（已配准优先）</option>
          <option value="fl" ${navSort === 'fl' ? 'selected' : ''}>排序：按楼层（单体 · 地下 → 地上）</option>
        </select>'''
SORT_NEW = '''        <span style="display:flex;gap:4px;align-items:center"><span class="muted" style="font-size:10px">排序</span>${[['st', '按状态'], ['time', '按时间'], ['fl', '按空间']].map(([v, tx]) => `<button class="btn sm ghost" style="padding:3px 10px;font-size:10px;${navSort === v ? 'border-color:var(--cy);color:var(--cy);background:rgba(34,211,238,.08)' : ''}" onclick="navSort='${v}';renderCfgDetail()">${tx}</button>`).join('')}</span>'''

for path in ['index.html', 'light/index.html']:
    s = io.open(path, encoding='utf-8').read()
    # 1. 去掉「分支：」前缀
    old = '分支：已开 → 直接通过'
    assert s.count(old) == 1, (path, '分支', s.count(old))
    s = s.replace(old, '已开 → 直接通过')
    # 2. 排序组件改为平铺按钮
    assert s.count(SORT_OLD) == 1, (path, 'sort', s.count(SORT_OLD))
    s = s.replace(SORT_OLD, SORT_NEW)
    # 3. 查看配准改为单一视口（整体/1v1）
    start = s.index('/* 查看配准')
    end = s.index('function cfgRegHtml(r){', start)
    s = s[:start] + NEW_PCV + s[end:]
    io.open(path, 'w', encoding='utf-8').write(s)
    print(path, 'patched: 分支/排序/查看配准')
