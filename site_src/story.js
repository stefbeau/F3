/* F3 story front door (D-056 stage 2). Four chapters; every number and every finding title is computed from window.F3DATA by core.js (no model numbers here). */
(function () {
  "use strict";
  var D = window.F3DATA, F3 = window.F3, C = window.F3C, W = D.world3, Y = W.years, N = Y.length - 1, AY = D.years;
  var $ = function (id) { return document.getElementById(id); };
  var LINKS = JSON.parse($("linksdata").textContent);
  var S = { c1: W.levers[0].standard_index, c2: "central", c3: "central", c4: "all" };
  var DASH = [null, "7 4", "2 3"];

  function seg(el, options, current, onPick) {
    el.innerHTML = options.map(function (o) { return '<button type="button" class="segb" data-v="' + o.value + '" aria-pressed="' + (String(o.value) === String(current)) + '">' + C.esc(o.label) + "</button>"; }).join("");
    el.querySelectorAll("button").forEach(function (b) { b.onclick = function () { onPick(b.dataset.v); }; });
  }
  function stdRun() { return W.runs[F3.runKey(W.levers.map(function (l) { return l.standard_index; }), "off")]; }

  /* ---- hero: the message in one generated sentence, readable with no interaction ---- */
  function hero() { $("hero_line").textContent = F3.popFinding(Y, stdRun(), null, "In the standard World3 run") + ". Four short steps follow, each with one chart and one control."; }

  /* ---- chapter 1: the standard world; control = starting resources ---- */
  function ch1() {
    var sc = C.scen(), lv = [S.c1, W.levers[1].standard_index, W.levers[2].standard_index], run = W.runs[F3.runKey(lv, "off")], std = stdRun(), isStd = F3.sameRun(run, std);
    seg($("c1_seg"), W.levers[0].value_labels.map(function (l, i) { return { value: i, label: l }; }), S.c1, function (v) { S.c1 = +v; ch1(); });
    var title = F3.popFinding(Y, run, std, isStd ? "In the standard run" : "With " + W.levers[0].value_labels[S.c1] + " starting resources");
    $("ch1_h").textContent = title;
    var pk = F3.peakOf(Y, run.pop), series = [{ name: isStd ? "Standard run" : "This run", label: isStd ? "Standard" : "This run", color: sc.a, tcolor: sc.aT, y: run.pop }];
    if (!isStd) series.unshift({ name: "Standard run", label: "Standard", color: sc.base, tcolor: sc.baseT, dash: "7 4", width: 2, y: std.pop });
    C.lineChart($("ch_s1"), { title: false, years: Y, series: series, unit: "People", fmt: "people", ymin: 0, xstep: 50, tableStep: 10, file: "f3-story-world3-population",
      annotations: [{ x: pk[0], y: pk[1], text: "Peak " + F3.human(pk[1]) + ", " + pk[0], color: sc.a, tcolor: sc.aT }], label: "World3 population, 1900-2100",
      summary: title + ". Model run, not a forecast.", caveat: "World3 2004 parameter set; changed runs are not compared with WorldDynamics.jl." });
    $("ch_s1").querySelector(".plot").setAttribute("aria-label", title);
  }

  /* ---- chapter 2: stripes and damage bars; control = damage option ---- */
  function stripes() {
    var T = D.climate.warming, lo = Math.min.apply(null, T), hi = Math.max.apply(null, T), n = T.length, w = 320 / n, A = [33, 102, 172], M = [247, 247, 247], R = [178, 24, 43];
    var mix = function (p, q, t) { return p.map(function (v, i) { return Math.round(v + (q[i] - v) * t); }); };
    var col = function (v) { var t = (v - lo) / ((hi - lo) || 1), c = t < 0.5 ? mix(A, M, t * 2) : mix(M, R, (t - 0.5) * 2); return "rgb(" + c.join(",") + ")"; };
    $("stripes_g").innerHTML = T.map(function (v, i) { return '<rect x="' + (i * w).toFixed(2) + '" y="0" width="' + (w + 0.6).toFixed(2) + '" height="84" fill="' + col(v) + '"/>'; }).join("");
    $("stripes_l").textContent = AY[0] + ": " + lo.toFixed(2) + " K"; $("stripes_r").textContent = AY[n - 1] + ": " + hi.toFixed(2) + " K";
  }
  function ch2() {
    var sc = C.scen(), std = W.levers.map(function (l) { return l.standard_index; }), off = W.runs[F3.runKey(std, "off")], opts = ["low", "central", "high"], eff = {}, cols = [sc.acc1, sc.acc2, sc.acc3], tcols = cols;
    opts.forEach(function (o) { eff[o] = F3.damageEffect(W.runs[F3.runKey(std, o)], off, N); });
    seg($("c2_seg"), F3.DMG_STATES.map(function (d) { return { value: d, label: d === "off" ? "Off" : d.charAt(0).toUpperCase() + d.slice(1) }; }), S.c2, function (v) { S.c2 = v; ch2(); });
    var sel = S.c2, title = F3.damageBarsFinding(Y, eff[sel] || null, sel);
    $("ch2_h").textContent = title;
    $("c2_notice").textContent = F3.damageNotice(sel);
    var pc = function (f) { return f * 100; };
    C.barChart($("ch_s2"), { title: false, categories: [{ label: "Industrial output, " + Y[N], values: opts.map(function (o) { return pc(eff[o].io); }) }, { label: "Population, " + Y[N], values: opts.map(function (o) { return pc(eff[o].pop); }) }],
      series: opts.map(function (o, i) { return { name: o + (o === "high" ? " (not the upper end of the literature)" : ""), short: o, color: cols[i], tcolor: tcols[i], dim: function () { return sel !== "off" && sel !== o; } }; }),
      fmt: function (v) { return F3.signedPct(v / 100); }, tickFmt: function (v) { return v + "%"; }, unit: "Change in " + Y[N] + " value against damage off, standard levers", catHead: "Measure",
      zeroNote: "The vertical line is zero: no change against the same run with climate damage off.", file: "f3-story-damage-bars",
      summary: title + ". Level-of-output effect, not the upper end of the literature. Not compared with WorldDynamics.jl.", caveat: F3.damageNotice(sel === "off" ? "central" : sel) });
    $("ch_s2").querySelector(".plot").setAttribute("aria-label", title);
  }

  /* ---- chapter 3: AI race, automation timing; control = investment setting ---- */
  function ch3() {
    var sc = C.scen(), cols = [sc.acc1, sc.acc2, sc.acc3], cut = AY.indexOf(2050) + 1, yrs = AY.slice(0, cut), sel = S.c3;
    seg($("c3_seg"), F3.AI_S.map(function (s) { return { value: s, label: s.charAt(0).toUpperCase() + s.slice(1) }; }), sel, function (v) { S.c3 = v; ch3(); });
    var fr = function (s) { return D.runs[F3.aiKey(s, "central")].frac_automated; }, title = F3.automationFinding(AY, fr(sel), sel);
    $("ch3_h").textContent = title;
    var y05 = F3.firstReach(AY, fr(sel), 0.5), ann = [];
    if (y05 !== null) ann.push({ x: y05, y: fr(sel)[AY.indexOf(y05)], text: "Half of tasks: " + y05, color: cols[F3.AI_S.indexOf(sel)], tcolor: cols[F3.AI_S.indexOf(sel)] });
    C.lineChart($("ch_s3"), { title: false, years: yrs, xstep: 5, tableStep: 5, unit: "Fraction of tasks automated (S3, levels unvalidated)", fmt: "fraction", ymin: 0, ymax: 1.02, file: "f3-story-ai-automation", label: "Automation fraction, 2025-2050",
      series: F3.AI_S.map(function (s, i) { return { name: s + (s === sel ? " (selected)" : ""), label: s, color: cols[i], tcolor: cols[i], dash: DASH[i], width: s === sel ? 3.6 : 1.8, y: fr(s).slice(0, cut) }; }), annotations: ann,
      summary: title + ". Shape only: S3's level is unvalidated after about 2027 (test A1.3 failed).", caveat: "S3 is unvalidated against GATE after about 2027 (test A1.3 failed); shape only." });
    $("ch_s3").querySelector(".plot").setAttribute("aria-label", title);
    var sp = F3.maxSpread(yrs, F3.AI_S.map(function (s) { return fr(s).slice(0, cut); }));
    $("c3_note").textContent = sp.gap < 0.005 ? "The three settings are the same to two decimals in every year shown." : "The three settings stay within " + sp.gap.toFixed(2) + " of each other in every year shown (largest gap in " + sp.year + "): the lines overlap because the settings barely differ in automation timing.";
  }

  /* ---- chapter 4: the strip of seven links; control = which status to show ---- */
  function ch4() {
    var count = function (s) { return LINKS.links.filter(function (l) { return l.status === s; }).length; }, total = LINKS.links.length;
    $("ch4_h").textContent = count("built") + " of " + total + " links between the models are built; " + count("withheld") + " more is built with outputs withheld, and " + count("not-built") + " are not built";
    seg($("c4_seg"), [{ value: "all", label: "All" }, { value: "built", label: "Built" }, { value: "withheld", label: "Withheld" }, { value: "not-built", label: "Not built" }], S.c4, function (v) { S.c4 = v; ch4(); });
    var node = {}; LINKS.nodes.forEach(function (n) { node[n.id] = n.label; });
    var dash = { built: "", withheld: ' stroke-dasharray="2 4"', "not-built": ' stroke-dasharray="6 4"' }, word = { built: "Built and tested", withheld: "Built, outputs withheld", "not-built": "Not built" };
    $("c4_list").innerHTML = LINKS.links.map(function (l) {
      var show = S.c4 === "all" || S.c4 === l.status;
      return '<li class="lk ' + l.status + (show ? "" : " dim") + '"><svg viewBox="0 0 44 10" aria-hidden="true"><line x1="0" y1="5" x2="44" y2="5" stroke-width="3.4"' + dash[l.status] + "/></svg><span><strong>" + l.n + ". " + C.esc(node[l.from]) + " to " + C.esc(node[l.to]) + ":</strong> " + C.esc(l.label) + ". <em>" + word[l.status] + ".</em></span></li>";
    }).join("");
  }

  /* ---- step indicator: the chapter in view ---- */
  function steps() {
    var links = document.querySelectorAll("#steps a"), ids = ["ch1", "ch2", "ch3", "ch4"];
    function mark(id) { links.forEach(function (a) { if (a.getAttribute("href") === "#" + id) a.setAttribute("aria-current", "step"); else a.removeAttribute("aria-current"); }); }
    mark("ch1");
    if (!("IntersectionObserver" in window)) return;
    var io = new IntersectionObserver(function (es) { es.forEach(function (e) { if (e.isIntersecting) mark(e.target.id); }); }, { rootMargin: "-30% 0px -60% 0px" });
    ids.forEach(function (i) { io.observe($(i)); });
  }
  function all() { hero(); ch1(); ch2(); ch3(); ch4(); stripes(); }
  all(); steps();
  var lastW = document.documentElement.clientWidth;
  window.addEventListener("f3theme", all);
  window.addEventListener("resize", function () { var w = document.documentElement.clientWidth; if (Math.abs(w - lastW) > 40) { lastW = w; all(); } });
})();
