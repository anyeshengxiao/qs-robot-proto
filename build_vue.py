# -*- coding: utf-8 -*-
"""从原型 index.html 生成 Vue 工程文件：页面骨架 SFC + runtime.js + mock 数据模块"""
import re, io, os

SRC = r"C:\Users\52560\Documents\Kimi\Workspaces\机器人\qs-robot-proto\index.html"
RAW = r"C:\Users\52560\Documents\Kimi\Workspaces\机器人\qs-robot-proto\runtime_raw.js"
DST = r"C:\Users\52560\Desktop\机器人\qs-robot-hub"

lines = io.open(SRC, encoding='utf8').read().splitlines()

def slice_html(a, b):  # 1-based inclusive
    return "\n".join(lines[a-1:b])

# ---- 1. 用 <div 平衡扫描，精确切出 pg-* 页面块 ----
def cut_div(start_line):
    """从 start_line（含 <div id=）开始，按 div 平衡找到结束行，返回 (text, end_line)"""
    depth = 0
    out = []
    for i in range(start_line-1, len(lines)):
        ln = lines[i]
        out.append(ln)
        depth += len(re.findall(r'<div\b', ln)) - ln.count('</div>')
        if depth == 0:
            return "\n".join(out), i+1
    raise RuntimeError('unbalanced from line %d' % start_line)

pages = {
    'LoginView':    ('loginMask', 647),
    'TopBar':       ('topbar', 666),
    'MonitorView':  ('pg-monitor', 700),
    'AccessView':   ('pg-config', 774),
    'TasksView':    ('pg-tasks', 810),
    'SpaceView':    ('pg-space', 997),
    'EvaluateView': ('pg-evaluate', 1088),
    'RecommendView':('pg-recommend', 1098),
    'SettingsView': ('pg-settings', 1117),
}
# 场景页（单行）与 aiAgent、全局弹窗层
scene_lines = { 'PropertyView':1111, 'SiteView':1112, 'GuideView':1113, 'DeliveryView':1114 }
aiagent, _ = cut_div(1405)

# 全局弹窗层：顶栏结束(697)之后、aiAgent(1405)之前，所有不属于 pg-* 页面块的顶层内容
page_ranges = []
for name, (did, start) in pages.items():
    _, end = cut_div(start)
    page_ranges.append((start, end))
for ln in scene_lines.values():
    page_ranges.append((ln, ln))
def in_page(ln):
    return any(a <= ln <= b for a, b in page_ranges)
over_parts, buf = [], []
ln = 698
while ln <= 1404:
    if in_page(ln):
        ln += 1; continue
    l = lines[ln-1]
    if l.startswith('<div class="mask"') or l.startswith('<div class="drawer'):
        blk, e = cut_div(ln)
        over_parts.append(blk)
        ln = e + 1
    elif l.strip().startswith('<!-- 页面') or l.strip().startswith('<!-- ='):
        ln += 1  # 跳过页面分隔注释
    else:
        if l.strip(): buf.append(l)
        ln += 1
if buf: over_parts.append("\n".join(buf))
overlays = "\n".join(over_parts)

