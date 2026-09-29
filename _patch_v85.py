# -*- coding: utf-8 -*-
"""V8.5 patch: index.html 精确替换补丁。每处断言唯一匹配，失败即停。"""
import io, shutil, os, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, 'index.html')
BAK = os.path.join(ROOT, 'backups', 'pre-v85')
os.makedirs(BAK, exist_ok=True)
shutil.copy2(SRC, os.path.join(BAK, 'index.html'))
shutil.copy2(os.path.join(ROOT, 'miniapp.html'), os.path.join(BAK, 'miniapp.html'))

s = io.open(SRC, encoding='utf-8').read()
fails = []

def rep(name, old, new, cnt=1):
    global s
    n = s.count(old)
    if cnt == -1:
        if n < 1:
            fails.append((name, n)); return
    elif n != cnt:
        fails.append((name, n)); return
    s = s.replace(old, new)
    print(f'OK  [{n}x] {name}')

# ============ A. 1.5 远程接管弹窗精简 ============
rep('A1 接管失败提示替换示意图', '''      <div id="tkFallback" style="display:none;position:absolute;inset:0;flex-direction:column;align-items:center;justify-content:center;gap:10px;background:#05080f;z-index:3">
        <img src="assets/dog_console_ref.png" alt="远程控制台界面示意" style="max-width:88%;max-height:72%;border:1px solid var(--border);border-radius:8px;opacity:.92">
        <div class="muted" style="font-size:11px">控制台内嵌加载失败（跨域 / 混合内容拦截）—— 以上为控制台界面示意</div>
      </div>''', '''      <div id="tkFallback" style="display:none;position:absolute;inset:0;flex-direction:column;align-items:center;justify-content:center;gap:10px;background:#05080f;z-index:3">
        <div style="font-size:34px">⚠️</div>
        <div style="font-size:13px;color:#fbbf24;font-weight:600">控制台加载失败</div>
        <div class="muted" style="font-size:11px;text-align:center;line-height:1.8;max-width:360px">内嵌控制台无法加载（跨域 / http 混合内容拦截 / 网络不可达）<br>可点击底部「↗ 新窗口打开」在浏览器新标签页中打开控制台</div>
      </div>''')

rep('A2 页脚去LoRa兜底文字', '<span class="muted" style="flex:1;min-width:260px">⚠ 远程操作为高权限指令，全部留痕审计；本体安全策略（防跌落/急停）始终生效；弱网/离线自动改走近场 LoRa/蓝牙兜底链路</span>',
    '<span class="muted" style="flex:1;min-width:260px">⚠ 远程操作为高权限指令，全部留痕审计；本体安全策略（防跌落/急停）始终生效</span>')

rep('A3 删显示示意图按钮', '''      <button class="btn sm ghost" onclick="tkShowFb()">🖼 显示示意图</button>
''', '')

rep('A4 tkDo超时显示加载失败', """  setTimeout(()=>{ if(!tkLoadedOk && document.getElementById('tkMask').classList.contains('on')) toast('控制台加载缓慢：若长时间空白，可能是跨域 / http 混合内容拦截 —— 可点底部「新窗口打开」或「显示示意图」'); }, 5000);""",
    """  setTimeout(()=>{ if(!tkLoadedOk && document.getElementById('tkMask').classList.contains('on')) document.getElementById('tkFallback').style.display = 'flex'; }, 5000);""")

rep('A5 删tkShowFb函数', """function tkShowFb(){ document.getElementById('tkFallback').style.display = 'flex'; }
""", '')

rep('A6 结束接管弹窗精简', """  c.innerHTML = `结束对 <b style="color:var(--tx-hi)">${curRobot.name}</b> 的接管？被挂起的任务如何处置：
    <div style="margin-top:10px;display:flex;flex-direction:column;gap:8px">
      <button class="btn sm" onclick="tkEnd('resume')">↩ 恢复原任务继续执行</button>
      <button class="btn sm ghost" onclick="tkEnd('postpone')">⏭ 顺延至下一排班</button>
      <button class="btn sm ghost" onclick="tkEnd('idle')">⏹ 保持待机（任务挂起保留）</button>
      <button class="btn sm ghost" onclick="document.getElementById('tkConfirm').style.display='none'">继续接管</button>
    </div>`;""",
    """  c.innerHTML = `<div style="display:flex;align-items:center;gap:6px;padding-right:22px">结束对 <b style="color:var(--tx-hi)">${curRobot.name}</b> 的接管？被挂起的任务如何处置：<button class="x" style="position:absolute;right:10px;top:8px" title="取消 · 继续接管" onclick="document.getElementById('tkConfirm').style.display='none'">✕</button></div>
    <div style="margin-top:12px;display:flex;flex-direction:column;gap:8px">
      <button class="btn sm" onclick="tkEnd('resume')">↩ 恢复原任务继续执行</button>
      <button class="btn sm ghost" onclick="tkEnd('dock')">🏠 回到充电桩/待命区</button>
    </div>`;""")

rep('A7 tkEnd处置映射', "  const tx = { resume:'已恢复原任务继续执行', postpone:'任务已顺延至下一排班', idle:'保持待机，任务挂起保留' }[how];",
    "  const tx = { resume:'已恢复原任务继续执行', dock:'已下发回桩指令，返回充电桩/待命区待机' }[how];")

# ============ B. 1.6 已取货断网处置区块 ============
rep('B1 LAST_KNOWN加货物', "const LAST_KNOWN = { cyber:{ loc:'外摆区', dur:'2h13m', time:'08-28 06:41' } };",
    "const LAST_KNOWN = { cyber:{ loc:'外摆区', dur:'2h13m', time:'08-28 06:41', cargo:'配送 · 拿铁咖啡 → 3F 办公区 301 会议室（已取货）' } };")

rep('B2 已取货断网区块', '''      <div id="offPacks" style="display:none;margin-top:8px;border-top:1px dashed var(--border);padding-top:8px">''',
    '''      <div id="offCargo" style="display:none;margin-top:8px;border:1px solid rgba(248,113,113,.45);border-radius:8px;padding:8px 10px;background:rgba(248,113,113,.07)">
        <div style="display:flex;align-items:center;gap:6px;font-size:12px;color:#f87171;font-weight:600">📦 已取货断网处置<span class="badge b-danger" style="margin-left:auto;font-size:9px">配送异常-处理中</span></div>
        <div class="muted" style="font-size:11px;line-height:1.8;margin-top:5px" id="offCargoDesc"></div>
        <div style="display:flex;gap:10px;font-size:11px;margin-top:6px;align-items:center"><span>⏱ 重连倒计时 <b style="color:#fbbf24;font-family:var(--mono)" id="offCargoCd">04:32</b></span><span class="muted">恢复在线后自动继续配送，无需人工干预</span></div>
      </div>
      <div id="offPacks" style="display:none;margin-top:8px;border-top:1px dashed var(--border);padding-top:8px">''')

