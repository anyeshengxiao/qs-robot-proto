# -*- coding: utf-8 -*-
"""v8.7 补丁：小程序退出登录入口 / 通行控制页左右比例+单体楼层双下拉"""
import io, sys

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

# ============ miniapp.html ============
m_subs = [
# 1) 我的订单页顶部加账号条 + 退出登录
("""  <div class="page" id="pg-orders">
    <div class="filters" id="ordFilters">""",
 """  <div class="page" id="pg-orders">
    <div style="display:flex;justify-content:space-between;align-items:center;padding:0 2px 10px;font-size:11px;color:var(--tx2)">
      <span>当前账号：<b id="acctTx" style="color:var(--tx)"></b></span>
      <span style="color:var(--pri);cursor:pointer" onclick="logout()">退出登录</span>
    </div>
    <div class="filters" id="ordFilters">"""),
# 2) 登录 JS：支持 ?logout=1 + logout() + 账号回显
("""const MY_ACCT = localStorage.getItem('my-user') || '';
if(MY_ACCT) document.getElementById('lgMask').classList.remove('on');
else document.getElementById('lgMask').classList.add('on');""",
 """if(new URLSearchParams(location.search).get('logout')) localStorage.removeItem('my-user');
const MY_ACCT = localStorage.getItem('my-user') || '';
if(MY_ACCT) document.getElementById('lgMask').classList.remove('on');
else document.getElementById('lgMask').classList.add('on');
document.getElementById('acctTx').textContent = myAcct();
function logout(){ localStorage.removeItem('my-user'); location.reload(); }"""),
]
patch('miniapp.html', m_subs)

# ============ index.html ============
i_subs = [
# 3) 通行控制页：左窄右宽
("""<div class="ttab" id="sb-pass" style="flex:1;display:none;grid-template-columns:1fr 480px;gap:12px;padding:12px 18px;min-height:0">""",
 """<div class="ttab" id="sb-pass" style="flex:1;display:none;grid-template-columns:minmax(340px,5fr) 7fr;gap:12px;padding:12px 18px;min-height:0">"""),
# 4) 地图上方改 单体 + 楼层 双下拉
("""<div style="display:flex;gap:8px;align-items:center;margin-bottom:8px"><span class="muted" style="font-size:10px">单体 / 楼层</span><select class="input" id="spPassFl" style="width:auto;padding:3px 8px;font-size:11px" onchange="spPassMapRender()"></select></div>""",
 """<div style="display:flex;gap:8px;align-items:center;margin-bottom:8px"><span class="muted" style="font-size:10px">单体</span><select class="input" id="spPassBd" style="width:auto;padding:3px 10px;font-size:11px" onchange="spPassMapRender()"></select><span class="muted" style="font-size:10px">楼层</span><select class="input" id="spPassFl" style="width:auto;padding:3px 10px;font-size:11px" onchange="spPassMapRender()"></select></div>"""),
# 5) spPassMapRender 重写：单体/楼层联动，空层给提示
("""function spPassMapRender(){
  const sel = document.getElementById('spPassFl'), box = document.getElementById('spPassMap');
  if(!sel || !box) return;
  if(!sel.options.length){
    Object.keys(SP_FL_MAP).forEach(k=>{
      if(DOORS.some(d=>d.fl===k) || LIFTS.some(l=>l.fl===k)){
        const bf = SP_FL_MAP[k];
        sel.insertAdjacentHTML('beforeend', `<option value="${k}">${bf[0]} · ${bf[1]}</option>`);
      }
    });
    sel.value = 'main-1f';
  }
  const flKey = sel.value || 'main-1f';
  box.innerHTML = fpSvg(true) +""",
 """function spPassMapRender(){
  const bdSel = document.getElementById('spPassBd'), sel = document.getElementById('spPassFl'), box = document.getElementById('spPassMap');
  if(!bdSel || !sel || !box) return;
  if(!bdSel.options.length){
    const bds = [...new Set(Object.values(SP_FL_MAP).map(bf=>bf[0]))];
    bdSel.innerHTML = bds.map(b=>`<option>${b}</option>`).join('');
    bdSel.value = '主楼';
  }
  const bd = bdSel.value;
  const seen = {}, fls = [];
  Object.keys(SP_FL_MAP).forEach(k=>{ const bf = SP_FL_MAP[k]; if(bf[0]===bd && !seen[bf[1]]){ seen[bf[1]]=1; fls.push(k); } });
  const oldFl = sel.value;
  sel.innerHTML = fls.map(k=>`<option value="${k}">${SP_FL_MAP[k][1]}</option>`).join('');
  sel.value = fls.includes(oldFl) ? oldFl : (fls.find(k=>DOORS.some(d=>d.fl===k)||LIFTS.some(l=>l.fl===k)) || fls[0]);
  const flKey = sel.value;
  const empty = (DOORS.some(d=>d.fl===flKey)||LIFTS.some(l=>l.fl===flKey)) ? '' :
    `<div class="muted" style="position:absolute;left:0;right:0;top:46%;text-align:center;font-size:11px">本层未识别到门 / 电梯构件</div>`;
  box.innerHTML = fpSvg(true) + empty +"""),
]
patch('index.html', i_subs)
print('ALL OK')
