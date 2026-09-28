# -*- coding: utf-8 -*-
import io
p = r'C:\Users\52560\Documents\Kimi\Workspaces\机器人\qs-robot-proto\index.html'
h = io.open(p, encoding='utf-8').read()

# ============ 1) CSS：面板加宽 + 对话流/气泡/卡片/胶囊/侧栏 ============
css_old = '.aa-panel{display:none;flex-direction:column;gap:8px;width:258px;pointer-events:auto;padding-bottom:16px}'
css_new = '''.aa-panel{display:none;flex-direction:column;gap:8px;width:336px;pointer-events:auto;padding-bottom:6px}
#aiAgent.docked{right:0;bottom:0;top:0;align-items:stretch}
#aiAgent.docked .aa-panel{width:360px;height:100vh;padding:10px 12px;background:rgba(7,12,24,.96);border-left:1px solid rgba(120,190,255,.3);backdrop-filter:blur(8px)}
#aiAgent.docked .aa-stage{position:absolute;bottom:16px;right:16px}
#aiAgent.docked .aa-msgs{max-height:none;flex:1}
.aa-hd{display:flex;align-items:center;gap:6px;padding:2px 2px 6px;border-bottom:1px solid rgba(120,190,255,.25);cursor:grab;user-select:none}
.aa-hd:active{cursor:grabbing}
.aa-hd .t{font-size:12px;font-weight:700;color:#bfe0ff;letter-spacing:1px;text-shadow:0 0 10px rgba(94,168,255,.4)}
.aa-sess{margin-left:auto;max-width:110px;background:rgba(94,168,255,.08);border:1px solid rgba(94,168,255,.3);border-radius:6px;color:#9cc4ee;font-size:10px;padding:2px 4px;outline:none}
.aa-hbtn{border:1px solid rgba(94,168,255,.3);background:rgba(94,168,255,.08);color:var(--tx-dim);border-radius:6px;width:20px;height:20px;font-size:10px;cursor:pointer;line-height:1}
.aa-hbtn:hover{color:var(--cy);border-color:var(--cy)}
.aa-msgs{display:flex;flex-direction:column;gap:8px;max-height:46vh;overflow-y:auto;padding:4px 2px;scrollbar-width:thin}
.aamsg{display:flex;animation:aanote .25s ease-out}
.aamsg .b{position:relative;padding:9px 12px;font-size:12.5px;line-height:1.7;border-radius:12px;max-width:88%;word-break:break-word}
.aamsg.a .b{background:rgba(12,20,40,.97);border:1px solid rgba(120,190,255,.45);color:#e6f1ff;border-top-left-radius:4px;box-shadow:0 6px 18px rgba(2,6,18,.5)}
.aamsg.u{justify-content:flex-end}
.aamsg.u .b{background:linear-gradient(120deg,rgba(34,211,238,.25),rgba(94,168,255,.3));border:1px solid rgba(34,211,238,.5);color:#eafcff;border-top-right-radius:4px}
.aamsg .b .mc-tt{font-size:11px;font-weight:700;color:var(--cy);margin-bottom:5px;letter-spacing:.5px}
.aamsg .b .mc-row{display:flex;justify-content:space-between;gap:10px;font-size:11px;padding:3px 0;border-bottom:1px dashed rgba(120,190,255,.15)}
.aamsg .b .mc-row:last-child{border-bottom:none}
.aamsg .b .mc-row b{color:#eaf6ff;font-weight:600;text-align:right}
.aamsg .b .mc-row .miss{color:#fbbf24}
.aamsg .b .mc-btns{display:flex;gap:6px;margin-top:8px}
.aamsg .b .mc-btns button{flex:1;padding:5px 8px;font-size:11px;border-radius:7px;cursor:pointer;border:1px solid rgba(34,211,238,.5);background:rgba(34,211,238,.12);color:#8be9ff}
.aamsg .b .mc-btns button:hover{background:rgba(34,211,238,.25)}
.aamsg .b .mc-btns button.ghost{background:none;border-color:var(--border);color:var(--tx-dim)}
.aamsg.alert .b{border-color:rgba(248,113,113,.55);background:rgba(26,12,18,.94);color:#ffe2e2}
.aa-chips{display:flex;gap:6px;overflow-x:auto;padding:2px 0;scrollbar-width:none}
.aa-chips::-webkit-scrollbar{display:none}
.aa-chips .chip{flex:none;font-size:11px;padding:5px 11px;border-radius:14px;border:1px solid rgba(120,190,255,.4);background:rgba(94,168,255,.1);color:#bfe0ff;cursor:pointer;white-space:nowrap;transition:.15s}
.aa-chips .chip:hover{background:rgba(94,168,255,.25);color:#e6f1ff}
.aa-voice-listening{animation:aaping 1s infinite;border-color:var(--cy)!important;color:var(--cy)!important}
@media (max-width:1100px){.aa-panel{width:min(380px,44vw)}.aamsg .b{font-size:13.5px}.aa-chips .chip{font-size:12px;padding:7px 13px}}'''
assert css_old in h
h = h.replace(css_old, css_new)

