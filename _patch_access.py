# -*- coding: utf-8 -*-
"""V8.4 补丁：接入中心（控制台地址/充电待命/模组四态/智能通行控制）+ 空间管理（门电梯过滤）+ 监控中心（接管iframe/弱网/离线包/充电桩门标记）"""
import io, shutil, os

P = 'index.html'
shutil.copy(P, 'backups/index_before_v84.html')
src = io.open(P, encoding='utf-8').read()

edits = []
def E(label, old, new):
    edits.append((label, old, new))

# ========== E1 CSS 追加 ==========
E('css', r""".tk-pad button:active{background:rgba(34,211,238,.3);transform:scale(.94)}""",
r""".tk-pad button:active{background:rgba(34,211,238,.3);transform:scale(.94)}
/* v8.4 电量刻度 / 离线位置 / 充电桩 / 门·电梯标记 */
.batt{position:relative}
.batt .tick{position:absolute;top:0;bottom:0;width:2px;background:#fbbf24;opacity:.95}
.batt .tick.r{background:#f87171}
.mn-bot .blast{font-size:9px;padding:0 6px;border-radius:6px;background:rgba(6,12,24,.85);border:1px solid rgba(248,113,113,.4);color:#f8a5a5;white-space:nowrap}
.chg-mk{position:absolute;z-index:7;transform:translate(-50%,-100%);display:flex;flex-direction:column;align-items:center;gap:2px}
.chg-mk .ic{width:20px;height:20px;border-radius:6px;display:flex;align-items:center;justify-content:center;font-size:11px;background:rgba(6,12,24,.9);border:1.5px solid}
.chg-mk.free .ic{border-color:#34d399;color:#34d399;box-shadow:0 0 8px rgba(52,211,153,.5)}
.chg-mk.occ .ic{border-color:#22d3ee;color:#22d3ee;box-shadow:0 0 8px rgba(34,211,238,.5)}
.chg-mk.fault .ic{border-color:#f87171;color:#f87171;box-shadow:0 0 8px rgba(248,113,113,.6)}
.chg-mk .lb2{font-size:9px;padding:0 6px;border-radius:6px;background:rgba(6,12,24,.85);border:1px solid var(--border);color:#9fb3c8;white-space:nowrap}
.gate-mk{position:absolute;z-index:7;transform:translate(-50%,-50%);width:22px;height:22px;border-radius:6px;display:flex;align-items:center;justify-content:center;font-size:12px;background:rgba(6,12,24,.92);border:1.5px solid #34d399;color:#34d399;cursor:pointer;box-shadow:0 0 8px rgba(52,211,153,.45)}
.gate-mk.noapi{border-color:#f87171;color:#f87171;box-shadow:0 0 10px rgba(248,113,113,.6)}
.gate-mk.visual{border-color:#38bdf8;color:#38bdf8;box-shadow:0 0 8px rgba(56,189,248,.45)}
.gate-mk.manual{border-color:#8a97a8;color:#8a97a8;box-shadow:none}
.gate-mk.lift{border-color:#a78bfa;color:#a78bfa;box-shadow:0 0 8px rgba(167,139,250,.45)}
.gate-mk.passing{animation:gateblink 1s infinite}
@keyframes gateblink{50%{box-shadow:0 0 16px currentColor;transform:translate(-50%,-50%) scale(1.15)}}
.gate-chip{padding:3px 10px;font-size:10.5px;border:1px solid var(--border);border-radius:7px;color:var(--tx-dim);cursor:pointer;transition:.15s;user-select:none}
.gate-chip.on{border-color:var(--cy);color:var(--cy);background:rgba(34,211,238,.1)}""")

# ========== E2 ROBOT_DEV / DOORS / LIFTS / CHARGES 数据 ==========
E('data', r"""            api:{mid360:'normal',g5:'exception',ctrl:'normal',speaker:'normal',pano:'normal',spatial:'normal'} },
};""",
r"""            api:{mid360:'normal',g5:'exception',ctrl:'normal',speaker:'normal',pano:'normal',spatial:'normal'} },
};
/* v8.4 设备扩展：控制台地址（远程接管 iframe）/ 固件 / SDK / 心跳 */
const ROBOT_DEV = {
  go1:    { console:'http://123.57.179.149:8188/', fw:'GO1 固件 v1.4.2',  sdk:'Unitree SDK2 v2.0.1' },
  mira:   { console:'http://123.57.179.149:8188/', fw:'MiraOS v2.3.0',    sdk:'AgiBot SDK v1.8.0' },
  panther:{ console:'http://123.57.179.149:8188/', fw:'B2 固件 v3.1.0',   sdk:'Unitree SDK2 v2.0.1' },
  cyber:  { console:'',                            fw:'X20 固件 v1.0.9',  sdk:'DeepRobotics SDK v1.2' },
  go2:    { console:'http://123.57.179.149:8188/', fw:'GO2 固件 v1.1.7',  sdk:'Unitree SDK2 v2.0.1' },
};
const BAT_CHG = 20, BAT_LOW = 35;   /* 回充阈值 / 禁派阈值（接入中心可配 · 需实测校准） */
/* 门 / 电梯（空间管理语义识别自 BIM · 空间组织过滤标识 + 接入中心智能通行控制 + 监控地图标记 共用） */
let GATE_UNIFIED = true;            /* 统一网关：勾选后全部自动门默认共用 GW-01 视为已配置，单门可覆盖 */
const DOORS = [
  { id:'D-01', name:'大堂入口自动门', space:'主楼 1F · 大堂',     fl:'main-1f', type:'auto',   api:'', ownGw:false, strategy:'开门请求 → 通行确认', route:'配送路线 · 取货段', x:47, y:80, vx:38, vy:62, passing:false },
  { id:'D-02', name:'闸机 G-02',      space:'主楼 1F · 大堂',     fl:'main-1f', type:'auto',   api:'', ownGw:false, strategy:'鉴权开门 → 防夹检测', route:'巡检路线 · 大堂段', x:58, y:74, vx:44, vy:66, passing:true },
  { id:'D-03', name:'办公区玻璃门',   space:'主楼 3F · 走廊',     fl:'main-3f', type:'auto',   api:'', ownGw:true,  strategy:'开门请求 → 通行确认', route:'—',                x:52, y:46, vx:52, vy:40, passing:false },
  { id:'D-04', name:'研发大厅消防门', space:'主楼 1F · 研发大厅', fl:'main-1f', type:'visual', api:'', ownGw:false, strategy:'视觉检测开/关 → 通行', route:'巡检路线 · 研发层', x:24, y:36, vx:30, vy:44, passing:false },
  { id:'D-05', name:'楼梯间防火门',   space:'主楼 1F · 楼梯间',   fl:'main-1f', type:'manual', api:'', ownGw:false, strategy:'手动门 → 绕行备选路线', route:'—',               x:82, y:30, vx:60, vy:36, passing:false },
];
const LIFTS = [
  { id:'L-01', name:'客梯 L1', space:'主楼 · 电梯厅', fl:'main-1f', floors:'B1 - 3F', api:'POST /lift/call · /lift/select · /lift/status', loc:'轿厢局部图 + 激光重定位', x:70, y:22, vx:47, vy:50 },
  { id:'L-02', name:'客梯 L2', space:'主楼 · 电梯厅', fl:'main-1f', floors:'B1 - 3F', api:'POST /lift/call · /lift/select · /lift/status', loc:'轿厢局部图 + 激光重定位', x:75, y:22, vx:50, vy:50 },
];
/* 充电桩（监控中心地图标记 · 空闲/占用/故障三态 · 接口依赖东方） */
const CHARGES = [
  { id:'chg-a', name:'充电桩 A', x:23, y:66, st:'occ',   by:'清星小智' },
  { id:'chg-b', name:'充电桩 B', x:29, y:71, st:'free',  by:'' },
  { id:'chg-c', name:'充电桩 C', x:26, y:60, st:'fault', by:'' },
];
/* 离线具身：最后已知位置 + 离线时长 */
const LAST_KNOWN = { cyber:{ loc:'外摆区', dur:'2h13m', time:'08-28 06:41' } };""")

