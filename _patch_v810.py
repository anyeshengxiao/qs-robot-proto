# -*- coding: utf-8 -*-
"""v8.10 补丁：小舆「去执行消防巡检」→ 单路径规划弹窗（新路径图 + 去备选）"""
import io

def patch(path, subs):
    with io.open(path, encoding='utf-8') as f: s = f.read()
    ok = 0
    for old, new in subs:
        if old not in s:
            print('MISS:', old[:70].replace('\n', '\\n')); continue
        assert s.count(old) == 1, 'not unique: ' + old[:60]
        s = s.replace(old, new); ok += 1
    with io.open(path, 'w', encoding='utf-8', newline='') as f: f.write(s)
    print(path, '->', ok, '/', len(subs))

subs = [
# 1) 小舆示例气泡增加「去执行消防巡检」
("""    ['帮我去奈雪取 A1024 送到301','去 1F 大堂巡检一圈','扫描 2F 采集点云','狗子状态怎么样'].map(s=>'<div class="aa-ex" data-t="'+s+'">'+s+'</div>').join('')});""",
 """    ['去执行消防巡检','帮我去奈雪取 A1024 送到301','去 1F 大堂巡检一圈','扫描 2F 采集点云','狗子状态怎么样'].map(s=>'<div class="aa-ex" data-t="'+s+'">'+s+'</div>').join('')});"""),
# 2) 全局单路径模式标记
("""let selPathIdx = 0;""",
 """let selPathIdx = 0;
let PLAN_SINGLE = false;   /* 单路径模式：消防巡检演示链路，图上与方案区只呈现一条推荐路径 */"""),
# 3) 弹窗标题包 span 便于切换
("""<div class="modal-hd">🧭 任务规划与路径比选<button class="x" onclick="closeMask('planMask')">✕</button></div>""",
 """<div class="modal-hd">🧭 <span id="planTitle">任务规划与路径比选</span><button class="x" onclick="closeMask('planMask')">✕</button></div>"""),
# 4) ② 图例加 id
("""<span style="float:right">🟢 推荐　🟠/⚪ 备选（含排除原因）</span>""",
 """<span id="planLegend" style="float:right">🟢 推荐　🟠/⚪ 备选（含排除原因）</span>"""),
# 5) SVG 加 id + 后插单路径图
("""<svg class="plan-canvas" viewBox="0 0 560 250" style="width:100%;display:block">""",
 """<svg class="plan-canvas" id="planSvg" viewBox="0 0 560 250" style="width:100%;display:block">"""),
("""          </svg>
          <div id="planWeakNote"></div>""",
 """          </svg>
          <img id="planImg" src="assets/path_fire_patrol.png" alt="路径子模型：消防巡检推荐路径" style="display:none;width:100%;border-radius:10px;border:1px solid rgba(34,211,238,.25)">
          <div id="planWeakNote"></div>"""),
# 6) ③ 标题加 id
("""<div class="muted" style="font-size:11px;margin-bottom:6px">③ 三路径推荐（高德式：推荐 / 距离最短 / 最稳妥）· 经验标签：近 3 天 + 前一次（含临时异常）</div>""",
 """<div class="muted" id="planOptsHd" style="font-size:11px;margin-bottom:6px">③ 三路径推荐（高德式：推荐 / 距离最短 / 最稳妥）· 经验标签：近 3 天 + 前一次（含临时异常）</div>"""),
# 7) sendCmd：按指令文本判定单路径模式并套用 UI
("""  document.getElementById('planCmd').textContent = t;
  const sp = mnInferSpace(t);
  document.getElementById('planTarget').textContent = sp.space + ' · 目标点位（语义解析）';
  document.getElementById('planFloor').textContent = sp.fl + ' ' + sp.bld;
  renderPathOpts();""",
 """  document.getElementById('planCmd').textContent = t;
  const sp = mnInferSpace(t);
  document.getElementById('planTarget').textContent = sp.space + ' · 目标点位（语义解析）';
  document.getElementById('planFloor').textContent = sp.fl + ' ' + sp.bld;
  PLAN_SINGLE = /消防巡检/.test(t);
  applyPlanMode();
  renderPathOpts();"""),
# 8) nlConfirm：单路径模式话术
("""  aaSay('解析已确认，为 '+curRobot.name+' 生成 3 条推荐路径，请比选后下发。');""",
 """  aaSay(/消防巡检/.test(NL_TXT) ? '解析已确认，已为 '+curRobot.name+' 生成推荐路径，请确认后下发。' : '解析已确认，为 '+curRobot.name+' 生成 3 条推荐路径，请比选后下发。');"""),
# 9) applyPlanMode 函数 + renderPathOpts 单路径渲染
("""function renderPathOpts(){
  const e = ENV_CFG[robotScene()];""",
 """function applyPlanMode(){
  const s = PLAN_SINGLE;
  document.getElementById('planSvg').style.display = s?'none':'block';
  document.getElementById('planImg').style.display = s?'block':'none';
  document.getElementById('planLegend').style.display = s?'none':'';
  document.getElementById('planOptsHd').innerHTML = s
    ? '③ 推荐路径 · 语义理由 + 经验标签（近 3 天 + 前一次执行情况）'
    : '③ 三路径推荐（高德式：推荐 / 距离最短 / 最稳妥）· 经验标签：近 3 天 + 前一次（含临时异常）';
  document.getElementById('planTitle').textContent = s ? '任务规划与路径确认' : '任务规划与路径比选';
  if(s) selPathIdx = 0;
}
function renderPathOpts(){
  const e = ENV_CFG[robotScene()];"""),
("""  document.getElementById('pathOpts').innerHTML = PATHS.map((p,i)=>`
    <div class="path-opt ${i===selPathIdx?'sel':'rej'}" onclick="selPathIdx=${i};renderPathOpts()">""",
 """  document.getElementById('pathOpts').innerHTML = (PLAN_SINGLE?[PATHS[0]]:PATHS).map((p,i)=>`
    <div class="path-opt ${(PLAN_SINGLE||i===selPathIdx)?'sel':'rej'}" ${PLAN_SINGLE?'':'onclick="selPathIdx='+i+';renderPathOpts()"'}>"""),
("""        <div class="why" style="color:${i===selPathIdx?'#34d399':'var(--tx-dim)'}">${i===selPathIdx?'✓ 推荐理由：':'✗ 排除原因：'}${whys[i]}</div>""",
 """        <div class="why" style="color:${(PLAN_SINGLE||i===selPathIdx)?'#34d399':'var(--tx-dim)'}">${(PLAN_SINGLE||i===selPathIdx)?'✓ 推荐理由：':'✗ 排除原因：'}${whys[i]}</div>"""),
]
patch('index.html', subs)
print('ALL OK')