# ============ 2) HTML：面板改为 会话头 + 消息流 + 胶囊 + 输入 ============
html_old = '''  <div class="aa-panel">
    <div class="aa-bubble"><button class="aa-close" onclick="aaToggle(false)">✕</button><span id="aaText"></span><i class="aa-cursor"></i></div>
    <div class="aa-actions">
      <button onclick="aaAct('task')">📋 下任务</button>
      <button onclick="aaAct('delivery')">📦 发起配送</button>
      <button onclick="aaAct('path')">🧭 规划路径</button>
      <button onclick="aaAct('alert')">⚠ 异常</button>
      <button onclick="aaAct('dog')">🐕 状态</button>
    </div>
    <div class="aa-inrow">
      <input class="input" id="aaInp" style="flex:1" placeholder="对我说：去大堂巡检 / 送杯咖啡到301 / 洗手间在哪…" onkeydown="if(event.key==='Enter')aaSend()">
      <button class="icon-btn" title="语音输入" onclick="toast('语音输入（ASR 实时转写）接入中，请先用文字～')">🎙</button>
      <button class="icon-btn" onclick="aaSend()">➤</button>
    </div>
  </div>'''
html_new = '''  <div class="aa-panel" id="aaPanel">
    <div class="aa-hd" id="aaHd" title="按住可拖拽">
      <span class="t">小舆 · AI 空间智能体</span>
      <select class="aa-sess" id="aaSess" onchange="aaSessSwitch(this.value)" title="历史会话"></select>
      <button class="aa-hbtn" title="新建会话" onclick="aaNewSess()">＋</button>
      <button class="aa-hbtn" title="吸附为右侧常驻栏（Pad 推荐）" onclick="aaDock()">⇥</button>
      <button class="aa-hbtn" title="收起" onclick="aaToggle(false)">✕</button>
    </div>
    <div class="aa-msgs" id="aaMsgs"></div>
    <div class="aa-chips" id="aaChips"></div>
    <div class="aa-inrow">
      <input class="input" id="aaInp" style="flex:1" placeholder="对我说：去大堂巡检 / 送杯咖啡到301 / 洗手间在哪…" onkeydown="if(event.key==='Enter')aaSend()">
      <button class="icon-btn" id="aaMic" title="语音输入" onclick="aaVoice()">🎙</button>
      <button class="icon-btn" onclick="aaSend()">➤</button>
    </div>
  </div>'''
assert html_old in h
h = h.replace(html_old, html_new)