# ========== E3 mira MID360 → 未搭载 ==========
E('mira-unmounted', r"""api:{mid360:'normal',g5:'normal',ctrl:'normal',speaker:'normal',pano:'disconnected',spatial:'normal'} },""",
r"""api:{mid360:'unmounted',g5:'normal',ctrl:'normal',speaker:'normal',pano:'disconnected',spatial:'normal'} },""")

# ========== E4 API_ST 四态 ==========
E('api-st', r"""const API_ST = { normal:['正常','b-ok','#34d399'], exception:['异常','b-danger','#f87171'], disconnected:['断开','b-danger','#f87171'] };""",
r"""const API_ST = { normal:['已连接','b-ok','#34d399'], exception:['异常','b-danger','#f87171'], disconnected:['未连接','b-dim','#8a97a8'], unmounted:['未搭载','b-dim','#5b6b85'] };""")

# ========== E5 MENU_L2 加智能通行控制 ==========
E('menu-l2', r"""config:[['base','基础信息',null],['reg','配准',null],['api','能力模组',null],['dispatch','工作分配',null]],""",
r"""config:[['base','基础信息',null],['reg','配准',null],['api','能力模组',null],['pass','智能通行控制',null],['dispatch','工作分配',null]],""")

# ========== E6 renderCfgDetail ==========
E('cfg-guard', r"""  if(!l2ok('config',curCfgTab)) curCfgTab = ['base','reg','api','dispatch'].find(x=>l2ok('config',x))||'base';""",
r"""  if(!l2ok('config',curCfgTab)) curCfgTab = ['base','reg','api','pass','dispatch'].find(x=>l2ok('config',x))||'base';""")
E('cfg-branch', r"""  else if(curCfgTab==='api') body = cfgApiHtml(r) + `<div class="td-sec">对接外部系统 / 组件</div>` + cfgLiftHtml(r) + cfgGateHtml(r);""",
r"""  else if(curCfgTab==='api') body = cfgApiHtml(r);
  else if(curCfgTab==='pass') body = cfgPassHtml(r);""")
E('cfg-tab', r"""      ${l2ok('config','api')?`<button class="ptab ${curCfgTab==='api'?'on':''}" onclick="cfgTab('api')"><span class="pi">🧩</span>能力模组</button>`:''}""",
r"""      ${l2ok('config','api')?`<button class="ptab ${curCfgTab==='api'?'on':''}" onclick="cfgTab('api')"><span class="pi">🧩</span>能力模组</button>`:''}
      ${l2ok('config','pass')?`<button class="ptab ${curCfgTab==='pass'?'on':''}" onclick="cfgTab('pass')"><span class="pi">🚦</span>智能通行控制</button>`:''}""")

# ========== E7 cfgBaseHtml ==========
E('base-dev', r"""function cfgBaseHtml(r){
  const stBadge = r.st==='online'?'b-ok':r.st==='executing'?'b-task':r.st==='offline'?'b-dim':'b-danger';
  const ext = ROBOT_EXT[curCfg];""",
r"""function cfgBaseHtml(r){
  const stBadge = r.st==='online'?'b-ok':r.st==='executing'?'b-task':r.st==='offline'?'b-dim':'b-danger';
  const ext = ROBOT_EXT[curCfg];
  const dev = ROBOT_DEV[curCfg]||{};""")

E('base-edit-rows', r"""<div class="form-row"><label>充电/待命区域</label><select class="input" onchange="ROBOTS[curCfg].dock=this.value">${POINTS.filter(p=>p.uses.includes('充电/待命')).map(p=>`<option ${p.bld+'-'+p.name===r.dock?'selected':''}>${p.bld}-${p.name}</option>`).join('')}</select></div>""",
r"""<div class="form-row"><label>充电/待命区域</label><select class="input" onchange="ROBOTS[curCfg].dock=this.value">${POINTS.filter(p=>p.uses.includes('充电/待命')).map(p=>`<option ${p.bld+'-'+p.name===r.dock?'selected':''}>${p.bld}-${p.name}</option>`).join('')}</select></div>
      <div class="form-row"><label>控制台地址</label><input class="input" value="${dev.console||''}" placeholder="远程接管控制台 URL（如 http://ip:port/）· 未配置则接管置灰" onchange="(ROBOT_DEV[curCfg]=ROBOT_DEV[curCfg]||{}).console=this.value"></div>
      <div class="form-row"><label>电量策略</label><span style="font-size:12px;display:flex;align-items:center;gap:6px">回充 <input class="input" style="width:52px;padding:3px 6px" value="${BAT_CHG}"> % · 禁派 <input class="input" style="width:52px;padding:3px 6px" value="${BAT_LOW}"> % <span class="muted" style="font-size:10px">需实测校准</span></span></div>""")

E('base-hero-5g', r"""<div style="font-size:18px;font-weight:700;color:var(--tx-hi)">${r.name} <span class="badge ${stBadge}">${r.stTx}</span></div>""",
r"""<div style="font-size:18px;font-weight:700;color:var(--tx-hi)">${r.name} <span class="badge ${stBadge}">${r.stTx}</span>${r.api.g5==='exception'?' <span class="badge b-danger">5G 异常 · 整机按离线</span>':''}</div>""")

E('base-attr', r"""      <tr><td>充电/待命区域</td><td>${r.dock} <span class="muted" style="font-size:10px">（点位在「空间管理 · 点位管理」维护，用途为 充电/待命）</span></td></tr>
      <tr><td>绑定 LocMap</td><td>${r.map}</td></tr>
      <tr><td>API 地址</td><td style="font-family:var(--mono);font-size:11px">http://101.133.138.114:8188/openapi/v1</td></tr>
    </table>""",
r"""      <tr><td>充电/待命区域</td><td>${r.dock} <span class="muted" style="font-size:10px">（点位在「空间管理 · 点位管理」维护，用途为 充电/待命）</span></td></tr>
      <tr><td>电量</td><td><span class="batt"><i style="width:${r.battery}%;background:${r.battery>50?'#34d399':r.battery>BAT_LOW?'#fbbf24':'#f87171'}"></i><i class="tick" style="left:${BAT_CHG}%" title="回充阈值 ${BAT_CHG}%"></i><i class="tick r" style="left:${BAT_LOW}%" title="禁派阈值 ${BAT_LOW}%"></i></span>${r.battery}%${r.battery<BAT_LOW?' <span class="badge b-warn" style="font-size:9px">低于禁派阈值 · 暂停派单</span>':''}</td></tr>
      <tr><td>电量策略</td><td style="font-size:11px">回充阈值 <b style="color:#fbbf24">${BAT_CHG}%</b> · 禁派阈值 <b style="color:#f87171">${BAT_LOW}%</b> <span class="muted">（双刻度见电量条 · 阈值需实测校准）</span></td></tr>
      <tr><td>控制台地址</td><td style="font-family:var(--mono);font-size:11px">${dev.console||'<span class="badge b-dim">未配置 · 远程接管置灰</span>'}</td></tr>
      <tr><td>固件 / SDK</td><td style="font-size:11px">${dev.fw||'—'} · ${dev.sdk||'—'}</td></tr>
      <tr><td>最近心跳</td><td style="font-size:11px">${r.st==='offline'?'08-28 06:41:02 <span class="muted">（离线 2h13m）</span>':'刚刚 <span class="muted">· 5s 周期</span>'}</td></tr>
      <tr><td>绑定 LocMap</td><td>${r.map}</td></tr>
      <tr><td>API 地址</td><td style="font-family:var(--mono);font-size:11px">http://101.133.138.114:8188/openapi/v1</td></tr>
    </table>""")

