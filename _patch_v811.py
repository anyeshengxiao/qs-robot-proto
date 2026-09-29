# -*- coding: utf-8 -*-
"""v8.11 补丁：① 弹窗压小舆 ② 下发后模型区路径行走动画 ③ 电梯/门控/充电桩图层开关（默认隐藏）"""
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
# ① 弹窗层级压过小舆（aiAgent z-400）+ 路径模式 CSS + 狗标记 CSS
(""".mask{position:fixed;inset:0;background:rgba(2,6,14,.7);backdrop-filter:blur(3px);z-index:100;display:none;align-items:center;justify-content:center}""",
 """.mask{position:fixed;inset:0;background:rgba(2,6,14,.7);backdrop-filter:blur(3px);z-index:100;display:none;align-items:center;justify-content:center}
#nlMask,#planMask,#woMask{z-index:450}
#mn-3d.path-mode img.bg3d{left:0;top:0;width:100%;height:100%;object-fit:fill;object-position:50% 50%}
.mn-path-dog{position:absolute;z-index:9;transform:translate(-50%,-100%);display:none;flex-direction:column;align-items:center;gap:2px;pointer-events:none}
.mn-path-dog .pd-name{font-size:10px;color:#e6f1ff;background:rgba(8,14,28,.88);border:1px solid var(--border-hi);border-radius:8px;padding:1px 8px;white-space:nowrap;box-shadow:0 2px 8px rgba(0,0,0,.5)}
.mn-path-dog img{width:56px;height:auto;filter:drop-shadow(0 3px 6px rgba(0,0,0,.65))}"""),
# ③-a 工具栏加三个图层开关（默认不点亮 = 隐藏）
("""      <button class="on" id="vmBots" title="具身位置标记（机器人 / 机器狗统一图层）" onclick="vmToggle(this,'具身');renderMnBots()">🐕 具身</button>""",
 """      <button class="on" id="vmBots" title="具身位置标记（机器人 / 机器狗统一图层）" onclick="vmToggle(this,'具身');renderMnBots()">🐕 具身</button>
      <button id="vmLift" title="电梯图层 · 默认隐藏，点亮显示" onclick="vmToggle(this,'电梯');renderMnBots()">🛗 电梯</button>
      <button id="vmGate" title="门控图层 · 默认隐藏，点亮显示" onclick="vmToggle(this,'门控');renderMnBots()">🚪 门控</button>
      <button id="vmChg" title="充电桩图层 · 默认隐藏，点亮显示" onclick="vmToggle(this,'充电桩');renderMnBots()">🔌 充电桩</button>"""),
# ③-b 充电桩标记受开关控制
("""  /* 充电桩标记（空闲/占用/故障 · 占用显示具身名 · 接口依赖东方） */
  html += CHARGES.map(cg=>""",
 """  /* 充电桩标记（图层开关控制 · 默认隐藏） */
  const _vmC=document.getElementById('vmChg'), _vmG=document.getElementById('vmGate'), _vmL=document.getElementById('vmLift');
  if(_vmC && _vmC.classList.contains('on'))
  html += CHARGES.map(cg=>"""),
# ③-c 门标记受开关控制
("""  /* 门标记（自动/非自动区分 · 通行中闪烁 · 自动门未配 API 红色） */
  html += DOORS.map(d=>{""",
 """  /* 门标记（图层开关控制 · 默认隐藏） */
  if(_vmG && _vmG.classList.contains('on'))
  html += DOORS.map(d=>{"""),
# ③-d 电梯标记（新增图层）+ 收尾
("""  }).join('');
  box.innerHTML = html;
  const chip=document.getElementById('chipBots');""",
 """  }).join('');
  /* 电梯标记（图层开关控制 · 默认隐藏） */
  if(_vmL && _vmL.classList.contains('on'))
  html += LIFTS.map(l=>`<div class="gate-mk lift ${l.usable?'':'noapi'}" style="left:${l.vx}%;top:${l.vy}%" title="${l.name} · 服务楼层 ${l.floors} · ${l.usable?'可乘 · 已接梯控':'不可乘 · 未接梯控'}">🛗</div>`).join('');
  box.innerHTML = html;
  const chip=document.getElementById('chipBots');"""),
# ②-a 下发后触发路径行走（单路径模式）
("""  aaEvent('🧭', `任务已下发：${curRobot.name} 出发执行「${cmdRaw.slice(0,20)}」，路径 ${p.tag} · ${p.dist}，我盯着呢。`);
}""",
 """  aaEvent('🧭', `任务已下发：${curRobot.name} 出发执行「${cmdRaw.slice(0,20)}」，路径 ${p.tag} · ${p.dist}，我盯着呢。`);
  if(PLAN_SINGLE) setTimeout(mnPathWalk, 400);
}

/* ---- 消防巡检演示：模型区切换路径图 + 狗沿路径行走 ---- */
const MN_FIRE_PATH = [[28.3,70.5],[28.6,58],[29.3,47.5],[31.5,50.5],[33.5,55.5],[38.5,54.3],[54.9,52.5]]; /* 图幅百分比坐标 */
function mnPathWalk(){
  const vp = document.getElementById('mn-3d'); if(!vp) return;
  const img = vp.querySelector('img.bg3d'); if(!img) return;
  if(img.dataset.origSrc===undefined) img.dataset.origSrc = img.getAttribute('src');
  img.src = 'assets/path_fire_patrol.png';
  vp.classList.add('path-mode');
  let dog = document.getElementById('mnPathDog');
  if(!dog){
    dog = document.createElement('div');
    dog.id = 'mnPathDog'; dog.className = 'mn-path-dog';
    dog.innerHTML = '<div class="pd-name"></div><img src="assets/crop_dog_go1.png" alt="宇树 GO2">';
    vp.appendChild(dog);
  }
  dog.querySelector('.pd-name').textContent = (curRobot?curRobot.name:'清星小智') + ' · 宇树 GO2';
  const path = MN_FIRE_PATH;
  dog.style.display = 'flex';
  dog.style.transition = 'none';
  dog.style.left = path[0][0]+'%'; dog.style.top = path[0][1]+'%';
  let i = 0;
  function step(){
    if(i>=path.length-1){
      toast((curRobot?curRobot.name:'狗')+' 已沿规划路径到达目标点位，开始消防巡检采集');
      aaEvent('✅','已沿推荐路径到达目标点位，开始执行消防巡检采集（拍照 ×4 方位 + 录像 30s）。');
      return;
    }
    i++;
    dog.style.transition = 'left 2.4s linear, top 2.4s linear';
    dog.style.left = path[i][0]+'%'; dog.style.top = path[i][1]+'%';
    setTimeout(step, 2550);
  }
  setTimeout(step, 700);
}
function mnPathRestore(){
  const vp = document.getElementById('mn-3d'); if(!vp || !vp.classList.contains('path-mode')) return;
  vp.classList.remove('path-mode');
  const img = vp.querySelector('img.bg3d');
  if(img && img.dataset.origSrc) img.src = img.dataset.origSrc;
  const dog = document.getElementById('mnPathDog'); if(dog) dog.style.display='none';
}
window.addEventListener('hashchange', ()=>{ if(location.hash.indexOf('monitor')<0) mnPathRestore(); });"""),
]
patch('index.html', subs)
print('ALL OK')
