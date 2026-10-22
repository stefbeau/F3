/* F3 Compare (D-056 stage 4): the standard run (damage off) against scenario A and scenario B. State lives in the URL hash. The headline, overlay chart, diverging bars
   and delta table are computed from window.F3DATA by core.js: this file holds no model numbers. */
(function () {
  "use strict";
  var D = window.F3DATA, F3 = window.F3, C = window.F3C, W = D.world3, WY = W.years, N = WY.length - 1;
  var $ = function (id) { return document.getElementById(id); };
  var STD = W.levers.map(function (l) { return l.standard_index; });
  var DMG_LABEL = { off: "Off", low: "Low", central: "Central", high: "High" };
  var NAMES = { a: "Scenario A", b: "Scenario B" };
  var S = F3.compareState(location.hash);
  var lastRows = null;

  function levKey(lv) { return lv.join("."); }
  function optionsFor(k) {
    var opts = F3.PRESETS.map(function (p) { return { value: levKey(p.levers), label: p.name }; });
    if (!F3.PRESETS.some(function (p) { return levKey(p.levers) === levKey(S[k].levers); })) opts.push({ value: levKey(S[k].levers), label: "Custom " + levKey(S[k].levers) });
    return opts;
  }
  function build() {
    ["a", "b"].forEach(function (k) {
      var sel = $("sel_" + k);
      sel.innerHTML = optionsFor(k).map(function (o) { return '<option value="' + o.value + '">' + C.esc(o.label) + "</option>"; }).join("");
      sel.value = levKey(S[k].levers);
      sel.onchange = function () { S[k].levers = sel.value.split(".").map(Number); refresh(); };
      $("seg_" + k).innerHTML = F3.DMG_STATES.map(function (d) { return '<button type="button" class="segb" data-v="' + d + '" aria-pressed="false">' + DMG_LABEL[d] + "</button>"; }).join("");
      $("seg_" + k).querySelectorAll("button").forEach(function (b) { b.onclick = function () { S[k].damage = b.dataset.v; refresh(); }; });
    });
    $("metric_seg").innerHTML = F3.COMPARE_METRICS.map(function (m) { return '<button type="button" class="segb" data-v="' + m.id + '" aria-pressed="false">' + C.esc(m.label.replace(/ \(.*\)/, "")) + "</button>"; }).join("");
    $("metric_seg").querySelectorAll("button").forEach(function (b) { b.onclick = function () { S.metric = b.dataset.v; refresh(); }; });
    $("swap").onclick = function () { var t = S.a; S.a = S.b; S.b = t; build(); refresh(); };
    $("reset").onclick = function () { S = F3.compareState(""); build(); refresh(); };
    $("delta_csv").onclick = deltaCsv;
  }
  function sync() {
    ["a", "b"].forEach(function (k) {
      $("seg_" + k).querySelectorAll("button").forEach(function (b) { b.setAttribute("aria-pressed", String(b.dataset.v === S[k].damage)); });
      var sel = $("sel_" + k); if (sel.value !== levKey(S[k].levers)) sel.value = levKey(S[k].levers);
    });
    $("metric_seg").querySelectorAll("button").forEach(function (b) { b.setAttribute("aria-pressed", String(b.dataset.v === S.metric)); });
  }
  function run(k) { return W.runs[F3.runKey(S[k].levers, S[k].damage)]; }
  function draw() {
    sync();
    var sc = C.scen(), base = W.runs[F3.runKey(STD, "off")], a = run("a"), b = run("b");
    var nm = { a: F3.scenarioName(S.a.levers, S.a.damage), b: F3.scenarioName(S.b.levers, S.b.damage) };
    var rows = F3.compareRows(WY, base, a, b, D.climate.warming);
    lastRows = rows;
    $("headline").textContent = F3.compareHeadline(WY, rows, NAMES);
    $("names").textContent = NAMES.a + ": " + nm.a + ". " + NAMES.b + ": " + nm.b + ". Baseline: the standard run, damage off.";
    var cav = [S.a.damage, S.b.damage].filter(function (d) { return d !== "off"; })[0];
    $("cmp_damage_notice").textContent = cav ? F3.damageNotice(cav) : "";
    var cavTxt = cav ? F3.damageNotice(cav) : "";
    /* overlay chart: baseline (grey dashed), A (blue), B (orange): three lines at most */
    var m = F3.COMPARE_METRICS.filter(function (x) { return x.id === S.metric; })[0], row = rows.filter(function (r) { return r.id === m.id; })[0];
    var title = F3.overlayFinding(WY, m.label.replace(/ \(.*\)/, ""), m.fmt, { base: row.base, a: row.a, b: row.b }, { a: NAMES.a, b: NAMES.b });
    var unit = { pop: "People", io: "Model dollars per year (World3's own constant dollars)", nrfr: "Fraction of starting stock", ppolx: "Pollution index (1 = 1970 level)" }[m.id];
    C.lineChart($("ch_over"), { title: title, years: WY, xstep: 50, tableStep: 10, unit: unit, fmt: m.fmt, ymin: 0, file: "f3-compare-" + m.id + "-" + S.a.levers.join("") + S.a.damage + "-vs-" + S.b.levers.join("") + S.b.damage,
      caveat: cavTxt, label: m.label + ", baseline, scenario A and scenario B", summary: title + ". " + NAMES.a + " is " + nm.a + "; " + NAMES.b + " is " + nm.b + ". Model runs, not forecasts.",
      series: [{ name: "Baseline: standard run, damage off", label: "Baseline", color: sc.base, tcolor: sc.baseT, dash: "7 4", width: 2.2, y: base[m.series] },
        { name: NAMES.a + ": " + nm.a, label: "A", color: sc.a, tcolor: sc.aT, y: a[m.series] }, { name: NAMES.b + ": " + nm.b, label: "B", color: sc.b, tcolor: sc.bT, y: b[m.series], dash: "2 3", width: 3 }] });
    /* diverging bars: 2100 change against the baseline, zero line visible */
    var shown = rows.filter(function (r) { return !r.identical; }), tb = F3.barsFinding(WY, rows, NAMES);
    if (!shown.length) { $("ch_bars")._c = null; $("ch_bars").innerHTML = "<h3 class=\"ct\">" + C.esc(tb) + "</h3><p class=\"note\">Nothing to draw: every measure equals the standard run.</p>"; }
    else C.barChart($("ch_bars"), { title: tb, categories: shown.map(function (r) { return { label: r.label.replace(/ \(.*\)/, "") + ", " + WY[N], values: [r.dA * 100, r.dB * 100] }; }),
      series: [{ name: NAMES.a, short: "A", color: sc.a, tcolor: sc.aT }, { name: NAMES.b, short: "B", color: sc.b, tcolor: sc.bT }],
      fmt: function (v) { return F3.signedPct(v / 100); }, tickFmt: function (v) { return v + "%"; }, unit: "Change in " + WY[N] + " value against the standard run (%)", catHead: "Measure",
      zeroNote: "The vertical line is zero: no change against the standard run (damage off).", file: "f3-compare-change-vs-baseline", caveat: cavTxt,
      summary: tb + ". " + NAMES.a + " is " + nm.a + "; " + NAMES.b + " is " + nm.b + ". Warming is identical in all three and is not drawn." });
    var ident = rows.filter(function (r) { return r.identical; }).map(function (r) { return r.label; });
    $("identical_note").textContent = ident.length ? "Identical in the baseline, A and B and therefore not drawn: " + ident.join("; ") + ". Emissions are prescribed, so every scenario has the same warming; the damage option changes output, not temperature." : "";
    $("identical_note").style.display = ident.length ? "block" : "none";
    $("tbl_year").textContent = String(WY[N]);
    var fm = function (r, v) { return F3.FMT[r.fmt](v); };
    $("tb_delta").innerHTML = "<tr><th scope=\"col\">Measure</th><th scope=\"col\">Baseline</th><th scope=\"col\">A</th><th scope=\"col\">B</th><th scope=\"col\">A vs baseline</th><th scope=\"col\">B vs baseline</th><th scope=\"col\">B minus A</th><th scope=\"col\">Note</th></tr>" +
      rows.map(function (r) {
        return "<tr><th scope=\"row\">" + C.esc(r.label) + "</th><td>" + fm(r, r.base) + "</td><td>" + fm(r, r.a) + "</td><td>" + fm(r, r.b) + "</td><td>" + F3.signedPct(r.dA) + "</td><td>" + F3.signedPct(r.dB) + "</td><td>" +
          (r.identical ? "0" : F3.signedFmt(r.bMinusA, r.fmt) + " (" + F3.signedPct(r.bMinusAFrac) + ")") + "</td><td>" + (r.identical ? "Identical in all three" : "") + "</td></tr>";
      }).join("");
  }
  function deltaCsv() {
    var q = function (t) { return /[",\n]/.test(t) ? '"' + t.replace(/"/g, '""') + '"' : t; }, lines = ["measure,baseline,A,B,A vs baseline,B vs baseline,B minus A,identical"];
    (lastRows || []).forEach(function (r) { lines.push([q(r.label), r.base, r.a, r.b, r.dA, r.dB, r.bMinusA, r.identical].join(",")); });
    lines.push("# F3 Explorer v0.2: conditional scenarios, not forecasts. Values are for " + WY[N] + "; changes are fractions of the baseline value.");
    var blob = new Blob([lines.join("\n") + "\n"], { type: "text/csv;charset=utf-8" }), a = document.createElement("a");
    a.href = URL.createObjectURL(blob); a.download = "f3-compare-table.csv"; document.body.appendChild(a); a.click(); a.remove();
  }
  function refresh() { try { history.replaceState(null, "", F3.encodeCompare(S)); } catch (e) { /* hash is a convenience */ } draw(); }
  function setStep(step) {
    $("dash").dataset.step = step;
    $("actionbar").querySelectorAll("button").forEach(function (b) { if (b.dataset.step === step) b.setAttribute("aria-current", "step"); else b.removeAttribute("aria-current"); });
    if (matchMedia("(max-width: 899px)").matches) window.scrollTo(0, 0);
    draw();
  }
  $("actionbar").querySelectorAll("button").forEach(function (b) { b.onclick = function () { setStep(b.dataset.step); }; });
  build(); draw();
  window.addEventListener("hashchange", function () { S = F3.compareState(location.hash); build(); draw(); });
  window.addEventListener("f3theme", draw);
  var lastW = document.documentElement.clientWidth;
  window.addEventListener("resize", function () { var w = document.documentElement.clientWidth; if (Math.abs(w - lastW) > 40) { lastW = w; draw(); } });
})();
