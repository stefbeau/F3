const D=/*DATA*/null;
const $=id=>document.getElementById(id);
const Y=D.years,N=Y.length;
const CSSV=n=>getComputedStyle(document.documentElement).getPropertyValue(n).trim();
$("s3status").textContent=D.meta.s3_status;$("s6status").textContent=D.meta.s6_status;
$("prov").textContent=JSON.stringify(D.meta.provenance,null,1);
function key(s,d,sup){return s+"|"+d+"|"+(sup||"1")}
const DASH=[null,"7 4","2 3","10 3 2 3","1 0"];
/*PURE-START*/
/* Pure functions (no DOM): everything a takeaway card, the URL hash and the CSV download say is computed here from the data it is given (tests/test_site_ux.py). */
function human(v){const a=Math.abs(v);if(a>=1e12)return (+(v/1e12).toPrecision(3))+" trillion";if(a>=1e9)return (+(v/1e9).toPrecision(3))+" billion";if(a>=1e6)return (+(v/1e6).toPrecision(3))+" million";return (+v.toPrecision(3)).toString()}
function peakOf(years,ys){let k=0;ys.forEach((v,i)=>{if(v>ys[k])k=i});return [years[k],ys[k]]}
function firstReach(years,ys,th){const j=ys.findIndex(v=>v>=th);return j<0?null:years[j]}
function w3Takeaway(years,run,off,damage){
  const n=years.length-1,end=years[n],pk=peakOf(years,run.pop),pp=peakOf(years,run.ppolx),nr=run.nrfr[n];
  let s=`In this run population peaks at ${human(pk[1])} around ${pk[0]} and is ${human(run.pop[n])} in ${end}; ${nr.toFixed(2)} of the starting non-renewable resources remain in ${end}; persistent pollution peaks at ${pp[1].toFixed(1)} times its 1970 level around ${pp[0]}.`;
  const tiles=[{k:"Peak population",v:`${human(pk[1])}, ${pk[0]}`},{k:`Resources left, ${end}`,v:`${nr.toFixed(2)} of the start`},{k:"Pollution peak",v:`${pp[1].toFixed(1)} times 1970, ${pp[0]}`}];
  if(damage!=="off"){
    const dp=(run.pop[n]/off.pop[n]-1)*100,di=(run.io[n]/off.io[n]-1)*100;
    s+=` With climate damage (${damage}) the ${end} population is ${dp.toFixed(1)}% and industrial output ${di.toFixed(1)}% against damage off at the same settings (a level-of-output effect, not a forecast).`;
    tiles.push({k:`Damage effect on ${end} population`,v:`${dp.toFixed(1)}%`});
  }
  return {sentence:s,tiles:tiles};
}
function climateTakeaway(years,mean,lo,hi){
  const n=years.length-1;
  return {sentence:`The FaIR ensemble mean reaches ${mean[n].toFixed(2)} K above 1850-1900 in ${years[n]} (5th to 95th percentile of the ensemble: ${lo[n].toFixed(2)} to ${hi[n].toFixed(2)} K), from ${mean[0].toFixed(2)} K in ${years[0]}. Emissions are prescribed, and FaIR starts about 0.04 to 0.07 K below observed (test A2.1 failed).`,
    tiles:[{k:`Mean, ${years[n]}`,v:`${mean[n].toFixed(2)} K`},{k:`5 to 95% band, ${years[n]}`,v:`${lo[n].toFixed(2)} to ${hi[n].toFixed(2)} K`},{k:`Mean, ${years[0]}`,v:`${mean[0].toFixed(2)} K`}]};
}
function aiTakeaway(years,frac,dmg){
  const n=years.length-1,end=years[n],y05=firstReach(years,frac,0.5),y10=firstReach(years,frac,0.999);
  const t05=y05===null?`not within ${end}`:String(y05),t10=y10===null?`not within ${end}`:String(y10),ds=(dmg[n]*100).toFixed(1)+"%";
  return {sentence:`In this run S3 first reaches half of tasks automated in ${t05} and full automation in ${t10}; damage takes ${ds} of S3's own output in ${end}. Shape only: S3's level is unvalidated after about 2027 (test A1.3 failed).`,
    tiles:[{k:"Automation reaches 0.5",v:t05},{k:"Automation reaches 1.0",v:t10},{k:`Damage share of S3 output, ${end}`,v:ds}]};
}
function damageNotice(damage){
  if(damage==="off")return "";
  return `Climate damage is ON (${damage}). This is a level-of-output effect, not the upper end of the literature. Damage-on runs are NOT compared with WorldDynamics.jl (it has no climate damage). S3's economy and World3's are not reconciled. There is no health or yield effect of warming.`;
}
const DEF_LEVERS=[1,0,0],DMG_STATES=["off","low","central","high"],AI_S=["low","central","race"],AI_D=["low","central","high"];
const PRESETS=[
  {name:"Standard",levers:[1,0,0],text:"World3 with its standard parameters."},
  {name:"More resources",levers:[2,0,0],text:"Twice the starting non-renewable resources."},
  {name:"Farming tech",levers:[1,1,0],text:"Land yield factor 1.5 after 1975."},
  {name:"Pollution cut",levers:[1,0,2],text:"Pollution generation factor 0.25 after 1975."},
  {name:"Combined",levers:[2,1,1],text:"Double resources, land yield 1.5, pollution generation 0.5."}
];
function encodeState(s){return "#w3="+s.levers.join(".")+"&d="+s.damage+"&ai="+s.ai+"&ad="+s.aidmg}
function decodeState(hash,nLevers){
  const out={levers:DEF_LEVERS.slice(0,nLevers),damage:"off",ai:"central",aidmg:"central"};
  try{
    const q={};String(hash||"").replace(/^#/,"").split("&").forEach(p=>{const i=p.indexOf("=");if(i>0)q[p.slice(0,i)]=p.slice(i+1)});
    if(q.w3){const v=q.w3.split(".");if(v.length===nLevers&&v.every(x=>/^[0-2]$/.test(x)))out.levers=v.map(Number)}
    if(DMG_STATES.indexOf(q.d)>=0)out.damage=q.d;
    if(AI_S.indexOf(q.ai)>=0)out.ai=q.ai;
    if(AI_D.indexOf(q.ad)>=0)out.aidmg=q.ad;
  }catch(e){}
  return out;
}
function csvOf(years,cols,notes){
  const q=s=>/[",\n]/.test(s)?'"'+s.replace(/"/g,'""')+'"':s;
  const lines=["year,"+cols.map(c=>q(c.name)).join(",")];
  years.forEach((y,i)=>lines.push(y+","+cols.map(c=>String(c.y[i])).join(",")));
  (notes||[]).forEach(t=>lines.push("# "+t));
  return lines.join("\n")+"\n";
}
/*PURE-END*/
/* ----- readable number formats ----- */
const FMT={
  people:v=>human(v),
  fraction:v=>(+v.toFixed(2)).toString(),
  index:v=>(+v.toPrecision(3)).toString(),
  pct:v=>(+v.toFixed(2))+"%",
  kelvin:v=>(+v.toFixed(2))+" K",
  usd:v=>human(v),
};
/* ----- chart: viewBox is the real pixel size, so text never shrinks ----- */
function niceTicks(lo,hi,n){
  const span=hi-lo||1;const raw=span/n;const mag=Math.pow(10,Math.floor(Math.log10(raw)));
  const f=raw/mag;const step=(f<=1?1:f<=2?2:f<=2.5?2.5:f<=5?5:10)*mag;
  const t0=Math.ceil(lo/step-1e-9)*step;const out=[];for(let v=t0;v<=hi+step*1e-9;v+=step)out.push(+v.toPrecision(12));
  return {ticks:out,step:step};
}
function chart(el,series,o){
  const wrap=$(el);const W=Math.max(300,Math.floor(wrap.clientWidth||340));
  const narrow=W<520;const H=narrow?320:300;
  const FS=13,R=26,B=34;
  const nl=series.filter(s=>s.label).length;const T=28+Math.max(0,nl-1)*15;   /* headroom so stacked end labels sit above the lines */
  const XS=o.years||Y;let xmin=XS[0],xmax=XS[XS.length-1];
  let ymin=Infinity,ymax=-Infinity;
  series.forEach(s=>{(s.band?[s.band[0],s.band[1]]:[]).concat([s.y]).forEach(a=>a.forEach(v=>{if(isFinite(v)){ymin=Math.min(ymin,v);ymax=Math.max(ymax,v)}}))});
  if(o.ymin!==undefined)ymin=o.ymin;if(o.ymax!==undefined)ymax=o.ymax;
  const pad=(ymax-ymin)*.03||1;if(o.ymin===undefined)ymin-=pad;if(o.ymax===undefined)ymax+=pad;
  const fm=FMT[o.fmt||"index"];
  const nt=narrow?4:5;
  const nice=niceTicks(ymin,ymax,nt);
  const labels=nice.ticks.map(fm);
  const L=Math.min(Math.round(W*0.34),Math.max(44,Math.ceil(Math.max(...labels.map(s=>s.length))*7.6)+14));
  const X=x=>L+(x-xmin)/(xmax-xmin)*(W-L-R),Yp=v=>T+(1-(v-ymin)/(ymax-ymin))*(H-T-B);
  const line=CSSV("--line"),mut=CSSV("--mut"),fg=CSSV("--fg");
  let g="";
  nice.ticks.forEach((v,i)=>{const yy=Yp(v);
    g+=`<line x1="${L}" x2="${W-R}" y1="${yy}" y2="${yy}" stroke="${line}"/><text x="${L-6}" y="${yy+4}" text-anchor="end" font-size="${FS}" fill="${mut}">${labels[i]}</text>`});
  const step=o.xstep||(narrow?25:15);
  for(let yr=Math.ceil(xmin/step)*step;yr<=xmax;yr+=step){const anchor="middle";g+=`<text x="${X(yr)}" y="${H-10}" text-anchor="${anchor}" font-size="${FS}" fill="${mut}">${yr}</text>`}
  g+=`<text x="${L}" y="16" font-size="${FS}" font-weight="600" fill="${fg}">${o.unit||""}</text>`;
  const ends=[];
  series.forEach(s=>{
    if(s.band){const up=XS.map((x,i)=>`${X(x)},${Yp(s.band[1][i])}`),dn=XS.map((x,i)=>`${X(x)},${Yp(s.band[0][i])}`).reverse();g+=`<polygon points="${up.concat(dn).join(" ")}" fill="${s.color}" opacity=".2"/>`}
    const pts=XS.map((x,i)=>isFinite(s.y[i])?`${X(x)},${Yp(s.y[i])}`:null).filter(Boolean).join(" ");
    g+=`<polyline points="${pts}" fill="none" stroke="${s.color}" stroke-width="2.4" ${s.dash?`stroke-dasharray="${s.dash}"`:""}/>`;
    if(s.label)ends.push({label:s.label,color:s.color,y:Yp(s.y[XS.length-1])-6});
  });
  /* direct labels at the right end, spaced apart so they never overlap (the legend with dash patterns is the fallback) */
  ends.sort((a,b)=>b.y-a.y);                               /* lowest on screen first; each next label goes up by at least 15 px */
  for(let i=1;i<ends.length;i++){if(ends[i-1].y-ends[i].y<15)ends[i].y=ends[i-1].y-15}
  ends.forEach(e=>{g+=`<text x="${W-R-6}" y="${Math.max(e.y,12)}" text-anchor="end" font-size="${FS}" font-weight="600" fill="${e.color}" stroke="${CSSV("--card")}" stroke-width="3" paint-order="stroke">${e.label}</text>`});
  wrap.innerHTML=`<svg viewBox="0 0 ${W} ${H}" width="${W}" height="${H}" role="img" aria-label="${o.label}. ${o.summary||""}"><title>${o.label}</title><desc>${o.summary||""}</desc>${g}</svg>`;
  wrap._m={XS:XS,series:series,X:X,Yp:Yp,T:T,B:B,W:W,H:H,fm:fm,o:o,el:el,cur:null};
  tools(wrap);
  if(wrap._m.cur!==null&&wrap._m.cur<XS.length)showCursor(wrap,wrap._m.cur);
}
function legend(el,items){$(el).innerHTML=items.map(i=>`<span><svg viewBox="0 0 34 10" aria-hidden="true"><line x1="0" y1="5" x2="34" y2="5" stroke="${i.color}" stroke-width="3" ${i.dash?`stroke-dasharray="${i.dash}"`:""}/></svg>${i.name}</span>`).join("")}
/* ----- reading a chart: hover, touch and keyboard crosshair with a visible readout; PNG and CSV download ----- */
const SVGNS="http://www.w3.org/2000/svg";
function showCursor(wrap,i){
  const m=wrap._m;if(!m)return;const svg=wrap.querySelector("svg");if(!svg)return;
  const n=m.XS.length;i=Math.max(0,Math.min(n-1,i));m.cur=i;
  svg.querySelectorAll(".cur").forEach(e=>e.remove());
  const x=m.X(m.XS[i]);
  const ln=document.createElementNS(SVGNS,"line");ln.setAttribute("class","cur");ln.setAttribute("x1",x);ln.setAttribute("x2",x);ln.setAttribute("y1",m.T);ln.setAttribute("y2",m.H-m.B);ln.setAttribute("stroke",CSSV("--fg"));ln.setAttribute("stroke-width","1.5");svg.appendChild(ln);
  m.series.forEach(s=>{if(!isFinite(s.y[i]))return;const c=document.createElementNS(SVGNS,"circle");c.setAttribute("class","cur");c.setAttribute("cx",x);c.setAttribute("cy",m.Yp(s.y[i]));c.setAttribute("r","4.5");c.setAttribute("fill",s.color);c.setAttribute("stroke",CSSV("--card"));c.setAttribute("stroke-width","1.5");svg.appendChild(c)});
  const rd=$("rd_"+m.el);
  rd.textContent=m.XS[i]+": "+m.series.map(s=>(s.name||"value")+" "+m.fm(s.y[i])+(s.band?" (5 to 95%: "+m.fm(s.band[0][i])+" to "+m.fm(s.band[1][i])+")":"")).join("; ");
}
function clearCursor(wrap){const m=wrap._m;if(!m)return;m.cur=null;wrap.querySelectorAll(".cur").forEach(e=>e.remove());$("rd_"+m.el).textContent="Hover, touch or use the left and right arrow keys to read values."}
function indexAt(wrap,ev){
  const m=wrap._m,svg=wrap.querySelector("svg"),r=svg.getBoundingClientRect(),k=m.W/r.width;
  const xv=(ev.clientX-r.left)*k,L=m.X(m.XS[0]),Rr=m.X(m.XS[m.XS.length-1]);
  return Math.round((xv-L)/(Rr-L)*(m.XS.length-1));
}
function download(blob,name){const a=document.createElement("a");a.href=URL.createObjectURL(blob);a.download=name;document.body.appendChild(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(a.href),2000)}
function caveatLines(m){
  const l=["F3 Explorer v0.1: a conditional scenario, not a forecast."];
  if(m.o.caveat)l.push(m.o.caveat);
  return l;
}
function chartCols(m){
  const cols=[];
  m.series.forEach(s=>{cols.push({name:s.name||"value",y:s.y});if(s.band){cols.push({name:(s.name||"value")+" 5th percentile",y:s.band[0]});cols.push({name:(s.name||"value")+" 95th percentile",y:s.band[1]})}});
  return cols;
}
function downloadCsv(wrap){const m=wrap._m;download(new Blob([csvOf(m.XS,chartCols(m),caveatLines(m))],{type:"text/csv;charset=utf-8"}),(m.o.file||m.el)+".csv")}
function downloadPng(wrap){
  const m=wrap._m,svg=wrap.querySelector("svg").cloneNode(true);
  svg.querySelectorAll(".cur").forEach(e=>e.remove());svg.setAttribute("xmlns",SVGNS);svg.setAttribute("font-family","system-ui, Segoe UI, Roboto, sans-serif");
  const lines=caveatLines(m),S=2,pad=8,lh=17;
  const cv=document.createElement("canvas"),ctx=cv.getContext("2d");
  ctx.font="13px system-ui, Segoe UI, Roboto, sans-serif";
  const wrapped=[];lines.forEach(t=>{let cur="";t.split(" ").forEach(w=>{const tt=cur?cur+" "+w:w;if(ctx.measureText(tt).width>m.W-2*pad&&cur){wrapped.push(cur);cur=w}else cur=tt});wrapped.push(cur)});
  const extra=wrapped.length*lh+pad*2;
  cv.width=m.W*S;cv.height=(m.H+extra)*S;
  const img=new Image();
  img.onload=()=>{
    const c=cv.getContext("2d");c.scale(S,S);c.fillStyle=CSSV("--card");c.fillRect(0,0,m.W,m.H+extra);c.drawImage(img,0,0,m.W,m.H);
    c.fillStyle=CSSV("--mut");c.font="13px system-ui, Segoe UI, Roboto, sans-serif";wrapped.forEach((t,i)=>c.fillText(t,pad,m.H+pad+13+i*lh));
    cv.toBlob(b=>download(b,(m.o.file||m.el)+".png"),"image/png");
  };
  img.src="data:image/svg+xml;charset=utf-8,"+encodeURIComponent(new XMLSerializer().serializeToString(svg));
}
function tools(wrap){
  if(wrap._tools)return;wrap._tools=true;
  wrap.tabIndex=0;wrap.setAttribute("role","group");wrap.setAttribute("aria-label",(wrap._m.o.label||"Chart")+". Use the left and right arrow keys to read values year by year.");
  wrap.insertAdjacentHTML("afterend",`<div class="rd" id="rd_${wrap.id}" aria-live="polite">Hover, touch or use the left and right arrow keys to read values.</div><div class="dl"><button type="button" data-dl="png">Download PNG</button><button type="button" data-dl="csv">Download CSV</button></div>`);
  const bar=wrap.nextElementSibling.nextElementSibling;
  bar.querySelector('[data-dl="png"]').onclick=()=>downloadPng(wrap);bar.querySelector('[data-dl="csv"]').onclick=()=>downloadCsv(wrap);
  const move=e=>{if(!wrap._m)return;showCursor(wrap,indexAt(wrap,e))};
  wrap.addEventListener("pointerdown",move);wrap.addEventListener("pointermove",e=>{if(e.pointerType==="mouse"||e.buttons)move(e)});
  wrap.addEventListener("pointerleave",e=>{if(e.pointerType==="mouse")clearCursor(wrap)});
  wrap.addEventListener("keydown",e=>{
    const m=wrap._m;if(!m)return;const n=m.XS.length;let i=m.cur;
    if(e.key==="ArrowRight"||e.key==="ArrowLeft"){const d=(e.key==="ArrowRight"?1:-1)*(e.shiftKey?10:1);i=i===null?(d>0?0:n-1):i+d}
    else if(e.key==="Home")i=0;else if(e.key==="End")i=n-1;else if(e.key==="Escape"){clearCursor(wrap);return}else return;
    e.preventDefault();showCursor(wrap,i);
  });
}
/* ----- takeaway cards ----- */
function setTake(id,t){
  const c=$(id);c.textContent="";
  const p=document.createElement("p");p.className="tk";p.textContent=t.sentence;c.appendChild(p);
  const row=document.createElement("div");row.className="tiles";
  t.tiles.forEach(x=>{const d=document.createElement("div");d.className="tile";const k=document.createElement("span");k.className="tk_k";k.textContent=x.k;const v=document.createElement("strong");v.className="tk_v";v.textContent=x.v;d.appendChild(k);d.appendChild(v);row.appendChild(d)});
  c.appendChild(row);
}
const C=["--c1","--c2","--c3","--c4","--c5"];
const cl=n=>CSSV(n);
const first=(a)=>a[0],last=(a)=>a[a.length-1];

/* ---------- World3 panel ---------- */
const W=D.world3,NL=W.levers.length,W3Y=W.years;
const DMG_LABEL={off:"off (default)",low:"low (Nordhaus 2017)",central:"central (Barrage and Nordhaus 2024)",high:"high (Howard and Sterner 2017; not the upper end)"};
function stdKey(){return W.standard+"|off"}
function readState(){return {levers:W.levers.map((l,i)=>+$("w3_"+i).value),damage:$("w3_damage").value,ai:$("sel_s").value,aidmg:$("sel_d").value}}
function writeState(s){s.levers.forEach((v,i)=>{$("w3_"+i).value=String(v)});$("w3_damage").value=s.damage;$("sel_s").value=s.ai;$("sel_d").value=s.aidmg}
function pushHash(){try{history.replaceState(null,"",encodeState(readState()))}catch(e){}}
function buildW3Controls(){
  $("w3_presets").innerHTML=PRESETS.map((p,i)=>`<button type="button" class="pre" data-i="${i}" title="${p.text}">${p.name}</button>`).join("")+`<button type="button" class="pre reset" id="w3_reset">Reset</button>`;
  $("w3_presets").querySelectorAll("button.pre[data-i]").forEach(b=>{b.onclick=()=>{const p=PRESETS[+b.dataset.i];const s=readState();s.levers=p.levers.slice();writeState(s);refresh()}});
  $("w3_reset").onclick=()=>{writeState(decodeState("",NL));refresh()};
  $("w3ctl").innerHTML=W.levers.map((l,i)=>`<label>${l.label}<br><select id="w3_${i}">${l.value_labels.map((v,j)=>`<option value="${j}"${j===l.standard_index?" selected":""}>${v}</option>`).join("")}</select></label>`).join("");
  W.levers.forEach((l,i)=>{$("w3_"+i).onchange=refresh});
  $("w3_damage").innerHTML=W.damage_states.map(d=>`<option value="${d}"${d==="off"?" selected":""}>${DMG_LABEL[d]}</option>`).join("");
  $("w3_damage").onchange=refresh;
  $("w3status").innerHTML=Object.entries(W.status).map(([k,v])=>`<li><strong>${k}</strong>: ${v}</li>`).join("")+`<li><strong>Parameter set</strong>: ${W.parameter_set}</li>`;
}
function drawChips(st){
  const chips=[];
  W.levers.forEach((l,i)=>{if(st.levers[i]!==l.standard_index)chips.push(`${l.label}: ${l.value_labels[st.levers[i]]}`)});
  if(st.damage!=="off")chips.push(`Climate damage: ${st.damage}`);
  $("w3_chips").innerHTML=chips.length?chips.map(c=>`<span class="chip">${c}</span>`).join(""):`<span class="chip std">Standard run, climate damage off</span>`;
  $("w3_presets").querySelectorAll("button.pre[data-i]").forEach(b=>{const p=PRESETS[+b.dataset.i];b.setAttribute("aria-pressed",String(p.levers.join(".")===st.levers.join(".")))});
  if(!PRESETS.some(p=>p.levers.join(".")===st.levers.join(".")))$("w3_custom").open=true;
}
function drawW3(){
  const st=readState(),lk=st.levers.join("|"),k=lk+"|"+st.damage,r=W.runs[k],std=W.runs[stdKey()],off=W.runs[lk+"|off"];
  drawChips(st);
  $("w3_damage_notice").textContent=damageNotice(st.damage);
  const refs=[];
  if(k!==stdKey())refs.push({n:"standard, damage off",run:std,dash:"7 4",col:"--mut"});
  if(st.damage!=="off"&&lk!==W.standard)refs.push({n:"same settings, damage off",run:off,dash:"2 3",col:"--c5"});
  $("w3_text").textContent=refs.length?"The grey dashed curve is the standard run (damage off)"+(refs.length>1?"; the dotted curve is the same lever settings with damage off":"")+", for comparison.":"";
  $("w3_text").style.display=refs.length?"block":"none";
  const ser=(name,kk,col)=>{const a=[{name:name+(refs.length?" (chosen)":""),color:cl(col),y:r[kk]}];refs.forEach(x=>a.push({name:name+" ("+x.n+")",color:cl(x.col),y:x.run[kk],dash:x.dash}));return a};
  const cav=st.damage==="off"?"":damageNotice(st.damage);
  const o=(u,l,f,sum,x,file)=>Object.assign({years:W3Y,xstep:50,unit:u,label:l,fmt:f,summary:sum,file:"f3-"+file+"-damage-"+st.damage+"-"+lk.replace(/\|/g,""),caveat:cav},x||{});
  const pk=peakOf(W3Y,r.pop),e=W3Y.length-1;
  const pop=ser("Population","pop","--c1");
  chart("ch_w3pop",pop,o("People","World3 population, 1900-2100","people",`Chosen run: ${human(r.pop[0])} in 1900, peak ${human(pk[1])} around ${pk[0]}, ${human(r.pop[e])} in 2100.`,null,"world3-population"));legend("lg_w3pop",pop);
  const io=ser("Industrial output","io","--c3");
  chart("ch_w3io",io,o("Model dollars per year","World3 industrial output, 1900-2100","usd",`Chosen run: ${human(r.io[W3Y.indexOf(2025)])} model dollars a year in 2025, ${human(r.io[e])} in 2100.${st.damage==="off"?"":" Climate damage lowers it from 2025 (level-of-output effect)."}`,{ymin:0},"world3-industrial-output"));legend("lg_w3io",io);
  const nr=ser("Resources remaining (fraction of start)","nrfr","--c2");
  chart("ch_w3nr",nr,o("Fraction of starting stock","World3 non-renewable resources remaining, 1900-2100","fraction",`Chosen run: falls from 1 to ${r.nrfr[e].toFixed(2)} by 2100.`,{ymin:0,ymax:1.02},"world3-resources"));legend("lg_w3nr",nr);
  const pp=peakOf(W3Y,r.ppolx);
  const pl=ser("Persistent pollution index (1 = 1970 level)","ppolx","--c4");
  chart("ch_w3pol",pl,o("Pollution index (1 = 1970)","World3 persistent pollution index, 1900-2100","index",`Chosen run: peaks at ${pp[1].toFixed(1)} times the 1970 level around ${pp[0]}, ${r.ppolx[e].toFixed(2)} in 2100.`,{ymin:0},"world3-pollution"));legend("lg_w3pol",pl);
  setTake("tk_w3",w3Takeaway(W3Y,r,off,st.damage));
}

/* ---------- AI race and climate panels ---------- */
function draw(){
  const s=$("sel_s").value,d=$("sel_d").value;
  $("setting_text").textContent="AI setting: "+s+" ("+D.meta.settings[s]+"). Damage option: "+d+" ("+D.meta.damage_sources[d]+").";
  const names=["low","central","race"];
  const au=names.map((n,i)=>({name:n+(n===s?" (selected)":""),color:cl(C[i]),dash:DASH[i],y:D.runs[key(n,d)].frac_automated,label:n}));
  const k50=n=>{const y=D.runs[key(n,d)].frac_automated;const i=y.findIndex(v=>v>=0.5);return i<0?"never":Y[i]};
  const cut=Y.indexOf(2050)+1;                                  /* 2025-2050 only; all settings reach 1.0 after about 2045 */
  const aus=au.map(s=>Object.assign({},s,{y:s.y.slice(0,cut)}));
  chart("ch_auto",aus,{years:Y.slice(0,cut),xstep:5,unit:"Fraction of tasks automated",fmt:"fraction",ymin:0,ymax:1.02,label:"Automation fraction, three AI settings, 2025-2050",file:"f3-ai-automation-damage-"+d,
     caveat:"S3 is unvalidated against GATE after about 2027 (test A1.3 failed); shape only.",
     summary:`Shape only, 2025 to 2050. Year the fraction first reaches 0.5: low ${k50("low")}, central ${k50("central")}, race ${k50("race")} (the same year; the race setting is higher before and after). All settings reach 1.0 after about 2045.`});legend("lg_auto",aus);
  const full=n=>{const y=D.runs[key(n,d)].frac_automated;const j=y.findIndex(v=>v>=0.999);return j<0?"not within 2100":Y[j]};
  $("auto_note").textContent=`Axis shows 2025-2050. All settings reach 1.0 after about 2045 (first year at 1.0: low ${full("low")}, central ${full("central")}, race ${full("race")}; a year after 2050 is beyond the axis).`;
  const T=D.climate;
  chart("ch_temp",[{name:"FaIR ensemble mean",color:cl("--c2"),y:T.warming,band:[T.warming_p05,T.warming_p95]}],{unit:"Warming above 1850-1900",fmt:"kelvin",label:"FaIR warming, 841 members",file:"f3-fair-warming",
     caveat:"FaIR starts about 0.04 to 0.07 K below observed (test A2.1 failed); emissions are prescribed.",
     summary:`Ensemble mean ${T.warming[0].toFixed(2)} K in 2025 and ${last(T.warming).toFixed(2)} K in 2100; 5-95% band ${T.warming_p05[N-1].toFixed(2)} to ${T.warming_p95[N-1].toFixed(2)} K in 2100. Starts about 0.04 to 0.07 K below observed.`});
  legend("lg_temp",[{name:"FaIR ensemble mean (line) and 5-95% band of 841 members (shaded)",color:cl("--c2")}]);
  setTake("tk_climate",climateTakeaway(Y,T.warming,T.warming_p05,T.warming_p95));
  const dm=["low","central","high"].map((o,i)=>({name:o+(o==="high"?" (not the upper end of the literature)":""),color:cl(C[i]),dash:DASH[i],y:D.runs[key(s,o)].damage_fraction.map(v=>v*100),label:o}));
  const i2100=N-1;
  chart("ch_dmg",dm,{unit:"Share of S3 output lost (%)",fmt:"pct",ymin:0,label:"Damage options as a share of S3 output",file:"f3-ai-damage-share",
     caveat:"Level-of-output effect, not the upper end of the literature; shares of S3's own, unvalidated output.",
     summary:`Share of S3's own (unvalidated) output lost in 2100: low ${(D.runs[key(s,"low")].damage_fraction[i2100]*100).toFixed(1)}%, central ${(D.runs[key(s,"central")].damage_fraction[i2100]*100).toFixed(1)}%, high ${(D.runs[key(s,"high")].damage_fraction[i2100]*100).toFixed(1)}%.`});legend("lg_dmg",dm);
  const run=D.runs[key(s,d)];
  setTake("tk_ai",aiTakeaway(Y,run.frac_automated,run.damage_fraction));
  $("tb_dmg").innerHTML="<tr><th>Option</th><th>c (% per K^2)</th><th>Share of S3 output lost in 2100</th></tr>"+["low","central","high"].map(o=>`<tr><td>${o}</td><td>${D.meta.damage_coeff_pct_per_K2[o].toFixed(4)}${o==="low"?"":" (derived)"}</td><td>${(D.runs[key(s,o)].damage_fraction[i2100]*100).toFixed(2)}%</td></tr>`).join("");
  $("tb_coef").innerHTML="<tr><th>Option</th><th>Source</th></tr>"+["low","central","high"].map(o=>`<tr><td>${o}</td><td>${D.meta.damage_sources[o]}</td></tr>`).join("");
}
/* The first year the automated fraction is at least 0.5, and the fraction the year before and in that year (all read from the data). */
function cross(y,th){const j=y.findIndex(v=>v>=th);return j<0?null:{year:Y[j],at:y[j],before:j>0?y[j-1]:null}}
function r1Sentence(){
  const parts=["low","central","race"].map(n=>{const c=cross(D.runs[key(n,"central")].frac_automated,0.5);
    return c?`${n}: ${c.year} (fraction ${c.before===null?"n/a":c.before.toFixed(2)} the year before, ${c.at.toFixed(2)} that year)`:`${n}: never`});
  const all=["low","central","race"].map(n=>cross(D.runs[key(n,"central")].frac_automated,0.5));
  const same=all.every(c=>c&&c.year===all[0].year);
  return `<strong>R1</strong> (more AI investment, more automation): the first year the automated fraction reaches 0.5 is ${parts.join("; ")}. `+
    (same?`The year is the same in all three settings because the crossing happens within one year-step; the race setting is already higher before and after it. `:"")+
    `Every setting reaches 1.0 after about 2045. (The recorded R1 sign test failed on exactly this kind of saturation.)`;
}
function signs(){
  $("signs").innerHTML="<ul>"+
  `<li id="r1text">${r1Sentence()}</li>`+
  `<li><strong>B1</strong> (less electricity, slower compute growth): the recorded test failed as written (a lower-supply run had more compute in some years). Compute values are withheld above.</li>`+
  `<li><strong>B2</strong> (more damage, lower output): the share of output lost in 2100 is ${(D.runs[key("central","high")].damage_fraction[N-1]*100).toFixed(1)}% (high) against ${(D.runs[key("central","low")].damage_fraction[N-1]*100).toFixed(1)}% (low); the sign test passed.</li></ul>`;
}
/* ---------- definitions on touch and keyboard (the title attribute alone does not work on a phone) ---------- */
function defs(){
  const close=()=>document.querySelectorAll(".defpop").forEach(x=>x.remove());
  document.querySelectorAll("abbr[title]").forEach(a=>{
    a.tabIndex=0;
    const toggle=()=>{const open=a._pop&&a._pop.isConnected;close();if(open)return;const p=document.createElement("span");p.className="defpop";p.setAttribute("role","status");p.textContent=a.getAttribute("title");a.after(p);a._pop=p};
    a.addEventListener("click",e=>{e.stopPropagation();toggle()});
    a.addEventListener("keydown",e=>{if(e.key==="Enter"||e.key===" "){e.preventDefault();toggle()}else if(e.key==="Escape")close()});
  });
  document.addEventListener("click",e=>{if(!e.target.closest("abbr"))close()});
}
function drawStripes(){
  const T=D.climate.warming,lo=Math.min(...T),hi=Math.max(...T),n=T.length,w=320/n;
  const A=[33,102,172],M=[247,247,247],R=[178,24,43];
  const mix=(p,q,t)=>p.map((v,i)=>Math.round(v+(q[i]-v)*t));
  const col=v=>{const t=(v-lo)/((hi-lo)||1);const c=t<0.5?mix(A,M,t*2):mix(M,R,(t-0.5)*2);return "rgb("+c.join(",")+")"};
  $("stripes_g").innerHTML=T.map((v,i)=>`<rect x="${(i*w).toFixed(2)}" y="0" width="${(w+0.6).toFixed(2)}" height="84" fill="${col(v)}"/>`).join("");
  $("stripes_l").textContent=Y[0]+": "+lo.toFixed(2)+" K";$("stripes_r").textContent=Y[n-1]+": "+hi.toFixed(2)+" K";
}
function refresh(){pushHash();drawW3();draw();signs()}
buildW3Controls();
$("sel_s").onchange=refresh;$("sel_d").onchange=refresh;
writeState(decodeState(location.hash,NL));
addEventListener("hashchange",()=>{writeState(decodeState(location.hash,NL));drawW3();draw()});
let lastW=0;
function all(){lastW=document.documentElement.clientWidth;drawW3();draw();signs();drawStripes()}all();
defs();
matchMedia("(prefers-color-scheme: dark)").addEventListener("change",all);
addEventListener("resize",()=>{if(Math.abs(document.documentElement.clientWidth-lastW)>40)all()});
