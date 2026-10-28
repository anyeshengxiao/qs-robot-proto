# -*- coding: utf-8 -*-
"""打两个前端交接 zip：平台（qs-robot-hub 仓库 feat/proto-v828）+ 小程序（qs-miniapp-frontend）。"""
import os, zipfile

WS = r"C:\Users\52560\Documents\Kimi\Workspaces\机器人"
HUB = r"C:\Users\52560\Desktop\机器人\qs-robot-hub"
MINI = os.path.join(WS, 'qs-miniapp-frontend')

def add(zf, src, arc):
    zf.write(src, arc)

# ---------- 平台端 ----------
z1 = os.path.join(WS, 'qs-robot-hub-frontend-v828.zip')
if os.path.exists(z1): os.remove(z1)
TOP_FILES = ['.gitignore', 'index.html', 'package.json', 'package-lock.json',
             'tsconfig.app.json', 'tsconfig.json', 'tsconfig.node.json', 'vite.config.ts']
TOP_DIRS = ['docs', os.path.join('public','assets'), os.path.join('public','proto'), 'src']
cnt = 0
with zipfile.ZipFile(z1, 'w', zipfile.ZIP_DEFLATED) as zf:
    for f in TOP_FILES:
        p = os.path.join(HUB, f)
        if os.path.exists(p): add(zf, p, f); cnt += 1
    for d in TOP_DIRS:
        for root, dirs, files in os.walk(os.path.join(HUB, d)):
            dirs[:] = [x for x in dirs if x not in ('node_modules', '.git')]
            for f in files:
                p = os.path.join(root, f)
                add(zf, p, os.path.relpath(p, HUB)); cnt += 1
print('platform zip', cnt, 'files', round(os.path.getsize(z1)/1e6, 1), 'MB')

# ---------- 小程序 ----------
z2 = os.path.join(WS, 'qs-miniapp-frontend-v828.zip')
if os.path.exists(z2): os.remove(z2)
cnt = 0
with zipfile.ZipFile(z2, 'w', zipfile.ZIP_DEFLATED) as zf:
    for root, dirs, files in os.walk(MINI):
        dirs[:] = [x for x in dirs if x not in ('node_modules', 'dist', '.git')]
        for f in files:
            p = os.path.join(root, f)
            add(zf, p, os.path.join('qs-miniapp-frontend', os.path.relpath(p, MINI))); cnt += 1
print('miniapp zip', cnt, 'files', round(os.path.getsize(z2)/1e6, 1), 'MB')