rep('B3 updateNetUI联动offCargo', """  const op = document.getElementById('offPacks'); if(op) op.style.display = eff==='off' ? 'block' : 'none';""",
    """  const op = document.getElementById('offPacks'); if(op) op.style.display = eff==='off' ? 'block' : 'none';
  const lk0 = curRobotId ? LAST_KNOWN[curRobotId] : null;
  const oc = document.getElementById('offCargo');
  if(oc){
    const show = eff==='off' && lk0 && lk0.cargo;
    oc.style.display = show ? 'block' : 'none';
    if(show) document.getElementById('offCargoDesc').textContent = `本机配送货物已取货（${lk0.cargo}）。断网后不支持原地等待，正按策略自动返回充电桩/待命区等待重连；订单状态已同步至配送小程序「配送异常-处理中」，取货凭证本地留存、回连后自动补传。`;
  }""")

# ============ C. 1.7 小舆 ============
rep('C1 删小舆名字标签', '''    <span class="aa-name">小舆 · XIAOYU</span>
''', '')

rep('C2 小舆面板背景', '.aa-panel{display:none;flex-direction:column;gap:8px;width:336px;pointer-events:auto;padding-bottom:6px}',
    '.aa-panel{display:none;flex-direction:column;gap:8px;width:336px;pointer-events:auto;padding:10px 12px;background:rgba(7,12,24,.94);border:1px solid rgba(120,190,255,.3);border-radius:14px;box-shadow:0 14px 44px rgba(2,6,18,.65);backdrop-filter:blur(10px)}')

rep('C3 消息区滚动条', '.aa-msgs{display:flex;flex-direction:column;gap:8px;max-height:46vh;overflow-y:auto;padding:4px 2px;scrollbar-width:thin}',
    '''.aa-msgs{display:flex;flex-direction:column;gap:8px;max-height:46vh;overflow-y:auto;padding:4px 6px 4px 2px;scrollbar-width:thin;scrollbar-color:rgba(94,168,255,.35) transparent}
.aa-msgs::-webkit-scrollbar{width:5px}
.aa-msgs::-webkit-scrollbar-thumb{background:rgba(94,168,255,.3);border-radius:3px}
.aa-msgs::-webkit-scrollbar-thumb:hover{background:rgba(94,168,255,.55)}
.aa-msgs::-webkit-scrollbar-track{background:transparent}
.aa-ex{font-size:11px;color:#9cc4ee;padding:4px 8px;border-radius:7px;cursor:pointer;border:1px dashed rgba(120,190,255,.25);margin-top:4px;transition:.15s}
.aa-ex:hover{background:rgba(94,168,255,.15);color:#e6f1ff;border-color:rgba(94,168,255,.5)}''')

rep('C4 快捷胶囊调整', "  const chips=[['📦 发起配送','delivery'],['📋 下任务','task'],['🧭 规划路径','path'],['🐕 狗子状态','dog'],['⚠ 异常复核','alert']];",
    "  const chips=[['📋 下任务','task'],['▦ 空间状态','space'],['🐕 狗子状态','dog'],['⚠ 异常复核','alert']];")

rep('C5a 下任务改NL引导', "    task:'好的，去任务中心选「临时任务」——我会先做 AI 任务识别（语义解析 + 岗位校验），再给你 3 条带语义理由的推荐路径。',",
    "    task:'直接在下方输入框用自然语言告诉我任务即可，比如「去 1F 大堂巡检一圈」「送杯咖啡到 301」「扫描 2F」——我会先做 AI 任务识别（语义解析 + 岗位校验），再给你 3 条带语义理由的推荐路径。',")

rep('C5b 加空间状态播报', """    dog:`当前 ${onlineN+execN}/${rs.length} 台活跃：执行中 ${execN} 台（${execNames}），在线待命 ${onlineN} 台。弱网 ${weakN} 台已启用指令队列。`};""",
    """    dog:`当前 ${onlineN+execN}/${rs.length} 台活跃：执行中 ${execN} 台（${execNames}），在线待命 ${onlineN} 台。弱网 ${weakN} 台已启用指令队列。`,
    space:'当前空间状态：主楼 1F 研发大厅存在 2 项巡检异常（照明未关 · 待复核），消防通道 1 处占用告警已转工单；B1 车库、2F 会议层、3F 办公区均正常。在监控中心点选具体空间可查看明细。'};""")

rep('C5c 下任务不跳页面', """  aaSay(M[k]);
  if(k==='task'||k==='alert') setTimeout(()=>{ location.hash='#/tasks'; },900);""",
    """  aaSay(M[k]);
  if(k==='alert') setTimeout(()=>{ location.hash='#/tasks'; },900);""")

rep('C6 欢迎语示例可点击', """  aaPush({r:'a',html:'<div class="mc-tt">可以这样说（按当前具身能力过滤）</div>'+
    ['📦 帮我去奈雪取 A1024 送到301','📋 去 1F 大堂巡检一圈','🛰 扫描 2F 采集点云','🐕 狗子状态怎么样'].map(s=>'<div style="font-size:11px;color:#9cc4ee;padding:3px 0">'+s+'</div>').join('')});
}""",
    """  aaPush({r:'a',html:'<div class="mc-tt">可以这样说（点击填入输入框 · 按当前具身能力过滤）</div>'+
    ['帮我去瑞幸取 A1024 送到301','去 1F 大堂巡检一圈','扫描 2F 采集点云','狗子状态怎么样'].map(s=>'<div class="aa-ex" data-t="'+s+'">'+s+'</div>').join('')});
}
function aaFill(t){ const inp=document.getElementById('aaInp'); inp.value=t; inp.focus(); }
document.addEventListener('click',e=>{ const ex=e.target.closest('.aa-ex'); if(ex) aaFill(ex.dataset.t); });""")

# ============ D. 监控视口压暗 ============
rep('D1 视口底图压暗', '#mn-3d img.bg3d{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}',
    '''#mn-3d img.bg3d{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;filter:brightness(.55) contrast(1.08) saturate(.9)}
[data-theme="light"] #mn-3d img.bg3d{filter:none}''')

rep('D2 视口叠加深蓝紫', '''#mn-3d::after{content:"";position:absolute;inset:0;pointer-events:none;z-index:6;
  background:repeating-linear-gradient(0deg,rgba(120,180,255,.035) 0 1px,transparent 1px 4px)}''',
    '''#mn-3d::after{content:"";position:absolute;inset:0;pointer-events:none;z-index:6;
  background:linear-gradient(160deg,rgba(23,15,58,.30),rgba(8,10,30,.40)),repeating-linear-gradient(0deg,rgba(120,180,255,.035) 0 1px,transparent 1px 4px)}''')

# ============ E. 1.8 任务中心去临时任务 ============
rep('E1 删临时任务选项', '<option>固定任务-人为触发</option><option>临时任务（NL 指令）</option></select>',
    '<option>固定任务-人为触发</option></select>')

rep('E2 teTypeChange删临时分支', """  else if(v.indexOf('人为')>=0) ht = '保存后标记为 <b style="color:var(--cy)">固定任务-人为触发</b>，不自动排班，由操作员手动启动';
  else ht = '保存后标记为 <b style="color:var(--warn)">临时任务</b>（等效监控中心 NL 指令下发）';""",
    """  else if(v.indexOf('人为')>=0) ht = '保存后标记为 <b style="color:var(--cy)">固定任务-人为触发</b>，不自动排班，由操作员手动启动';""")

