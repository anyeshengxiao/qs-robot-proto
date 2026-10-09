
/* ---------- 登录（微信手机号授权 · 记住账号） ---------- */
if(new URLSearchParams(location.search).get('logout')) localStorage.removeItem('my-user');
const MY_ACCT = localStorage.getItem('my-user') || '';
if(MY_ACCT) document.getElementById('lgMask').classList.remove('on');
else document.getElementById('lgMask').classList.add('on');
document.getElementById('acctTx').textContent = myAcct();
function logout(){ localStorage.removeItem('my-user'); location.reload(); }
function lgOk(){
  localStorage.setItem('my-user','138****5678');
  document.getElementById('authMask').classList.remove('on');
  document.getElementById('lgMask').classList.remove('on');
  toast('登录成功，欢迎回来');
}
function myAcct(){ return localStorage.getItem('my-user')||'138****5678'; }

/* ---------- 数据（商铺 / 送达点与机器人平台同源） ---------- */
const SHOPS=[
 {id:'dq',ic:'🍦',nm:'DQ 冰雪皇后',tp:'甜品 · 主楼1F 大堂',tel:'0755-8821-0023'},
 {id:'naixue',ic:'🧋',nm:'奈雪的茶',tp:'茶饮 · 主楼1F 大堂',tel:'138-2388-1024'}];
/* 送达点预设：与平台端「配送 · 送达点预设与管理」一致；支持手动输入 + 空间语义匹配 */
const POINTS=['3F 办公区 301 会议室','3F 办公区 302 开放工位','1F 前台','2F 会议层东','大堂服务台'];
const ORDERS=[
 {no:'A1024',ch:'美团',shop:'奈雪的茶',ic:'🧋',dest:'3F 办公区 301 会议室',time:'今天 14:20',st:'ing',stTx:'配送中',queue:0,eta:'约 8 分钟',acct:'138****5678'},
 {no:'DQ2055',ch:'饿了么',shop:'DQ 冰雪皇后',ic:'🍦',dest:'3F 办公区 302 开放工位',time:'今天 13:45',st:'queue',stTx:'排队中 · 第1位',queue:1,eta:'约 22 分钟',acct:'138****5678'},
 {no:'A0987',ch:'美团',shop:'奈雪的茶',ic:'🧋',dest:'1F 前台',time:'今天 11:05',st:'done',stTx:'已送达',acct:'138****5678'},
 {no:'DQ2018',ch:'商家小程序',shop:'DQ 冰雪皇后',ic:'🍦',dest:'2F 会议层东',time:'昨天 16:32',st:'done',stTx:'已送达',acct:'138****5678'},
 {no:'A0966',ch:'美团',shop:'奈雪的茶',ic:'🧋',dest:'3F 办公区 301 会议室',time:'昨天 16:05',st:'err',stTx:'配送异常-处理中',acct:'138****5678'},
 {no:'DQ1990',ch:'饿了么',shop:'DQ 冰雪皇后',ic:'🍦',dest:'大堂服务台',time:'昨天 11:40',st:'stuck',stTx:'滞留提醒',acct:'138****5678'},
 {no:'A0942',ch:'门店自点',shop:'奈雪的茶',ic:'🧋',dest:'3F 办公区 302 开放工位',time:'昨天 10:18',st:'cancel',stTx:'已取消',acct:'138****5678'}];
const STEPS=['已下单','待取货','配送中','已送达'];
let curShop='naixue',cfAction=null,curDetail=-1;

/* ---------- 下单页 ---------- */
document.getElementById('shops').innerHTML=SHOPS.map(s=>
 `<div class="shop ${s.id===curShop?'on':''}" onclick="pickShop('${s.id}',this)"><div class="ic">${s.ic}</div><div class="nm">${s.nm}</div><div class="tp">${s.tp}</div></div>`).join('');
document.getElementById('ptags').innerHTML=POINTS.map(p=>
 `<span class="ptag" onclick="pickPoint('${p}',this)">${p}</span>`).join('');

