# -*- coding: utf-8 -*-
import io
root=r'C:\Users\52560\Documents\Kimi\Workspaces\机器人\qs-robot-proto'

def patch(path, pairs):
    s=io.open(path,encoding='utf-8').read()
    n=0
    for a,b in pairs:
        assert s.count(a)==1,('anchor fail',path,a[:70],s.count(a))
        s=s.replace(a,b); n+=1
    io.open(path,'w',encoding='utf-8').write(s)
    print(path.split('\\')[-1],'patched',n)

# ================= 小程序 =================
mini=root+r'\miniapp.html'
pairs=[

# 1) CSS: 待取货状态样式
(""".st.queue{background:#fffbeb;color:#92600a}""",
 """.st.queue{background:#fffbeb;color:#92600a}
.st.pickup{background:#f5f3ff;color:#6d28d9}"""),

# 2) 订单数据：两条改其他账号（顾客视角看不到，店员可见全部）；DQ2055 后插入一条待取货订单
("""{no:'DQ2018',ch:'商家小程序',shop:'DQ 冰雪皇后',ic:'🍦',dest:'2F 会议层东',time:'昨天 16:32',st:'done',stTx:'已送达',acct:'138****5678'}""",
 """{no:'DQ2018',ch:'商家小程序',shop:'DQ 冰雪皇后',ic:'🍦',dest:'2F 会议层东',time:'昨天 16:32',st:'done',stTx:'已送达',acct:'139****2333'}"""),
("""{no:'DQ1990',ch:'饿了么',shop:'DQ 冰雪皇后',ic:'🍦',dest:'大堂服务台',time:'昨天 11:40',st:'stuck',stTx:'滞留提醒',acct:'138****5678'}""",
 """{no:'DQ1990',ch:'饿了么',shop:'DQ 冰雪皇后',ic:'🍦',dest:'大堂服务台',time:'昨天 11:40',st:'stuck',stTx:'滞留提醒',acct:'137****9001'}"""),
("""queue:1,eta:'约 22 分钟',acct:'138****5678'},""",
 """queue:1,eta:'约 22 分钟',acct:'138****5678'},
 {no:'A1031',ch:'美团',shop:'奈雪的茶',ic:'🧋',dest:'2F 会议层东',time:'今天 14:32',st:'pickup',stTx:'待取货',queue:0,eta:'取货后约 10 分钟',acct:'139****2333'},"""),

# 3) 账号条：加角色切换入口
("""<span>当前账号：<b id="acctTx" style="color:var(--tx)"></b></span>""",
 """<span>当前账号：<b id="acctTx" style="color:var(--tx)"></b> <span id="roleTx" style="color:var(--pri);cursor:pointer" onclick="toggleRole()"></span></span>"""),

# 4) 角色函数 + renderAcct 替换原 acctTx 赋值
("""document.getElementById('acctTx').textContent = myAcct();
function logout()""",
 """function myRole(){ return localStorage.getItem('my-role')||'cust'; }
function isClerk(){ return myRole()==='clerk'; }
function toggleRole(){
  localStorage.setItem('my-role',isClerk()?'cust':'clerk');
  renderAcct(); renderOrders('');
  toast(isClerk()?'已切换为店员账号 · 可见本店全部订单':'已切换为顾客账号 · 仅看自己的订单');
}
function renderAcct(){
  document.getElementById('acctTx').textContent = isClerk()?'店员 · 龙岗星河WORLD店':myAcct();
  document.getElementById('roleTx').textContent = isClerk()?'（店员 ⇄ 切换）':'（顾客 ⇄ 切换）';
}
renderAcct();
function logout()"""),

# 5) 订单列表：店员看全部，顾客只看自己；进行中包含待取货
("""  const list=ORDERS.filter(o=>!f||o.st===f
    ||(f==='ing'&&o.st==='queue')
    ||(f==='err'&&o.st==='stuck'));""",
 """  const list=ORDERS.filter(o=>(isClerk()||o.acct===myAcct())&&(!f||o.st===f
    ||(f==='ing'&&(o.st==='queue'||o.st==='pickup'))
    ||(f==='err'&&o.st==='stuck')));"""),

# 6) 详情按钮：店员 + 待取货 → 已取货按钮
("""  if(o.st==='queue')btns.push('<button class="bbtn" onclick="confirmAct(\\'cancel\\')">取消订单</button>');""",
 """  if(o.st==='queue')btns.push('<button class="bbtn" onclick="confirmAct(\\'cancel\\')">取消订单</button>');
  if(o.st==='pickup'&&isClerk())btns.push('<button class="bbtn pri" onclick="confirmAct(\\'picked\\')">✅ 已取货 · 通知机器狗配送</button>');"""),

# 7) 详情时间线：待取货分支
("""  else if(o.st==='queue')base.push(['cur','排队中','当前第 '+o.queue+' 位，预计 '+o.eta]);""",
 """  else if(o.st==='pickup')base.push(['cur','待取货','机器狗已到店停靠，等待店员核对订单号并放货'+(isClerk()?'，确认后点击上方「已取货」按钮':'')]);
  else if(o.st==='queue')base.push(['cur','排队中','当前第 '+o.queue+' 位，预计 '+o.eta]);"""),

# 8) confirmAct / doConfirm：已取货分支
("""function confirmAct(a){
  cfAction=a;
  document.getElementById('cfTitle').textContent=a==='cancel'?'确认取消订单？':'确认重新配送？';
  document.getElementById('cfDesc').textContent=a==='cancel'?'取消后本次配送终止，商品将退回商铺。':'将重新调度机器狗执行本次配送，请确认商品仍在商铺。';
  document.getElementById('cfMask').classList.add('on');
}""",
 """function confirmAct(a){
  cfAction=a;
  document.getElementById('cfTitle').textContent=a==='cancel'?'确认取消订单？':(a==='picked'?'确认已取货？':'确认重新配送？');
  document.getElementById('cfDesc').textContent=a==='cancel'?'取消后本次配送终止，商品将退回商铺。':(a==='picked'?'已核对订单号并将物品放置货箱，确认后机器狗立即出发配送。':'将重新调度机器狗执行本次配送，请确认商品仍在商铺。');
  document.getElementById('cfMask').classList.add('on');
}"""),
("""function doConfirm(){
  closeMask();
  if(cfAction==='cancel'&&curDetail>=0){ORDERS[curDetail].st='cancel';ORDERS[curDetail].stTx='已取消';renderOrders('');openDetail(curDetail);toast('订单已取消');}
  else toast('已重新发起配送');
}""",
 """function doConfirm(){
  closeMask();
  if(cfAction==='cancel'&&curDetail>=0){ORDERS[curDetail].st='cancel';ORDERS[curDetail].stTx='已取消';renderOrders('');openDetail(curDetail);toast('订单已取消');}
  else if(cfAction==='picked'&&curDetail>=0){ORDERS[curDetail].st='ing';ORDERS[curDetail].stTx='配送中';ORDERS[curDetail].eta='约 8 分钟';renderOrders('');openDetail(curDetail);toast('已确认取货，机器狗开始配送');}
  else toast('已重新发起配送');
}"""),
]
patch(mini,pairs)

