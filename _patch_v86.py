# -*- coding: utf-8 -*-
"""V8.6 patch：商铺 DQ/奈雪 + 小程序 logo/滞留状态 + 接管×按钮 + 通行控制左右布局 + 电梯楼层可选 + 视口深化"""
importBase = None
import io, shutil, os, sys, re

ROOT = os.path.dirname(os.path.abspath(__file__))
BAK = os.path.join(ROOT, 'backups', 'pre-v86')
os.makedirs(BAK, exist_ok=True)
for f in ('index.html', 'miniapp.html'):
    shutil.copy2(os.path.join(ROOT, f), os.path.join(BAK, f))

fails = []

def load(f): return io.open(os.path.join(ROOT, f), encoding='utf-8').read()
def save(f, s): io.open(os.path.join(ROOT, f), 'w', encoding='utf-8', newline='').write(s)

def rep(s, name, old, new, cnt=1):
    n = s.count(old)
    if cnt == -1:
        if n < 1: fails.append((name, n)); return s
    elif n != cnt:
        fails.append((name, n)); return s
    print(f'OK  [{n}x] {name}')
    return s.replace(old, new)

# ================= index.html =================
s = load('index.html')

# ① 商铺改 DQ / 奈雪
s = rep(s, 'P1 取货点 DQ/奈雪', """const DL_PICKS = [
  { id:'PK-01', name:'罗森便利店（取货柜台）', bld:'主楼', fl:'1F', space:'大堂', use:'买商品', tel:'0755-8821-0023', desc:'大堂西侧便利店柜台 · 出示取货码取货' },
  { id:'PK-02', name:'瑞幸咖啡（出品台）', bld:'主楼', fl:'1F', space:'大堂', use:'买咖啡', tel:'138-2388-1024', desc:'大堂东侧出品台 · 取餐码核销' },
];""", """const DL_PICKS = [
  { id:'PK-01', name:'DQ 冰雪皇后（取货柜台）', bld:'主楼', fl:'1F', space:'大堂', use:'买商品', tel:'0755-8821-0023', desc:'大堂西侧甜品柜台 · 出示取货码取货' },
  { id:'PK-02', name:'奈雪的茶（出品台）', bld:'主楼', fl:'1F', space:'大堂', use:'买奶茶', tel:'138-2388-1024', desc:'大堂东侧出品台 · 取餐码核销' },
];""")

s = rep(s, 'P2 配送记录 DQ/奈雪', """const DL_RECS = [
  { t:'今天 14:32', from:'瑞幸咖啡（出品台）', what:'拿铁 ×2', to:'3F 办公区 301 会议室', acct:'138****5678', rcv:'张工 138****2210', st:['配送中','b-task'] },
  { t:'今天 14:05', from:'罗森便利店（取货柜台）', what:'三明治 + 咖啡套餐 ×1', to:'3F 办公区 302 开放工位', acct:'137****8890', rcv:'前台代收', st:['排队中 · 第 1 位','b-warn'] },
  { t:'今天 11:20', from:'瑞幸咖啡（出品台）', what:'美式 ×1', to:'1F 前台', acct:'138****5678', rcv:'前台', st:['已送达','b-ok'] },
  { t:'昨天 16:05', from:'瑞幸咖啡（出品台）', what:'拿铁 ×1', to:'3F 办公区 301 会议室', acct:'139****3356', rcv:'张工', st:['配送异常-处理中 · 断网回桩','b-danger'] },
  { t:'昨天 15:40', from:'罗森便利店（取货柜台）', what:'文件袋 ×1', to:'2F 会议层东', acct:'135****7742', rcv:'李工', st:['取货超时 · 带回服务台','b-warn'] },
  { t:'昨天 10:18', from:'罗森便利店（取货柜台）', what:'咖啡套餐 ×1', to:'3F 办公区 301 会议室', acct:'138****5678', rcv:'张工', st:['已取消','b-dim'] },
];""", """const DL_RECS = [
  { t:'今天 14:32', from:'奈雪的茶（出品台）', what:'霸气芝士草莓 ×2', to:'3F 办公区 301 会议室', acct:'138****5678', rcv:'张工 138****2210', st:['配送中','b-task'] },
  { t:'今天 14:05', from:'DQ 冰雪皇后（取货柜台）', what:'暴风雪套餐 ×1', to:'3F 办公区 302 开放工位', acct:'137****8890', rcv:'前台代收', st:['排队中 · 第 1 位','b-warn'] },
  { t:'今天 11:20', from:'奈雪的茶（出品台）', what:'奈雪初雪 ×1', to:'1F 前台', acct:'138****5678', rcv:'前台', st:['已送达','b-ok'] },
  { t:'昨天 16:05', from:'奈雪的茶（出品台）', what:'霸气橙子 ×1', to:'3F 办公区 301 会议室', acct:'139****3356', rcv:'张工', st:['配送异常-处理中 · 断网回桩','b-danger'] },
  { t:'昨天 15:40', from:'DQ 冰雪皇后（取货柜台）', what:'文件袋 ×1', to:'2F 会议层东', acct:'135****7742', rcv:'李工', st:['取货超时 · 带回服务台','b-warn'] },
  { t:'昨天 10:18', from:'DQ 冰雪皇后（取货柜台）', what:'冰淇淋蛋糕 ×1', to:'3F 办公区 301 会议室', acct:'138****5678', rcv:'张工', st:['已取消','b-dim'] },
];""")

