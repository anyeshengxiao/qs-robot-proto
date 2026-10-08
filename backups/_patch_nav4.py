# -*- coding: utf-8 -*-
import io

RESIZE_JS = '''/* 小舆对话框大小拖拽（左上角手柄） */
(function(){
  let sx, sy, sw, sh, rs = false;
  document.addEventListener('mousedown', e=>{
    if(!e.target.closest('#aaRs')) return;
    const p = document.getElementById('aaPanel');
    rs = true; sx = e.clientX; sy = e.clientY; sw = p.offsetWidth; sh = p.offsetHeight;
    e.preventDefault(); e.stopPropagation();
  });
  document.addEventListener('mousemove', e=>{ if(!rs) return;
    const p = document.getElementById('aaPanel');
    p.style.width  = Math.max(300, Math.min(640, sw + (sx - e.clientX))) + 'px';
    p.style.height = Math.max(340, Math.min(innerHeight * 0.86, sh + (sy - e.clientY))) + 'px';
  });
  document.addEventListener('mouseup', ()=>{ rs = false; });
})();
function aaDock(){'''

for path in ['index.html', 'light/index.html']:
    s = io.open(path, encoding='utf-8').read()

    # A1 小舆 panel CSS 加 relative + 手柄样式
    old = '.aa-panel{display:none;flex-direction:column;'
    assert s.count(old) == 1, (path, 'css1')
    s = s.replace(old, '.aa-rs{position:absolute;left:-6px;top:-6px;width:16px;height:16px;cursor:nwse-resize;z-index:6;border-radius:3px;background:repeating-linear-gradient(135deg,transparent 0 3px,rgba(120,190,255,.6) 3px 4.5px);opacity:.85}\n.aa-panel{display:none;flex-direction:column;position:relative;')

    # A2 手柄 HTML
    old = '<div class="aa-panel" id="aaPanel">'
    assert s.count(old) == 1, (path, 'html1')
    s = s.replace(old, '<div class="aa-panel" id="aaPanel">\n    <div class="aa-rs" id="aaRs" title="拖拽调整对话框大小"></div>')

    # A3 resize JS（挂在 aaDock 前）
    old = 'function aaDock(){'
    assert s.count(old) == 1, (path, 'js1')
    s = s.replace(old, RESIZE_JS)

    # B1 弹窗标题
    old = '🧩 点云 · BIM 合模情况'
    assert s.count(old) == 1, (path, 'title')
    s = s.replace(old, '🧩 点云 · BIM 模型配准')

    # B2 整体合模视图去掉解释
    old = '<b style="font-size:11px;color:var(--tx-hi)">🏢 整体合模视图</b><br><span class="muted" style="font-size:10px">整单体 · 多层 BIM + 全部点云</span>'
    assert s.count(old) == 1, (path, 'b2')
    s = s.replace(old, '<b style="font-size:11px;color:var(--tx-hi)">🏢 整体合模视图</b>')

    # B3 配对列表头
    old = "配对列表（${pairs.length}）· 点击看 1v1 合模"
    assert s.count(old) == 1, (path, 'b3')
    s = s.replace(old, "配准列表（${pairs.length}）")

    # B4 徽标：已配准 → 配准（弹窗内 3 处）
    n = s.count("${m.reg ? '已配准' : '未配准'}")
    assert n == 3, (path, 'b4', n)
    s = s.replace("${m.reg ? '已配准' : '未配准'}", "${m.reg ? '配准' : '未配准'}")

    # B5 未配对区徽标统一为 未配准
    old = '<span class="badge b-warn" style="font-size:9px">点云 · 未选 BIM</span>'
    assert s.count(old) == 1, (path, 'b5a')
    s = s.replace(old, '<span class="badge b-warn" style="font-size:9px">未配准</span>')
    old = '<span class="badge b-dim" style="font-size:9px">BIM · 无点云</span>'
    assert s.count(old) == 1, (path, 'b5b')
    s = s.replace(old, '<span class="badge b-dim" style="font-size:9px">未配准</span>')

    # B6 右侧整体视图去掉解释文字
    old = '<div class="muted" style="font-size:10px;margin-top:4px">多层 BIM 与全部点云同窗叠加；青色为 BIM、品红为点云，偏移层标注「未配准」</div>'
    assert s.count(old) == 1, (path, 'b6')
    s = s.replace(old, '')

    # B7 整层视图：去掉按图未配准标注，改到 B 层标注
    old = """      if(!m.reg) g += `<text x="${x + 236}" y="${y - 7}" text-anchor="end" font-size="8" fill="#fbbf24">未配准</text>`;\n"""
    assert s.count(old) == 1, (path, 'b7a', s.count(old))
    s = s.replace(old, '')
    old = """      <text x="${x - 8}" y="${y - 7}" text-anchor="end" font-size="10" fill="#6b7a90">${f}</text>`;"""
    assert s.count(old) == 1, (path, 'b7b')
    s = s.replace(old, """      <text x="${x - 8}" y="${y - 7}" text-anchor="end" font-size="10" fill="#6b7a90">${f}</text>`;
    if(f.charAt(0) === 'B') g += `<text x="${x + 236}" y="${y - 7}" text-anchor="end" font-size="8" fill="#fbbf24">未配准</text>`;""")

    # B8 三条默认点云全部已配准
    old = "reg:id==='go1'"
    assert s.count(old) == 1, (path, 'b8a')
    s = s.replace(old, 'reg:true')
    old = "reg:false, bim:bi('主楼-2F')"
    assert s.count(old) == 1, (path, 'b8b')
    s = s.replace(old, "reg:true, bim:bi('主楼-2F')")
    old = "reg:false, bim:bi('主楼-3F')"
    assert s.count(old) == 1, (path, 'b8c')
    s = s.replace(old, "reg:true, bim:bi('主楼-3F')")

    # C 浅色底适配：视口底色随主题
    old = 'background:rgba(4,8,16,.5);border-radius:6px'
    n = s.count(old)
    assert n == 2, (path, 'c1', n)
    s = s.replace(old, "background:${thV('rgba(4,8,16,.5)','#e9edf7')};border-radius:6px")
    old = '/* 查看配准：'
    assert s.count(old) == 1, (path, 'c2')
    s = s.replace(old, "function thV(d, l){ return document.documentElement.dataset.theme === 'light' ? l : d; }\n/* 查看配准：")

    io.open(path, 'w', encoding='utf-8').write(s)
    print(path, 'patched all')