E('base-modblock', r"""  return `<div class="cfg-hero">${img}""",
r"""  /* 模组异常 → 反向置灰对应可执行任务（5G 异常整机离线，全部置灰） */
  const modBlock = {};
  if(r.api.pano!=='normal') modBlock['巡检']='全景相机模块 · '+API_ST[r.api.pano][0];
  if(r.api.speaker!=='normal') modBlock['导引']='扬声器拾音器模组 · '+API_ST[r.api.speaker][0];
  if(r.api.g5==='exception') modBlock['*']='5G 数据模块异常 · 整机按离线处理';
  return `<div class="cfg-hero">${img}""")

E('base-tasks', r"""    ${[['巡检','property'],['导引','guide'],['配送','delivery']].map(([post,sceneKey])=>{
      const bound = ext.scenes.includes(sceneKey);
      const list = POST_TASKS[post]||[];
      const head = post==='巡检' ? '巡检（消防 / 一般物业 / 设备巡检）' : post;
      return `<div class="muted" style="font-size:10.5px;margin:8px 0 2px">— ${head} · 对应场景「${BIND_SCENES[sceneKey]}」${bound?'':' <span class="badge b-dim" style="font-size:9px">未绑定场景 · 不可启用</span>'}</div>` +
        list.map(t=>`<div class="pt-item" style="${bound?'cursor:pointer':'opacity:.4;pointer-events:none'}" onclick="dspToggleTask('${t}')">
          <span class="tg ${ds.tasks[t]&&bound?'on':''}" style="pointer-events:none"><i></i></span>
          <span style="font-size:12px">${t}</span>
          <span class="badge ${ds.tasks[t]&&bound?'b-ok':'b-dim'}" style="margin-left:auto">${ds.tasks[t]&&bound?'已启用':'未启用'}</span>
        </div>`).join('');
    }).join('')}`;""",
r"""    ${[['巡检','property'],['导引','guide'],['配送','delivery']].map(([post,sceneKey])=>{
      const bound = ext.scenes.includes(sceneKey);
      const mBlock = modBlock['*'] || modBlock[post] || '';
      const usable = bound && !mBlock;
      const list = POST_TASKS[post]||[];
      const head = post==='巡检' ? '巡检（消防 / 一般物业 / 设备巡检）' : post;
      return `<div class="muted" style="font-size:10.5px;margin:8px 0 2px">— ${head} · 对应场景「${BIND_SCENES[sceneKey]}」${bound?'':' <span class="badge b-dim" style="font-size:9px">未绑定场景 · 不可启用</span>'}${mBlock?` <span class="badge b-danger" style="font-size:9px" title="模组恢复后自动解除置灰">⚠ ${mBlock} · 暂不可用</span>`:''}</div>` +
        list.map(t=>`<div class="pt-item" style="${usable?'cursor:pointer':'opacity:.4;pointer-events:none'}" onclick="dspToggleTask('${t}')">
          <span class="tg ${ds.tasks[t]&&usable?'on':''}" style="pointer-events:none"><i></i></span>
          <span style="font-size:12px">${t}</span>
          <span class="badge ${ds.tasks[t]&&usable?'b-ok':'b-dim'}" style="margin-left:auto">${ds.tasks[t]&&usable?'已启用':'未启用'}</span>
        </div>`).join('');
    }).join('')}`;""")

# ========== E8 cfgApiHtml 重写 ==========
old_api = src[src.index('function cfgApiHtml(r){'):src.index('function cfgTasksHtml(r){')]
new_api = r"""function cfgApiHtml(r){
  const cards = API_MODS.map(m=>{
    const s = r.api[m.key], [tx,bd] = API_ST[s];
    const unm = s==='unmounted';
    return `<div class="api-card"${unm?' style="opacity:.55"':''}>
      <div style="display:flex;align-items:center;gap:8px"><span style="font-size:16px">${m.icon}</span><b style="font-size:13px;color:var(--tx-hi)">${m.name}</b><span class="badge ${bd}" style="margin-left:auto">${tx}</span></div>
      <div class="ep">${m.ep}</div>
      <div class="muted" style="font-size:11px">${m.desc}</div>
      <div class="hb"><span>心跳 ${s==='normal'?'2026-08-28 14:32:08':'—'}</span><span>延迟 ${s==='normal'?(10+m.key.length*3)+'ms':'—'}</span></div>
      <div style="display:flex;gap:8px;flex-wrap:wrap">
        ${unm?'<span class="muted" style="font-size:10px">该机型未搭载此模组（清单固定 6 项，按机型配置）</span>':`<button class="btn sm btn-test" onclick="toast('测试连接 ${m.ep}：${s==='normal'?'✓ 连接正常':'✗ '+tx+'，请检查模组状态'}')">测试连接</button>
        ${s==='exception'||s==='disconnected'?`<button class="btn sm" onclick="toast('正在重试连接 ${m.name}…（结果写入连接日志）')">重试连接</button>`:''}
        ${s==='exception'?`<button class="btn sm ghost" onclick="modLogOpen('${m.key}')">📄 连接日志</button>`:''}`}
      </div>
    </div>`;
  }).join('');
  const n = Object.values(r.api).filter(v=>v==='normal').length;
  const total = API_MODS.length;
  const col = n===total?'#00BFA5':n>=total/2?'#fbbf24':'#f87171';
  const blockTx = [];
  if(r.api.pano==='exception'||r.api.pano==='disconnected') blockTx.push('巡检类任务（全景相机模块'+API_ST[r.api.pano][0]+'）');
  if(r.api.speaker==='exception'||r.api.speaker==='disconnected') blockTx.push('导览类任务（扬声器拾音器模组'+API_ST[r.api.speaker][0]+'）');
  return `<div class="api-grid">${cards}</div>
    ${r.api.g5==='exception'?`<div class="dbg-banner fail" style="margin-top:10px">⚠ 5G 数据模块异常 —— 整机按「离线」处理：任务包本地自治执行，数据回连补传；请优先恢复 5G 链路</div>`:''}
    ${blockTx.length?`<div class="sug" style="margin-top:10px;border-color:#fbbf2455;background:#fbbf2411;font-size:11px">⚠ 模组异常已联动置灰可执行任务：${blockTx.join('；')}（详见「基础信息 · 可执行任务」，模组恢复后自动解除）</div>`:''}
    <div class="api-ov">
      <div style="display:flex;align-items:center;justify-content:space-between"><b style="font-size:13px;color:var(--tx-hi)">模组连接状态总览</b><span style="font-family:var(--mono);color:${col}">${n}/${total} 已连接</span></div>
      <div class="bar"><i style="width:${n/total*100}%;background:${col}"></i></div>
      <button class="btn sm ghost" onclick="toast('一键重连全部模组…（演示）')">🔁 一键重连全部</button>
    </div>`;
}
/* 模组连接日志（最近 10 条连接事件） */
const MOD_LOGS = {
  spatial:[['14:20:11','连接断开：心跳超时 15s'],['14:20:26','重连尝试 ① 失败（EOF）'],['14:21:02','重连尝试 ② 失败（超时）'],['14:22:40','重连成功，延迟 220ms'],['14:23:05','数据校验异常：点云帧丢失 ×3'],['14:23:05','标记模组状态 = 异常'],['14:25:31','重连尝试 ① 失败'],['14:28:10','重连尝试 ② 失败'],['14:30:44','平台健康检查：异常保持'],['14:32:08','等待人工处理 / 自动重试中（60s 间隔）']],
  g5:[['09:12:03','5G 信号强度 -96dBm（弱）'],['09:12:40','注册基站失败'],['09:14:22','切换备用 APN 失败'],['09:15:01','模组状态 = 异常 · 整机按离线'],['09:18:33','重试连接失败'],['09:24:10','重试连接失败'],['09:30:00','重试连接失败'],['09:36:20','信号恢复 -82dBm · 尝试注册'],['09:36:41','注册失败（SIM 状态异常）'],['09:40:00','告警推送：已通知运维（小舆）']],
};
function modLogOpen(key){
  const m = API_MODS.find(x=>x.key===key); if(!m) return;
  document.getElementById('mlName').textContent = m.name;
  document.getElementById('mlBody').innerHTML = (MOD_LOGS[key]||MOD_LOGS.g5).map(l=>`<div style="display:flex;gap:10px;padding:4px 0;border-bottom:1px dashed var(--border)"><span style="font-family:var(--mono);color:var(--tx-dim);flex:none">${l[0]}</span><span style="font-size:11.5px">${l[1]}</span></div>`).join('');
  document.getElementById('mlMask').classList.add('on');
}
"""
edits.append(('api-rewrite', old_api, new_api))

