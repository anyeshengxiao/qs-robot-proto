# -*- coding: utf-8 -*-
"""从原型 light/index.html（平台版 v8.28 · 深浅双主题）生成 Vue 工程文件：
页面骨架 SFC + proto.css + runtime.js + mock 数据模块。
沿用 proto-v8 的「Vue 壳 + 原型运行时」混合架构，壳（App.vue/router/main.ts）不动。"""
import re, io, os, shutil

SRC = r"C:\Users\52560\Documents\Kimi\Workspaces\机器人\qs-robot-proto\light\index.html"
ASSETS = r"C:\Users\52560\Documents\Kimi\Workspaces\机器人\qs-robot-proto\assets"
DST = r"C:\Users\52560\Desktop\机器人\qs-robot-hub"

s = io.open(SRC, encoding='utf8').read()
lines = s.splitlines()

def find_line(pat, start=1):
    rx = re.compile(pat)
    for i in range(start-1, len(lines)):
        if rx.search(lines[i]): return i+1
    raise RuntimeError('not found: '+pat)

def cut_div(start_line):
    depth = 0; out = []
    for i in range(start_line-1, len(lines)):
        ln = lines[i]; out.append(ln)
        depth += len(re.findall(r'<div\b', ln)) - ln.count('</div>')
        if depth == 0: return "\n".join(out), i+1
    raise RuntimeError('unbalanced from %d' % start_line)

def fix(p):  # 资源路径：light/ 子目录相对路径 → Vue public 绝对路径
    return p.replace('../assets/', '/assets/')

# ---------- 1. 样式 ----------
css_a, css_b = find_line(r'<style>'), find_line(r'</style>')
css = fix("\n".join(lines[css_a:css_b-1]))
css_path = os.path.join(DST, 'src/styles/proto.css')
io.open(css_path, 'w', encoding='utf8').write(css + "\n")
print('proto.css', css_b-css_a-1, 'lines')

# ---------- 2. 页面骨架 ----------
L = {
 'loginMask':  find_line(r'<div id="loginMask">'),
 'topbar':     find_line(r'<div id="topbar">'),
 'pg-monitor': find_line(r'<div id="pg-monitor"'),
 'pg-config':  find_line(r'<div id="pg-config"'),
 'pg-tasks':   find_line(r'<div id="pg-tasks"'),
 'pg-space':   find_line(r'<div id="pg-space"'),
 'pg-evaluate':find_line(r'<div id="pg-evaluate"'),
 'pg-recommend':find_line(r'<div id="pg-recommend"'),
 'pg-settings':find_line(r'<div id="pg-settings"'),
 'aiAgent':    find_line(r'<div id="aiAgent">'),
}
scenes = {k: find_line(r'<div id="%s"' % k) for k in ['pg-property','pg-site','pg-guide','pg-delivery']}
login_script_a = find_line(r'^<script>$', L['loginMask'])
login_script_b = find_line(r'</script>', login_script_a)