const CHS=['美团','饿了么','商家小程序','门店自点'];
let curCh='美团';
document.getElementById('chs').innerHTML=CHS.map(c=>`<span class="ptag ${c===curCh?'on':''}" onclick="pickCh('${c}',this)">${c}</span>`).join('');
function pickCh(c,el){curCh=c;document.querySelectorAll('#chs .ptag').forEach(e=>e.classList.remove('on'));el.classList.add('on');}
function pickShop(id,el){curShop=id;document.querySelectorAll('.shop').forEach(e=>e.classList.remove('on'));el.classList.add('on');}
function pickPoint(p,el){document.getElementById('fDest').value=p;matchDest(p);}
/* 空间语义模糊匹配：去空格归一 + 别名关键词 + 打分排序，支持「301」「会议室」「前台」等口语输入 */
const DEST_ALIAS={'会议室':'301','会议层':'2F 会议层东','会议':'2F 会议层东','工位':'302','前台':'1F 前台','大堂':'大堂服务台','服务台':'大堂服务台','办公':'3F 办公区','楼层东':'2F 会议层东'};
function matchDest(v){
  const m=document.getElementById('pmatch');v=(v||'').trim();
  if(!v){m.className='pmatch';return;}
  const nv=v.replace(/\s+/g,'').toLowerCase();
  const scored=POINTS.map(p=>{
    const np=p.replace(/\s+/g,'').toLowerCase();let s=0;
    if(np===nv)s=100;else if(np.includes(nv))s=60;else if(nv.includes(np))s=50;
    if(!s)for(const k in DEST_ALIAS){if(nv.includes(k)){const t=DEST_ALIAS[k].replace(/\s+/g,'').toLowerCase();if(np.includes(t)||t.includes(np)){s=40;break;}}}
    if(!s&&nv.length>=2){let hit=0;for(const ch of nv)if(np.includes(ch))hit++;if(hit/nv.length>=0.8)s=30;}
    return {p,s};
  }).filter(x=>x.s>0).sort((a,b)=>b.s-a.s);
  if(!scored.length){m.className='pmatch no';m.innerHTML='😥 未匹配到该空间，可能<b>不在配送范围</b>，请换预设点或联系店员';return;}
  if(scored.length===1||(scored[0].s>=50&&scored[0].s>(scored[1]?scored[1].s:0))){
    const hit=scored[0].p;
    if(hit!==v)document.getElementById('fDest').value=hit;
    m.className='pmatch ok';m.innerHTML='✅ 已匹配空间：<b>'+hit+'</b>（空间语义已确认可达）';return;
  }
  m.className='pmatch multi';
  m.innerHTML='🔎 匹配到 '+Math.min(scored.length,4)+' 个空间，请点击确认：<br>'+scored.slice(0,4).map(x=>`<span class="sg" onclick="pickPoint('${x.p}')">${x.p}</span>`).join('');
}
function shopTel(nm){const s=SHOPS.find(x=>nm.includes(x.nm)||x.nm.includes(nm));return s?s.tel:'138-2388-1024';}
function callShop(nm){toast('📞 店铺电话：'+shopTel(nm||'瑞幸')+'（长按可复制）');}
let vBusy=false;
function doVoice(){
  if(vBusy)return;vBusy=true;
  const b=document.getElementById('vbtn'),t=document.getElementById('vt'),r=document.getElementById('vres');
  b.classList.add('on');t.textContent='正在聆听…请说出取货商铺、订单号和送达地点';
  setTimeout(()=>{
    b.classList.remove('on');t.textContent='识别完成，已自动填写下方表单';
    r.style.display='block';r.textContent='🗣 "帮我去奈雪取 A1024，送到 3F 办公区 301"';
    pickShop('naixue',document.querySelectorAll('.shop')[1]);
    document.getElementById('fOrderNo').value='A1024';
    document.getElementById('fDest').value='3F 办公区 301 会议室';matchDest('3F 办公区 301 会议室');
    toast('已识别并填写，请确认后提交');vBusy=false;
  },1800);
}
function submitOrder(){
  const no=document.getElementById('fOrderNo').value.trim(),dest=document.getElementById('fDest').value.trim();
  if(!no)return toast('请填写订单号');
  if(!dest)return toast('请选择或输入送达点');
  const pm=document.getElementById('pmatch');
  if(pm.className!=='pmatch ok')return toast('送达点未匹配成功，不在配送范围');
  const sh=SHOPS.find(s=>s.id===curShop);
  ORDERS.unshift({no:no,ch:curCh,shop:sh.nm,ic:sh.ic,dest:dest,time:'刚刚',st:'queue',stTx:'排队中 · 第2位',queue:2,eta:'约 18 分钟',acct:myAcct(),note:document.getElementById('fNote').value.trim()});
  renderOrders('');
  document.getElementById('qNum').textContent='2';
  document.getElementById('okEta').textContent='18 分钟';
  document.getElementById('okMask').classList.add('on');
}
function closeMask(){document.querySelectorAll('.mask').forEach(m=>{if(m.id!=='lgMask')m.classList.remove('on');});}

