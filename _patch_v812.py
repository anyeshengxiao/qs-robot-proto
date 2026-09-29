# -*- coding: utf-8 -*-
"""v8.12 补丁：路径弹窗加载态3s / 语义改3F·4F / 推荐理由替换 / 行走向反转+MIRA小圆点"""
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
# 1) CSS：加载动画 + 小圆点标记（替换狗图样式）
(""".mn-path-dog img{width:56px;height:auto;filter:drop-shadow(0 3px 6px rgba(0,0,0,.65))}""",
 """.mn-path-dog .pd-dot{width:14px;height:14px;border-radius:50%;background:#22d3ee;box-shadow:0 0 12px #22d3ee,0 0 4px #22d3ee;animation:pulse 1.6s infinite}
.plan-loading{display:none;flex-direction:column;align-items:center;justify-content:center;gap:12px;min-height:280px;border:1px dashed rgba(34,211,238,.3);border-radius:10px;background:rgba(34,211,238,.03)}
.plan-loading .spin{width:30px;height:30px;border-radius:50%;border:3px solid rgba(34,211,238,.18);border-top-color:#22d3ee;animation:aaspin 1s linear infinite}
.plan-loading .tx{font-size:12px;color:var(--cy);letter-spacing:1px}"""),
# 2) 弹窗内加加载占位（img 前）
("""          <img id="planImg" src="assets/path_fire_patrol.png" alt="路径子模型：消防巡检推荐路径" style="display:none;width:100%;border-radius:10px;border:1px solid rgba(34,211,238,.25)">""",
 """          <div class="plan-loading" id="planLoading"><div class="spin"></div><div class="tx">路径子模型规划及提取中…</div><div class="muted" style="font-size:10px">子模型提取：仅空间 + 重点系统/设备 + 重点位置，不加载全量模型</div></div>
          <img id="planImg" src="assets/path_fire_patrol.png" alt="路径子模型：消防巡检推荐路径" style="display:none;width:100%;border-radius:10px;border:1px solid rgba(34,211,238,.25)">"""),
# 3) ① 语义面板加 id（便于单路径模式替换）
("""        <div style="font-size:11px;line-height:1.9;color:var(--tx)">
          目的地语义：<b>1F-研发层</b>（空间）→ <b>消防通道</b>（POI）→ 意图：<b>巡检</b>（拍照 + 录像）<br>""",
 """        <div style="font-size:11px;line-height:1.9;color:var(--tx)" id="aiSemBd">
          目的地语义：<b>1F-研发层</b>（空间）→ <b>消防通道</b>（POI）→ 意图：<b>巡检</b>（拍照 + 录像）<br>"""),
# 4) applyPlanMode：加载态 3s + 语义/目标替换与还原
("""function applyPlanMode(){
  const s = PLAN_SINGLE;
  document.getElementById('planSvg').style.display = s?'none':'block';
  document.getElementById('planImg').style.display = s?'block':'none';
  document.getElementById('planLegend').style.display = s?'none':'';
  document.getElementById('planOptsHd').innerHTML = s
    ? '③ 推荐路径 · 语义理由 + 经验标签（近 3 天 + 前一次执行情况）'
    : '③ 三路径推荐（高德式：推荐 / 距离最短 / 最稳妥）· 经验标签：近 3 天 + 前一次（含临时异常）';
  document.getElementById('planTitle').textContent = s ? '任务规划与路径确认' : '任务规划与路径比选';
  if(s) selPathIdx = 0;
}""",
 """function applyPlanMode(){
  const s = PLAN_SINGLE;
  document.getElementById('planSvg').style.display = s?'none':'block';
  document.getElementById('planLegend').style.display = s?'none':'';
  document.getElementById('planOptsHd').innerHTML = s
    ? '③ 推荐路径 · 语义理由 + 经验标签（近 3 天 + 前一次执行情况）'
    : '③ 三路径推荐（高德式：推荐 / 距离最短 / 最稳妥）· 经验标签：近 3 天 + 前一次（含临时异常）';
  document.getElementById('planTitle').textContent = s ? '任务规划与路径确认' : '任务规划与路径比选';
  /* 路径图加载态：先「规划及提取中」动画，3s 后显示路径子模型图 */
  const pi = document.getElementById('planImg'), ld = document.getElementById('planLoading');
  clearTimeout(window._planLdT);
  if(s){ pi.style.display='none'; ld.style.display='flex';
    window._planLdT = setTimeout(()=>{ ld.style.display='none'; pi.style.display='block'; }, 3000);
  } else { ld.style.display='none'; pi.style.display='none'; }
  /* 语义面板：消防巡检链路指向 3F、4F */
  const sem = document.getElementById('aiSemBd');
  if(sem){
    if(!sem.dataset.orig) sem.dataset.orig = sem.innerHTML;
    sem.innerHTML = s
      ? '目的地语义：<b>3F、4F</b>（空间）→ <b>消防通道</b>（POI）→ 意图：<b>巡检</b>（拍照 + 录像）<br><span id="aiPostCheck">岗位校验：能力集 {巡检、导引} ✓ 可执行</span><br>命中预设模板：「区域巡检 · 消防通道专项」· 覆盖 3F / 4F 全部消防点位（采集要求：拍照 ×4 方位 + 录像 30s + 停留 10s）'
      : sem.dataset.orig;
  }
  if(s){
    document.getElementById('planTarget').textContent = '3F · 4F · 消防通道（消防设备在位与状态核查）';
    document.getElementById('planFloor').textContent = '3F · 4F 共青130寓';
  }
  if(s) selPathIdx = 0;
}"""),
# 5) 推荐理由：单路径模式替换为指定文案
("""  const whys = [e.sel, e.rejB, e.rejC];""",
 """  const whys = PLAN_SINGLE ? ['4F经楼梯到3F：检查所有消防设备是否在指定位置且状态正常。'] : [e.sel, e.rejB, e.rejC];"""),
# 6) 行走向反转（终点→起点）+ 换 MIRA 同款小圆点
("""const MN_FIRE_PATH = [[28.3,70.5],[28.6,58],[29.3,47.5],[31.5,50.5],[33.5,55.5],[38.5,54.3],[54.9,52.5]]; /* 图幅百分比坐标 */""",
 """const MN_FIRE_PATH = [[54.9,52.5],[38.5,54.3],[33.5,55.5],[31.5,50.5],[29.3,47.5],[28.6,58],[28.3,70.5]]; /* 图幅百分比坐标 · 由路径终点走向起点 */"""),
("""    dog.innerHTML = '<div class="pd-name"></div><img src="assets/crop_dog_go1.png" alt="宇树 GO2">';""",
 """    dog.innerHTML = '<div class="pd-name"></div><div class="pd-dot"></div>';"""),
("""  dog.querySelector('.pd-name').textContent = (curRobot?curRobot.name:'清星小智') + ' · 宇树 GO2';""",
 """  dog.querySelector('.pd-name').textContent = curRobot ? curRobot.name : 'Mira';"""),
]
patch('index.html', subs)
print('ALL OK')
