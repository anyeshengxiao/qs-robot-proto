# -*- coding: utf-8 -*-
"""v8.8 补丁：电梯服务楼层点击选中 / 视口深化去光带 / 平台名 / 临时任务恢复"""
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
# ③-a 服务楼层 chip 样式（CSS，锚定 .vm-toolbar 前插入）
(""".vm-toolbar{position:absolute;left:14px;top:14px;display:flex;flex-direction:column;gap:6px;z-index:5}""",
 """.sgLf2{padding:3px 12px;border:1px solid var(--border);border-radius:14px;font-size:11px;cursor:pointer;color:var(--tx-dim);transition:all .15s;user-select:none}
.sgLf2:hover{border-color:rgba(34,211,238,.5);color:var(--tx)}
.sgLf2.on{border-color:var(--cy);background:rgba(34,211,238,.16);color:#7de8ff;box-shadow:0 0 8px rgba(34,211,238,.25)}
.vm-toolbar{position:absolute;left:14px;top:14px;display:flex;flex-direction:column;gap:6px;z-index:5}"""),
# ③-b 服务楼层改点击胶囊（去勾选框）
("""<div class="form-row"><label>服务楼层</label><span style="display:flex;gap:6px;flex-wrap:wrap;flex:1">${(SP_BOX.find(x=>x.id===(SP_FL_MAP[gl.fl]||['主楼'])[0])||SP_BOX[0]).floors.map(f=>`<label style="display:flex;align-items:center;gap:3px;font-size:11px;cursor:pointer;padding:2px 8px;border:1px solid ${gl.floors.includes(f)?'var(--cy)':'var(--border)'};border-radius:6px;background:${gl.floors.includes(f)?'rgba(34,211,238,.1)':'transparent'}"><input type="checkbox" class="sgLf" value="${f}" ${gl.floors.includes(f)?'checked':''} style="accent-color:#22d3ee">${f}</label>`).join('')}</span></div>""",
 """<div class="form-row"><label>服务楼层</label><span style="display:flex;gap:6px;flex-wrap:wrap;flex:1">${(SP_BOX.find(x=>x.id===(SP_FL_MAP[gl.fl]||['主楼'])[0])||SP_BOX[0]).floors.map(f=>`<span class="sgLf2 ${gl.floors.includes(f)?'on':''}" data-v="${f}" onclick="this.classList.toggle('on')">${f}</span>`).join('')}</span></div>"""),
# ③-c 保存逻辑改读 .sgLf2.on
("""const fls=[...document.querySelectorAll('.sgLf:checked')].map(c=>c.value); if(fls.length) l.floors = fls.join('、');""",
 """const fls=[...document.querySelectorAll('.sgLf2.on')].map(c=>c.dataset.v); if(fls.length) l.floors = fls.join('、');"""),
# ④-a 去掉巡航扫光带（::before + sweep 关键帧）
("""#mn-3d::before{content:"";position:absolute;left:0;right:0;top:0;height:130px;z-index:6;pointer-events:none;
  background:linear-gradient(180deg,transparent,rgba(56,189,248,.10) 55%,rgba(139,92,246,.14) 85%,transparent);
  animation:sweep 8s linear infinite}
@keyframes sweep{from{transform:translateY(-140px)}to{transform:translateY(110vh)}}
[data-theme="light"] #mn-3d::before,[data-theme="light"] #mn-3d::after{display:none}""",
 """[data-theme="light"] #mn-3d::after{display:none}"""),
# ④-b 叠加层更深更透（深蓝紫）
("""  background:radial-gradient(115% 85% at 46% 30%,rgba(16,13,44,.05) 0%,rgba(16,13,44,.16) 55%,rgba(5,6,22,.45) 100%),linear-gradient(160deg,rgba(23,15,58,.18),rgba(6,8,26,.30)),repeating-linear-gradient(0deg,rgba(120,180,255,.035) 0 1px,transparent 1px 4px)}""",
 """  background:radial-gradient(115% 85% at 46% 30%,rgba(14,11,42,.10) 0%,rgba(14,11,42,.26) 55%,rgba(4,5,20,.58) 100%),linear-gradient(160deg,rgba(26,16,62,.26),rgba(5,7,24,.40)),repeating-linear-gradient(0deg,rgba(120,180,255,.03) 0 1px,transparent 1px 4px)}"""),
# ④-c 底图再压暗
("""object-position:36% 24%;filter:brightness(.68) contrast(1.3) saturate(1.3)}""",
 """object-position:36% 24%;filter:brightness(.60) contrast(1.32) saturate(1.35)}"""),
# ⑤ 平台名（标题 + 登录后顶栏）
("""<title>模舆机器人平台</title>""",
 """<title>模舆具身智能管理平台</title>"""),
("""<div><div class="bt">模舆机器人平台</div><div class="bs">SPACEMOR ROBOT PLATFORM</div></div>""",
 """<div><div class="bt">模舆具身智能管理平台</div><div class="bs">SPACEMOR EMBODIED AI PLATFORM</div></div>"""),
# ⑥-a 任务类型恢复「临时任务」
("""<select class="input" id="teType" onchange="teTypeChange()"><option>固定任务-周期</option><option>固定任务-定期（单次）</option><option>固定任务-人为触发</option></select>""",
 """<select class="input" id="teType" onchange="teTypeChange()"><option>固定任务-周期</option><option>固定任务-定期（单次）</option><option>固定任务-人为触发</option><option>临时任务</option></select>"""),
# ⑥-b 类型提示补临时任务
("""  else if(v.indexOf('人为')>=0) ht = '保存后标记为 <b style="color:var(--cy)">固定任务-人为触发</b>，不自动排班，由操作员手动启动';
  if(hint) hint.innerHTML = ht;""",
 """  else if(v.indexOf('人为')>=0) ht = '保存后标记为 <b style="color:var(--cy)">固定任务-人为触发</b>，不自动排班，由操作员手动启动';
  else if(v.indexOf('临时')>=0) ht = '保存后标记为 <b style="color:#fbbf24">临时任务</b>，单次执行，不进入固定排班';
  if(hint) hint.innerHTML = ht;"""),
# ⑥-c 配送业务默认临时任务；巡检/导览切回时复位
("""  if(b==='delivery'){
    document.getElementById('teName').value = '跨楼层物品配送（奈雪 → 3F 办公区）';
    teRobots = ['mira']; renderTeRobots();
  } else if(b==='guide'){
    document.getElementById('teName').value = '园区访客导览（大门 → 在水一方）';""",
 """  if(b==='delivery'){
    tt.value='临时任务'; teTypeChange();
    document.getElementById('teName').value = '跨楼层物品配送（奈雪 → 3F 办公区）';
    teRobots = ['mira']; renderTeRobots();
  } else if(b==='guide'){
    if(tt.value==='临时任务'){ tt.value='固定任务-人为触发'; teTypeChange(); }
    document.getElementById('teName').value = '园区访客导览（大门 → 在水一方）';"""),
("""  } else {
    teBld = teSpaces[0];
  }
  renderTePlan();""",
 """  } else {
    if(tt.value==='临时任务'){ tt.value='固定任务-周期'; teTypeChange(); }
    teBld = teSpaces[0];
  }
  renderTePlan();"""),
# ⑥-d 编辑回填：临时任务正确回显
("""  tt.value = t.cat==='fixed' ? (t.period ? '固定任务-周期' : '固定任务-人为触发') : '固定任务-人为触发';""",
 """  tt.value = t.cat==='fixed' ? (t.period ? '固定任务-周期' : '固定任务-人为触发') : '临时任务';"""),
]
patch('index.html', subs)
print('ALL OK')