s = rep(s, 'P3 t-007 任务名', "name:'罗森咖啡配送至 3F 办公区'", "name:'奈雪茶饮配送至 3F 办公区'")
s = rep(s, 'P4 t-007 描述', "desc:'跨楼层物品配送：罗森取货 → 闸机 → 3F 301 会议室'", "desc:'跨楼层物品配送：奈雪取货 → 闸机 → 3F 301 会议室'")
s = rep(s, 'P5 t-007 取货', "delivery:{ from:'罗森便利店（1F 大堂东侧 · 语义找店「罗森」）', item:'咖啡 ×2 / 文件袋 ×1'",
    "delivery:{ from:'奈雪的茶（1F 大堂东侧 · 语义找店「奈雪」）', item:'奶茶 ×2 / 文件袋 ×1'")
s = rep(s, 'P6 断网货物', "cargo:'配送 · 拿铁咖啡 → 3F 办公区 301 会议室（已取货）'", "cargo:'配送 · 奈雪奶茶 → 3F 办公区 301 会议室（已取货）'")
s = rep(s, 'P7 任务名预填', "'跨楼层物品配送（罗森 → 3F 办公区）'", "'跨楼层物品配送（奈雪 → 3F 办公区）'")
s = rep(s, 'P8 地图取货点标', "取货点：罗森便利店（语义找店匹配）", "取货点：奈雪的茶（语义找店匹配）")
s = rep(s, 'P9 地图取货点名', ">罗森便利店</div>", ">奈雪的茶</div>")
s = rep(s, 'P10 默认取货商铺', "||'罗森便利店')", "||'奈雪的茶')")
s = rep(s, 'P11 时间轴嵌套名', "└ t-007 罗森咖啡配送至 3F", "└ t-007 奈雪茶饮配送至 3F")
s = rep(s, 'P12 场景模板', "取货点组（罗森 / 瑞幸）", "取货点组（奈雪 / DQ）")
s = rep(s, 'P13 导览问答', "{keys:['咖啡','瑞幸','奶茶'], anss:['1F 大堂有瑞幸咖啡，需要我带您过去吗？','想喝咖啡的话，大堂 1F 就有瑞幸，跟我走吧～'], hits:41}",
    "{keys:['奶茶','奈雪','冰淇淋','DQ'], anss:['1F 大堂有奈雪的茶和 DQ 冰雪皇后，需要我带您过去吗？','想喝奶茶的话，大堂 1F 就有奈雪，跟我走吧～'], hits:41}")
s = rep(s, 'P14 小舆示例', "'帮我去瑞幸取 A1024 送到301'", "'帮我去奈雪取 A1024 送到301'")
s = rep(s, 'P15 取货点表单占位', 'placeholder="如：罗森便利店（取货柜台）"', 'placeholder="如：奈雪的茶（出品台）"')

# ④ 接管确认框 × 按钮
s = rep(s, 'W1 确认框×按钮', '''<button class="x" style="position:absolute;right:10px;top:8px" title="取消 · 继续接管" onclick="document.getElementById('tkConfirm').style.display='none'">✕</button>''',
    '''<button style="position:absolute;right:6px;top:4px;background:none;border:none;color:var(--tx-dim);font-size:15px;cursor:pointer;padding:4px 7px;line-height:1;border-radius:6px;transition:.15s" onmouseover="this.style.color='#e6f1ff';this.style.background='rgba(120,190,255,.12)'" onmouseout="this.style.color='var(--tx-dim)';this.style.background='none'" title="取消 · 继续接管" onclick="document.getElementById('tkConfirm').style.display='none'">✕</button>''')

