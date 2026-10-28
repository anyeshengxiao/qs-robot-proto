# -*- coding: utf-8 -*-
import io
p=r'C:\Users\52560\Documents\Kimi\Workspaces\机器人\qs-robot-proto\light\index.html'
s=io.open(p,encoding='utf-8').read()
n=0
def rep(a,b):
    global s,n
    assert s.count(a)==1,('anchor fail',a[:70],s.count(a))
    s=s.replace(a,b); n+=1

# 1) 默认提示音常量
rep("const BAT_CHG = 20, BAT_LOW = 35;",
    "const DOCK_ON_SAY = '已到达充电桩，开始充电，请勿移动。';   /* 上桩提示音（默认文案，可编辑） */\n"
    "const DOCK_OFF_SAY = '充电完成，已离开充电桩，可以正常执行任务。';   /* 退桩提示音（默认文案，可编辑） */\n"
    "const BAT_CHG = 20, BAT_LOW = 35;")

# 2) 接入向导 step3：充电桩下方增加两条提示音文本框（在待命区域之前）
rep('      <div class="form-row"><label>待命区域</label><select class="input" id="wzIdle">',
    '      <div class="form-row"><label>上桩提示音</label><input class="input" id="wzDockOn" value="${DOCK_ON_SAY}" placeholder="狗上桩充电时播报的提示语"></div>\n'
    '      <div class="form-row"><label>退桩提示音</label><input class="input" id="wzDockOff" value="${DOCK_OFF_SAY}" placeholder="狗退桩离开时播报的提示语"></div>\n'
    '      <div class="form-row"><label>待命区域</label><select class="input" id="wzIdle">')

# 3) 向导数据收集
rep("wzData.dock = g('wzDock'); } }",
    "wzData.dock = g('wzDock'); wzData.dockOn = g('wzDockOn'); wzData.dockOff = g('wzDockOff'); } }")

# 4) 注册完成写入设备数据
rep("ROBOT_DEV[key] = { console:(wzData.ctrl||'').trim(), fw:'—', sdk:'—' };",
    "ROBOT_DEV[key] = { console:(wzData.ctrl||'').trim(), fw:'—', sdk:'—', dockOn:wzData.dockOn||DOCK_ON_SAY, dockOff:wzData.dockOff||DOCK_OFF_SAY };")

# 5) 基础信息编辑表单：充电/待命区域下方增加两条提示音（编辑即存 ROBOT_DEV）
rep('id="cfgDockSt">${cfgDockOk?\'✓ 已对接\':\'未测试\'}</span></span></div>\n      <div class="form-row"><label>连接控制地址</label>',
    'id="cfgDockSt">${cfgDockOk?\'✓ 已对接\':\'未测试\'}</span></span></div>\n'
    '      <div class="form-row"><label>上桩提示音</label><input class="input" value="${dev.dockOn||DOCK_ON_SAY}" placeholder="狗上桩充电时播报的提示语" onchange="(ROBOT_DEV[curCfg]=ROBOT_DEV[curCfg]||{}).dockOn=this.value"></div>\n'
    '      <div class="form-row"><label>退桩提示音</label><input class="input" value="${dev.dockOff||DOCK_OFF_SAY}" placeholder="狗退桩离开时播报的提示语" onchange="(ROBOT_DEV[curCfg]=ROBOT_DEV[curCfg]||{}).dockOff=this.value"></div>\n'
    '      <div class="form-row"><label>连接控制地址</label>')

# 6) 基础信息查看态：充电/待命区域行后增加两条提示音展示行
rep('      <tr><td>电量</td><td><span class="batt">',
    '      <tr><td>上桩提示音</td><td style="font-size:11px">${dev.dockOn||DOCK_ON_SAY}</td></tr>\n'
    '      <tr><td>退桩提示音</td><td style="font-size:11px">${dev.dockOff||DOCK_OFF_SAY}</td></tr>\n'
    '      <tr><td>电量</td><td><span class="batt">')

io.open(p,'w',encoding='utf-8').write(s)
print('patched',n)