# ========== E9 cfgLiftHtml / cfgGateHtml → 智能通行控制 ==========
old_pass = src[src.index('function cfgLiftHtml(r){'):src.index('function cfgBaseHtml(r){')]
new_pass = r"""/* ---- 智能通行控制：门控 / 梯控（v8.4 · 门/电梯数据与空间管理、监控地图共用） ---- */
let passTab = 'gate';
function doorApiTx(d){
  if(d.type!=='auto') return d.type==='visual'?'—（视觉检测）':'—（手动绕行）';
  if(d.api) return d.api;
  if(GATE_UNIFIED && !d.ownGw) return '统一网关 GW-01 <span class="badge b-cy" style="font-size:9px">继承</span>';
  return '<span class="badge b-danger" style="font-size:9px">未配置 API ⚠</span>';
}
function doorTypeTx(d){ return d.type==='auto'?'自动门':d.type==='visual'?'非自动门 · 视觉检测':'手动门 · 绕行'; }
function doorNoApi(d){ return d.type==='auto' && !d.api && (!GATE_UNIFIED || d.ownGw); }
function cfgPassHtml(r){
  return `
  <div class="ptabs" style="padding:0 0 10px">
    <button class="ptab ${passTab==='gate'?'on':''}" onclick="passTab='gate';renderCfgDetail()"><span class="pi">🚪</span>门控</button>
    <button class="ptab ${passTab==='lift'?'on':''}" onclick="passTab='lift';renderCfgDetail()"><span class="pi">🛗</span>梯控</button>
    <span class="muted" style="font-size:10px;margin-left:auto;align-self:center">门 / 电梯构件由空间管理语义识别自动提取（空间组织模型区「门 / 电梯」过滤查看）</span>
  </div>
  ${passTab==='gate'?cfgGateHtml(r):cfgLiftHtml(r)}`;
}
function cfgGateHtml(r){
  const unCfg = DOORS.filter(doorNoApi);
  return `
  <div class="panel" style="margin-bottom:10px"><div class="panel-hd"><span class="dot"></span>门点管理<span class="extra">${DOORS.length} 个门点 · 自动门 ${DOORS.filter(d=>d.type==='auto').length}</span></div>
    <div class="panel-bd" style="font-size:12px">
      <label style="display:flex;align-items:center;gap:8px;font-size:12px;margin-bottom:8px;cursor:pointer"><input type="checkbox" ${GATE_UNIFIED?'checked':''} style="accent-color:#22d3ee" onchange="gateUnified(this.checked)"> <span><b style="color:var(--tx-hi)">统一网关（GW-01）</b> —— 勾选后全部自动门默认共用该网关、视为已配置；单门仍可单独覆盖（兼容「商铺各自网关」与「整楼统一网关」两种形态）</span></label>
      ${DOORS.map(d=>{
        const noApi = doorNoApi(d);
        return `<div class="pt-item" style="${noApi?'border-left:2px solid #f87171':''}">
          <span style="font-size:14px">${d.type==='auto'?'🚪':d.type==='visual'?'👁':'🖐'}</span>
          <span style="min-width:0"><b style="font-size:12px;color:${noApi?'#f87171':'var(--tx-hi)'}">${d.name}</b> <span class="badge b-dim" style="font-size:9px">${d.id}</span><br><span class="muted" style="font-size:10px">${d.space} · ${doorTypeTx(d)} · ${d.strategy}</span></span>
          <span style="margin-left:auto;text-align:right;font-size:10.5px">${doorApiTx(d)}<br><span class="muted" style="font-size:10px">关联：${d.route}</span></span>
          <button class="btn sm ghost" onclick="doorSetOpen('${d.id}')">设置</button>
        </div>`;
      }).join('')}
      ${unCfg.length?`<div class="dbg-banner fail" style="margin-top:8px">⚠ ${unCfg.map(d=>d.name).join('、')} 为自动门但未配置门控 API（空间管理与监控地图中红色显示）—— 请配置 API 或改标为「非自动门」</div>`:''}
    </div>
  </div>
  <div class="panel" style="margin-bottom:10px"><div class="panel-hd"><span class="dot"></span>通行状态机<span class="extra">超时重试次数可配</span></div>
    <div class="panel-bd">
      <div class="pipe" style="margin-top:0;flex-wrap:wrap">
        <div class="pipe-node done"><b>接近门</b>减速停驻</div><div class="pipe-arrow">→</div>
        <div class="pipe-node done"><b>停下检测</b>视觉识别开/关</div><div class="pipe-arrow">→</div>
        <div class="pipe-node cur"><b>开门请求</b>门控 API 下发</div><div class="pipe-arrow">→</div>
        <div class="pipe-node"><b>等待确认</b>门开到位回执</div><div class="pipe-arrow">→</div>
        <div class="pipe-node"><b>通过</b>防夹检测通行</div>
      </div>
      <p class="muted" style="font-size:11px;margin-top:6px">分支：已开 → 直接通过；未开 → 发开门请求；超时（默认 20s）→ 重试 ×2 → 人工兜底（小舆推送 → 远程开门 / 改路线 / 终止任务）。</p>
    </div>
  </div>
  <div class="panel"><div class="panel-hd"><span class="dot"></span>通行日志<span class="extra">演示</span></div>
    <div class="panel-bd" style="font-size:11px">
      ${[['14:02:11','闸机 G-02','开门请求 → 回执 180ms → 通行完成','b-ok','成功'],['13:47:52','大堂入口自动门','检测未开 → 开门请求 → 确认 → 通过','b-ok','成功'],['11:20:03','办公区玻璃门','开门请求超时 ×2 → 转人工兜底（远程开门）','b-warn','人工']].map(l=>`<div class="queue-item"><span>${l[0]} · ${l[1]} — ${l[2]}</span><span class="badge ${l[3]}" style="font-size:9px">${l[4]}</span></div>`).join('')}
    </div>
  </div>`;
}
function gateUnified(on){ GATE_UNIFIED=on; renderCfgDetail(); renderMnBots(); renderSpcView(); toast(on?'统一网关 GW-01 已启用：全部自动门默认继承（单门可覆盖）':'已关闭统一网关：各自动门需单独配置门控 API'); }
function cfgLiftHtml(r){
  return `
  <div class="panel" style="margin-bottom:10px"><div class="panel-hd"><span class="dot"></span>梯控配置<span class="extra"><span class="badge b-warn" style="font-weight:400">云际 · 联调中</span></span></div>
    <div class="panel-bd" style="font-size:12px">
      ${LIFTS.map(l=>`<div class="pt-item"><span style="font-size:14px">🛗</span><span style="min-width:0"><b style="font-size:12px;color:var(--tx-hi)">${l.name}</b> <span class="badge b-dim" style="font-size:9px">${l.id}</span><br><span class="muted" style="font-size:10px">${l.space} · 服务楼层 ${l.floors} · 轿厢定位：${l.loc}</span></span><span style="margin-left:auto;font-family:var(--mono);font-size:10px;text-align:right">${l.api}</span><button class="btn sm btn-test" onclick="toast('测试连接 ${l.name} 梯控 API：✓ 呼叫响应 320ms（演示）')">测试</button></div>`).join('')}
      <div class="muted" style="font-size:10.5px;margin-top:6px">选层指令按「支持 API」设计；<b style="color:#fbbf24">降级说明</b>：电梯不支持选层 API 时，由人工 / 机械按层，平台仅下发呼梯与到层检测。</div>
    </div>
  </div>
  <div class="panel" style="margin-bottom:10px"><div class="panel-hd"><span class="dot"></span>乘梯指令集（定稿顺序）<span class="extra">每步含成功判定 / 超时重试</span></div>
    <div class="panel-bd">
      <div class="pipe" style="margin-top:0;flex-wrap:wrap;row-gap:8px">
        ${['呼梯','到梯检测','进轿厢（不改位姿）','选层','切图目标层','轿厢内重定位','到达判定','开电梯门','出轿厢'].map((s,i)=>`${i?'<div class="pipe-arrow">→</div>':''}<div class="pipe-node ${i<3?'done':i===3?'cur':''}"><b>${i+1}. ${s}</b>${['厅门呼叫','门开到位','保持朝向直入','API · 降级人工/机械','切换目标层地图','平台指定点位 · 失败重试/上报','楼层回执比对','门开确认','驶出续行'][i]}</div>`).join('')}
      </div>
      <p class="muted" style="font-size:11px;margin-top:6px">异常分支：呼梯无响应 → 重试 → 转人工；轿厢内断网 → 到站自动恢复定位；跨层任务在任务详情与地图上显示「乘梯中」节点。</p>
      <div style="display:flex;gap:8px;margin-top:6px">
        <button class="btn sm btn-test" onclick="toast('测试连接 梯控 API：✓ 呼叫响应 320ms（演示）')">测试连接</button>
        <button class="btn sm ghost" onclick="toast('已发起一次模拟乘梯联调（演示）')">模拟乘梯</button>
      </div>
    </div>
  </div>`;
}
/* 门点设置弹窗（空间管理 / 门控页签 / 监控地图共用） */
let doorSetId = null;
function doorSetOpen(id){
  doorSetId = id;
  const d = DOORS.find(x=>x.id===id); if(!d) return;
  document.getElementById('dsName').textContent = d.name;
  document.getElementById('dsType').value = d.type;
  document.getElementById('dsApi').value = d.api||'';
  dsTypeHint();
  document.getElementById('dsMask').classList.add('on');
}
function dsTypeHint(){
  const t = document.getElementById('dsType').value;
  document.getElementById('dsApiRow').style.display = t==='auto'?'':'none';
  document.getElementById('dsHint').textContent = t==='auto'
    ? (GATE_UNIFIED?'自动门需配置门控 API；留空则继承统一网关 GW-01（单门可覆盖）':'自动门需配置门控 API；留空将在模型与地图中红色标记「未配置 API」')
    : t==='visual' ? '非自动门：视觉识别开/关状态，开门由人协助通行' : '手动门：不经此门通行，路径规划自动绕行备选路线';
}
function dsSave(){
  const d = DOORS.find(x=>x.id===doorSetId); if(!d) return;
  d.type = document.getElementById('dsType').value;
  d.api = document.getElementById('dsApi').value.trim();
  closeMask('dsMask');
  renderSpcView(); renderMnBots();
  if(curCfgTab==='pass') renderCfgDetail();
  toast('门点「'+d.name+'」已保存：'+doorTypeTx(d)+(d.type==='auto'?' · '+(d.api||'继承统一网关 GW-01'):''));
}
"""
edits.append(('pass-rewrite', old_pass, new_pass))