def write_sfc(rel, html):
    path = os.path.join(DST, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    io.open(path, 'w', encoding='utf8').write("<template>\n" + fix(html) + "\n</template>\n")
    print('SFC', rel)

mapping = [('LoginView','loginMask'),('TopBar','topbar'),('MonitorView','pg-monitor'),
           ('AccessView','pg-config'),('TasksView','pg-tasks'),('SpaceView','pg-space'),
           ('EvaluateView','pg-evaluate'),('RecommendView','pg-recommend'),('SettingsView','pg-settings')]
page_ranges = []
for name, key in mapping:
    html, end = cut_div(L[key])
    if name == 'TopBar':
        write_sfc('src/components/layout/TopBar.vue', html)
    else:
        write_sfc('src/views/%s/index.vue' % name, html)
    page_ranges.append((L[key], end))
for pid, ln in scenes.items():
    write_sfc('src/views/%s/index.vue' % {'pg-property':'PropertyView','pg-site':'SiteView','pg-guide':'GuideView','pg-delivery':'DeliveryView'}[pid], lines[ln-1])
    page_ranges.append((ln, ln))
ai_html, ai_end = cut_div(L['aiAgent'])
write_sfc('src/components/layout/AiAgent.vue', ai_html)

def in_page(ln): return any(a <= ln <= b for a, b in page_ranges)
over, ln = [], L['topbar']
_, top_end = cut_div(L['topbar'])
ln = top_end + 1
while ln < L['aiAgent']:
    if in_page(ln): ln += 1; continue
    l = lines[ln-1]
    if re.match(r'<script', l):  # 登录页内联脚本，单独处理
        ln = find_line(r'</script>', ln) + 1; continue
    if l.startswith('<div class="mask"') or l.startswith('<div class="drawer'):
        blk, e = cut_div(ln); over.append(blk); ln = e + 1
    else:
        ln += 1
write_sfc('src/components/layout/Overlays.vue', "\n".join(over))
print('overlays', len(over))

# ---------- 3. 运行时 ----------
rt_a = find_line(r'^<script>$', find_line(r'xiaoyu_b64'))
rt_b = find_line(r'</script>', rt_a)
rt = fix("\n".join(lines[rt_a:rt_b-1]))
# 登录页小脚本并入运行时
lg = "\n".join(lines[login_script_a:login_script_b-1])
lg = lg.replace("lg9Fit();addEventListener('resize',lg9Fit);", "addEventListener('resize',lg9Fit);")
rt = lg + "\n" + rt

MOCK = {
 'robots.ts':   ['ROBOTS','ROBOT_DEV','BAT_CHG','DOORS','LIFTS','CHARGES','LAST_KNOWN','ROBOT_EXT','API_MODS','CFG_TASKS','API_ST','REG_RES','PC_MAPS','PCV_DOTS','POST_TASKS','MOD_LOGS','WZ_STEPS','MN_POS','NET_TX'],
 'space.ts':    ['TREE','ATTRS','SP_META','SP_BOX','SP_ROOMS','SP_ISSUES','ANOMS','ANOM_BY_TASK','SP_TREE','SP_NODES','SP_FL_MAP','SPC_TAGS','SPC_DEVS','SP_LV_KIDS','NM_TYPES','SC_DEVS','FL_Z','ENV_CFG','PATHS','TJ_PATH'],
 'tasks.ts':    ['TASKS','CAT_TX','TST','HST','BIZ_TX','BNAMES','OP_CONF','CMD_HIST','TE_SPACES','TE_POOL','TE_ACT_POOL','MT_POINTS','POINTS'],
 'scenes.ts':   ['SCENE_KEYS','SCENES','SCENE_TABS','ALGO_CTYPE','ALGO_CFG_DFT','SCENE_NAMES','BIND_SCENES','MENU_L1','MENU_L2','MENU_PERM','PROJECTS','USERS'],
 'delivery.ts': ['DL_PICKS','DL_DROPS','DL_VOICE','DL_ACTS','DL_RECS'],
 'guide.ts':    ['GUIDE_FAQ','TOUR_PTS'],
}
all_names = {n for v in MOCK.values() for n in v}

def cut_const(text, name):
    m = re.search(r'(?m)^const %s = ' % name, text)
    if not m: raise RuntimeError('const %s not found' % name)
    i = m.start(); depth = 0; j = m.end(); in_str = None; esc = False
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
                k = j+1
                while k < len(text) and text[k] == '\n': k += 1
                return text[i:j+1], text[:i] + text[k:]
        j += 1
    raise RuntimeError('unterminated const %s' % name)

blocks = {}
for n in sorted(all_names):
    b, rt = cut_const(rt, n); blocks[n] = b

HDR = "/**\n * 平台版 v8.28 mock 数据（自动生成，勿手改逻辑）\n * 运行时装载：赋值到 window 供 public/proto/runtime.js 使用；\n * 后续接真实 API 时，service 层改为读接口、保持字段签名不变。\n */\n/* eslint-disable */\n// @ts-nocheck\n"
os.makedirs(os.path.join(DST, 'src/mock'), exist_ok=True)
for fn, names in MOCK.items():
    parts = [HDR]
    for n in names:
        parts.append(re.sub(r'^const %s = ' % n, 'const %s: any = ' % n, blocks[n]))
    parts.append("Object.assign(window as any, { %s })\n" % ", ".join(names))
    io.open(os.path.join(DST, 'src/mock', fn), 'w', encoding='utf8').write("\n".join(parts))
    print('mock', fn)

# 运行时变换
assert "window.addEventListener('hashchange', applyRoute);" in rt
rt = rt.replace("window.addEventListener('hashchange', applyRoute);",
  "/* 路由切换由 Vue router 驱动：router.afterEach -> window.protoGo(name) */\n"
  "window.protoGo = function(name){ window.__protoRoute = name; applyRoute(); };")
assert "const r = (location.hash.replace('#/','') || 'monitor');" in rt
rt = rt.replace("const r = (location.hash.replace('#/','') || 'monitor');",
                "const r = (window.__protoRoute || location.hash.replace('#/','') || 'monitor');")
rt = rt.replace("function tick(){", "function tick(){ if(!document.getElementById('clock')) return;")

# 原型源码遗留：openUpdateModal 顶层重复定义（浏览器经典脚本后者覆盖前者；
# ESM 解析会报重复声明，把前一个死定义改名消除，运行时行为不变——浏览器本就只用后一个）
_dup = 'function openUpdateModal(title){'
_i1 = rt.find(_dup); _i2 = rt.find(_dup, _i1+1)
assert _i1 > 0 and _i2 > 0
rt = rt[:_i1] + 'function openUpdateModal_legacy(title){' + rt[_i1+len(_dup):]

init_snips = []
def grab(pattern):
    global rt
    m = re.search(pattern, rt, re.S)
    if not m: raise RuntimeError('pattern missing: ' + pattern[:50])
    init_snips.append(m.group(0))
    rt = rt[:m.start()] + rt[m.end():]

grab(r"(?m)^\(function\(\)\{ const walk=[\s\S]*?\}\)\(\);\n")
grab(r"(?m)^\(function\(\)\{ try\{ renderSpcTrees[\s\S]*?\}\)\(\);\n")
grab(r"if\(new URLSearchParams\(location\.search\)\.get\('login'\)==='0'\)\{[\s\S]*?\n\}\n")
grab(r"document\.querySelectorAll\('\.mask'\)[^\n]*\n")
grab(r"let _initTheme = 'dark';[\s\S]*?applyRoute\(\);\n")
grab(r"(?m)^aaAlertLoop\(\);\n")
grab(r"window\.addEventListener\('mousemove'[\s\S]*$")

init_body = "lg9Fit();\n" + "\n".join(init_snips)
rt += "\n/* ============ Vue 壳挂载完成后的初始化入口 ============ */\nwindow.initProto = function(){\n" + init_body + "\n};\n"

hdr = ("/* ============================================================\n"
       " * 模舆具身智能管理平台 · 原型运行时（移植自平台版 v8.28 light/index.html 内联脚本）\n"
       " * 经典脚本加载（非模块）：顶层 function/数据引用挂全局，\n"
       " * 页面内 inline onclick 与 v-html 片段可直接调用。\n"
       " * mock 数据来自 src/mock/*（挂 window）；路由由 Vue 驱动 protoGo()。\n"
       " * ============================================================ */\n")
os.makedirs(os.path.join(DST, 'public/proto'), exist_ok=True)
io.open(os.path.join(DST, 'public/proto/runtime.js'), 'w', encoding='utf8').write(hdr + rt)
print('runtime.js', len(rt.splitlines()), 'lines')

# ---------- 4. 素材同步 ----------
pub = os.path.join(DST, 'public/assets')
os.makedirs(pub, exist_ok=True)
for f in os.listdir(ASSETS):
    if f.endswith(('.png','.svg','.jpg','.js')) and f != 'rebuild_glb.py':
        shutil.copy2(os.path.join(ASSETS, f), os.path.join(pub, f))
        print('asset', f)

# ---------- 5. 站点标题 ----------
idx = os.path.join(DST, 'index.html')
h = io.open(idx, encoding='utf8').read()
h = h.replace('模舆机器人平台 · SpaceMor Robot Platform', '模舆具身智能管理平台 · SpaceMor Embodied AI Platform')
io.open(idx, 'w', encoding='utf8').write(h)
print('DONE')