rep('E3 编辑任务类型回填', "  tt.value = t.cat==='fixed' ? (t.period ? '固定任务-周期' : '固定任务-人为触发') : '临时任务（NL 指令）';",
    "  tt.value = t.cat==='fixed' ? (t.period ? '固定任务-周期' : '固定任务-人为触发') : '固定任务-人为触发';")

# ============ F. 4.1 充电桩连接测试 ============
rep('F1 向导第3步充电桩测试', '''      <div class="form-row"><label>充电桩</label><select class="input" id="wzDock">${docks.map(p=>`<option>${p.bld}-${p.name}</option>`).join('')}</select></div>''',
    '''      <div class="form-row"><label>充电桩</label><span style="display:flex;gap:8px;align-items:center;flex:1"><select class="input" id="wzDock" style="flex:1" onchange="wzData.dockOk=false;document.getElementById('wzDockSt').className='badge b-dim';document.getElementById('wzDockSt').textContent='未测试'">${docks.map(p=>`<option>${p.bld}-${p.name}</option>`).join('')}</select><button class="btn sm btn-test" type="button" onclick="wzDockTest()">测试连接</button><span class="badge b-dim" id="wzDockSt">未测试</span></span></div>
      <div class="muted" style="font-size:10.5px;margin:-2px 0 2px">充电桩测试通过才能完成注册；也可跳过，接入后在「基础信息」中绑定充电/待命区域。</div>''')

rep('F2 向导页脚按钮', '''    F.innerHTML = `<button class="btn ghost" onclick="wzCancel()">取消</button><button class="btn" onclick="wzGo(4)">完成注册 →</button>`;''',
    '''    F.innerHTML = `<button class="btn ghost" onclick="wzCancel()">取消</button><button class="btn ghost" onclick="wzSkipDock()">跳过，稍后配置 →</button><button class="btn" onclick="wzDockNext()">完成注册 →</button>`;''')

rep('F3 wzGo尊重跳过标记', """  if(wzStep===3 && n>3){ const g=id=>{const el=document.getElementById(id);return el?el.value:'';}; wzData.dock = g('wzDock'); }""",
    """  if(wzStep===3 && n>3){ if(!wzData.dockSkip){ const g=id=>{const el=document.getElementById(id);return el?el.value:'';}; wzData.dock = g('wzDock'); } }""")

rep('F4 充电桩测试函数', '''function wzLog(t){''',
    '''function wzDockTest(){
  const st = document.getElementById('wzDockSt'); if(!st) return;
  st.className='badge b-warn'; st.textContent='测试中…';
  wzTimers.push(setTimeout(()=>{ st.className='badge b-ok'; st.textContent='✓ 连接通过'; wzData.dockOk = true; toast('充电桩连接测试通过：握手 12ms · 计费/状态回传正常'); },900));
}
function wzDockNext(){
  if(!wzData.dockOk){ toast('请先点击「测试连接」确认充电桩连通，或选择「跳过，稍后配置」'); return; }
  wzGo(4);
}
function wzSkipDock(){ wzData.dockSkip = true; wzGo(4); }
function wzLog(t){''')

rep('F5 wzFinish未配置文案', "    model:wzData.model||'Go2', role:wzData.role||'通用机器人', location:'—', caps:wzData.caps||'—', dock:wzData.dock||'B1-充电桩 A',",
    "    model:wzData.model||'Go2', role:wzData.role||'通用机器人', location:'—', caps:wzData.caps||'—', dock:wzData.dock||'—（未配置）',")

rep('F6 基础信息编辑充电位测试', '''      <div class="form-row"><label>充电/待命区域</label><select class="input" onchange="ROBOTS[curCfg].dock=this.value">${POINTS.filter(p=>p.uses.includes('充电/待命')).map(p=>`<option ${p.bld+'-'+p.name===r.dock?'selected':''}>${p.bld}-${p.name}</option>`).join('')}</select></div>''',
    '''      <div class="form-row"><label>充电/待命区域</label><span style="display:flex;gap:8px;align-items:center;flex:1"><select class="input" style="flex:1" onchange="cfgDockChg(this.value)">${POINTS.filter(p=>p.uses.includes('充电/待命')).map(p=>`<option ${p.bld+'-'+p.name===r.dock?'selected':''}>${p.bld}-${p.name}</option>`).join('')}</select><button class="btn sm btn-test" type="button" onclick="cfgDockTest()">测试连接</button><span class="badge ${cfgDockOk?'b-ok':'b-dim'}" id="cfgDockSt">${cfgDockOk?'✓ 已对接':'未测试'}</span></span></div>''')

rep('F7 基础信息保存拦截', """        <button class="btn" onclick="toast('保存成功（演示）');cfgEditing=false;renderCfgDetail()">保存</button>""",
    """        <button class="btn" onclick="cfgBaseSave()">保存</button>""")

rep('F8 编辑入口重置测试态', '''        <button class="btn sm" onclick="cfgEditing=true;renderCfgDetail()">✏️ 编辑</button>''',
    '''        <button class="btn sm" onclick="cfgEditing=true;cfgDockOk=true;renderCfgDetail()">✏️ 编辑</button>''')

rep('F9 充电桩测试/保存函数', '''function cfgBaseHtml(r){''',
    '''let cfgDockOk = true;
function cfgDockChg(v){ ROBOTS[curCfg].dock = v; cfgDockOk = false; const st=document.getElementById('cfgDockSt'); if(st){ st.className='badge b-dim'; st.textContent='未测试'; } }
function cfgDockTest(){
  const st = document.getElementById('cfgDockSt'); if(!st) return;
  st.className='badge b-warn'; st.textContent='测试中…';
  setTimeout(()=>{ st.className='badge b-ok'; st.textContent='✓ 连接通过'; cfgDockOk = true; toast('充电桩连接测试通过：握手 12ms · 计费/状态回传正常'); },900);
}
function cfgBaseSave(){
  if(!cfgDockOk){ toast('充电/待命区域已变更：请先「测试连接」通过后再保存'); return; }
  toast('保存成功'); cfgEditing=false; renderCfgDetail();
}
function cfgBaseHtml(r){''')

rep('F10 查看态已对接徽标', '''      <tr><td>充电/待命区域</td><td>${r.dock} <span class="muted" style="font-size:10px">（点位在「空间管理 · 点位管理」维护，用途为 充电/待命）</span></td></tr>''',
    '''      <tr><td>充电/待命区域</td><td>${r.dock} ${r.dock.includes('未配置')?'':'<span class="badge b-ok" style="font-size:9px">已对接 ✓</span>'} <span class="muted" style="font-size:10px">（点位在「空间管理 · 点位管理」维护，用途为 充电/待命）</span></td></tr>''')

# ============ G. 4.2 模组四态 + 一键重连 ============
rep('G1 panther四态示意', "            api:{mid360:'normal',g5:'normal',ctrl:'normal',speaker:'normal',pano:'normal',spatial:'exception'} },",
    "            api:{mid360:'normal',g5:'normal',ctrl:'disconnected',speaker:'unmounted',pano:'normal',spatial:'exception'} },")