# ========== E10 弹窗 HTML：门点设置 + 模组日志 ==========
E('modals', r"""<!-- 轨迹回放 -->""",
r"""<!-- 门点设置 -->
<div class="mask" id="dsMask">
  <div class="modal" style="width:440px">
    <div class="modal-hd">🚪 门点设置 · <span id="dsName">—</span><button class="x" onclick="closeMask('dsMask')">✕</button></div>
    <div class="modal-bd">
      <div class="form-row"><label>门类型</label><select class="input" id="dsType" onchange="dsTypeHint()"><option value="auto">自动门（配门控 API）</option><option value="visual">非自动门 · 视觉检测</option><option value="manual">手动门 · 绕行</option></select></div>
      <div class="form-row" id="dsApiRow"><label>门控 API</label><input class="input" id="dsApi" placeholder="留空则继承统一网关 GW-01（可单门覆盖）"></div>
      <div class="muted" style="font-size:11px;line-height:1.7" id="dsHint"></div>
      <div style="display:flex;gap:10px;margin-top:12px"><button class="btn" onclick="dsSave()">保存</button><button class="btn ghost" onclick="closeMask('dsMask')">取消</button></div>
    </div>
  </div>
</div>

<!-- 模组连接日志（最近 10 条） -->
<div class="mask" id="mlMask">
  <div class="modal" style="width:480px">
    <div class="modal-hd">📄 连接日志 · <span id="mlName">—</span><button class="x" onclick="closeMask('mlMask')">✕</button></div>
    <div class="modal-bd"><div class="muted" style="font-size:10px;margin-bottom:6px">最近 10 条连接事件（模组黑匣子同步）</div><div id="mlBody"></div></div>
  </div>
</div>

<!-- 轨迹回放 -->""")

