# -*- coding: utf-8 -*-
"""v8.13 补丁：NL解析卡目标位置改3F/4F + 行走标记换logo三维小狗"""
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
# 1) NL 解析确认卡：消防巡检目标位置 3F、4F
("""  const rows=[
    ['任务类型', biz, ''],
    ['目标位置', hasDest? sp.space+' · '+sp.bld+' '+sp.fl : '⚠ 未识别到目的地，请补充（如"去 3F 办公区"）', hasDest?'':'miss'],""",
 """  const fire=/消防巡检/.test(t);
  const rows=[
    ['任务类型', biz, ''],
    ['目标位置', fire? '3F、4F · 主楼（消防通道）' : (hasDest? sp.space+' · '+sp.bld+' '+sp.fl : '⚠ 未识别到目的地，请补充（如"去 3F 办公区"）'), (hasDest||fire)?'':'miss'],"""),
# 2) 行走标记：小圆点 → logo 三维小狗
(""".mn-path-dog .pd-dot{width:14px;height:14px;border-radius:50%;background:#22d3ee;box-shadow:0 0 12px #22d3ee,0 0 4px #22d3ee;animation:pulse 1.6s infinite}""",
 """.mn-path-dog .pd-dog{width:44px;height:auto;filter:drop-shadow(0 0 8px rgba(111,240,255,.6)) drop-shadow(0 3px 5px rgba(0,0,0,.6))}"""),
("""    dog.innerHTML = '<div class="pd-name"></div><div class="pd-dot"></div>';""",
 """    dog.innerHTML = '<div class="pd-name"></div><img class="pd-dog" src="assets/login_logo.svg" alt="模舆机器狗">';"""),
("""  dog.querySelector('.pd-name').textContent = curRobot ? curRobot.name : 'Mira';""",
 """  dog.querySelector('.pd-name').textContent = '🐕 ' + (curRobot ? curRobot.name : 'Mira');"""),
]
patch('index.html', subs)
print('ALL OK')