rep('G2 一键重连生效', """      <button class="btn sm ghost" onclick="toast('一键重连全部模组…（演示）')">🔁 一键重连全部</button>""",
    """      <button class="btn sm ghost" onclick="modReconnectAll()">🔁 一键重连全部</button>""")

rep('G3 重连函数', '''/* 模组连接日志（最近 10 条连接事件） */''',
    '''function modReconnectAll(){
  const r = ROBOTS[curCfg]; let n=0, skip=0;
  Object.keys(r.api).forEach(k=>{ const st=r.api[k]; if(st==='exception'||st==='disconnected'){ r.api[k]='normal'; n++; } else if(st==='unmounted') skip++; });
  renderCfgList(); renderCfgDetail();
  toast(n ? '已重连 '+n+' 个模组，状态恢复「已连接」'+(skip?'；'+skip+' 个未搭载模组不参与重连':'') : '当前无异常/断连模组');
  aaEvent('🔁', r.name+' 模组一键重连完成：异常/断连模组已恢复「已连接」。');
}
/* 模组连接日志（最近 10 条连接事件） */''')

# ============ H. 4.3/4.4 智能通行控制迁空间管理 ============
rep('H1 菜单配置迁移', """  space:[['org','空间组织','st-org'],['pt','点位管理','st-pt'],['cmp','比对与更新','st-cmp']],
  config:[['base','基础信息',null],['reg','配准',null],['api','能力模组',null],['pass','智能通行控制',null],['dispatch','工作分配',null]],""",
    """  space:[['org','空间组织','st-org'],['pt','点位管理','st-pt'],['pass','智能通行控制','st-pass'],['cmp','比对与更新','st-cmp']],
  config:[['base','基础信息',null],['reg','配准',null],['api','能力模组',null],['dispatch','工作分配',null]],""")

rep('H2 接入中心守卫去pass', "  if(!l2ok('config',curCfgTab)) curCfgTab = ['base','reg','api','pass','dispatch'].find(x=>l2ok('config',x))||'base';",
    "  if(!l2ok('config',curCfgTab)) curCfgTab = ['base','reg','api','dispatch'].find(x=>l2ok('config',x))||'base';")

rep('H3 接入中心去pass分支', "  else if(curCfgTab==='pass') body = cfgPassHtml(r);\n", '')

rep('H4 接入中心去pass页签', '''      ${l2ok('config','pass')?`<button class="ptab ${curCfgTab==='pass'?'on':''}" onclick="cfgTab('pass')"><span class="pi">🚦</span>智能通行控制</button>`:''}
''', '')

rep('H5 空间页签加通行控制', '''      <button class="ptab" id="st-pt" onclick="spaceTab('pt')"><span class="pi">📍</span>点位管理</button>
      <button class="ptab" id="st-cmp" onclick="spaceTab('cmp')"><span class="pi">🧊</span>比对与更新</button>''',
    '''      <button class="ptab" id="st-pt" onclick="spaceTab('pt')"><span class="pi">📍</span>点位管理</button>
      <button class="ptab" id="st-pass" onclick="spaceTab('pass')"><span class="pi">🚦</span>智能通行控制</button>
      <button class="ptab" id="st-cmp" onclick="spaceTab('cmp')"><span class="pi">🧊</span>比对与更新</button>''')

rep('H6 通行控制容器', '''    <!-- ③ 比对与更新（α-2 链路） -->''',
    '''    <!-- ③ 智能通行控制（门 / 电梯 · 门控梯控配置） -->
    <div class="ttab" id="sb-pass" style="flex:1;display:none;overflow:auto;padding:14px 18px">
      <div id="spPass" style="max-width:980px"></div>
    </div>

    <!-- ④ 比对与更新（α-2 链路） -->''')

rep('H7 spaceTab重写', """function spaceTab(t){
  if(!l2ok('space', t)) t = ['org','pt','cmp'].find(k=>l2ok('space',k)) || 'org';
  ['org','pt','cmp'].forEach(k=>{
    document.getElementById('st-'+k).classList.toggle('on', k===t);
    document.getElementById('sb-'+k).style.display = k===t ? (k==='cmp'?'block':'grid') : 'none';
  });
  if(t==='org'){ renderSpcTrees(); renderSpcView(); renderSpcInfo(); }
  if(t==='pt'){ renderSpcTrees(); renderPm(); }
  if(t==='cmp'){ renderPipe(); renderVer(); }
}""",
    """let curSpaceTab = 'org';
function spaceTab(t){
  if(!l2ok('space', t)) t = ['org','pt','pass','cmp'].find(k=>l2ok('space',k)) || 'org';
  curSpaceTab = t;
  ['org','pt','pass','cmp'].forEach(k=>{
    document.getElementById('st-'+k).classList.toggle('on', k===t);
    document.getElementById('sb-'+k).style.display = k===t ? ((k==='org'||k==='pt')?'grid':'block') : 'none';
  });
  if(t==='org'){ renderSpcTrees(); renderSpcView(); renderSpcInfo(); }
  if(t==='pt'){ renderSpcTrees(); renderPm(); }
  if(t==='pass'){ spPassRender(); }
  if(t==='cmp'){ renderPipe(); renderVer(); }
}
function spPassRender(){
  const el = document.getElementById('spPass'); if(!el) return;
  el.innerHTML = `<div class="ptabs" style="padding:0 0 10px">
      <button class="ptab ${passTab==='gate'?'on':''}" onclick="passTab='gate';spPassRender()"><span class="pi">🚪</span>门控</button>
      <button class="ptab ${passTab==='lift'?'on':''}" onclick="passTab='lift';spPassRender()"><span class="pi">🛗</span>梯控</button>
      <span class="muted" style="font-size:10px;margin-left:auto;align-self:center">门 / 电梯构件由空间语义识别自动提取（空间组织模型区「门 / 电梯」过滤查看 · 点标记看构件信息）</span>
    </div>` + (passTab==='gate' ? cfgGateHtml() : cfgLiftHtml());
}""")

rep('H8 统一网关联动刷新', "function gateUnified(on){ GATE_UNIFIED=on; renderCfgDetail(); renderMnBots(); renderSpcView();",
    "function gateUnified(on){ GATE_UNIFIED=on; renderMnBots(); renderSpcView(); if(curSpaceTab==='pass') spPassRender();")

rep('H9 dsSave保存门状态', """function dsSave(){
  const d = DOORS.find(x=>x.id===doorSetId); if(!d) return;
  d.type = document.getElementById('dsType').value;
  d.api = document.getElementById('dsApi').value.trim();
  closeMask('dsMask');
  renderSpcView(); renderMnBots();
  if(curCfgTab==='pass') renderCfgDetail();
  toast('门点「'+d.name+'」已保存：'+doorTypeTx(d)+(d.type==='auto'?' · '+(d.api||'继承统一网关 GW-01'):''));
}""",
    """function dsSave(){
  const d = DOORS.find(x=>x.id===doorSetId); if(!d) return;
  d.type = document.getElementById('dsType').value;
  d.api = document.getElementById('dsApi').value.trim();
  d.dstate = document.getElementById('dsState').value;
  closeMask('dsMask');
  renderSpcView(); renderMnBots();
  if(curSpaceTab==='pass') spPassRender();
  if(spcGate && spcGate.id===d.id) renderSpcInfo();
  toast('门点「'+d.name+'」已保存：'+doorTypeTx(d)+' · '+d.dstate+(d.type==='auto'?' · '+(d.api||'继承统一网关 GW-01'):''));
}""")