# ========== E11 向导加「充电与待命」 ==========
E('wz-steps', r"""const WZ_STEPS = ['新建设备','现场连接','模组测试','注册完成'];""",
r"""const WZ_STEPS = ['新建设备','现场连接','模组测试','充电与待命','注册完成'];""")
E('wz-go3', r"""wzGo(3)">完成注册 →""", r"""wzGo(3)">下一步：充电与待命 →""")
E('wz-capture', r"""  wzTimers.forEach(clearTimeout); wzTimers = []; wzStep = n; wzRender();
}
function wzLog(t){""",
r"""  if(wzStep===3 && n>3){ const g=id=>{const el=document.getElementById(id);return el?el.value:'';}; wzData.dock = g('wzDock'); }
  wzTimers.forEach(clearTimeout); wzTimers = []; wzStep = n; wzRender();
}
function wzLog(t){""")
E('wz-step3', r"""  } else {
    B.innerHTML = `<div style="text-align:center;padding:26px 0">""",
r"""  } else if(wzStep===3){
    const docks = POINTS.filter(p=>p.uses.includes('充电/待命'));
    B.innerHTML = `
      <div class="form-row"><label>充电桩</label><select class="input" id="wzDock">${docks.map(p=>`<option>${p.bld}-${p.name}</option>`).join('')}</select></div>
      <div class="form-row"><label>待命区域</label><select class="input" id="wzIdle">${docks.map(p=>`<option>${p.bld}-${p.name}</option>`).join('')}<option>主楼-1F 大堂待命点</option></select></div>
      <div class="form-row"><label>电量策略</label><span style="font-size:12px;display:flex;align-items:center;gap:6px">回充阈值 <input class="input" id="wzBatC" style="width:52px;padding:3px 6px" value="20"> % · 禁派阈值 <input class="input" id="wzBatL" style="width:52px;padding:3px 6px" value="35"> %</span></div>
      <div class="muted" style="font-size:11px;line-height:1.7">低于回充阈值自动回桩充电；低于禁派阈值标黄「暂停派单」并拦截任务下发。<b style="color:#fbbf24">阈值需实测校准</b>，接入后可在「基础信息」随时修改。</div>`;
    F.innerHTML = `<button class="btn ghost" onclick="wzCancel()">取消</button><button class="btn" onclick="wzGo(4)">完成注册 →</button>`;
  } else {
    B.innerHTML = `<div style="text-align:center;padding:26px 0">""")
E('wz-finish-dock', r"""caps:wzData.caps||'—', dock:'B1-充电桩 A',""",
r"""caps:wzData.caps||'—', dock:wzData.dock||'B1-充电桩 A',""")

# ========== E12 空间管理：门/电梯过滤 ==========
E('spc-filter-state', r"""let spcHidden = {};                 /* id → true 隐藏（分级加载显隐） */""",
r"""let spcHidden = {};                 /* id → true 隐藏（分级加载显隐） */
let spcGateF = { door:true, lift:true };   /* 模型区「门 / 电梯」过滤开关（语义识别构件单独标识） */
function spcGateTog(k){ spcGateF[k]=!spcGateF[k]; renderSpcView(); }""")
E('spc-view', r"""  el.innerHTML = `<div style="position:relative;flex:1;min-height:0;display:flex;flex-direction:column">${fpSvg(true)}""",
r"""  const gateChips = `<div style="display:flex;gap:6px;padding:0 2px 8px;align-items:center;flex-wrap:wrap"><span class="muted" style="font-size:10px">构件过滤：</span><span class="gate-chip ${spcGateF.door?'on':''}" onclick="spcGateTog('door')">🚪 门</span><span class="gate-chip ${spcGateF.lift?'on':''}" onclick="spcGateTog('lift')">🛗 电梯</span><span class="muted" style="font-size:9.5px">语义识别自 BIM · 点击标记可设置（自动门未配 API 红色显示）</span></div>`;
  const gateMks = (spcGateF.door?DOORS.filter(d=>d.fl===flKey):[]).map(d=>{
    const noApi = doorNoApi(d);
    const cls = d.type==='auto'?(noApi?'noapi':''):d.type==='visual'?'visual':'manual';
    return `<div class="gate-mk ${cls} ${d.passing?'passing':''}" style="left:${d.x}%;top:${d.y}%" title="${d.name} · ${doorTypeTx(d)}${noApi?' · ⚠ 未配置门控 API':''}（点击设置）" onclick="event.stopPropagation();doorSetOpen('${d.id}')">${d.type==='auto'?'🚪':d.type==='visual'?'👁':'🖐'}</div>`;
  }).join('') + (spcGateF.lift?LIFTS.filter(l=>l.fl===flKey):[]).map(l=>`<div class="gate-mk lift" style="left:${l.x}%;top:${l.y}%" title="${l.name} · 服务楼层 ${l.floors} · 轿厢定位：${l.loc}" onclick="event.stopPropagation();toast('${l.name}：梯控配置在「接入中心 · 智能通行控制 · 梯控」维护')">🛗</div>`).join('');
  el.innerHTML = gateChips + `<div style="position:relative;flex:1;min-height:0;display:flex;flex-direction:column">${fpSvg(true)}
      ${gateMks}""")

# ========== E13 接管弹窗改全屏 iframe ==========
old_tk = src[src.index('<!-- 远程接管'):src.index('<!-- 门点设置 -->') if '<!-- 门点设置 -->' in src else src.index('<!-- 轨迹回放 -->')]
new_tk = r"""<!-- 远程接管（全屏弹窗 · 内嵌狗原生控制台 iframe · 降级示意图 · 结束接管选恢复策略 · 急停长按 2s · 仅管理员） -->
<div class="mask" id="tkMask">
  <div class="modal" style="width:94vw;max-width:1240px;height:88vh;display:flex;flex-direction:column;position:relative">
    <div class="modal-hd">🎮 远程接管 · <span id="tkRobot">—</span>
      <span class="badge b-warn" id="tkState" style="margin-left:6px;display:none">接管中 · 自动任务挂起</span>
      <button class="btn sm danger" id="tkEstop" style="margin-left:10px" onmousedown="tkHoldDown()" onmouseup="tkHoldUp()" onmouseleave="tkHoldUp()" ontouchstart="tkHoldDown()" ontouchend="tkHoldUp()">⏹ 急停（长按 2s）</button>
      <button class="x" onclick="tkEndAsk()">✕</button></div>
    <div style="height:5px;border-radius:3px;background:rgba(255,255,255,.08);overflow:hidden;margin:0 14px"><i id="tkBar" style="display:block;height:100%;width:0;background:linear-gradient(90deg,#fbbf24,#f87171)"></i></div>
    <div style="flex:1;position:relative;background:#05080f;min-height:0;margin-top:8px">
      <iframe id="tkFrame" src="about:blank" title="具身原生控制台" style="width:100%;height:100%;border:0;display:block" onload="tkFrameOk()"></iframe>
      <div id="tkFallback" style="display:none;position:absolute;inset:0;flex-direction:column;align-items:center;justify-content:center;gap:10px;background:#05080f;z-index:3">
        <img src="assets/dog_console_ref.png" alt="远程控制台界面示意" style="max-width:88%;max-height:72%;border:1px solid var(--border);border-radius:8px;opacity:.92">
        <div class="muted" style="font-size:11px">控制台内嵌加载失败（跨域 / 混合内容拦截）—— 以上为控制台界面示意</div>
      </div>
      <div id="tkConfirm" style="display:none;position:absolute;left:50%;top:50%;transform:translate(-50%,-50%);z-index:5;background:#0b1220;border:1px solid var(--border-hi);border-radius:10px;padding:14px 16px;font-size:12px;width:400px;box-shadow:0 12px 40px rgba(0,0,0,.6)"></div>
    </div>
    <div style="padding:8px 14px;border-top:1px solid var(--border);display:flex;gap:8px;align-items:center;font-size:11px;flex-wrap:wrap">
      <span class="muted" style="flex:1;min-width:260px">⚠ 远程操作为高权限指令，全部留痕审计；本体安全策略（防跌落/急停）始终生效；弱网/离线自动改走近场 LoRa/蓝牙兜底链路</span>
      <button class="btn sm ghost" onclick="tkShowFb()">🖼 显示示意图</button>
      <button class="btn sm ghost" onclick="window.open((ROBOT_DEV[curRobotId]||{}).console,'_blank')">↗ 新窗口打开</button>
      <button class="btn sm" onclick="tkEndAsk()">↩ 结束接管</button>
    </div>
  </div>
</div>

"""
edits.append(('tk-modal', old_tk, new_tk))

