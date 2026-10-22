/* F3 Explorer core (D-056): PURE functions only, no DOM. Everything a headline, tile, delta, bar or CSV says is computed here from the data it is given;
   page scripts hold no model numbers (tests/test_site_v02_core.py runs this file in Node on the committed data and on synthetic data, and scans the page
   scripts for hard-coded values). Loaded in the browser as window.F3, in Node as require("core.js"). */
(function (root, factory) {
  if (typeof module === "object" && module.exports) module.exports = factory(); else root.F3 = factory();
})(this, function () {
  "use strict";
  /* ---------- number formats ---------- */
  function human(v) {
    var a = Math.abs(v);
    if (a >= 1e12) return (+(v / 1e12).toPrecision(3)) + " trillion";
    if (a >= 1e9) return (+(v / 1e9).toPrecision(3)) + " billion";
    if (a >= 1e6) return (+(v / 1e6).toPrecision(3)) + " million";
    return (+v.toPrecision(3)).toString();
  }
  var FMT = {
    people: human, usd: human,
    fraction: function (v) { return (+v.toFixed(2)).toString(); },
    index: function (v) { return (+v.toPrecision(3)).toString(); },
    pct: function (v) { return (+v.toFixed(2)) + "%"; },
    kelvin: function (v) { return (+v.toFixed(2)) + " K"; }
  };
  /* A change as a plain-language phrase: "12.3% lower", "4.0% higher", "unchanged". */
  function rel(x) {
    var p = x * 100, a = Math.abs(p);
    if (a < 0.05) return "unchanged";
    return a.toFixed(1) + "% " + (p < 0 ? "lower" : "higher");
  }
  /* A change as a signed percentage for tiles and tables: "-12.3%", "+4.0%", "0.0%". */
  function signedPct(x) {
    var p = x * 100;
    return (Math.abs(p) < 0.05 ? "0.0" : (p > 0 ? "+" : "") + p.toFixed(1)) + "%";
  }
  /* ---------- series helpers ---------- */
  function peakOf(years, ys) { var k = 0; ys.forEach(function (v, i) { if (v > ys[k]) k = i; }); return [years[k], ys[k]]; }
  function firstReach(years, ys, th) { var j = ys.findIndex(function (v) { return v >= th; }); return j < 0 ? null : years[j]; }
  function indexOfYear(years, y) { return years.indexOf(y); }
  function sameSeries(a, b) {
    if (!a || !b || a.length !== b.length) return false;
    for (var i = 0; i < a.length; i++) if (a[i] !== b[i]) return false;
    return true;
  }
  function sameRun(a, b) { return Object.keys(a).every(function (k) { return sameSeries(a[k], b[k]); }); }
  /* The largest gap between any two of several series, and the year it occurs (used to say how far apart overlapping lines really are). */
  function maxSpread(years, arrays) {
    var best = { gap: 0, year: years[0] };
    years.forEach(function (y, i) {
      var vs = arrays.map(function (a) { return a[i]; }), g = Math.max.apply(null, vs) - Math.min.apply(null, vs);
      if (g > best.gap) best = { gap: g, year: y };
    });
    return best;
  }
  /* ---------- scenario state ---------- */
  var DEF_LEVERS = [1, 0, 0], DMG_STATES = ["off", "low", "central", "high"], AI_S = ["low", "central", "race"], AI_D = ["low", "central", "high"];
  var PRESETS = [
    { name: "Standard", levers: [1, 0, 0], text: "World3 with its standard parameters: the run The Limits to Growth made famous." },
    { name: "More resources", levers: [2, 0, 0], text: "Twice the starting non-renewable resources: does the turn come later?" },
    { name: "Farming tech", levers: [1, 1, 0], text: "Land yield factor 1.5 after 1975: more food from the same land." },
    { name: "Pollution cut", levers: [1, 0, 2], text: "Pollution generation factor 0.25 after 1975: much cleaner industry." },
    { name: "Combined", levers: [2, 1, 1], text: "Double resources, land yield 1.5 and pollution generation 0.5 together." }
  ];
  function runKey(levers, damage) { return levers.join("|") + "|" + damage; }
  function aiKey(setting, damage) { return setting + "|" + damage + "|1"; }
  function encodeState(s) { return "#w3=" + s.levers.join(".") + "&d=" + s.damage + "&ai=" + s.ai + "&ad=" + s.aidmg; }
  function parseHash(hash) {
    var q = {};
    String(hash || "").replace(/^#/, "").split("&").forEach(function (p) { var i = p.indexOf("="); if (i > 0) q[p.slice(0, i)] = p.slice(i + 1); });
    return q;
  }
  function parseLevers(txt, nLevers) {
    var v = String(txt || "").split(".");
    return v.length === nLevers && v.every(function (x) { return /^[0-2]$/.test(x); }) ? v.map(Number) : null;
  }
  function decodeState(hash, nLevers) {
    var out = { levers: DEF_LEVERS.slice(0, nLevers), damage: "off", ai: "central", aidmg: "central" };
    try {
      var q = parseHash(hash), lv = parseLevers(q.w3, nLevers);
      if (lv) out.levers = lv;
      if (DMG_STATES.indexOf(q.d) >= 0) out.damage = q.d;
      if (AI_S.indexOf(q.ai) >= 0) out.ai = q.ai;
      if (AI_D.indexOf(q.ad) >= 0) out.aidmg = q.ad;
    } catch (e) { /* fall back to defaults */ }
    return out;
  }
  function csvOf(years, cols, notes) {
    var q = function (s) { return /[",\n]/.test(s) ? '"' + s.replace(/"/g, '""') + '"' : s; };
    var lines = ["year," + cols.map(function (c) { return q(c.name); }).join(",")];
    years.forEach(function (y, i) { lines.push(y + "," + cols.map(function (c) { return String(c.y[i]); }).join(",")); });
    (notes || []).forEach(function (t) { lines.push("# " + t); });
    return lines.join("\n") + "\n";
  }
  function damageNotice(damage) {
    if (damage === "off") return "";
    return "Climate damage is ON (" + damage + "). This is a level-of-output effect, not the upper end of the literature. Damage-on runs are NOT compared with WorldDynamics.jl (it has no climate damage). S3's economy and World3's are not reconciled. There is no health or yield effect of warming.";
  }
  /* ---------- finding titles (generated from data; tests/test_site_v02_core.py) ---------- */
  function popFinding(years, run, std, who) {
    var n = years.length - 1, end = years[n], pk = peakOf(years, run.pop), falls = run.pop[n] < pk[1] * 0.999;
    var s = (who || "In this run") + ", population peaks at " + human(pk[1]) + " in " + pk[0] +
      (falls ? ", then falls to " + human(run.pop[n]) + " by " + end : " and is still " + human(run.pop[n]) + " in " + end);
    if (std && !sameSeries(run.pop, std.pop)) {
      var sp = peakOf(years, std.pop);
      s += "; the standard run peaks at " + human(sp[1]) + " in " + sp[0];
    }
    return s;
  }
  function industryFinding(years, run, off, damage) {
    var n = years.length - 1, end = years[n], pk = peakOf(years, run.io);
    var s = "World3 industrial output peaks at " + human(pk[1]) + " model dollars a year in " + pk[0] + " and is " + human(run.io[n]) + " in " + end;
    if (damage !== "off") s += "; climate damage (" + damage + ") makes " + end + " output " + rel(run.io[n] / off.io[n] - 1) + " than with damage off";
    return s;
  }
  function resourcesFinding(years, run) {
    var n = years.length - 1;
    return "Only " + run.nrfr[n].toFixed(2) + " of the starting non-renewable resources remain in " + years[n];
  }
  function pollutionFinding(years, run) {
    var n = years.length - 1, pp = peakOf(years, run.ppolx);
    return "Persistent pollution peaks at " + pp[1].toFixed(1) + " times its 1970 level in " + pp[0] + " and is " + run.ppolx[n].toFixed(2) + " times in " + years[n];
  }
  function temperatureFinding(years, mean, lo, hi) {
    var n = years.length - 1;
    return "FaIR ensemble mean warming reaches " + mean[n].toFixed(2) + " K by " + years[n] + " (5th to 95th percentile " + lo[n].toFixed(2) + " to " + hi[n].toFixed(2) + " K)";
  }
  function automationFinding(years, frac, label) {
    var end = years[years.length - 1], y05 = firstReach(years, frac, 0.5), y10 = firstReach(years, frac, 0.999);
    return "In the " + label + " AI run, automation reaches half of tasks in " + (y05 === null ? "no year before " + end : y05) + " and all tasks in " + (y10 === null ? "no year before " + end : y10);
  }
  function aiDamageFinding(years, dmgByOption) {
    var n = years.length - 1;
    return "Damage takes " + (dmgByOption.low[n] * 100).toFixed(1) + "% to " + (dmgByOption.high[n] * 100).toFixed(1) + "% of S3's own output in " + years[n] + " (low to high option)";
  }
  /* Effect of a damage option on 2100 values, at the same lever settings: fractions (run / damage off - 1). */
  function damageEffect(run, off, n) {
    return { io: run.io[n] / off.io[n] - 1, pop: run.pop[n] / off.pop[n] - 1, nrfr: run.nrfr[n] / off.nrfr[n] - 1, ppolx: run.ppolx[n] / off.ppolx[n] - 1 };
  }
  function damageBarsFinding(years, eff, damage) {
    var end = years[years.length - 1];
    if (damage === "off") return "With climate damage off, warming does not reach World3: pick an option to see its effect on " + end + " output and population";
    return "Under " + damage + " damage, " + end + " industrial output is " + rel(eff.io) + " and population " + rel(eff.pop) + " than with no damage";
  }
  /* ---------- dashboard tiles (at most 5) ---------- */
  function w3Kpis(years, run, std, off, damage) {
    var n = years.length - 1, end = years[n], pk = peakOf(years, run.pop), same = sameSeries(run.pop, std.pop);
    var tiles = [
      { id: "peak", k: "Peak population", v: human(pk[1]), sub: "in " + pk[0] },
      { id: "end", k: "Population in " + end, v: human(run.pop[n]), sub: same ? "same as the standard run" : signedPct(run.pop[n] / std.pop[n] - 1) + " vs the standard run" },
      { id: "res", k: "Resources left, " + end, v: run.nrfr[n].toFixed(2), sub: "of the starting stock" }
    ];
    if (damage === "off") tiles.push({ id: "dmg", k: "Damage effect on " + end + " industry", v: "n/a", sub: "climate damage is off" });
    else tiles.push({ id: "dmg", k: "Damage effect on " + end + " industry", v: signedPct(run.io[n] / off.io[n] - 1), sub: "vs damage off, same settings" });
    return tiles;
  }
  /* ---------- compare mode (baseline vs A vs B) ---------- */
  var COMPARE_METRICS = [
    { id: "pop", label: "Population", series: "pop", fmt: "people" },
    { id: "io", label: "Industrial output", series: "io", fmt: "usd" },
    { id: "nrfr", label: "Resources remaining (fraction of start)", series: "nrfr", fmt: "fraction" },
    { id: "ppolx", label: "Persistent pollution (1 = 1970 level)", series: "ppolx", fmt: "index" }
  ];
  /* rows: baseline value, A, B, change of A and of B vs baseline (fractions), B minus A (absolute and as a fraction of A), and a flag for identical rows. */
  function compareRows(years, base, a, b, warming) {
    var n = years.length - 1;
    var rows = COMPARE_METRICS.map(function (m) {
      var v0 = base[m.series][n], va = a[m.series][n], vb = b[m.series][n];
      return { id: m.id, label: m.label, fmt: m.fmt, base: v0, a: va, b: vb, dA: va / v0 - 1, dB: vb / v0 - 1, bMinusA: vb - va, bMinusAFrac: vb / va - 1, identical: va === vb && va === v0 };
    });
    if (warming) {
      var w = warming[warming.length - 1];
      rows.push({ id: "warming", label: "Warming above 1850-1900 (K)", fmt: "kelvin", base: w, a: w, b: w, dA: 0, dB: 0, bMinusA: 0, bMinusAFrac: 0, identical: true });
    }
    return rows;
  }
  function compareHeadline(years, rows, names) {
    var end = years[years.length - 1], by = {};
    rows.forEach(function (r) { by[r.id] = r; });
    var p = by.pop, io = by.io;
    if (Math.abs(p.bMinusA) < 1e-9 * Math.abs(p.a) && Math.abs(io.bMinusA) < 1e-9 * Math.abs(io.a)) {
      return names.a + " and " + names.b + " end " + end + " with the same population and industrial output: the settings do not change this run.";
    }
    var more = p.bMinusA > 0;
    return names.b + " ends " + end + " with " + human(Math.abs(p.bMinusA)) + (more ? " more" : " fewer") + " people than " + names.a + " (" + human(p.b) + " against " + human(p.a) +
      ") and " + rel(io.b / io.a - 1) + " industrial output; against the standard run, population is " + rel(p.dA) + " in " + names.a + " and " + rel(p.dB) + " in " + names.b + ".";
  }
  /* A value with an explicit sign in the metric's format: "+1.2 billion", "-0.05". */
  function signedFmt(v, fmtName) { var f = FMT[fmtName]; return (v < 0 ? "-" : v > 0 ? "+" : "") + f(Math.abs(v)); }
  function overlayFinding(years, label, fmtName, vals, names) {
    var f = FMT[fmtName], end = years[years.length - 1];
    return label + " in " + end + ": " + names.a + " ends at " + f(vals.a) + ", " + names.b + " at " + f(vals.b) + ", the standard run at " + f(vals.base);
  }
  /* The largest 2100 change against the baseline in either scenario, among rows that differ. */
  function barsFinding(years, rows, names) {
    var end = years[years.length - 1], best = null;
    rows.forEach(function (r) {
      if (r.identical) return;
      [["a", r.dA], ["b", r.dB]].forEach(function (p) { if (best === null || Math.abs(p[1]) > Math.abs(best.d)) best = { who: names[p[0]], d: p[1], label: r.label }; });
    });
    if (best === null) return "Both scenarios match the standard run in " + end + " on every measure shown";
    return "Against the standard run, the largest " + end + " change is " + best.label.toLowerCase() + " in " + best.who + " (" + signedPct(best.d) + ")";
  }
  function compareState(hash) {
    var def = { a: { levers: [1, 0, 0], damage: "central" }, b: { levers: [2, 1, 1], damage: "central" }, metric: "pop" };
    var out = { a: { levers: def.a.levers.slice(), damage: def.a.damage }, b: { levers: def.b.levers.slice(), damage: def.b.damage }, metric: def.metric };
    try {
      var q = parseHash(hash);
      ["a", "b"].forEach(function (k) {
        var m = /^([0-2])\.([0-2])\.([0-2])-(off|low|central|high)$/.exec(q[k] || "");
        if (m) out[k] = { levers: [+m[1], +m[2], +m[3]], damage: m[4] };
      });
      if (COMPARE_METRICS.some(function (m) { return m.id === q.m; })) out.metric = q.m;
    } catch (e) { /* defaults */ }
    return out;
  }
  function encodeCompare(s) { return "#a=" + s.a.levers.join(".") + "-" + s.a.damage + "&b=" + s.b.levers.join(".") + "-" + s.b.damage + "&m=" + s.metric; }
  function scenarioName(levers, damage) {
    var p = PRESETS.filter(function (x) { return x.levers.join(".") === levers.join("."); })[0];
    return (p ? p.name : "Custom " + levers.join(".")) + (damage === "off" ? " (damage off)" : " (" + damage + " damage)");
  }
  return {
    human: human, FMT: FMT, rel: rel, signedPct: signedPct, peakOf: peakOf, firstReach: firstReach, indexOfYear: indexOfYear, sameSeries: sameSeries, sameRun: sameRun, maxSpread: maxSpread,
    DEF_LEVERS: DEF_LEVERS, DMG_STATES: DMG_STATES, AI_S: AI_S, AI_D: AI_D, PRESETS: PRESETS, runKey: runKey, aiKey: aiKey, encodeState: encodeState, decodeState: decodeState,
    csvOf: csvOf, damageNotice: damageNotice, popFinding: popFinding, industryFinding: industryFinding, resourcesFinding: resourcesFinding, pollutionFinding: pollutionFinding,
    temperatureFinding: temperatureFinding, automationFinding: automationFinding, aiDamageFinding: aiDamageFinding, damageEffect: damageEffect, damageBarsFinding: damageBarsFinding,
    w3Kpis: w3Kpis, COMPARE_METRICS: COMPARE_METRICS, compareRows: compareRows, compareHeadline: compareHeadline, compareState: compareState, signedFmt: signedFmt, overlayFinding: overlayFinding, barsFinding: barsFinding, encodeCompare: encodeCompare, scenarioName: scenarioName
  };
});