# ② 通行控制左右布局
s = rep(s, 'W2 通行控制容器', '''    <!-- ③ 智能通行控制（门 / 电梯 · 门控梯控配置） -->
    <div class="ttab" id="sb-pass" style="flex:1;display:none;overflow:auto;padding:14px 18px">
      <div id="spPass" style="max-width:980px"></div>
    </div>''',
    '''    <!-- ③ 智能通行控制（左：空间地图 · 右：门控/梯控设置列表） -->
    <div class="ttab" id="sb-pass" style="flex:1;display:none;grid-template-columns:1fr 480px;gap:12px;padding:12px 18px;min-height:0">
      <div class="panel">
        <div class="panel-hd"><span class="dot"></span>空间地图 · 门 / 电梯构件<span class="extra">点门标记弹设置 · 点电梯定位到梯控列表</span></div>
        <div class="panel-bd" style="overflow:auto;display:flex;flex-direction:column">
          <div style="display:flex;gap:8px;align-items:center;margin-bottom:8px"><span class="muted" style="font-size:10px">单体 / 楼层</span><select class="input" id="spPassFl" style="width:auto;padding:3px 8px;font-size:11px" onchange="spPassMapRender()"></select></div>
          <div id="spPassMap" style="position:relative;flex:1;min-height:0;border:1px solid var(--border);border-radius:8px;overflow:hidden"></div>
        </div>
      </div>
      <div class="panel"><div class="panel-bd" style="overflow:auto" id="spPass"></div></div>
    </div>''')

s = rep(s, 'W3 spaceTab通行页grid', "document.getElementById('sb-'+k).style.display = k===t ? ((k==='org'||k==='pt')?'grid':'block') : 'none';",
    "document.getElementById('sb-'+k).style.display = k===t ? (k==='cmp'?'block':'grid') : 'none';")

s = rep(s, 'W4 通行地图渲染', """    </div>` + (passTab==='gate' ? cfgGateHtml() : cfgLiftHtml());
}""", """    </div>` + (passTab==='gate' ? cfgGateHtml() : cfgLiftHtml());
  spPassMapRender();
}
function spPassMapRender(){
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
  box.innerHTML = fpSvg(true) +
    DOORS.filter(d=>d.fl===flKey).map(d=>{
      const noApi = doorNoApi(d);
      const cls = d.type==='auto' ? (noApi?'noapi':'') : 'visual';
      return `<div class="gate-mk ${cls}" style="left:${d.x}%;top:${d.y}%" title="${d.name} · ${doorTypeTx(d)} · ${d.dstate||'常关'}${noApi?' · ⚠ 未配置门控 API':''}（点击设置）" onclick="doorSetOpen('${d.id}')">${d.type==='auto'?'🚪':'👁'}</div>`;
    }).join('') +
    LIFTS.filter(l=>l.fl===flKey).map(l=>`<div class="gate-mk lift ${l.usable?'':'noapi'}" style="left:${l.x}%;top:${l.y}%" title="${l.name} · ${l.usable?'可乘 · 已接梯控':'不可乘 · 未接梯控'}（点击定位到梯控列表）" onclick="passTab='lift';spPassRender();toast('已定位到梯控列表 · ${l.name}')">🛗</div>`).join('');
}""")

# ③ 电梯服务楼层可选 + 服务单体
s = rep(s, 'W5 电梯楼层可选', '''      <div class="form-row"><label>服务楼层</label><input class="input" id="sgLiftFloors" value="${gl.floors}"></div>''',
    '''      <div class="form-row"><label>服务单体</label><span style="font-size:12px;color:var(--tx-hi)">${(SP_FL_MAP[gl.fl]||['主楼'])[0]}（当前所在单体）</span></div>
      <div class="form-row"><label>服务楼层</label><span style="display:flex;gap:6px;flex-wrap:wrap;flex:1">${(SP_BOX.find(x=>x.id===(SP_FL_MAP[gl.fl]||['主楼'])[0])||SP_BOX[0]).floors.map(f=>`<label style="display:flex;align-items:center;gap:3px;font-size:11px;cursor:pointer;padding:2px 8px;border:1px solid ${gl.floors.includes(f)?'var(--cy)':'var(--border)'};border-radius:6px;background:${gl.floors.includes(f)?'rgba(34,211,238,.1)':'transparent'}"><input type="checkbox" class="sgLf" value="${f}" ${gl.floors.includes(f)?'checked':''} style="accent-color:#22d3ee">${f}</label>`).join('')}</span></div>''')

