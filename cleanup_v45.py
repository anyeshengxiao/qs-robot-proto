# -*- coding: utf-8 -*-
"""v4.5 清理：删除分期标签（α-x / 1.0-β 等）、演示说明文字、实现状态标注系统"""
import re, io, sys

P = 'index.html'
s = io.open(P, encoding='utf-8').read()
n0 = len(s)

# ① 删除所有 <i class="stag ...">...</i> 标注
s, n_stag = re.subn(r'\s*<i class="stag[^"]*"[^>]*>.*?</i>', '', s)

# ② 删除 实现状态标注栏 / 图例 / 关于本原型 弹窗 / toggleAnno 函数
s = s.replace('''<div id="anno-bar">
  <button id="annoBtn" onclick="toggleAnno()">📌 实现状态标注：关</button>
  <button onclick="document.getElementById('aboutMask').classList.add('on')">ℹ 关于本原型</button>
</div>
<div id="anno-legend">
  <p><span class="stag ok static">✅</span> 已实现 / 主路径可用</p>
  <p><span class="stag wip static">🚧</span> 半成品 / mock 数据 / 已知割裂</p>
  <p><span class="stag none static">❌</span> 占位 / 未启动（多为 1.0+ 范围）</p>
  <p style="margin-top:8px;border-top:1px solid var(--border);padding-top:8px">标注依据：qs-robot-hub 代码实况 + docs/ 技术文档 + V17 版本口径，供 α 版设计基线讨论。</p>
</div>

<!-- 关于 -->
<div class="mask" id="aboutMask">
  <div class="modal">
    <div class="modal-hd">ℹ 关于本原型<button class="x" onclick="closeMask('aboutMask')">✕</button></div>
    <div class="modal-bd" style="font-size:12px;line-height:1.9">
      <p><b style="color:var(--cy)">原型性质：</b>α 版原型 V2 —— 在 V1（全量交互设计）基础上按 8-18 确认的「三层信息架构」重构：泛化层 + 场景包 + 系统设置。</p>
      <p><b style="color:var(--cy)">导航结构（V3）：</b>顶栏 = 泛化层 4 项（监控中心 /monitor、任务中心 /tasks、空间管理 /space、接入中心 /config）+ 场景层 3 项平铺（🏢 物业巡检 /property、🏗 工地质安 /site、🧭 园区导览 /guide；&gt;3 时收敛为「场景工作台」下拉）+ 右上角 ⚙ 系统设置（/settings：菜单与场景配置 / 权限 / 网络策略默认 / 对接管理 / 主键冻结）。平台名「模舆机器人平台」，支持暗色/亮色双主题。空间评价、空间推荐下顶栏，可在系统设置中开启。</p>
      <p><b style="color:var(--cy)">狗—任务模型：</b>岗位能力集由搭载模组决定（如清星小智 = {巡检, 导引}），只能派能力集内任务；可绑定多场景任务但同时只执行单任务；排班制，可叫停插入临时任务（恢复策略操作员当场选：剩余点位不多→恢复继续 / 过半→顺延）；所有任务含临时任务必须命中预设模板。</p>
      <p><b style="color:var(--cy)">任务流水线：</b>① AI 任务识别（语义解析 + 岗位校验 + 模板命中）→ ② 路径规划（空间规则 + 历史经验 + 实时环境）→ ③ 三路径推荐（带语义理由 / 排除原因 / 经验标签：近 3 天 + 前一次执行情况，标注临时异常如渣土堆遮挡）→ ④ 确认下发 → ⑤ 数据回流。点位采集要求（停留/朝向/拍照数/点云）逐项可配。</p>
      <p><b style="color:var(--cy)">网络模式：</b>在线 / 弱网 / 离线 / 自动，逐机设置（面向复杂长程任务），离线机仅执行本地队列、拒收云端指令。</p>
      <p class="muted">素材来源：proto_shots/ 真实运行截图裁切（3D 视口 / 导航地图 / Logo）。</p>
    </div>
    <div class="modal-ft"><button class="btn" onclick="closeMask('aboutMask')">知道了</button></div>
  </div>
</div>
''', '')
s, n_fn = re.subn(r'let annoOn = false;\nfunction toggleAnno\(\)\{[\s\S]*?\n\}\n', '', s)