rep('H10 门点弹窗去手动门加状态', '''      <div class="form-row"><label>门类型</label><select class="input" id="dsType" onchange="dsTypeHint()"><option value="auto">自动门（配门控 API）</option><option value="visual">非自动门 · 视觉检测</option><option value="manual">手动门 · 绕行</option></select></div>''',
    '''      <div class="form-row"><label>门类型</label><select class="input" id="dsType" onchange="dsTypeHint()"><option value="auto">自动门（配门控 API）</option><option value="visual">非自动门 · 视觉识别</option></select></div>
      <div class="form-row"><label>门状态</label><select class="input" id="dsState"><option>常关</option><option>常开</option></select></div>''')

rep('H11 doorSetOpen回填状态', """  document.getElementById('dsApi').value = d.api||'';
  dsTypeHint();""",
    """  document.getElementById('dsApi').value = d.api||'';
  document.getElementById('dsState').value = d.dstate||'常关';
  dsTypeHint();""")

rep('H12 dsTypeHint去手动门', """    : t==='visual' ? '非自动门：视觉识别开/关状态，开门由人协助通行' : '手动门：不经此门通行，路径规划自动绕行备选路线';""",
    """    : '非自动门：视觉识别开/关状态，开门由人协助通行';""")

rep('H13 门类型文案', "function doorTypeTx(d){ return d.type==='auto'?'自动门':d.type==='visual'?'非自动门 · 视觉检测':'手动门 · 绕行'; }",
    "function doorTypeTx(d){ return d.type==='auto'?'自动门 · 配门控':'非自动门 · 视觉识别'; }")

rep('H14 DOORS数据重构', """const DOORS = [
  { id:'D-01', name:'大堂入口自动门', space:'主楼 1F · 大堂',     fl:'main-1f', type:'auto',   api:'', ownGw:false, strategy:'开门请求 → 通行确认', route:'配送路线 · 取货段', x:47, y:80, vx:38, vy:62, passing:false },
  { id:'D-02', name:'闸机 G-02',      space:'主楼 1F · 大堂',     fl:'main-1f', type:'auto',   api:'', ownGw:false, strategy:'鉴权开门 → 防夹检测', route:'巡检路线 · 大堂段', x:58, y:74, vx:44, vy:66, passing:true },
  { id:'D-03', name:'办公区玻璃门',   space:'主楼 3F · 走廊',     fl:'main-3f', type:'auto',   api:'', ownGw:true,  strategy:'开门请求 → 通行确认', route:'—',                x:52, y:46, vx:52, vy:40, passing:false },
  { id:'D-04', name:'研发大厅消防门', space:'主楼 1F · 研发大厅', fl:'main-1f', type:'visual', api:'', ownGw:false, strategy:'视觉检测开/关 → 通行', route:'巡检路线 · 研发层', x:24, y:36, vx:30, vy:44, passing:false },
  { id:'D-05', name:'楼梯间防火门',   space:'主楼 1F · 楼梯间',   fl:'main-1f', type:'manual', api:'', ownGw:false, strategy:'手动门 → 绕行备选路线', route:'—',               x:82, y:30, vx:60, vy:36, passing:false },
];""",
    """const DOORS = [
  { id:'D-01', name:'大堂入口自动门', space:'主楼 1F · 大堂',     fl:'main-1f', type:'auto',   api:'', ownGw:false, strategy:'开门请求 → 通行确认', route:'配送路线 · 取货段', x:47, y:80, vx:38, vy:62, passing:false, dstate:'常开' },
  { id:'D-02', name:'闸机 G-02',      space:'主楼 1F · 大堂',     fl:'main-1f', type:'auto',   api:'', ownGw:false, strategy:'鉴权开门 → 防夹检测', route:'巡检路线 · 大堂段', x:58, y:74, vx:44, vy:66, passing:true,  dstate:'常关' },
  { id:'D-03', name:'办公区玻璃门',   space:'主楼 3F · 走廊',     fl:'main-3f', type:'auto',   api:'', ownGw:true,  strategy:'开门请求 → 通行确认', route:'—',                x:52, y:46, vx:52, vy:40, passing:false, dstate:'常关' },
  { id:'D-04', name:'研发大厅消防门', space:'主楼 1F · 研发大厅', fl:'main-1f', type:'visual', api:'', ownGw:false, strategy:'视觉检测开/关 → 通行', route:'巡检路线 · 研发层', x:24, y:36, vx:30, vy:44, passing:false, dstate:'常关' },
  { id:'D-05', name:'楼梯间防火门',   space:'主楼 1F · 楼梯间',   fl:'main-1f', type:'visual', api:'', ownGw:false, strategy:'视觉检测开/关 → 通行', route:'巡检路线 · 大堂段', x:82, y:30, vx:60, vy:36, passing:false, dstate:'常关' },
];""")

rep('H15 LIFTS加可乘标记', """const LIFTS = [
  { id:'L-01', name:'客梯 L1', space:'主楼 · 电梯厅', fl:'main-1f', floors:'B1 - 3F', api:'POST /lift/call · /lift/select · /lift/status', loc:'轿厢局部图 + 激光重定位', x:70, y:22, vx:47, vy:50 },
  { id:'L-02', name:'客梯 L2', space:'主楼 · 电梯厅', fl:'main-1f', floors:'B1 - 3F', api:'POST /lift/call · /lift/select · /lift/status', loc:'轿厢局部图 + 激光重定位', x:75, y:22, vx:50, vy:50 },
];""",
    """const LIFTS = [
  { id:'L-01', name:'客梯 L1', space:'主楼 · 电梯厅', fl:'main-1f', floors:'B1 - 3F', api:'POST /lift/call · /lift/select · /lift/status', loc:'轿厢局部图 + 激光重定位', x:70, y:22, vx:47, vy:50, usable:true },
  { id:'L-02', name:'客梯 L2', space:'主楼 · 电梯厅', fl:'main-1f', floors:'B1 - 3F', api:'POST /lift/call · /lift/select · /lift/status', loc:'轿厢局部图 + 激光重定位', x:75, y:22, vx:50, vy:50, usable:false },
];""")

rep('H16 梯控列表可乘徽标', '''<span style="margin-left:auto;font-family:var(--mono);font-size:10px;text-align:right">${l.api}</span>''',
    '''<span style="margin-left:auto;text-align:right"><span class="badge ${l.usable?'b-ok':'b-danger'}" style="font-size:9px">${l.usable?'可乘 · 已接梯控':'不可乘 · 未接梯控'}</span><br><span style="font-family:var(--mono);font-size:10px">${l.api}</span></span>''')