# ========== E14 接管 JS 重写 ==========
old_tkjs = src[src.index('/* ---- 远程接管 / 急停安全确认 / 轨迹回放 ---- */'):src.index('/* 轨迹回放 */')]
new_tkjs = r"""/* ---- 远程接管（iframe 控制台）/ 急停安全确认 ---- */
let tkHoldTimer = null, tkHoldStart = 0, tkLoadedOk = false;
function openTakeover(){
  if(!curRobot){ toast('请先选择机器人'); return; }
  if(curIdentity!=='admin'){ toast('远程接管仅管理员账号可用'); return; }
  const dev = ROBOT_DEV[curRobotId]||{};
  if(!dev.console){ toast(curRobot.name+' 未配置控制台地址（接入中心 · 基础信息 可配置），远程接管不可用'); return; }
  document.getElementById('tkRobot').textContent = curRobot.name;
  document.getElementById('tkState').style.display = 'none';
  document.getElementById('tkFallback').style.display = 'none';
  document.getElementById('tkFrame').src = 'about:blank';
  document.getElementById('tkBar').style.width = '0%';
  const c = document.getElementById('tkConfirm');
  c.style.display = 'block';
  c.innerHTML = `确认接管 <b style="color:var(--tx-hi)">${curRobot.name}</b>？
    <div class="muted" style="font-size:11px;margin-top:6px;line-height:1.7">接管后当前自动任务<b style="color:#fbbf24">自动暂停挂起</b>，执行记录写入「人工接管」节点；弹窗内嵌该具身原生控制台（<span style="font-family:var(--mono);font-size:10px">${dev.console}</span>），可随时结束接管交还自主。</div>
    <div style="margin-top:10px;display:flex;gap:8px"><button class="btn sm" onclick="tkDo('take')">确认接管</button><button class="btn sm ghost" onclick="closeMask('tkMask')">取消</button></div>`;
  document.getElementById('tkMask').classList.add('on');
}
function tkDo(a){
  const dev = ROBOT_DEV[curRobotId]||{};
  document.getElementById('tkConfirm').style.display = 'none';
  document.getElementById('tkState').style.display = '';
  tkLoadedOk = false;
  document.getElementById('tkFrame').src = dev.console;
  toast(`已接管 ${curRobot.name}：控制台通道建立中 · 自动任务已挂起，执行记录写入「人工接管」节点`);
  aaEvent('🎮', `已接管 ${curRobot.name}：远程控制台已打开，自动任务挂起并留痕「人工接管」节点，注意周边障碍。`);
  tkActive = true; onRobotSelect(curRobotId); mnSecSet('mnBotSec', false);
  setTimeout(()=>{ if(!tkLoadedOk && document.getElementById('tkMask').classList.contains('on')) toast('控制台加载缓慢：若长时间空白，可能是跨域 / http 混合内容拦截 —— 可点底部「新窗口打开」或「显示示意图」'); }, 5000);
}
function tkFrameOk(){ tkLoadedOk = true; }
function tkShowFb(){ document.getElementById('tkFallback').style.display = 'flex'; }
function tkEndAsk(){
  if(!tkActive){ closeMask('tkMask'); return; }
  const c = document.getElementById('tkConfirm');
  c.style.display = 'block';
  c.innerHTML = `结束对 <b style="color:var(--tx-hi)">${curRobot.name}</b> 的接管？被挂起的任务如何处置：
    <div style="margin-top:10px;display:flex;flex-direction:column;gap:8px">
      <button class="btn sm" onclick="tkEnd('resume')">↩ 恢复原任务继续执行</button>
      <button class="btn sm ghost" onclick="tkEnd('postpone')">⏭ 顺延至下一排班</button>
      <button class="btn sm ghost" onclick="tkEnd('idle')">⏹ 保持待机（任务挂起保留）</button>
      <button class="btn sm ghost" onclick="document.getElementById('tkConfirm').style.display='none'">继续接管</button>
    </div>`;
}
function tkEnd(how){
  closeMask('tkMask');
  document.getElementById('tkFrame').src = 'about:blank';
  tkActive = false;
  const tx = { resume:'已恢复原任务继续执行', postpone:'任务已顺延至下一排班', idle:'保持待机，任务挂起保留' }[how];
  toast('已结束接管：'+curRobot.name+' 交还自主 · '+tx);
  aaEvent('↩', curRobot.name+' 接管结束：'+tx+'。');
  onRobotSelect(curRobotId);
}
function tkHoldDown(){
  if(!curRobot) return;
  tkHoldStart = Date.now();
  clearInterval(tkHoldTimer);
  tkHoldTimer = setInterval(()=>{
    const p = Math.min(100,(Date.now()-tkHoldStart)/20);
    document.getElementById('tkBar').style.width = p+'%';
    if(p>=100){ tkHoldUp(true); }
  },30);
}
function tkHoldUp(done){
  clearInterval(tkHoldTimer);
  if(done===true){
    toast(`⏹ 急停已下发：${curRobot.name} 安全停机（本体安全能力属厂商责任边界 MB-09 · 指令已留痕审计）`);
    aaEvent('⏹', `${curRobot.name} 已安全停机！急停指令已留痕，恢复前建议先远程查看现场画面。`);
  }
  const bar = document.getElementById('tkBar'); if(bar) bar.style.width = '0%';
}
"""
edits.append(('tk-js', old_tkjs, new_tkjs))

# ========== E15 监控卡片：接管按钮（管理员 + 控制台地址置灰） ==========
E('mn-tk-btn', r"""      <button class="btn sm" onclick="openTakeover()">🎮 远程接管</button>""",
r"""      ${curIdentity==='admin'?((ROBOT_DEV[id]||{}).console?'<button class="btn sm" onclick="openTakeover()">🎮 远程接管</button>':'<button class="btn sm" style="opacity:.45" title="未配置控制台地址（接入中心 · 基础信息 可配置）" onclick="toast(\'未配置控制台地址：接入中心 · 基础信息 中配置后可用\')">🎮 远程接管</button>'):''}""")

