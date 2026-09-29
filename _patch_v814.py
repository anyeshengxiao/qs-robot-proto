# -*- coding: utf-8 -*-
import io, sys
p = 'index.html'
s = io.open(p, encoding='utf-8').read()
n = 0
def rep(old, new):
    global s, n
    assert s.count(old) == 1, 'NOT UNIQUE (%d): %s' % (s.count(old), old[:60])
    s = s.replace(old, new); n += 1

# 1) 小狗图标水平翻转：头朝左、尾巴朝右（只翻转 img，名牌不动）
rep('.mn-path-dog .pd-dog{width:44px;height:auto;filter:drop-shadow(0 0 8px rgba(111,240,255,.6)) drop-shadow(0 3px 5px rgba(0,0,0,.6))}',
    '.mn-path-dog .pd-dog{width:44px;height:auto;transform:scaleX(-1);filter:drop-shadow(0 0 8px rgba(111,240,255,.6)) drop-shadow(0 3px 5px rgba(0,0,0,.6))}\n'
    '#planTrace{position:absolute;inset:0;width:100%;height:100%;pointer-events:none;filter:drop-shadow(0 0 6px rgba(34,211,238,.55))}\n'
    '#planTrace .pt-glow{stroke:#22d3ee;stroke-width:11px;opacity:.38;fill:none;stroke-linecap:round;stroke-linejoin:round;vector-effect:non-scaling-stroke;stroke-dasharray:100;stroke-dashoffset:100}\n'
    '#planTrace .pt-core{stroke:#cffafe;stroke-width:3.6px;fill:none;stroke-linecap:round;stroke-linejoin:round;vector-effect:non-scaling-stroke;stroke-dasharray:100;stroke-dashoffset:100}\n'
    '#planTrace.draw .pt-glow{stroke-dashoffset:0;transition:stroke-dashoffset 3s linear .15s}\n'
    '#planTrace.draw .pt-core{stroke-dashoffset:0;transition:stroke-dashoffset 3s linear .15s}')

# 2) planImg 外包一层 relative 容器，叠加 SVG 描边动画路径（viewBox=原图像素 1620x1100，终点延伸到 3F 灭火器）
TRACE_PTS = '883,579 779,582 630,595 543,605 480,558 441,620 429,660 424,720 460,745 480,730 486,652'
rep('<img id="planImg" src="assets/path_fire_patrol.png" alt="路径子模型：消防巡检推荐路径" style="display:none;width:100%;border-radius:10px;border:1px solid rgba(34,211,238,.25)">',
    '<div id="planImgWrap" style="display:none;position:relative">\n'
    '            <img id="planImg" src="assets/path_fire_patrol.png" alt="路径子模型：消防巡检推荐路径" style="display:block;width:100%;border-radius:10px;border:1px solid rgba(34,211,238,.25)">\n'
    '            <svg id="planTrace" viewBox="0 0 1620 1100" preserveAspectRatio="none">'
    '<polyline class="pt-glow" pathLength="100" points="' + TRACE_PTS + '"/>'
    '<polyline class="pt-core" pathLength="100" points="' + TRACE_PTS + '"/>'
    '</svg>\n          </div>')

# 3) 行走路径与 SVG 轨迹一致，终点延伸至 3F 灭火器（图幅百分比）
rep("const MN_FIRE_PATH = [[54.9,52.5],[38.5,54.3],[33.5,55.5],[31.5,50.5],[29.3,47.5],[28.6,58],[28.3,70.5]]; /* 图幅百分比坐标 · 由路径终点走向起点 */",
    "const MN_FIRE_PATH = [[54.5,52.6],[48.1,52.9],[38.9,54.1],[33.5,55],[29.6,50.7],[27.2,56.4],[26.5,60],[26.2,65.5],[28.4,67.7],[29.6,66.4],[29.9,59.3]]; /* 图幅百分比坐标 · 4F走廊→楼梯→3F消防灭火器 */")

# 4) 行走节奏稍加快 + 到达提示点名 3F 灭火器
rep("      toast((curRobot?curRobot.name:'狗')+' 已沿规划路径到达目标点位，开始消防巡检采集');",
    "      toast((curRobot?curRobot.name:'狗')+' 已到达 3F 消防灭火器点位，开始消防巡检采集');")
rep("    dog.style.transition = 'left 2.4s linear, top 2.4s linear';\n    dog.style.left = path[i][0]+'%'; dog.style.top = path[i][1]+'%';\n    setTimeout(step, 2550);",
    "    dog.style.transition = 'left 2s linear, top 2s linear';\n    dog.style.left = path[i][0]+'%'; dog.style.top = path[i][1]+'%';\n    setTimeout(step, 2150);")

# 5) applyPlanMode：加载完显示 wrap 并重启描边动画
rep("  const pi = document.getElementById('planImg'), ld = document.getElementById('planLoading');\n  clearTimeout(window._planLdT);\n  if(s){ pi.style.display='none'; ld.style.display='flex';\n    window._planLdT = setTimeout(()=>{ ld.style.display='none'; pi.style.display='block'; }, 3000);\n  } else { ld.style.display='none'; pi.style.display='none'; }",
    "  const piw = document.getElementById('planImgWrap'), ld = document.getElementById('planLoading');\n  clearTimeout(window._planLdT);\n  if(s){ piw.style.display='none'; ld.style.display='flex';\n    window._planLdT = setTimeout(()=>{ ld.style.display='none'; piw.style.display='block';\n      const tr = document.getElementById('planTrace'); tr.classList.remove('draw'); void tr.getBoundingClientRect(); tr.classList.add('draw');\n    }, 3000);\n  } else { ld.style.display='none'; piw.style.display='none'; }")

io.open(p, 'w', encoding='utf-8', newline='').write(s)
print(p, '->', n, '/ 6')
print('ALL OK')
