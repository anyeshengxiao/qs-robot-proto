# -*- coding: utf-8 -*-
"""从 miniapp.html（配送小程序 v8.28）生成独立 Vue3 H5 前端工程 qs-miniapp-frontend。
架构与平台版一致：Vue 壳 + 原型 runtime.js + mock 挂 window。"""
import re, io, os, shutil

SRC = r"C:\Users\52560\Documents\Kimi\Workspaces\机器人\qs-robot-proto\miniapp.html"
ASSETS = r"C:\Users\52560\Documents\Kimi\Workspaces\机器人\qs-robot-proto\assets"
DST = r"C:\Users\52560\Documents\Kimi\Workspaces\机器人\qs-miniapp-frontend"

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

def fix(p):
    return p.replace('src="assets/', 'src="/assets/').replace("url(assets/", "url(/assets/")

def W(rel, content):
    path = os.path.join(DST, rel.replace('/', os.sep))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    io.open(path, 'w', encoding='utf8').write(content)
    print('write', rel)

def write_sfc(rel, html):
    W(rel, "<template>\n" + fix(html) + "\n</template>\n")

# ---------- 页面 ----------
pages = {'OrderView':'pg-order','TrackView':'pg-track','OrdersView':'pg-orders','DetailView':'pg-detail'}
ranges = []
for name, pid in pages.items():
    ln = find_line(r'id="%s"' % pid)
    html, end = cut_div(ln)
    write_sfc('src/views/%s.vue' % name, html)
    ranges.append((ln, end))
# 弹窗
over = []
for mid in ['lgMask','authMask','cfMask','toast']:
    ln = find_line(r'id="%s"' % mid)
    html, end = cut_div(ln)
    over.append(html)
write_sfc('src/components/Overlays.vue', "\n".join(over))
# tabbar
tb_ln = find_line(r'<div class="tabbar">')
tb_html, _ = cut_div(tb_ln)

# ---------- App.vue ----------
app = """<template>
  <div class="phone">
    <div class="back" id="backBtn" onclick="goTab('orders')">‹</div>
    <div class="hd">
      <div class="t1"><span class="dog"><img src="/assets/dog_head.svg" alt="模舆"></span>模舆配送</div>
      <div class="t2">龙岗AI · 机器狗即时配送</div>
    </div>
    <OrderView />
    <TrackView />
    <OrdersView />
    <DetailView />
%s
    <Overlays />
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import OrderView from './views/OrderView.vue'
import TrackView from './views/TrackView.vue'
import OrdersView from './views/OrdersView.vue'
import DetailView from './views/DetailView.vue'
import Overlays from './components/Overlays.vue'
onMounted(() => { (window as any).initProto?.() })
</script>
""" % fix(tb_html).replace('\n', '\n    ')
W('src/App.vue', app)

# ---------- 样式 ----------
css_a, css_b = find_line(r'<style>'), find_line(r'</style>')
W('src/styles/proto.css', "\n".join(lines[css_a:css_b-1]) + "\n")

# ---------- 运行时 ----------
rt_a, rt_b = find_line(r'^<script>$'), find_line(r'</script>')
rt = "\n".join(lines[rt_a:rt_b-1])

MOCK = ['SHOPS','POINTS','ORDERS','CHS','STEPS']
def cut_const(text, name):
    m = re.search(r'(?m)^const %s ?=' % name, text)
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
    raise RuntimeError('unterminated %s' % name)

blocks = {}
for n in MOCK:
    b, rt = cut_const(rt, n); blocks[n] = b

HDR = "/**\n * 配送小程序 v8.28 mock 数据（自动生成）\n * 商铺 / 送达点 / 订单与机器人平台同源——接真实 API 时保持字段签名不变。\n */\n/* eslint-disable */\n// @ts-nocheck\n"
parts = [HDR]
for n in MOCK:
    parts.append(re.sub(r'^const %s ?=' % n, 'const %s: any =' % n, blocks[n]))