def write_sfc(rel, html, script=''):
    path = os.path.join(DST, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    body = "<template>\n" + html + "\n</template>\n"
    if script:
        body += "\n<script setup lang=\"ts\">\n" + script + "\n</script>\n"
    io.open(path, 'w', encoding='utf8').write(body)
    print('SFC', rel)

for name, (did, start) in pages.items():
    html, _ = cut_div(start)
    write_sfc(f'src/views/{name}/index.vue', html)
for name, ln in scene_lines.items():
    write_sfc(f'src/views/{name}/index.vue', lines[ln-1])
write_sfc('src/components/layout/Overlays.vue', overlays)

# ---- 2. runtime.js ----
rt = io.open(RAW, encoding='utf8').read()

# 要抽到 src/mock/ 的纯数据常量
MOCK = {
 'robots.ts':   ['ROBOTS','ROBOT_EXT','API_MODS','CFG_TASKS','API_ST','REG_RES','POST_TASKS','WZ_STEPS','MN_POS','NET_TX'],
 'space.ts':    ['TREE','ATTRS','SP_META','SP_BOX','SP_ROOMS','SP_ISSUES','ANOMS','ANOM_BY_TASK','SP_TREE','SP_NODES','SP_FL_MAP','SPC_TAGS','SPC_DEVS','SC_DEVS','FL_Z','ENV_CFG','PATHS','TJ_PATH'],
 'tasks.ts':    ['TASKS','CAT_TX','TST','HST','BIZ_TX','BNAMES','OP_CONF','CMD_HIST','TE_SPACES','TE_POOL','TE_ACT_POOL','MT_POINTS','POINTS'],
 'scenes.ts':   ['SCENES','SCENE_TABS','ALGO_CTYPE','ALGO_CFG_DFT','SCENE_NAMES','BIND_SCENES','MENU_L1','MENU_L2','MENU_PERM','PROJECTS','USERS'],
 'delivery.ts': ['DL_PICKS','DL_DROPS','DL_VOICE','DL_ACTS','DL_RECS'],
 'guide.ts':    ['GUIDE_FAQ','TOUR_PTS'],
}
all_names = {n for v in MOCK.values() for n in v}

def cut_const(text, name):
    """切除顶层 `const NAME = ...;` 块，返回 (block, text)"""
    m = re.search(r'(?m)^const %s = ' % name, text)
    if not m: raise RuntimeError('const %s not found' % name)
    i = m.start()
    depth = 0; j = m.end()
    in_str = None; esc = False
    while j < len(text):
        c = text[j]
        if in_str:
            if esc: esc = False
            elif c == '\\': esc = True
            elif c == in_str: in_str = None
        else:
            if c in '\'"`': in_str = c
            elif c in '([{': depth += 1
            elif c in ')]}': depth -= 1
            elif c == ';' and depth == 0:
                block = text[i:j+1]
                # 吃掉块后的换行
                k = j+1
                while k < len(text) and text[k] == '\n': k += 1
                return block, text[:i] + text[k:]
        j += 1
    raise RuntimeError('unterminated const %s' % name)

blocks = {}
for n in sorted(all_names):
    b, rt = cut_const(rt, n)
    blocks[n] = b

# 生成 mock 模块
HDR = "/**\n * 原型 v8.3 mock 数据（自动生成，勿手改逻辑）\n * 运行时装载：赋值到 window 供 public/proto/runtime.js 使用；\n * 后续接真实 API 时，service 层改为读接口、保持字段签名不变。\n */\n/* eslint-disable */\n// @ts-nocheck\n"
os.makedirs(os.path.join(DST, 'src/mock'), exist_ok=True)
for fn, names in MOCK.items():
    parts = [HDR]
    wins = []
    for n in names:
        b = blocks[n]
        b = re.sub(r'^const %s = ' % n, 'const %s: any = ' % n, b)
        parts.append(b)
        wins.append(n)
    parts.append("Object.assign(window as any, { %s })\n" % ", ".join(wins))
    io.open(os.path.join(DST, 'src/mock', fn), 'w', encoding='utf8').write("\n".join(parts))
    print('mock', fn)
# barrel
io.open(os.path.join(DST, 'src/mock/index.ts'), 'w', encoding='utf8').write(
    "// mock 数据统一装载入口（在 main.ts 中最先引入，先于 runtime 调用）\nimport './robots'\nimport './space'\nimport './tasks'\nimport './scenes'\nimport './delivery'\nimport './guide'\n")

# runtime 变换
rt = rt.replace("window.addEventListener('hashchange', applyRoute);",
  "/* 路由切换由 Vue router 驱动：router.afterEach -> window.protoGo(name) */\n"
  "window.protoGo = function(name){ window.__protoRoute = name; applyRoute(); };")
rt = rt.replace("const r = (location.hash.replace('#/','') || 'monitor');",
                "const r = (window.__protoRoute || location.hash.replace('#/','') || 'monitor');")
rt = rt.replace("function tick(){",
                "function tick(){ if(!document.getElementById('clock')) return;")

# 顶层立即执行语句 → 收进 window.initProto（Vue 挂载后调用）
init_snips = []
def grab(pattern):
    global rt
    m = re.search(pattern, rt, re.S)
    if not m: raise RuntimeError('pattern missing: ' + pattern[:40])
    init_snips.append(m.group(0))
    rt = rt[:m.start()] + rt[m.end():]

grab(r"(?m)^\(function\(\)\{ const walk=[\s\S]*?\}\)\(\);\n")
grab(r"(?m)^\(function\(\)\{ try\{ renderSpcTrees[\s\S]*?\}\)\(\);\n")
grab(r"if\(new URLSearchParams\(location\.search\)\.get\('login'\)==='0'\)\{[\s\S]*?\n\}")
grab(r"document\.querySelectorAll\('\.mask'\)[^\n]*\n")
grab(r"let _initTheme = 'dark';\ntry\{ _initTheme = localStorage\.getItem\('qs-theme'\) \|\| 'dark'; \}catch\(e\)\{\}\n[\s\S]*?applyRoute\(\);\n")
grab(r"aaAlertLoop\(\);\n")
grab(r"window\.addEventListener\('mousemove'[\s\S]*?aaInit\(\);?\s*$")

init_body = "\n".join(init_snips)
rt += "\n/* ============ Vue 壳挂载完成后的初始化入口 ============ */\nwindow.initProto = function(){\n" + init_body + "\n};\n"

hdr = ("/* ============================================================\n"
       " * 模舆机器人平台 · 原型运行时（移植自原型 v8.3 index.html 内联脚本）\n"
       " * 经典脚本加载（非模块）：顶层 function/数据引用挂全局，\n"
       " * 页面内 inline onclick 与 v-html 片段可直接调用。\n"
       " * mock 数据来自 src/mock/*（挂 window）；路由由 Vue 驱动 protoGo()。\n"
       " * ============================================================ */\n")
os.makedirs(os.path.join(DST, 'public/proto'), exist_ok=True)
io.open(os.path.join(DST, 'public/proto/runtime.js'), 'w', encoding='utf8').write(hdr + rt)
print('runtime.js', len(rt.splitlines()), 'lines')
print('DONE')