# ③ 显式文案替换对
pairs = [
 ('<title>模舆机器人平台 · α 版原型 V3（三层架构 + 紫调双主题）</title>', '<title>模舆机器人平台</title>'),
 ('    <div class="lg-foot">α 演示版 · 复兴岛项目 · 建议使用 Chrome 浏览器</div>\n', ''),
 ('语音输入：语音识别（ASR）转写 + POI 级语义解析，α-3 能力（B5 引擎层）', '语音输入：语音识别（ASR）转写 + POI 级语义解析'),
 ('临时任务（NL 指令 α-3）', '临时任务（NL 指令）'),
 ('含走楼梯跨层段（α-1）· 梯控乘梯 α-3', '跨层方式可选：梯控乘梯 / 走楼梯'),
 ('<span class="bd badge b-warn">α-2</span>', ''),
 ('<div>B4 不直连机器人 · 空间规则 <b style="color:#fbbf24">1.0-β</b></div>', '<div>B4 不直连机器人 · 空间规则（禁行区 / 围栏）</div>'),
 ('点云比对与空间更新链路（α-2）：机器人回传点云', '点云比对与空间更新链路：机器人回传点云'),
 ('A7 单版发布（自动化 1.0-RC）', 'A7 单版发布'),
 ('（α-0 平台配置口径；此页为弱入口，不出现在主导航）', '（此页为弱入口，不出现在主导航）'),
 ('<span class="badge b-warn" style="margin-left:auto">α-3 联调中</span>', '<span class="badge b-warn" style="margin-left:auto">联调中</span>'),
 ('<span class="badge b-ok" style="margin-left:auto">α-2 已对接</span>', '<span class="badge b-ok" style="margin-left:auto">已对接</span>'),
 ('宇树 Go2（α 期单一型号）', '宇树 Go2'),
 ('其他型号（1.0-RC 经模组 C 接入）', '其他型号（经模组 C 接入）'),
 ('⚙ 平台配置（α-0 · 主键与开放 API 已冻结）', '⚙ 平台配置（主键与开放 API 已冻结）'),
 ('（规则引擎为 1.0-β 内容，当前为展示态）', '（规则引擎对接中，当前为展示态）'),
 ('按 V17 口径：α-2 阶段底图更新为「点云比对 → 手动配准 → <b style="color:var(--warn)">人工确认</b>」单版底图；版本管理 / 历史追溯 / 多机同步为 1.0 内容。',
  '底图更新链路：点云比对 → 手动配准 → <b style="color:var(--warn)">人工确认</b> → 单版发布；版本管理 / 历史追溯 / 多机同步为后续版本内容。'),
 ('② 转空间数据底座配准（α 期手动）', '② 转空间数据底座配准（手动）'),
 ('title="语音输入（ASR · α-3）"', 'title="语音输入"'),
 ("toast('语音输入（ASR 实时转写）为 α-3 能力，α 版请先用文字～')", "toast('语音输入（ASR 实时转写）接入中，请先用文字～')"),
 ('梯控乘梯 <span class="badge b-warn" style="font-size:9px">α-3</span>', '梯控乘梯'),
 ('（多机不串单，α 里程碑③）', '（多机不串单）'),
 ('梯控对接（云际 · α-3 · 9 月联调 J3）', '梯控对接（云际 · 联调中）'),
 ('（α-1 多层作业兜底）', '（多层作业兜底）'),
 ('生成巡检报告：M7 报告引擎 α 期为基础版（结构化初稿 Word/PDF）', '生成巡检报告：M7 报告引擎输出结构化初稿（Word / PDF）'),
 ('发起工单：轻量工单闭环（隐患→派单→整改→复查→销项）为 1.0-β 内容', '发起工单：轻量工单闭环（隐患→派单→整改→复查→销项）'),
 ('底图模型 vs 回传点云差异高亮（α-2 手动配准链路）', '底图模型 vs 回传点云差异高亮（手动配准链路）'),
 ('送达段 · 约 142 m · 含乘梯段 α-3', '送达段 · 约 142 m · 含乘梯段'),
 ('⇅ 路线含楼梯间点位：自动生成「走楼梯跨层段」（α-1 多层作业）；梯控乘梯（α-3）联调后可在编排中选择乘梯段。',
  '⇅ 路线含楼梯间点位：跨层方式可选择「梯控乘梯」或「走楼梯」。'),
 ('已同步归档（α 演示为占位预览）· 类型：', '已同步归档 · 类型：'),
 ('已加入报告素材（M7 报告引擎 · α 基础版）', '已加入报告素材（M7 报告引擎）'),
 ('支持版本管理（草稿 → 审核 → 发布 → 可回滚），TTS 语音合成 α-3。', '支持版本管理（草稿 → 审核 → 发布 → 可回滚）与 TTS 语音合成。'),
 ('<span class="extra">α 演示 · 大模型自由问答 1.0</span>', '<span class="extra">固定资料库问答</span>'),
 ('识别结果空间化与人工复核（α-2）：云端识别', '识别结果空间化与人工复核：云端识别'),
 ('（流程模板由场景插件定义；泛化工单框架由平台提供，完整版 1.0-β）', '（流程模板由场景插件定义，泛化工单框架由平台提供）'),
 ('（整改→复查→销项流程为 1.0-β 内容）', '（整改→复查→销项）'),
 ('样本回流用于模型优化（1.0-β）', '样本回流用于模型优化'),
 ('（α 期仅支持固定资料库问答）', '（当前仅支持固定资料库问答）'),
]
miss = []
for old, new in pairs:
    if old in s: s = s.replace(old, new)
    else: miss.append(old[:30])

io.open(P, 'w', encoding='utf-8', newline='').write(s)
print('stag removed:', n_stag, '| toggleAnno removed:', n_fn, '| bytes:', n0, '->', len(s))
print('MISS:', miss if miss else 'none')