parts.append("Object.assign(window as any, { %s })\n" % ", ".join(MOCK))
W('src/mock/data.ts', "\n".join(parts))

init_snips = []
def grab(pattern):
    global rt
    m = re.search(pattern, rt, re.S)
    if not m: raise RuntimeError('pattern missing: ' + pattern[:50])
    init_snips.append(m.group(0))
    rt = rt[:m.start()] + rt[m.end():]

grab(r"if\(new URLSearchParams\(location\.search\)\.get\('logout'\)\)[^\n]*\n")
grab(r"if\(MY_ACCT\)[^\n]*\nelse[^\n]*\n")
grab(r"renderAcct\(\);\n")
grab(r"document\.getElementById\('shops'\)\.innerHTML=[\s\S]*?\.join\(''\);\n")
grab(r"document\.getElementById\('ptags'\)\.innerHTML=[\s\S]*?\.join\(''\);\n")
grab(r"document\.getElementById\('chs'\)\.innerHTML=[\s\S]*?\.join\(''\);\n")
grab(r"renderFlow\('ing'\);\ndocument\.getElementById\('trackTl'\)\.innerHTML=[\s\S]*?\.join\(''\);\n")
grab(r"(?m)^renderOrders\(''\);\n")
grab(r"const _h=[^\n]*\nif\(\['order','track','orders','detail'\]\.includes\(_h\)\)goTab\(_h\);\n")

rt += "\n/* ============ Vue 壳挂载完成后的初始化入口 ============ */\nwindow.initProto = function(){\n" + "\n".join(init_snips) + "\n};\n"
hdr = ("/* ============================================================\n"
       " * 模舆配送小程序 · 原型运行时（移植自 miniapp.html v8.28 内联脚本）\n"
       " * 经典脚本：顶层函数挂 window，页面 inline onclick 直接可用。\n"
       " * mock 数据来自 src/mock/data.ts（挂 window）。\n"
       " * ============================================================ */\n")
W('public/proto/runtime.js', hdr + rt)

# ---------- 工程文件 ----------
W('package.json', """{
  "name": "qs-miniapp-frontend",
  "version": "8.28.0",
  "private": true,
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "vue": "^3.5.13"
  },
  "devDependencies": {
    "@vitejs/plugin-vue": "^5.2.1",
    "typescript": "^5.7.3",
    "vite": "^6.0.7"
  }
}
""")
W('vite.config.ts', """import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: { host: true }
})
""")
W('tsconfig.json', """{
  "compilerOptions": {
    "target": "ES2020",
    "module": "ESNext",
    "moduleResolution": "bundler",
    "strict": false,
    "jsx": "preserve",
    "types": ["vite/client"],
    "skipLibCheck": true
  },
  "include": ["src/**/*.ts", "src/**/*.vue"]
}
""")
W('index.html', """<!doctype html>
<html lang="zh-CN">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no" />
    <title>模舆配送 · 龙岗AI</title>
    <!-- 原型运行时：经典脚本，顶层函数挂全局供页面 inline 交互调用 -->
    <script src="/proto/runtime.js"></script>
  </head>
  <body>
    <div id="app"></div>
    <script type="module" src="/src/main.ts"></script>
  </body>
</html>
""")
W('src/main.ts', """import { createApp } from 'vue'
import App from './App.vue'
import './styles/proto.css'
import './mock/data'   // mock 挂 window，必须先于 initProto 调用

createApp(App).mount('#app')
""")
W('src/shims-vue.d.ts', """declare module '*.vue' {
  import type { DefineComponent } from 'vue'
  const c: DefineComponent<{}, {}, any>
  export default c
}
""")
# 素材
os.makedirs(os.path.join(DST, 'public/assets'), exist_ok=True)
shutil.copy2(os.path.join(ASSETS, 'dog_head.svg'), os.path.join(DST, 'public/assets/dog_head.svg'))
print('asset dog_head.svg')
print('DONE')