# ================= 平台端 =================
plat=root+r'\light\index.html'
ppairs=[

# 1) a2 触发条件：店员语音 + 小程序触发（默认都勾选）
("""{ id:'a2', name:'② 触发取货成功', icon:'✅', trigger:'店员语音：「货物已放好，可以去送货了」',""",
 """{ id:'a2', name:'② 触发取货成功', icon:'✅', trigger:'店员语音：「货物已放好，可以去送货了」 或 小程序「已取货」确认', trig:{voice:true,mini:true},"""),

# 2) dlTrig 函数（插在 DL_ACTS 数组结束后）
("""function dlPickAddOpen(){""",
 """function dlTrig(k,v){
  const a=DL_ACTS[1]; a.trig[k]=v; const t=[];
  if(a.trig.voice)t.push('店员语音：「货物已放好，可以去送货了」');
  if(a.trig.mini)t.push('小程序「已取货」确认');
  a.trigger=t.join(' 或 ')||'（未配置触发条件）';
}
function dlPickAddOpen(){"""),

# 3) 触发条件渲染：a2 用双勾选，其余保持单行输入
("""          <div class="form-row"><label>触发条件</label><input class="input" style="font-size:11px" value="${a.trigger}" onchange="DL_ACTS[${i}].trigger=this.value"></div>""",
 """          ${a.id==='a2' ? `<div class="form-row"><label>触发条件（任一满足即触发）</label><label style="display:flex;align-items:flex-start;gap:6px;font-size:11px;font-weight:400;cursor:pointer;text-transform:none;letter-spacing:0"><input type="checkbox" style="margin-top:2px" ${a.trig.voice?'checked':''} onchange="dlTrig('voice',this.checked)">店员语音：「货物已放好，可以去送货了」</label><label style="display:flex;align-items:flex-start;gap:6px;font-size:11px;font-weight:400;cursor:pointer;margin-top:4px;text-transform:none;letter-spacing:0"><input type="checkbox" style="margin-top:2px" ${a.trig.mini?'checked':''} onchange="dlTrig('mini',this.checked)">小程序触发：店员在订单详情点击「已取货」</label></div>` : `<div class="form-row"><label>触发条件</label><input class="input" style="font-size:11px" value="${a.trigger}" onchange="DL_ACTS[${i}].trigger=this.value"></div>`}"""),
]
patch(plat,ppairs)