rep('H17 空间组织门梯标记改构件面板', """  const gateMks = (spcGateF.door?DOORS.filter(d=>d.fl===flKey):[]).map(d=>{
    const noApi = doorNoApi(d);
    const cls = d.type==='auto'?(noApi?'noapi':''):d.type==='visual'?'visual':'manual';
    return `<div class="gate-mk ${cls} ${d.passing?'passing':''}" style="left:${d.x}%;top:${d.y}%" title="${d.name} · ${doorTypeTx(d)}${noApi?' · ⚠ 未配置门控 API':''}（点击设置）" onclick="event.stopPropagation();doorSetOpen('${d.id}')">${d.type==='auto'?'🚪':d.type==='visual'?'👁':'🖐'}</div>`;
  }).join('') + (spcGateF.lift?LIFTS.filter(l=>l.fl===flKey):[]).map(l=>`<div class="gate-mk lift" style="left:${l.x}%;top:${l.y}%" title="${l.name} · 服务楼层 ${l.floors} · 轿厢定位：${l.loc}" onclick="event.stopPropagation();toast('${l.name}：梯控配置在「接入中心 · 智能通行控制 · 梯控」维护')">🛗</div>`).join('');""",
    """  const gateMks = (spcGateF.door?DOORS.filter(d=>d.fl===flKey):[]).map(d=>{
    const noApi = doorNoApi(d);
    const cls = d.type==='auto'?(noApi?'noapi':''):'visual';
    const sel = spcGate && spcGate.id===d.id ? 'outline:2px solid #e6f1ff;outline-offset:1px;' : '';
    return `<div class="gate-mk ${cls} ${d.passing?'passing':''}" style="left:${d.x}%;top:${d.y}%;${sel}" title="${d.name} · ${doorTypeTx(d)} · ${d.dstate||'常关'}${noApi?' · ⚠ 未配置门控 API':''}（点击查看构件信息）" onclick="event.stopPropagation();spcSelGate('${d.id}')">${d.type==='auto'?'🚪':'👁'}</div>`;
  }).join('') + (spcGateF.lift?LIFTS.filter(l=>l.fl===flKey):[]).map(l=>`<div class="gate-mk lift ${l.usable?'':'noapi'}" style="left:${l.x}%;top:${l.y}%;${spcGate&&spcGate.id===l.id?'outline:2px solid #e6f1ff;outline-offset:1px;':''}" title="${l.name} · 服务楼层 ${l.floors} · ${l.usable?'可乘 · 已接梯控':'不可乘 · 未接梯控'}（点击查看构件信息）" onclick="event.stopPropagation();spcSelGate('${l.id}')">🛗</div>`).join('');""")

rep('H18 监控门标记样式同步', """    const cls = d.type==='auto'?(noApi?'noapi':''):d.type==='visual'?'visual':'manual';
    return `<div class="gate-mk ${cls} ${d.passing?'passing':''}" style="left:${d.vx}%;top:${d.vy}%" title="${d.name} · ${doorTypeTx(d)}${noApi?' · ⚠ 未配置门控 API':''}${d.passing?' · 通行中':''}" onclick="event.stopPropagation();doorSetOpen('${d.id}')">${d.type==='auto'?'🚪':d.type==='visual'?'👁':'🖐'}</div>`;""",
    """    const cls = d.type==='auto'?(noApi?'noapi':''):'visual';
    return `<div class="gate-mk ${cls} ${d.passing?'passing':''}" style="left:${d.vx}%;top:${d.vy}%" title="${d.name} · ${doorTypeTx(d)}${noApi?' · ⚠ 未配置门控 API':''}${d.passing?' · 通行中':''}" onclick="event.stopPropagation();doorSetOpen('${d.id}')">${d.type==='auto'?'🚪':'👁'}</div>`;""")

rep('H19 门控列表图标与状态', '''          <span style="font-size:14px">${d.type==='auto'?'🚪':d.type==='visual'?'👁':'🖐'}</span>''',
    '''          <span style="font-size:14px">${d.type==='auto'?'🚪':'👁'}</span>''')

rep('H20 门控列表显示门状态', '''<span class="muted" style="font-size:10px">${d.space} · ${doorTypeTx(d)} · ${d.strategy}</span>''',
    '''<span class="muted" style="font-size:10px">${d.space} · ${doorTypeTx(d)} · ${d.dstate||'常关'} · ${d.strategy}</span>''')

rep('H21 spcSelNode清空门梯选中', "function spcSelNode(id){ spcSel=id; spcComp=null; renderSpcTrees(); renderSpcView(); renderSpcInfo(); }",
    "function spcSelNode(id){ spcSel=id; spcComp=null; spcGate=null; renderSpcTrees(); renderSpcView(); renderSpcInfo(); }")

rep('H22 spcSelDev清空门梯选中', """function spcSelDev(name){
  spcComp = {""", """function spcSelDev(name){
  spcGate = null;
  spcComp = {""")

rep('H23 门梯构件选中函数', '''/* 构件点选 → 构件信息 / 打标 */
let spcCompTags = ['巡检设备'];''',
    '''/* 构件点选 → 构件信息 / 打标 */
let spcCompTags = ['巡检设备'];
/* 门 / 电梯构件点选 → 构件信息面板（构件标签 / 列为关联设备 与通用构件一致，另附门控/梯控配置） */
let spcGate = null;
function spcSelGate(id){
  const d = DOORS.find(x=>x.id===id), l = d ? null : LIFTS.find(x=>x.id===id);
  if(!d && !l) return;
  spcGate = { kind: d?'door':'lift', id };
  spcCompTags = ['巡检设备'];
  const g = d||l;
  spcComp = { n:g.name, coord:'X '+(12340+g.vx*1.9).toFixed(1)+', Y '+(3330+g.vy*1.05).toFixed(1)+', Z 1.2（构件中心点）' };
  renderSpcInfo();
}
function sgGateSave(){
  if(!spcGate) return;
  if(spcGate.kind==='door'){
    const d = DOORS.find(x=>x.id===spcGate.id); if(!d) return;
    d.type = document.getElementById('sgDoorType').value;
    d.api = document.getElementById('sgDoorApi').value.trim();
    d.dstate = document.getElementById('sgDoorState').value;
    toast('门构件「'+d.name+'」已保存：'+doorTypeTx(d)+' · '+d.dstate+(d.type==='auto'?' · '+(d.api||'继承统一网关 GW-01'):''));
  } else {
    const l = LIFTS.find(x=>x.id===spcGate.id); if(!l) return;
    l.usable = document.getElementById('sgLiftUsable').value==='1';
    l.floors = document.getElementById('sgLiftFloors').value.trim()||l.floors;
    l.api = document.getElementById('sgLiftApi').value.trim();
    toast('电梯构件「'+l.name+'」已保存：'+(l.usable?'可乘 · 已接梯控':'不可乘 · 未接梯控'));
  }
  renderSpcView(); renderMnBots();
  if(curSpaceTab==='pass') spPassRender();
  renderSpcInfo();
}''')

