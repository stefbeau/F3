const D=/*DATA*/null;
const $=id=>document.getElementById(id);
const Y=D.years,N=Y.length;
const CSSV=n=>getComputedStyle(document.documentElement).getPropertyValue(n).trim();
$("s3status").textContent=D.meta.s3_status;$("s6status").textContent=D.meta.s6_status;
$("prov").textContent=JSON.stringify(D.meta.provenance,null,1);
function key(s,d,sup){return s+"|"+d+"|"+(sup||"1")}
const DASH=[null,"7 4","2 3","10 3 2 3","1 0"];
/* ----- readable number formats ----- */
function human(v){const a=Math.abs(v);if(a>=1e9)return (+(v/1e9).toPrecision(3))+" billion";if(a>=1e6)return (+(v/1e6).toPrecision(3))+" million";return (+v.toPrecision(3)).toString()}
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
}
function legend(el,items){$(el).innerHTML=items.map(i=>`<span><svg viewBox="0 0 34 10" aria-hidden="true"><line x1="0" y1="5" x2="34" y2="5" stroke="${i.color}" stroke-width="3" ${i.dash?`stroke-dasharray="${i.dash}"`:""}/></svg>${i.name}</span>`).join("")}
const C=["--c1","--c2","--c3","--c4","--c5"];
const cl=n=>CSSV(n);
const first=(a)=>a[0],last=(a)=>a[a.length-1];
const peak=(y,xs)=>{let k=0;y.forEach((v,i)=>{if(v>y[k])k=i});return [xs[k],y[k]]};

/* ---------- World3 panel ---------- */
const W=D.world3;
function buildW3Controls(){
  $("w3ctl").innerHTML=W.levers.map((l,i)=>`<label>${l.label}<br><select id="w3_${i}">${l.value_labels.map((v,j)=>`<option value="${j}"${j===l.standard_index?" selected":""}>${v}</option>`).join("")}</select></label>`).join("");
  W.levers.forEach((l,i)=>{$("w3_"+i).onchange=drawW3});
  $("w3status").innerHTML=Object.entries(W.status).map(([k,v])=>`<li><strong>${k}</strong>: ${v}</li>`).join("")+`<li><strong>Parameter set</strong>: ${W.parameter_set}</li>`;
}
function w3key(){return W.levers.map((l,i)=>$("w3_"+i).value).join("|")}
function drawW3(){
  const k=w3key(),r=W.runs[k],s=W.runs[W.standard],isStd=(k===W.standard);
  $("w3_text").textContent=isStd?"":"Changed parameters: "+W.levers.map((l,i)=>l.value_labels[+$("w3_"+i).value]).join("; ")+". The grey dashed curve is the standard run, for comparison.";
  $("w3_text").style.display=isStd?"none":"block";
  const ser=(name,key,col,fmt)=>{const a=[{name:name+(isStd?"":" (chosen)"),color:cl(col),y:r[key]}];if(!isStd)a.push({name:name+" (standard)",color:cl("--mut"),y:s[key],dash:"7 4"});return a};
  const o=(u,l,f,sum,x)=>Object.assign({years:W.years,xstep:50,unit:u,label:l,fmt:f,summary:sum},x||{});
  const pk=peak(r.pop,W.years);
  const pop=ser("Population","pop","--c1");
  chart("ch_w3pop",pop,o("People","World3 population, 1900-2100","people",`Chosen run: ${human(r.pop[0])} in 1900, peak ${human(pk[1])} around ${pk[0]}, ${human(last(r.pop))} in 2100.`));legend("lg_w3pop",pop);
  const nr=ser("Resources remaining (fraction of start)","nrfr","--c2");
  chart("ch_w3nr",nr,o("Fraction of starting stock","World3 non-renewable resources remaining, 1900-2100","fraction",`Chosen run: falls from 1 to ${last(r.nrfr).toFixed(2)} by 2100.`,{ymin:0,ymax:1.02}));legend("lg_w3nr",nr);
  const pp=peak(r.ppolx,W.years);
  const pl=ser("Persistent pollution index (1 = 1970 level)","ppolx","--c4");
  chart("ch_w3pol",pl,o("Pollution index (1 = 1970)","World3 persistent pollution index, 1900-2100","index",`Chosen run: peaks at ${pp[1].toFixed(1)} times the 1970 level around ${pp[0]}, ${last(r.ppolx).toFixed(2)} in 2100.`,{ymin:0}));legend("lg_w3pol",pl);
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
  chart("ch_auto",aus,{years:Y.slice(0,cut),xstep:5,unit:"Fraction of tasks automated",fmt:"fraction",ymin:0,ymax:1.02,label:"Automation fraction, three AI settings, 2025-2050",
     summary:`Shape only, 2025 to 2050. Year the fraction first reaches 0.5: low ${k50("low")}, central ${k50("central")}, race ${k50("race")} (the same year; the race setting is higher before and after). All settings reach 1.0 after about 2045.`});legend("lg_auto",aus);
  const full=n=>{const y=D.runs[key(n,d)].frac_automated;const j=y.findIndex(v=>v>=0.999);return j<0?"not within 2100":Y[j]};
  $("auto_note").textContent=`Axis shows 2025-2050. All settings reach 1.0 after about 2045 (first year at 1.0: low ${full("low")}, central ${full("central")}, race ${full("race")}; a year after 2050 is beyond the axis).`;
  const T=D.climate;
  chart("ch_temp",[{name:"FaIR ensemble mean, 5-95% band",color:cl("--c2"),y:T.warming,band:[T.warming_p05,T.warming_p95]}],{unit:"Warming above 1850-1900",fmt:"kelvin",label:"FaIR warming, 841 members",
     summary:`Ensemble mean ${T.warming[0].toFixed(2)} K in 2025 and ${last(T.warming).toFixed(2)} K in 2100; 5-95% band ${T.warming_p05[N-1].toFixed(2)} to ${T.warming_p95[N-1].toFixed(2)} K in 2100. Starts about 0.04 to 0.07 K below observed.`});
  legend("lg_temp",[{name:"FaIR ensemble mean (line) and 5-95% band of 841 members (shaded)",color:cl("--c2")}]);
  const dm=["low","central","high"].map((o,i)=>({name:o+(o==="high"?" (not the upper end of the literature)":""),color:cl(C[i]),dash:DASH[i],y:D.runs[key(s,o)].damage_fraction.map(v=>v*100),label:o}));
  const i2100=N-1;
  chart("ch_dmg",dm,{unit:"Share of S3 output lost (%)",fmt:"pct",ymin:0,label:"Damage options as a share of S3 output",
     summary:`Share of S3's own (unvalidated) output lost in 2100: low ${(D.runs[key(s,"low")].damage_fraction[i2100]*100).toFixed(1)}%, central ${(D.runs[key(s,"central")].damage_fraction[i2100]*100).toFixed(1)}%, high ${(D.runs[key(s,"high")].damage_fraction[i2100]*100).toFixed(1)}%.`});legend("lg_dmg",dm);
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
buildW3Controls();
$("sel_s").onchange=draw;$("sel_d").onchange=draw;
let lastW=0;
function all(){lastW=document.documentElement.clientWidth;drawW3();draw();signs()}all();
matchMedia("(prefers-color-scheme: dark)").addEventListener("change",all);
addEventListener("resize",()=>{if(Math.abs(document.documentElement.clientWidth-lastW)>40)all()});