s = rep(s, 'W6 电梯楼层保存', "    l.floors = document.getElementById('sgLiftFloors').value.trim()||l.floors;",
    "    const fls=[...document.querySelectorAll('.sgLf:checked')].map(c=>c.value); if(fls.length) l.floors = fls.join('、');")

# ⑤ 监控视口深化 + 铺满
s = rep(s, 'W7 视口底图', '''#mn-3d img.bg3d{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;filter:brightness(.55) contrast(1.08) saturate(.9)}
[data-theme="light"] #mn-3d img.bg3d{filter:none}''',
    '''#mn-3d img.bg3d{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;object-position:36% 24%;transform:scale(1.24);transform-origin:36% 24%;filter:brightness(.5) contrast(1.16) saturate(1.08)}
[data-theme="light"] #mn-3d img.bg3d{filter:none;transform:none}''')

s = rep(s, 'W8 视口叠加层', '''#mn-3d::after{content:"";position:absolute;inset:0;pointer-events:none;z-index:6;
  background:linear-gradient(160deg,rgba(23,15,58,.30),rgba(8,10,30,.40)),repeating-linear-gradient(0deg,rgba(120,180,255,.035) 0 1px,transparent 1px 4px)}''',
    '''#mn-3d::after{content:"";position:absolute;inset:0;pointer-events:none;z-index:6;
  background:radial-gradient(115% 85% at 46% 30%,rgba(30,20,72,.05) 0%,rgba(14,12,40,.36) 55%,rgba(5,6,22,.68) 100%),linear-gradient(160deg,rgba(23,15,58,.34),rgba(6,8,26,.48)),repeating-linear-gradient(0deg,rgba(120,180,255,.035) 0 1px,transparent 1px 4px)}''')

save('index.html', s)

# ================= miniapp.html =================
m = load('miniapp.html')

m = rep(m, 'M1 商铺 DQ/奈雪', """const SHOPS=[
 {id:'lawson',ic:'🏪',nm:'罗森便利店',tp:'便利店 · 主楼1F 大堂',tel:'0755-8821-0023'},
 {id:'luckin',ic:'☕',nm:'瑞幸咖啡',tp:'咖啡 · 主楼1F 大堂',tel:'138-2388-1024'}];""",
    """const SHOPS=[
 {id:'dq',ic:'🍦',nm:'DQ 冰雪皇后',tp:'甜品 · 主楼1F 大堂',tel:'0755-8821-0023'},
 {id:'naixue',ic:'🧋',nm:'奈雪的茶',tp:'茶饮 · 主楼1F 大堂',tel:'138-2388-1024'}];""")