rep('H24 构件信息面板门梯分支', """  if(ttl) ttl.textContent = spcComp ? '构件信息' : '空间信息';
  if(spcComp){""",
    """  if(ttl) ttl.textContent = (spcComp||spcGate) ? '构件信息' : '空间信息';
  if(spcGate){
    const gd = spcGate.kind==='door' ? DOORS.find(x=>x.id===spcGate.id) : null;
    const gl = spcGate.kind==='lift' ? LIFTS.find(x=>x.id===spcGate.id) : null;
    if(!gd && !gl){ spcGate=null; renderSpcInfo(); return; }
    const gDev = Object.values(SPC_DEVS).some(list=>list.some(x=>x[0].endsWith(spcComp.n)));
    el.innerHTML = `
      <div class="badge ${gd?'b-ok':'b-warn'}" style="margin-bottom:8px">构件模式 · ${gd?'门构件':'电梯构件'}</div>
      <div class="form-row"><label>构件名称</label><input class="input" value="${spcComp.n}"></div>
      <div class="form-row"><label>构件类型</label><span style="font-size:12px;color:var(--tx-hi)">${gd?'门':'电梯'}（空间语义识别自 BIM）</span></div>
      <div class="form-row"><label>中心点坐标</label><span style="font-family:var(--mono);font-size:11px;color:var(--cy)">${spcComp.coord}</span></div>
      ${gd?`
      <div class="td-sec">门控配置</div>
      <div class="form-row"><label>门类型</label><select class="input" id="sgDoorType"><option value="auto" ${gd.type==='auto'?'selected':''}>自动门（配门控 API）</option><option value="visual" ${gd.type==='visual'?'selected':''}>非自动门 · 视觉识别</option></select></div>
      <div class="form-row"><label>门控 API</label><input class="input" id="sgDoorApi" value="${gd.api||''}" placeholder="留空则继承统一网关 GW-01（可单门覆盖）"></div>
      <div class="form-row"><label>门状态</label><select class="input" id="sgDoorState"><option ${gd.dstate==='常关'?'selected':''}>常关</option><option ${gd.dstate==='常开'?'selected':''}>常开</option></select></div>
      <div class="form-row"><label>通行策略</label><span style="font-size:11px;color:var(--tx-dim)">${gd.strategy}</span></div>`:`
      <div class="td-sec">梯控配置</div>
      <div class="form-row"><label>梯控状态</label><select class="input" id="sgLiftUsable"><option value="1" ${gl.usable?'selected':''}>可乘 · 已接梯控</option><option value="0" ${gl.usable?'':'selected'}>不可乘 · 未接梯控</option></select></div>
      <div class="form-row"><label>服务楼层</label><input class="input" id="sgLiftFloors" value="${gl.floors}"></div>
      <div class="form-row"><label>梯控 API</label><input class="input" id="sgLiftApi" style="font-size:11px" value="${gl.api||''}" placeholder="如 POST /lift/call · /lift/select"></div>
      <div class="form-row"><label>轿厢定位</label><span style="font-size:11px;color:var(--tx-dim)">${gl.loc}</span></div>`}
      <div style="margin-top:10px"><button class="btn sm" onclick="sgGateSave()">💾 保存${gd?'门':'梯'}配置</button></div>
      <div class="td-sec">构件标签 <span class="muted" style="font-weight:400">（可多选 · 支持自定义）</span></div>
      <div style="display:flex;gap:6px;flex-wrap:wrap;align-items:center">
        ${['巡检设备','消防设施','物业配套'].map(t=>`<span class="badge ${spcCompTags.includes(t)?'b-cy':'b-dim'}" style="cursor:pointer" onclick="spcCompTag('${t}')">${t}</span>`).join('')}
        ${spcCompTags.filter(t=>!['巡检设备','消防设施','物业配套'].includes(t)).map(t=>`<span class="badge b-cy">${t} <i style="cursor:pointer;font-style:normal" onclick="spcCompTag('${t}')">✕</i></span>`).join('')}
        <input class="input" style="width:80px;padding:3px 8px;font-size:11px" placeholder="+ 自定义" onkeydown="spcCompTagKey(event)">
      </div>
      <div style="margin-top:10px"><button class="btn sm" ${gDev?'disabled':''} onclick="spcMarkDev()">🏷 列为关联设备</button></div>
      ${gDev?'<div class="muted" style="font-size:11px;margin-top:6px">✓ 已列入关联设备</div>':''}`;
    return;
  }
  if(spcComp){""")

# ============ I. 配送平台端联动 ============
rep('I1 取货点加电话', """const DL_PICKS = [
  { id:'PK-01', name:'罗森便利店（取货柜台）', bld:'主楼', fl:'1F', space:'大堂', use:'买商品', desc:'大堂西侧便利店柜台 · 出示取货码取货' },
  { id:'PK-02', name:'瑞幸咖啡（出品台）', bld:'主楼', fl:'1F', space:'大堂', use:'买咖啡', desc:'大堂东侧出品台 · 取餐码核销' },
];""",
    """const DL_PICKS = [
  { id:'PK-01', name:'罗森便利店（取货柜台）', bld:'主楼', fl:'1F', space:'大堂', use:'买商品', tel:'0755-8821-0023', desc:'大堂西侧便利店柜台 · 出示取货码取货' },
  { id:'PK-02', name:'瑞幸咖啡（出品台）', bld:'主楼', fl:'1F', space:'大堂', use:'买咖啡', tel:'138-2388-1024', desc:'大堂东侧出品台 · 取餐码核销' },
];""")

rep('I2 取货点列表显示电话', '''        <div class="muted" style="font-size:10px;margin-top:2px">🏛 ${bName(m.bld)} / ${m.fl} / ${m.space}（模型空间）· ${m.desc}</div>''',
    '''        <div class="muted" style="font-size:10px;margin-top:2px">🏛 ${bName(m.bld)} / ${m.fl} / ${m.space}（模型空间）· 📞 ${m.tel||'电话未配置'} · ${m.desc}</div>''')

rep('I3 取货点用途选项', "            ${['买咖啡','买商品','取餐','取文件'].map(u=>`<option ${m.use===u?'selected':''}>${u}</option>`).join('')}",
    "            ${['买咖啡','买奶茶','买商品','取餐','取物'].map(u=>`<option ${m.use===u?'selected':''}>${u}</option>`).join('')}")

rep('I4 新增取货点表单', '''    <div class="form-row"><label>用途</label><select class="input" id="dlPkU"><option>买咖啡</option><option>买商品</option><option>取餐</option><option>取文件</option></select></div>''',
    '''    <div class="form-row"><label>用途</label><select class="input" id="dlPkU"><option>买咖啡</option><option>买奶茶</option><option>买商品</option><option>取餐</option><option>取物</option></select></div>
    <div class="form-row"><label>店铺联系电话</label><input class="input" id="dlPkT" placeholder="如：0755-8821-0023（小程序「联系店员」展示）"></div>''')

rep('I5 保存取货点带电话', """  const u = document.getElementById('dlPkU').value;
  DL_PICKS.push({ id:'PK-0'+(DL_PICKS.length+1), name:n, bld:b, fl:f, space:s, use:u, desc:d||'（暂无描述）' });""",
    """  const u = document.getElementById('dlPkU').value;
  const tp = (document.getElementById('dlPkT').value||'').trim();
  DL_PICKS.push({ id:'PK-0'+(DL_PICKS.length+1), name:n, bld:b, fl:f, space:s, use:u, tel:tp, desc:d||'（暂无描述）' });""")