/* ---------- 进度页 ---------- */
function renderFlow(state){
  const cur=state==='err'?2:(state==='queue'?0:2);
  document.getElementById('flow').innerHTML=STEPS.map((s,i)=>{
    const cls=state==='err'&&i===2?'err':(i<cur?'done':(i===cur?'cur':''));
    return `<div class="fstep ${cls}"><span class="dot">${state==='err'&&i===2?'!':(i<cur?'✓':i+1)}</span><div class="lb">${s}</div></div>`;
  }).join('');
}
renderFlow('ing');
document.getElementById('trackTl').innerHTML=[
 ['done','已下单','14:20 · 订单 A1024 已提交，排队第 1 位'],
 ['done','已派单','14:22 · 机器狗「龙岗小白」接单，前往奈雪的茶'],
 ['done','到达取货点','14:26 · 店员核对订单号 A1024'],
 ['done','取货成功','14:27 · 店员语音确认"货物已放好"'],
 ['cur','配送中','14:28 · 前往 3F 办公区 301 会议室，预计 8 分钟']
].map(t=>`<div class="ti ${t[0]}"><span class="d"></span><div><div class="tx">${t[1]}</div><div class="tm">${t[2]}</div></div></div>`).join('');
/* 狗位置缓慢移动动画 */
let dp=38;setInterval(()=>{dp+=1.2;if(dp>70)dp=38;const d=document.getElementById('dogpos');if(d)d.style.left=dp+'%';},1200);

/* ---------- 订单列表 ---------- */
function renderOrders(f){
  const list=ORDERS.filter(o=>!f||o.st===f
    ||(f==='ing'&&o.st==='queue')
    ||(f==='err'&&o.st==='stuck'));
  document.getElementById('ordList').innerHTML=list.map((o,i)=>
   `<div class="ord" onclick="openDetail(${ORDERS.indexOf(o)})">
     <div class="ic">${o.ic}</div>
     <div class="inf"><div class="l1">${o.shop} · ${o.no}</div><div class="l2">送至 ${o.dest} · ${o.time}</div></div>
     <span class="st ${o.st==='stuck'?'hold':o.st}">${o.stTx}</span></div>`).join('')||'<div style="text-align:center;color:var(--tx2);font-size:12px;padding:40px 0">暂无相关订单</div>';
}
function filterOrd(el,f){document.querySelectorAll('#ordFilters span').forEach(e=>e.classList.remove('on'));el.classList.add('on');renderOrders(f);}
renderOrders('');

/* ---------- 订单详情 ----------
   按钮规则（与平台端配送记录状态一致）：
   排队中 queue → 联系店员 + 取消订单（不可重新配送）
   配送中 ing / 已送达 done → 仅联系店员
   配送异常-处理中 err / 滞留提醒 stuck → 联系店员 + 重新配送
   已取消 cancel → 仅联系店员 */
