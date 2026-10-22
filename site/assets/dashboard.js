/* F3 Explorer dashboard (D-056 stage 3). Left rail chooses the scenario; one main chart; details and tests below. Every number, headline and tile is
   computed from window.F3DATA by core.js: this file holds no model numbers. */
(function () {
  "use strict";
  var D = window.F3DATA, F3 = window.F3, C = window.F3C, W = D.world3, WY = W.years, N = WY.length - 1, NL = W.levers.length, AY = D.years;
  var $ = function (id) { return document.getElementById(id); };
  var DASH = [null, "7 4", "2 3"];
  var STD = W.levers.map(function (l) { return l.standard_index; });
  var DMG_LABEL = { off: "Off", low: "Low", central: "Central", high: "High" };
  $("s3status").textContent = D.meta.s3_status; $("s6status").textContent = D.meta.s6_status;
  $("prov").textContent = JSON.stringify(D.meta.provenance, null, 1);
  $("w3status").innerHTML = Object.entries(W.status).map(function (kv) { return "<li><strong>" + C.esc(kv[0]) + "</strong>: " + C.esc(kv[1]) + "</li>"; }).join("") + "<li><strong>Parameter set</strong>: " + C.esc(W.parameter_set) + "</li>";

  /* ---------- state: the controls are the single source; the URL hash mirrors them ---------- */
  function readState() { return { levers: W.levers.map(function (l, i) { return +$("w3_" + i).value; }), damage: $("dmg_seg").dataset.v || "off", ai: $("sel_s").value, aidmg: $("sel_d").value }; }
  function writeState(s) { s.levers.forEach(function (v, i) { $("w3_" + i).value = String(v); }); $("dmg_seg").dataset.v = s.damage; $("sel_s").value = s.ai; $("sel_d").value = s.aidmg; }
  function pushHash() { try { history.replaceState(null, "", F3.encodeState(readState())); } catch (e) { /* hash is a convenience */ } }
  function buildControls() {
    $("presets").innerHTML = F3.PRESETS.map(function (p, i) { return '<button type="button" class="presetbtn" data-i="' + i + '" aria-pressed="false"><strong>' + C.esc(p.name) + "</strong><span>" + C.esc(p.text) + "</span></button>"; }).join("");
    $("presets").querySelectorAll("button").forEach(function (b) { b.onclick = function () { var s = readState(); s.levers = F3.PRESETS[+b.dataset.i].levers.slice(); writeState(s); refresh(); }; });
    $("w3ctl").innerHTML = W.levers.map(function (l, i) {
      return "<label>" + C.esc(l.label) + '<select id="w3_' + i + '">' + l.value_labels.map(function (v, j) { return '<option value="' + j + '"' + (j === l.standard_index ? " selected" : "") + ">" + C.esc(v) + "</option>"; }).join("") + "</select></label>";
    }).join("");
    W.levers.forEach(function (l, i) { $("w3_" + i).onchange = refresh; });
    $("dmg_seg").dataset.v = "off";
    $("reset").onclick = function () { writeState(F3.decodeState("", NL)); refresh(); };
    $("sel_s").onchange = refresh; $("sel_d").onchange = refresh;
  }
  function drawSeg() {
    var cur = $("dmg_seg").dataset.v, have = $("dmg_seg").querySelectorAll("button");
    if (have.length === F3.DMG_STATES.length) { have.forEach(function (b) { b.setAttribute("aria-pressed", String(b.dataset.v === cur)); }); return; }      /* update in place so keyboard focus is kept */
    $("dmg_seg").innerHTML = F3.DMG_STATES.map(function (d) { return '<button type="button" class="segb" data-v="' + d + '" aria-pressed="' + (d === cur) + '">' + DMG_LABEL[d] + "</button>"; }).join("");
    $("dmg_seg").querySelectorAll("button").forEach(function (b) { b.onclick = function () { $("dmg_seg").dataset.v = b.dataset.v; refresh(); }; });
  }

  /* ---------- World3: headline, tiles, main chart, secondary charts ---------- */
  function drawW3() {
    var st = readState(), sc = C.scen(), lk = st.levers.join("|"), run = W.runs[F3.runKey(st.levers, st.damage)], std = W.runs[F3.runKey(STD, "off")], off = W.runs[F3.runKey(st.levers, "off")];
    var isStd = st.levers.join(".") === STD.join(".") && st.damage === "off", name = F3.scenarioName(st.levers, st.damage);
    drawSeg();
    $("presets").querySelectorAll("button").forEach(function (b) { b.setAttribute("aria-pressed", String(F3.PRESETS[+b.dataset.i].levers.join(".") === st.levers.join("."))); });
    if (!F3.PRESETS.some(function (p) { return p.levers.join(".") === st.levers.join("."); })) $("custom").open = true;
    var chips = [];
    W.levers.forEach(function (l, i) { if (st.levers[i] !== l.standard_index) chips.push(l.label + ": " + l.value_labels[st.levers[i]]); });
    if (st.damage !== "off") chips.push("Climate damage: " + st.damage);
    $("w3_chips").innerHTML = chips.length ? chips.map(function (c) { return '<span class="chip">' + C.esc(c) + "</span>"; }).join("") : '<span class="chip std">Standard run, climate damage off</span>';
    $("w3_damage_notice").textContent = F3.damageNotice(st.damage);
    var head = F3.popFinding(WY, run, std, isStd ? "In the standard run" : "In " + name);
    $("headline").textContent = head;
    $("kpis").innerHTML = F3.w3Kpis(WY, run, std, off, st.damage).slice(0, 5).map(function (t) { return '<div class="tile"><span class="tk_k">' + C.esc(t.k) + '</span><strong class="tk_v">' + C.esc(t.v) + '</strong><span class="tk_s">' + C.esc(t.sub) + "</span></div>"; }).join("");
    var refs = [];
    if (!isStd) refs.push({ n: "standard, damage off", run: std, dash: "7 4", color: sc.base, tcolor: sc.baseT, label: "Standard", width: 2 });
    if (st.damage !== "off" && lk !== STD.join("|")) refs.push({ n: "same settings, damage off", run: off, dash: "2 3", color: sc.a, tcolor: sc.aT, label: "Damage off", width: 2 });
    else if (st.damage !== "off" && !refs.length) refs.push({ n: "damage off", run: off, dash: "2 3", color: sc.a, tcolor: sc.aT, label: "Damage off", width: 2 });
    $("w3_text").textContent = refs.length ? "Dashed grey: the standard run (damage off), for comparison." + (refs.some(function (r) { return r.n !== "standard, damage off"; }) ? " Dotted: the same settings with damage off." : "") : "";
    var cav = F3.damageNotice(st.damage);
    var lines = function (kk, nm) {
      var a = refs.map(function (r) { return { name: nm + " (" + r.n + ")", label: r.label, color: r.color, tcolor: r.tcolor, dash: r.dash, width: r.width, y: r.run[kk] }; });
      a.push({ name: nm + " (" + name + ")", label: isStd ? "Standard" : "Chosen", color: sc.a, tcolor: sc.aT, y: run[kk] });
      return a;
    };
    var file = function (x) { return "f3-" + x + "-damage-" + st.damage + "-" + lk.replace(/\|/g, ""); };
    var pk = F3.peakOf(WY, run.pop);
    var sum = head + ". " + (cav ? cav + " " : "") + "Model run, not a forecast.";
    C.lineChart($("ch_main"), { title: false, years: WY, xstep: 50, tableStep: 10, unit: "People (World3 population, 1900-2100)", fmt: "people", ymin: 0, file: file("world3-population"), caveat: cav, label: "World3 population", summary: sum, series: lines("pop", "Population"),
      annotations: [{ x: pk[0], y: pk[1], text: "Peak " + F3.human(pk[1]) + ", " + pk[0], color: sc.a, tcolor: sc.aT }] });
    $("ch_main").querySelector(".plot").setAttribute("aria-label", head);
    var sec = function (id, kk, nm, title, unit, fmt, extra, f, summary) {
      C.lineChart($(id), Object.assign({ title: title, years: WY, xstep: 50, tableStep: 10, unit: unit, fmt: fmt, file: file(f), caveat: cav, label: nm, summary: summary, series: lines(kk, nm) }, extra || {}));
    };
    var tio = F3.industryFinding(WY, run, off, st.damage), tnr = F3.resourcesFinding(WY, run), tpo = F3.pollutionFinding(WY, run);
    sec("ch_io", "io", "Industrial output", tio, "Model dollars per year (World3's own constant dollars)", "usd", { ymin: 0 }, "world3-industrial-output", tio + "." + (cav ? " " + cav : ""));
    sec("ch_nr", "nrfr", "Resources remaining", tnr, "Fraction of starting stock", "fraction", { ymin: 0, ymax: 1.02 }, "world3-resources", tnr + ".");
    sec("ch_pol", "ppolx", "Persistent pollution index", tpo, "Pollution index (1 = 1970 level)", "index", { ymin: 0 }, "world3-pollution", tpo + ".");
  }

  /* ---------- climate and AI race (in Details) ---------- */
  function stripes() {
    var T = D.climate.warming, lo = Math.min.apply(null, T), hi = Math.max.apply(null, T), n = T.length, w = 320 / n, A = [33, 102, 172], M = [247, 247, 247], R = [178, 24, 43];
    var mix = function (p, q, t) { return p.map(function (v, i) { return Math.round(v + (q[i] - v) * t); }); };
    var col = function (v) { var t = (v - lo) / ((hi - lo) || 1), c = t < 0.5 ? mix(A, M, t * 2) : mix(M, R, (t - 0.5) * 2); return "rgb(" + c.join(",") + ")"; };
    $("stripes_g").innerHTML = T.map(function (v, i) { return '<rect x="' + (i * w).toFixed(2) + '" y="0" width="' + (w + 0.6).toFixed(2) + '" height="84" fill="' + col(v) + '"/>'; }).join("");
    $("stripes_l").textContent = AY[0] + ": " + lo.toFixed(2) + " K"; $("stripes_r").textContent = AY[n - 1] + ": " + hi.toFixed(2) + " K";
  }
  function drawClimate() {
    var sc = C.scen(), T = D.climate, t = F3.temperatureFinding(AY, T.warming, T.warming_p05, T.warming_p95);
    C.lineChart($("ch_temp"), { title: t, years: AY, xstep: 15, tableStep: 5, unit: "Warming above 1850-1900", fmt: "kelvin", file: "f3-fair-warming", label: "FaIR warming, 841 members",
      caveat: "FaIR starts about 0.04 to 0.07 K below observed (test A2.1 failed); emissions are prescribed.", summary: t + ". FaIR starts about 0.04 to 0.07 K below observed (test A2.1 failed); emissions are prescribed.",
      series: [{ name: "FaIR ensemble mean (line) and 5-95% band of 841 members (shaded)", label: "FaIR mean", color: sc.heat, tcolor: sc.heat, y: T.warming, band: [T.warming_p05, T.warming_p95] }] });
  }
  function cross(y, th) { var j = y.findIndex(function (v) { return v >= th; }); return j < 0 ? null : { year: AY[j], at: y[j], before: j > 0 ? y[j - 1] : null }; }
  function r1Sentence() {
    var fr = function (n) { return D.runs[F3.aiKey(n, "central")].frac_automated; };
    var parts = F3.AI_S.map(function (n) { var c = cross(fr(n), 0.5); return c ? n + ": " + c.year + " (fraction " + (c.before === null ? "n/a" : c.before.toFixed(2)) + " the year before, " + c.at.toFixed(2) + " that year)" : n + ": never"; });
    var all = F3.AI_S.map(function (n) { return cross(fr(n), 0.5); });
    var same = all.every(function (c) { return c && c.year === all[0].year; });
    return "<strong>R1</strong> (more AI investment, more automation): the first year the automated fraction reaches 0.5 is " + parts.join("; ") + ". " +
      (same ? "The year is the same in all three settings because the crossing happens within one year-step; the race setting is already higher before and after it. " : "") +
      "Every setting reaches 1.0 after about 2045. (The recorded R1 sign test failed on exactly this kind of saturation.)";
  }
  function signs() {
    var n = AY.length - 1, hi = D.runs[F3.aiKey("central", "high")].damage_fraction[n], lo = D.runs[F3.aiKey("central", "low")].damage_fraction[n];
    $("signs").innerHTML = "<ul><li id=\"r1text\">" + r1Sentence() + "</li>" +
      "<li><strong>B1</strong> (less electricity, slower compute growth): the recorded test failed as written (a lower-supply run had more compute in some years). Compute values are withheld above.</li>" +
      "<li><strong>B2</strong> (more damage, lower output): the share of output lost in " + AY[n] + " is " + (hi * 100).toFixed(1) + "% (high) against " + (lo * 100).toFixed(1) + "% (low); the sign test passed.</li></ul>";
  }
  function drawAI() {
    var sc = C.scen(), s = $("sel_s").value, d = $("sel_d").value, cols = [sc.acc1, sc.acc2, sc.acc3], cut = AY.indexOf(2050) + 1, yrs = AY.slice(0, cut);
    $("setting_text").textContent = "AI setting: " + s + " (" + D.meta.settings[s] + "). Damage option: " + d + " (" + D.meta.damage_sources[d] + ").";
    var fr = function (n) { return D.runs[F3.aiKey(n, d)].frac_automated; }, t = F3.automationFinding(AY, fr(s), s);
    C.lineChart($("ch_auto"), { title: t, years: yrs, xstep: 5, tableStep: 5, unit: "Fraction of tasks automated (S3, levels unvalidated)", fmt: "fraction", ymin: 0, ymax: 1.02, file: "f3-ai-automation-damage-" + d, label: "Automation fraction, three AI settings, 2025-2050",
      caveat: "S3 is unvalidated against GATE after about 2027 (test A1.3 failed); shape only.", summary: t + ". Shape only, 2025 to 2050: S3 is unvalidated against GATE after about 2027 (test A1.3 failed).",
      series: F3.AI_S.map(function (n, i) { return { name: n + (n === s ? " (selected)" : ""), label: n, color: cols[i], tcolor: cols[i], dash: DASH[i], width: n === s ? 3.6 : 1.8, y: fr(n).slice(0, cut) }; }) });
    var full = function (n) { var j = fr(n).findIndex(function (v) { return v >= 0.999; }); return j < 0 ? "not within " + AY[AY.length - 1] : AY[j]; };
    $("auto_note").textContent = "Axis shows 2025-2050. First year at 1.0: low " + full("low") + ", central " + full("central") + ", race " + full("race") + " (a year after 2050 is beyond the axis).";
    var dm = {}; F3.AI_D.forEach(function (o) { dm[o] = D.runs[F3.aiKey(s, o)].damage_fraction; });
    var td = F3.aiDamageFinding(AY, dm), n1 = AY.length - 1;
    C.lineChart($("ch_dmg"), { title: td, years: AY, xstep: 15, tableStep: 5, unit: "Share of S3 output lost (%)", fmt: "pct", ymin: 0, file: "f3-ai-damage-share", label: "Damage options as a share of S3 output",
      caveat: "Level-of-output effect, not the upper end of the literature; shares of S3's own, unvalidated output.", summary: td + ". Level-of-output effect, not the upper end of the literature; shares of S3's own, unvalidated output.",
      series: F3.AI_D.map(function (o, i) { return { name: o + (o === "high" ? " (not the upper end of the literature)" : ""), label: o, color: cols[i], tcolor: cols[i], dash: DASH[i], y: dm[o].map(function (v) { return v * 100; }) }; }) });
    $("tb_dmg").innerHTML = "<tr><th>Option</th><th>c (% per K^2)</th><th>Share of S3 output lost in " + AY[n1] + "</th></tr>" + F3.AI_D.map(function (o) { return "<tr><td>" + o + "</td><td>" + D.meta.damage_coeff_pct_per_K2[o].toFixed(4) + (o === "low" ? "" : " (derived)") + "</td><td>" + (dm[o][n1] * 100).toFixed(2) + "%</td></tr>"; }).join("");
    $("tb_coef").innerHTML = "<tr><th>Option</th><th>Source</th></tr>" + F3.AI_D.map(function (o) { return "<tr><td>" + o + "</td><td>" + C.esc(D.meta.damage_sources[o]) + "</td></tr>"; }).join("");
  }

  /* ---------- phone step flow: Choose story, Result, Reliability ---------- */
  function setStep(step) {
    $("dash").dataset.step = step;
    $("actionbar").querySelectorAll("button").forEach(function (b) { if (b.dataset.step === step) b.setAttribute("aria-current", "step"); else b.removeAttribute("aria-current"); });
    if (step === "reliability") $("details").open = true;
    if (matchMedia("(max-width: 899px)").matches) window.scrollTo(0, 0);
    all();                                    /* charts drawn while their section was hidden have the wrong width: redraw now it is visible */
  }
  $("actionbar").querySelectorAll("button").forEach(function (b) { b.onclick = function () { setStep(b.dataset.step); }; });

  function refresh() { pushHash(); drawW3(); drawAI(); }
  function all() { drawW3(); drawClimate(); drawAI(); signs(); stripes(); }
  buildControls();
  writeState(F3.decodeState(location.hash, NL));
  all();
  window.addEventListener("hashchange", function () { writeState(F3.decodeState(location.hash, NL)); drawW3(); drawAI(); });
  window.addEventListener("f3theme", all);
  var lastW = document.documentElement.clientWidth;
  window.addEventListener("resize", function () { var w = document.documentElement.clientWidth; if (Math.abs(w - lastW) > 40) { lastW = w; all(); } });
  /* charts inside a closed <details> measure zero width: redraw when it opens */
  $("details").addEventListener("toggle", function () { if ($("details").open) all(); });
})();