rep('I6 配送记录状态机扩展', """const DL_RECS = [
  { t:'今天 14:32', from:'瑞幸咖啡（出品台）', what:'拿铁 ×2', to:'3F 办公区 301 会议室', st:['已送达','b-ok'] },
  { t:'今天 11:20', from:'罗森便利店（取货柜台）', what:'三明治 + 咖啡套餐 ×1', to:'3F 办公区 302 开放工位', st:['已送达','b-ok'] },
  { t:'昨天 16:05', from:'瑞幸咖啡（出品台）', what:'美式 ×1', to:'1F 前台', st:['取货超时 · 带回服务台','b-warn'] },
  { t:'昨天 09:40', from:'罗森便利店（取货柜台）', what:'文件袋 ×1', to:'3F 办公区 301 会议室', st:['已送达','b-ok'] },
];""",
    """const DL_RECS = [
  { t:'今天 14:32', from:'瑞幸咖啡（出品台）', what:'拿铁 ×2', to:'3F 办公区 301 会议室', acct:'138****5678', rcv:'张工 138****2210', st:['配送中','b-task'] },
  { t:'今天 14:05', from:'罗森便利店（取货柜台）', what:'三明治 + 咖啡套餐 ×1', to:'3F 办公区 302 开放工位', acct:'137****8890', rcv:'前台代收', st:['排队中 · 第 1 位','b-warn'] },
  { t:'今天 11:20', from:'瑞幸咖啡（出品台）', what:'美式 ×1', to:'1F 前台', acct:'138****5678', rcv:'前台', st:['已送达','b-ok'] },
  { t:'昨天 16:05', from:'瑞幸咖啡（出品台）', what:'拿铁 ×1', to:'3F 办公区 301 会议室', acct:'139****3356', rcv:'张工', st:['配送异常-处理中 · 断网回桩','b-danger'] },
  { t:'昨天 15:40', from:'罗森便利店（取货柜台）', what:'文件袋 ×1', to:'2F 会议层东', acct:'135****7742', rcv:'李工', st:['取货超时 · 带回服务台','b-warn'] },
  { t:'昨天 10:18', from:'罗森便利店（取货柜台）', what:'咖啡套餐 ×1', to:'3F 办公区 301 会议室', acct:'138****5678', rcv:'张工', st:['已取消','b-dim'] },
];""")

rep('I7 配送记录表格与异常说明', """  const secRec = `
    <div class="panel"><div class="panel-hd"><span class="dot"></span>配送记录<span class="extra">按时间 · 下单内容 / 取货商店 / 送达点</span></div><div class="panel-bd" style="font-size:12px">
      <table class="task-table"><thead><tr><th>时间</th><th>取货点（从哪里买）</th><th>物品</th><th>送达点</th><th>状态</th></tr></thead><tbody>
      ${DL_RECS.map(r=>`<tr><td class="mono">${r.t}</td><td>${r.from}</td><td>${r.what}</td><td>${r.to}</td><td><span class="badge ${r.st[1]}">${r.st[0]}</span></td></tr>`).join('')}
      </tbody></table>
    </div></div>`;""",
    """  const secRec = `
    <div class="panel"><div class="panel-hd"><span class="dot"></span>配送记录<span class="extra">全部订单（含小程序下单 · 店员账号可见全部订单）</span></div><div class="panel-bd" style="font-size:12px">
      <table class="task-table"><thead><tr><th>时间</th><th>取货点（从哪里买）</th><th>物品</th><th>送达点</th><th>下单账号</th><th>收件联系</th><th>状态</th></tr></thead><tbody>
      ${DL_RECS.map(r=>`<tr><td class="mono">${r.t}</td><td>${r.from}</td><td>${r.what}</td><td>${r.to}</td><td class="mono" style="font-size:11px">${r.acct}</td><td style="font-size:11px">${r.rcv}</td><td><span class="badge ${r.st[1]}">${r.st[0]}</span></td></tr>`).join('')}
      </tbody></table>
      <div class="muted" style="font-size:10.5px;margin-top:8px;line-height:1.8">异常处置逻辑：① 取货超时 → 带回服务台保管并通知收件人；② 已取货断网 → 不允许原地等待，自动回充电桩/待命区等待重连，订单标记「配送异常-处理中」，恢复在线后自动续送；③ 长时间未移动 / 长时间未送达（且未在执行其他订单）→ 小程序提示「前往充电桩自取或联系店员」；④ 排队中订单可取消（商品退回商铺），已取消订单保留记录不删除。</div>
    </div></div>`;""")

# ============ J. 全局文案清理（去开发向提示） ============
rep('J1 全局去（演示）', '（演示）', '', -1)
rep('J2 去演示备注1', '（演示：不删除真实数据）', '')
rep('J3 去演示备注2', '（演示：列表未真实移除）', '')
rep('J4 去mock标记', '（数据来自定位回传 · mock）', '（数据来自定位回传）')
rep('J5 离线包去编号', '📥 离线任务包（预置本体 · 回连完整性校验补传 PL-09）', '📥 离线任务包（预置本体 · 回连后校验补传）')
rep('J6 离线描述去编号', '回连后按完整性校验（PL-09）补传归档', '回连后校验补传归档')
rep('J7 连接参数去编号', '192.168.7.21:8081 · 本体 SDK 直连（边缘单元 PL-07 随行）', '192.168.7.21:8081 · 本体 SDK 直连（边缘单元随行）')
rep('J8 急停去编号', '（本体安全能力属厂商责任边界 MB-09 · 指令已留痕审计）', '（指令已留痕审计）')
rep('J9 两段式去POC', 'POC 口径', '两段式', -1)
rep('J10 充电桩去依赖标注', ' · 状态接口依赖东方', '')
rep('J11 通行日志去演示', '通行日志<span class="extra">演示</span>', '通行日志')
rep('J12 问答示例', '问答演示', '问答示例')
rep('J13 空间规则规划', '（后续版本）', '（规划中）')
rep('J14 场景配置提示', '场景配置暂不开放（功能保留，后续版本启用）', '场景配置暂不开放（规划中）', -1)
rep('J15 平台能力徽标', '<span class="badge b-dim">隐藏（外链演示）</span>', '<span class="badge b-dim">隐藏</span>')
rep('J16 系统设置口径', '需求分析口径：空间评价与推荐（舒适度/使用率/空置研判）为「场景空间发展方向」，半年内不投入，复兴岛项目可作概念演示（非承诺交付）',
    '空间评价与推荐为场景扩展能力，默认关闭，可按项目开启')
rep('J18 版本管理文案', '版本管理 / 历史追溯 / 多机同步为后续版本内容', '版本管理 / 历史追溯 / 多机同步规划中')

if fails:
    print('\n!!! 失败项：')
    for n, c in fails: print(f'  {n} 匹配数={c}')
    sys.exit(1)

io.open(SRC, 'w', encoding='utf-8', newline='').write(s)
print('\n全部替换完成，已写回 index.html')

# 残留检查
import re
left = [(m.start(), s[m.start()-40:m.start()+40].replace('\n',' ')) for m in re.finditer('演示', s)]
print(f'\n残留「演示」{len(left)} 处：')
for _, ctx in left: print('  …' + ctx + '…')