function openDetail(i){
  const o=ORDERS[i];curDetail=i;
  document.getElementById('dtTitle').textContent='订单 '+o.no;
  document.getElementById('dtInfo').innerHTML=
   `购买渠道：<b>${o.ch||'美团'}</b> · 订单号：<b>${o.no}</b><br>商铺：${o.shop}（📞 ${shopTel(o.shop)}）<br>送达点：${o.dest}<br>下单时间：${o.time}<br>下单账号：${o.acct||myAcct()}（微信授权手机号）${o.note?'<br>送达提示语：「'+o.note+'」':''}<br>当前状态：<b>${o.stTx}</b>${o.eta?' · 预计 '+o.eta:''}`;
  document.getElementById('dtStuck').classList.toggle('on',o.st==='stuck');
  const btns=['<button class="bbtn" onclick="callShop(\''+o.shop+'\')">📞 联系店员</button>'];
  if(o.st==='queue')btns.push('<button class="bbtn" onclick="confirmAct(\'cancel\')">取消订单</button>');
  if(o.st==='err'||o.st==='stuck')btns.push('<button class="bbtn pri" onclick="confirmAct(\'redo\')">重新配送</button>');
  document.getElementById('dtBtns').innerHTML=btns.join('');
  const base=[['done','已下单',o.time+' · 订单提交成功'+(o.queue?'，排队第 '+o.queue+' 位':'')],['done','已派单','机器狗接单并出发']];
  if(o.st==='done')base.push(['done','取货成功','店员核对订单号并放货'],['done','配送中','途经门控 2 道'],['done','已送达','送达 '+o.dest+(o.note?'，播报「'+o.note+'」':'')+'，完成签收']);
  else if(o.st==='err')base.push(['done','取货成功','店员核对订单号并放货'],['err','配送异常','已取货断网 · 机器狗自动回充电桩等待重连，恢复后自动续送，无需人工干预']);
  else if(o.st==='stuck')base.push(['done','取货成功','店员核对订单号并放货'],['err','滞留提醒','机器狗长时间未移动 / 未送达，可前往充电桩自取或联系店员']);
  else if(o.st==='cancel')base.push(['err','已取消','订单取消，商品已退回商铺']);
  else if(o.st==='queue')base.push(['cur','排队中','当前第 '+o.queue+' 位，预计 '+o.eta]);
  else base.push(['done','取货成功','店员核对订单号并放货'],['cur','配送中','前往 '+o.dest+'，预计 '+o.eta]);
  document.getElementById('dtTl').innerHTML=base.map(t=>`<div class="ti ${t[0]}"><span class="d"></span><div><div class="tx">${t[1]}</div><div class="tm">${t[2]}</div></div></div>`).join('');
  document.getElementById('backBtn').classList.add('on');
  goTab('detail');
}
function confirmAct(a){
  cfAction=a;
  document.getElementById('cfTitle').textContent=a==='cancel'?'确认取消订单？':'确认重新配送？';
  document.getElementById('cfDesc').textContent=a==='cancel'?'取消后本次配送终止，商品将退回商铺。':'将重新调度机器狗执行本次配送，请确认商品仍在商铺。';
  document.getElementById('cfMask').classList.add('on');
}
function doConfirm(){
  closeMask();
  if(cfAction==='cancel'&&curDetail>=0){ORDERS[curDetail].st='cancel';ORDERS[curDetail].stTx='已取消';renderOrders('');openDetail(curDetail);toast('订单已取消');}
  else toast('已重新发起配送');
}

/* ---------- 通用 ---------- */
const _h=location.hash.replace('#','');
if(['order','track','orders','detail'].includes(_h))goTab(_h);
function goTab(t){
  document.querySelectorAll('.page').forEach(p=>p.classList.remove('on'));
  document.getElementById('pg-'+t).classList.add('on');
  document.querySelectorAll('.tabbar .tb').forEach(b=>b.classList.toggle('on',b.dataset.t===t));
  if(t!=='detail')document.getElementById('backBtn').classList.remove('on');
}
let tt;function toast(m){const t=document.getElementById('toast');t.textContent=m;t.classList.add('on');clearTimeout(tt);tt=setTimeout(()=>t.classList.remove('on'),2600);}