# ============ 3) JS：消息模型 + 多轮上下文 + 语音态 + 拖拽/侧栏 ============
js_old_aaSay = '''function aaSay(txt){
  const el=document.getElementById('aaText'); el.textContent='';
  clearInterval(aaTimer); let i=0;
  aaTimer=setInterval(()=>{ el.textContent=txt.slice(0,++i); if(i>=txt.length)clearInterval(aaTimer); },34);
}'''
js_new_aaSay = '''/* ---- 会话消息模型：多轮对话 + 历史会话 ---- */
const AA_SESS=[{id:1,title:'新会话',msgs:[]}]; let AA_CUR=0, AA_SEED=1;
function aaSess(){ return AA_SESS[AA_CUR]; }
function aaRenderMsgs(){
  const box=document.getElementById('aaMsgs'); box.innerHTML='';
  aaSess().msgs.forEach(m=>box.appendChild(aaMsgEl(m)));
  box.scrollTop=box.scrollHeight;
  const sel=document.getElementById('aaSess');
  sel.innerHTML=AA_SESS.map((s,i)=>`<option value="${i}" ${i===AA_CUR?'selected':''}>${s.title}</option>`).join('');
}
function aaMsgEl(m){
  const d=document.createElement('div'); d.className='aamsg '+(m.r==='u'?'u':'a')+(m.alert?' alert':'');
  const b=document.createElement('div'); b.className='b';
  if(m.html) b.innerHTML=m.html; else b.textContent=m.t;
  if(m.cardBtns){ const btns=document.createElement('div'); btns.className='mc-btns';
    m.cardBtns.forEach(cb=>{ const bn=document.createElement('button'); bn.textContent=cb[0]; if(cb[2])bn.className='ghost';
      bn.onclick=()=>cb[1](); btns.appendChild(bn); });
    b.appendChild(btns); }
  d.appendChild(b); return d;
}
function aaPush(m){ aaSess().msgs.push(m); const box=document.getElementById('aaMsgs');
  const el=aaMsgEl(m); box.appendChild(el); box.scrollTop=box.scrollHeight; return el; }
function aaSay(txt){
  const m={r:'a',t:''}; aaSess().msgs.push(m);
  const el=aaMsgEl(m); document.getElementById('aaMsgs').appendChild(el);
  const b=el.querySelector('.b');
  clearInterval(aaTimer); let i=0;
  aaTimer=setInterval(()=>{ m.t=txt.slice(0,++i); b.textContent=m.t;
    document.getElementById('aaMsgs').scrollTop=1e9;
    if(i>=txt.length)clearInterval(aaTimer); },26);
}
function aaCard(title,rows,btns,alert){
  const html='<div class="mc-tt">'+title+'</div>'+rows.map(r=>'<div class="mc-row"><span>'+r[0]+'</span><b class="'+(r[2]||'')+'">'+r[1]+'</b></div>').join('');
  aaPush({r:'a',html:html,cardBtns:btns,alert:alert});
}
function aaSessSwitch(i){ AA_CUR=+i; aaRenderMsgs(); }
function aaNewSess(){ AA_SESS.push({id:++AA_SEED,title:'会话 '+AA_SEED,msgs:[]}); AA_CUR=AA_SESS.length-1; aaRenderMsgs(); aaWelcome(); }
function aaWelcome(){
  const sceneNames=(ROBOT_EXT[curRobotId]&&ROBOT_EXT[curRobotId].scenes||['property','guide','delivery']).map(k=>SCENES[k]?SCENES[k].name:k).join('、');
  aaSay('你好，我是小舆～ 当前支持「'+sceneNames+'」场景。可以说：「送杯咖啡到301」「去大堂巡检」「扫描 2F」「狗子状态」，我会记住我们聊的内容。');
  aaPush({r:'a',html:'<div class="mc-tt">可以这样说（按当前具身能力过滤）</div>'+
    ['📦 帮我去奈雪取 A1024 送到301','📋 去 1F 大堂巡检一圈','🛰 扫描 2F 采集点云','🐕 狗子状态怎么样'].map(s=>'<div style="font-size:11px;color:#9cc4ee;padding:3px 0">'+s+'</div>').join('')});
}
/* 快捷胶囊（原固定按钮移入对话区） */
function aaRenderChips(){
  const chips=[['📦 发起配送','delivery'],['📋 下任务','task'],['🧭 规划路径','path'],['🐕 狗子状态','dog'],['⚠ 异常复核','alert']];
  document.getElementById('aaChips').innerHTML=chips.map(c=>'<span class="chip" onclick="aaAct(\\''+c[1]+'\\')">'+c[0]+'</span>').join('');
}
/* 语音输入三态：拾音中 → 识别中 → 回填 */
function aaVoice(){
  const mic=document.getElementById('aaMic'),inp=document.getElementById('aaInp');
  if(mic.dataset.busy)return; mic.dataset.busy=1;
  mic.classList.add('aa-voice-listening'); mic.textContent='⏺'; inp.placeholder='正在聆听…请说出任务';
  setTimeout(()=>{ mic.textContent='⏳'; inp.placeholder='识别中…'; },1400);
  setTimeout(()=>{ mic.classList.remove('aa-voice-listening'); mic.textContent='🎙'; delete mic.dataset.busy;
    inp.value='帮我去奈雪取杯咖啡送到301'; inp.placeholder='对我说：去大堂巡检 / 送杯咖啡到301 / 洗手间在哪…';
    toast('语音识别完成，可编辑后发送'); },2400);
}
/* 拖拽 + 右缘吸附侧栏 */
(function(){
  let sx,sy,sl,st0,drag=false;
  document.addEventListener('mousedown',e=>{
    const hd=e.target.closest('#aaHd'); if(!hd||e.target.closest('button,select'))return;
    const ag=document.getElementById('aiAgent'),r=ag.getBoundingClientRect();
    drag=true;sx=e.clientX;sy=e.clientY;sl=r.left;st0=r.top;
    ag.style.left=sl+'px';ag.style.top=st0+'px';ag.style.right='auto';ag.style.bottom='auto';
    e.preventDefault();
  });
  document.addEventListener('mousemove',e=>{ if(!drag)return;
    const ag=document.getElementById('aiAgent');
    ag.style.left=Math.max(0,Math.min(innerWidth-120,sl+e.clientX-sx))+'px';
    ag.style.top=Math.max(0,Math.min(innerHeight-120,st0+e.clientY-sy))+'px'; });
  document.addEventListener('mouseup',()=>{ if(!drag)return; drag=false;
    const ag=document.getElementById('aiAgent'),r=ag.getBoundingClientRect();
    if(innerWidth-r.right<80){ ag.style.left='auto';ag.style.top='auto';ag.style.right='16px';ag.style.bottom='16px'; } });
})();
function aaDock(){
  const ag=document.getElementById('aiAgent');
  ag.classList.toggle('docked');
  if(ag.classList.contains('docked')){ ag.style.left='auto';ag.style.top='auto';ag.style.right='0';ag.style.bottom='0'; toast('小舆已吸附为右侧常驻栏'); }
  else { ag.style.right='16px';ag.style.bottom='16px'; toast('已恢复悬浮形态'); }
  setTimeout(aaResize,100);
}'''
assert js_old_aaSay in h
h = h.replace(js_old_aaSay, js_new_aaSay)