# ========== E16 监控卡片：电量双刻度 ==========
E('mn-batt', r"""      <b>电量</b><span><span class="batt"><i style="width:${curRobot.battery}%;background:${curRobot.battery>50?'#34d399':curRobot.battery>30?'#fbbf24':'#f87171'}"></i></span>${curRobot.battery}%</span>""",
r"""      <b>电量</b><span><span class="batt"><i style="width:${curRobot.battery}%;background:${curRobot.battery>50?'#34d399':curRobot.battery>BAT_LOW?'#fbbf24':'#f87171'}"></i><i class="tick" style="left:${BAT_CHG}%" title="回充阈值 ${BAT_CHG}%"></i><i class="tick r" style="left:${BAT_LOW}%" title="禁派阈值 ${BAT_LOW}%"></i></span>${curRobot.battery}%${curRobot.battery<BAT_LOW?' <span class="badge b-warn" style="font-size:9px">低于禁派阈值 · 暂停派单</span>':''}</span>""")

# ========== E17 弱网点击提示 ==========
E('nr-weak', r"""<div class="nr" id="nr-weak" style="opacity:.38;pointer-events:none;filter:grayscale(.6)" title="弱网模式：后续版本开放">📳 弱网</div>""",
r"""<div class="nr" id="nr-weak" style="opacity:.45;filter:grayscale(.6);cursor:not-allowed" title="弱网模式开发中" onclick="toast('📳 弱网模式开发中：本期支持 在线 / 离线 / 自动 切换，弱网将于联调后开放')">📳 弱网</div>""")

# ========== E18 离线任务包区块 ==========
E('offpacks', r"""        <div class="queue-item"><span>⬆ 点云续传：pc_20260814_07.laz</span><span style="color:var(--cy)">62% · 断续续传</span></div>
      </div>""",
r"""        <div class="queue-item"><span>⬆ 点云续传：pc_20260814_07.laz</span><span style="color:var(--cy)">62% · 断续续传</span></div>
      </div>
      <div id="offPacks" style="display:none;margin-top:8px;border-top:1px dashed var(--border);padding-top:8px">
        <div class="muted" style="font-size:10.5px;margin-bottom:5px">📥 离线任务包（预置本体 · 回连完整性校验补传 PL-09）</div>
        <div class="queue-item"><span>休闲区A巡检 · 6 点位</span><span style="color:var(--ok)">✓ 完整接收</span></div>
        <div class="queue-item"><span>外摆区夜间巡查 · 4 点位</span><span style="color:var(--warn)">⚠ 待补传 · 缺 2 点位</span></div>
        <div class="queue-item"><span>⬆ 媒体回传：图像 18/24 · 视频 2/3</span><span style="color:var(--cy)">断点待续传</span></div>
      </div>""")
E('offpacks-ui', r"""  document.getElementById('weakEstop').style.display = eff==='off' ? '' : 'none';""",
r"""  document.getElementById('weakEstop').style.display = eff==='off' ? '' : 'none';
  const op = document.getElementById('offPacks'); if(op) op.style.display = eff==='off' ? 'block' : 'none';""")

# ========== E19 视口标记：离线位置 + 充电桩 + 门 ==========
old_mnbots = src[src.index('function renderMnBots(){'):src.index('function mnBotSelect(id){')]
new_mnbots = r"""function renderMnBots(){
  const box=document.getElementById('mnBots'); if(!box) return;
  const on = document.getElementById('vmBots');
  let html = '';
  if(!(on && !on.classList.contains('on'))){
    const cols={ online:'#34d399', executing:'#22d3ee', offline:'#8a97a8', exception:'#f87171' };
    html += Object.entries(MN_POS).map(([id,pos])=>{
      const r = ROBOTS[id]; if(!r) return '';
      const c = cols[r.st]||'#8a97a8';
      const lk = LAST_KNOWN[id];
      return `<div class="mn-bot ${r.st==='executing'?'exec':''} ${curRobotId===id?'sel':''}" style="left:${pos[0]}%;top:${pos[1]}%;color:${c}" title="${r.name} · ${r.stTx} · ${r.location||''}${r.st==='offline'&&lk?' · 最后已知位置 '+lk.loc+'（'+lk.time+'）':''}" onclick="mnBotSelect('${id}')">
        <div class="bdot"></div><div class="bname">${r.emoji||'🐕'} ${r.name}</div>${r.st==='offline'&&lk?`<div class="blast">📍 最后位置 ${lk.loc} · 离线 ${lk.dur}</div>`:''}</div>`;
    }).join('');
  }
  /* 充电桩标记（空闲/占用/故障 · 占用显示具身名 · 接口依赖东方） */
  html += CHARGES.map(cg=>`<div class="chg-mk ${cg.st}" style="left:${cg.x}%;top:${cg.y}%" title="${cg.name} · ${cg.st==='free'?'空闲':cg.st==='occ'?'占用（'+cg.by+'）':'故障'} · 状态接口依赖东方"><div class="ic">🔌</div><div class="lb2">${cg.name.replace('充电桩 ','桩 ')} · ${cg.st==='free'?'空闲':cg.st==='occ'?cg.by:'故障'}</div></div>`).join('');
  /* 门标记（自动/非自动区分 · 通行中闪烁 · 自动门未配 API 红色） */
  html += DOORS.map(d=>{
    const noApi = doorNoApi(d);
    const cls = d.type==='auto'?(noApi?'noapi':''):d.type==='visual'?'visual':'manual';
    return `<div class="gate-mk ${cls} ${d.passing?'passing':''}" style="left:${d.vx}%;top:${d.vy}%" title="${d.name} · ${doorTypeTx(d)}${noApi?' · ⚠ 未配置门控 API':''}${d.passing?' · 通行中':''}" onclick="event.stopPropagation();doorSetOpen('${d.id}')">${d.type==='auto'?'🚪':d.type==='visual'?'👁':'🖐'}</div>`;
  }).join('');
  box.innerHTML = html;
  const chip=document.getElementById('chipBots');
  if(chip){ const act=Object.values(ROBOTS).filter(r=>r.st==='online'||r.st==='executing').length; chip.textContent=`🐕 ${act} / ${Object.keys(ROBOTS).length} 活跃`; }
}
"""
edits.append(('mnbots', old_mnbots, new_mnbots))

# ========== E20 电量不足拦截下发 ==========
E('sendcmd-batt', r"""  if(ROBOT_EXT[curRobotId].net==='off'){ toast('该具身为离线模式：指令已缓存至边缘单元，回连后自动下发'); return; }""",
r"""  if(ROBOT_EXT[curRobotId].net==='off'){ toast('该具身为离线模式：指令已缓存至边缘单元，回连后自动下发'); return; }
  if(curRobot.battery<BAT_LOW){ toast('⛔ '+curRobot.name+' 电量 '+curRobot.battery+'% 低于禁派阈值（'+BAT_LOW+'%），已拦截下发 · 请先充电（接入中心可调阈值）'); return; }""")
E('te-batt', r"""    setTimeout(()=>{ openTakeover(); },700);
    return;
  }""",
r"""    setTimeout(()=>{ openTakeover(); },700);
    return;
  }
  const rb0 = ROBOTS[teRobots[0]];
  if(rb0 && rb0.battery<BAT_LOW){ toast('⛔ '+rb0.name+' 电量 '+rb0.battery+'% 低于禁派阈值（'+BAT_LOW+'%），任务未下发 · 请先充电（接入中心可调阈值）'); return; }""")

# ========== 应用 ==========
fails = []
for label, old, new in edits:
    n = src.count(old)
    if n != 1:
        fails.append((label, n))
        continue
    src = src.replace(old, new, 1)

if fails:
    print('FAILED anchors:')
    for f in fails: print(' ', f)
else:
    io.open(P, 'w', encoding='utf-8', newline='').write(src)
    print('OK: all', len(edits), 'edits applied')
