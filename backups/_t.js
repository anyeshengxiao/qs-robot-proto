const POINTS=['3F 办公区 301 会议室','3F 办公区 302 开放工位','1F 前台','2F 会议层东','大堂服务台'];
let last={};
const document={getElementById:(id)=>{ if(!last[id])last[id]={className:'',innerHTML:'',value:''}; return last[id]; }};
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
  if(!scored.length){m.className='pmatch no';m.innerHTML='😥 未匹配到该空间，可能不在配送范围';return;}
  if(scored.length===1||(scored[0].s>=50&&scored[0].s>(scored[1]?scored[1].s:0))){
    const hit=scored[0].p;
    if(hit!==v)document.getElementById('fDest').value=hit;
    m.className='pmatch ok';m.innerHTML='✅ 已匹配空间：'+hit;return;
  }
  m.className='pmatch multi';
  m.innerHTML='🔎 匹配到 '+Math.min(scored.length,4)+' 个空间：'+scored.slice(0,4).map(x=>x.p).join(' / ');
}
for(const t of ['301','会议室','前台','大堂','会议','2F','办公区','301会议','月球基地','302 工位','3F 办公区 301 会议室','服务台','奶茶']){
  last={};matchDest(t);
  console.log(t,'=>',last.pmatch.className,'|',last.pmatch.innerHTML.slice(0,70),'| fill:',last.fDest?last.fDest.value:'');
}