m = rep(m, 'M2 订单商铺名', """const ORDERS=[
 {no:'A1024',shop:'瑞幸咖啡',ic:'☕',dest:'3F 办公区 301 会议室',time:'今天 14:20',st:'ing',stTx:'配送中',queue:0,eta:'约 8 分钟',acct:'138****5678'},
 {no:'LS2055',shop:'罗森便利店',ic:'🏪',dest:'3F 办公区 302 开放工位',time:'今天 13:45',st:'queue',stTx:'排队中 · 第1位',queue:1,eta:'约 22 分钟',acct:'138****5678'},
 {no:'A0987',shop:'瑞幸咖啡',ic:'☕',dest:'1F 前台',time:'今天 11:05',st:'done',stTx:'已送达',acct:'138****5678'},
 {no:'LS2018',shop:'罗森便利店',ic:'🏪',dest:'2F 会议层东',time:'昨天 16:32',st:'done',stTx:'已送达',acct:'138****5678'},
 {no:'A0966',shop:'瑞幸咖啡',ic:'☕',dest:'3F 办公区 301 会议室',time:'昨天 16:05',st:'err',stTx:'配送异常-处理中',acct:'138****5678'},
 {no:'LS1990',shop:'罗森便利店',ic:'🏪',dest:'大堂服务台',time:'昨天 11:40',st:'stuck',stTx:'滞留提醒',acct:'138****5678'},
 {no:'A0942',shop:'瑞幸咖啡',ic:'☕',dest:'3F 办公区 302 开放工位',time:'昨天 10:18',st:'cancel',stTx:'已取消',acct:'138****5678'}];""",
    """const ORDERS=[
 {no:'A1024',shop:'奈雪的茶',ic:'🧋',dest:'3F 办公区 301 会议室',time:'今天 14:20',st:'ing',stTx:'配送中',queue:0,eta:'约 8 分钟',acct:'138****5678'},
 {no:'DQ2055',shop:'DQ 冰雪皇后',ic:'🍦',dest:'3F 办公区 302 开放工位',time:'今天 13:45',st:'queue',stTx:'排队中 · 第1位',queue:1,eta:'约 22 分钟',acct:'138****5678'},
 {no:'A0987',shop:'奈雪的茶',ic:'🧋',dest:'1F 前台',time:'今天 11:05',st:'done',stTx:'已送达',acct:'138****5678'},
 {no:'DQ2018',shop:'DQ 冰雪皇后',ic:'🍦',dest:'2F 会议层东',time:'昨天 16:32',st:'done',stTx:'已送达',acct:'138****5678'},
 {no:'A0966',shop:'奈雪的茶',ic:'🧋',dest:'3F 办公区 301 会议室',time:'昨天 16:05',st:'err',stTx:'配送异常-处理中',acct:'138****5678'},
 {no:'DQ1990',shop:'DQ 冰雪皇后',ic:'🍦',dest:'大堂服务台',time:'昨天 11:40',st:'stuck',stTx:'滞留提醒',acct:'138****5678'},
 {no:'A0942',shop:'奈雪的茶',ic:'🧋',dest:'3F 办公区 302 开放工位',time:'昨天 10:18',st:'cancel',stTx:'已取消',acct:'138****5678'}];""")

m = rep(m, 'M3 滞留订单状态显示', '<span class="st ${o.st}">${o.stTx}</span>', '<span class="st ${o.st===\'stuck\'?\'hold\':o.st}">${o.stTx}</span>')

m = rep(m, 'M4 默认商铺', "let curShop='luckin',cfAction=null,curDetail=-1;", "let curShop='naixue',cfAction=null,curDetail=-1;")
m = rep(m, 'M5 语音示例1', '按住或点击说话，例如："帮我去瑞幸取 A1024，送到 3F 办公区 301"', '按住或点击说话，例如："帮我去奈雪取 A1024，送到 3F 办公区 301"')
m = rep(m, 'M6 语音示例2', "r.textContent='🗣 \"帮我去瑞幸取 A1024，送到 3F 办公区 301\"';", "r.textContent='🗣 \"帮我去奈雪取 A1024，送到 3F 办公区 301\"';")
m = rep(m, 'M7 语音选店', "pickShop('luckin',document.querySelectorAll('.shop')[1]);", "pickShop('naixue',document.querySelectorAll('.shop')[1]);")
m = rep(m, 'M8 进度页商铺', 'A1024 · 瑞幸咖啡', 'A1024 · 奈雪的茶')
m = rep(m, 'M9 地图取货标', '>瑞幸·取货<', marker := '>奈雪·取货<')
m = rep(m, 'M10 时间线商铺', "['done','已派单','14:22 · 机器狗「龙岗小白」接单，前往瑞幸咖啡'],", "['done','已派单','14:22 · 机器狗「龙岗小白」接单，前往奈雪的茶'],")
m = rep(m, 'M11 进度页联系店员', 'callShop(\'瑞幸咖啡\')', 'callShop(\'奈雪的茶\')')
m = rep(m, 'M12 电话兜底', "return s?s.tel:'0755-8821-0023';}", "return s?s.tel:'138-2388-1024';}")

# logo 三处：头部 / 登录页 / 地图狗位
m = rep(m, 'M13 logo替换', 'assets/xiaoyu_head.png', 'assets/dog_head.svg', -1)

save('miniapp.html', m)

if fails:
    print('\n!!! 失败项：')
    for n, c in fails: print(f'  {n} 匹配数={c}')
    sys.exit(1)
print('\nV8.6 全部替换完成')