# aaToggle 欢迎语改为多轮会话初始化
old_tw = '''  if(aaOn){ aaWave=(performance.now()-aaT0)/1000+1.6;
    if(aaUnread>0){
      aaSay(`你有 ${aaUnread} 条未读提醒～ 最新：${aaLastAlert ? aaLastAlert.text : ''}`);
      aaUnread = 0; aaDotUpdate();
    } else {
      aaSay('你好，我是小舆～ 可以直接对我说：「送杯咖啡到301」「去大堂巡检」「洗手间在哪」，也可以点下面按钮。');
    }
    aaLoad3D(); }'''
new_tw = '''  if(aaOn){ aaWave=(performance.now()-aaT0)/1000+1.6;
    if(!aaSess().msgs.length){
      if(aaUnread>0){
        aaSay(`你有 ${aaUnread} 条未读提醒～ 最新：${aaLastAlert ? aaLastAlert.text : ''}`);
        aaUnread = 0; aaDotUpdate();
      } else aaWelcome();
      aaRenderChips();
    } else aaRenderMsgs();
    aaLoad3D(); }'''
assert old_tw in h
h = h.replace(old_tw, new_tw)

# 告警进会话卡片
old_push = '''function aaPushAlert(a){
  aaLastAlert = a;
  aaUnread++; aaDotUpdate();
  if(aaOn){ aaSay(a.text); return; }'''
new_push = '''function aaPushAlert(a){
  aaLastAlert = a;
  aaUnread++; aaDotUpdate();
  if(aaOn){ aaCard(a.icon+' 主动提醒',[['内容',a.text]],[['前往处置 →',()=>a.act&&a.act()],['知道了',()=>{},true]],true); return; }'''
assert old_push in h
h = h.replace(old_push, new_push)

# aaSend：用户消息入会话 + 上下文追问
old_send_head = '''function aaSend(){
  const inp=document.getElementById('aaInp');
  const t=(inp.value||'').trim(); if(!t) return;
  inp.value='';'''
new_send_head = '''const AA_CTX={};
function aaSend(){
  const inp=document.getElementById('aaInp');
  const t=(inp.value||'').trim(); if(!t) return;
  inp.value='';
  aaPush({r:'u',t:t});
  /* 上下文追问：「改成 XF / 换成 XX / 顺便…」 */
  const mf=t.match(/^(改成|换成|改到)\\s*(\\S+)/);
  if(mf && AA_CTX.lastText){
    const nt=AA_CTX.lastText.replace(/[0-9一二三四五六七八九十]+[Ff层]/,mf[2]);
    aaSay('好的，已结合上文把目的地调整为「'+mf[2]+'」，按新目的地重新解析任务。');
    AA_CTX.lastText=nt; setTimeout(()=>aaDispatch(nt),700); return;
  }
  if(/^顺便/.test(t) && AA_CTX.lastText){
    aaSay('收到，在主任务基础上追加：「'+t.replace(/^顺便/,'')+'」，我会合并为一条多点任务。');
    return;
  }'''
assert old_send_head in h
h = h.replace(old_send_head, new_send_head)

# aaDispatch 记录上下文
h = h.replace("function aaDispatch(t){\n  if(!curRobotId){",
              "function aaDispatch(t){\n  AA_CTX.lastText=t;\n  if(!curRobotId){")

io.open(p, 'w', encoding='utf-8').write(h)
print('xiaoyu patch ok')
