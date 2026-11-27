/* F3 Explorer core (D-056): PURE functions only, no DOM. Everything a headline, tile, delta, bar or CSV says is computed here from the data it is given;
   page scripts hold no model numbers (tests/test_site_v02_core.py runs this file in Node on the committed data and on synthetic data, and scans the page
   scripts for hard-coded values). Loaded in the browser as window.F3, in Node as require("core.js"). */
(function (root, factory) {
  if (typeof module === "object" && module.exports) module.exports = factory(); else root.F3 = factory();
})(this, function () {
  "use strict";
  /* ---------- no value: the data file uses null for "no value" (never zero). the global isFinite is true for null in JavaScript, so every test of a data value goes through isNum ---------- */
  var NA = "no value";
  function isNum(v) { return typeof v === "number" && isFinite(v); }
  function scale(v, k) { return isNum(v) ? v * k : null; }
  function scaleArr(a, k) { return a.map(function (v) { return scale(v, k); }); }
  function chg(a, b) { return isNum(a) && isNum(b) && b !== 0 ? a / b - 1 : null; }       /* a change as a fraction (a / b - 1), or null when either value is missing */
  function diff(a, b) { return isNum(a) && isNum(b) ? a - b : null; }
  function fx(v, d) { return isNum(v) ? v.toFixed(d) : NA; }
  /* contiguous runs of numeric values: [[first, last], ...] (a line is drawn per run, so a gap is never bridged and never read as zero) */
  function runs(ys) {
    var out = [], s = -1;
    ys.forEach(function (v, i) { if (isNum(v)) { if (s < 0) s = i; } else if (s >= 0) { out.push([s, i - 1]); s = -1; } });
    if (s >= 0) out.push([s, ys.length - 1]);
    return out;
  }
  function lastNum(ys) { for (var i = ys.length - 1; i >= 0; i--) if (isNum(ys[i])) return i; return -1; }
  /* ---------- number formats ---------- */
  function human(v) {
    if (!isNum(v)) return NA;
    var a = Math.abs(v);
    if (a >= 1e12) return (+(v / 1e12).toPrecision(3)) + " trillion";
    if (a >= 1e9) return (+(v / 1e9).toPrecision(3)) + " billion";
    if (a >= 1e6) return (+(v / 1e6).toPrecision(3)) + " million";
    return (+v.toPrecision(3)).toString();
  }
  var FMT = {
    people: human, usd: human,
    fraction: function (v) { return isNum(v) ? (+v.toFixed(2)).toString() : NA; },
    index: function (v) { return isNum(v) ? (+v.toPrecision(3)).toString() : NA; },
    pct: function (v) { return isNum(v) ? (+v.toFixed(2)) + "%" : NA; },
    kelvin: function (v) { return isNum(v) ? (+v.toFixed(2)) + " K" : NA; },
    bn: function (v) { return isNum(v) ? (+v.toFixed(2)) + " billion" : NA; }
  };
  /* A change as a plain-language phrase: "12.3% lower", "4.0% higher", "unchanged". */
  function rel(x) {
    if (!isNum(x)) return NA;
    var p = x * 100, a = Math.abs(p);
    if (a < 0.05) return "unchanged";
    return a.toFixed(1) + "% " + (p < 0 ? "lower" : "higher");
  }
  /* A change as a signed percentage for tiles and tables: "-12.3%", "+4.0%", "0.0%". */
  function signedPct(x) {
    if (!isNum(x)) return NA;
    var p = x * 100;
    return (Math.abs(p) < 0.05 ? "0.0" : (p > 0 ? "+" : "") + p.toFixed(1)) + "%";
  }
  /* ---------- series helpers ---------- */
  function peakOf(years, ys) { var k = -1; ys.forEach(function (v, i) { if (isNum(v) && (k < 0 || v > ys[k])) k = i; }); return k < 0 ? [null, null] : [years[k], ys[k]]; }
  function firstReach(years, ys, th) { var j = ys.findIndex(function (v) { return isNum(v) && v >= th; }); return j < 0 ? null : years[j]; }
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
      var vs = arrays.map(function (a) { return a[i]; }).filter(isNum);
      if (vs.length < 2) return;                                                     /* a missing value is skipped, never counted as zero */
      var g = Math.max.apply(null, vs) - Math.min.apply(null, vs);
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
    var anyNull = false;
    years.forEach(function (y, i) { lines.push(y + "," + cols.map(function (c) { if (isNum(c.y[i])) return String(c.y[i]); anyNull = true; return ""; }).join(",")); });
    (notes || []).forEach(function (t) { lines.push("# " + t); });
    if (anyNull) lines.push("# An empty cell means no value (null in the data file), not zero.");
    return lines.join("\n") + "\n";
  }
  function damageNotice(damage) {
    if (damage === "off") return "";
    return "Climate damage is ON (" + damage + "). This is a level-of-output effect, not the upper end of the literature. Damage-on runs are NOT compared with WorldDynamics.jl (it has no climate damage). S3's economy and World3's are not reconciled. There is no health or yield effect of warming.";
  }
  /* ---------- finding titles (generated from data; tests/test_site_v02_core.py) ---------- */
  function popFinding(years, run, std, who) {
    var n = years.length - 1, end = years[n], pk = peakOf(years, run.pop);
    if (pk[0] === null) return (who || "In this run") + ", population has " + NA + " in any year";
    var falls = isNum(run.pop[n]) && run.pop[n] < pk[1] * 0.999;
    var s = (who || "In this run") + ", population peaks at " + human(pk[1]) + " in " + pk[0] +
      (!isNum(run.pop[n]) ? " and has " + NA + " in " + end : falls ? ", then falls to " + human(run.pop[n]) + " by " + end : " and is still " + human(run.pop[n]) + " in " + end);
    if (std && !sameSeries(run.pop, std.pop)) {
      var sp = peakOf(years, std.pop);
      if (sp[0] !== null) s += "; the standard run peaks at " + human(sp[1]) + " in " + sp[0];
    }
    return s;
  }
  function industryFinding(years, run, off, damage) {
    var n = years.length - 1, end = years[n], pk = peakOf(years, run.io);
    if (pk[0] === null) return "World3 industrial output has " + NA + " in any year";
    var s = "World3 industrial output peaks at " + human(pk[1]) + " model dollars a year in " + pk[0] + " and is " + human(run.io[n]) + " in " + end;
    if (damage !== "off") {
      var c = chg(run.io[n], off.io[n]);
      s += c === null ? "; the effect of climate damage (" + damage + ") on " + end + " output cannot be computed (" + NA + ")" : "; climate damage (" + damage + ") makes " + end + " output " + rel(c) + " than with damage off";
    }
    return s;
  }
  function resourcesFinding(years, run) {
    var n = years.length - 1;
    return "Only " + fx(run.nrfr[n], 2) + " of the starting non-renewable resources remain in " + years[n];
  }
  function pollutionFinding(years, run) {
    var n = years.length - 1, pp = peakOf(years, run.ppolx);
    if (pp[0] === null) return "Persistent pollution has " + NA + " in any year";
    return "Persistent pollution peaks at " + fx(pp[1], 1) + " times its 1970 level in " + pp[0] + " and is " + fx(run.ppolx[n], 2) + " times in " + years[n];
  }
  function temperatureFinding(years, mean, lo, hi) {
    var n = years.length - 1;
    return "FaIR ensemble mean warming reaches " + fx(mean[n], 2) + " K by " + years[n] + " (5th to 95th percentile " + fx(lo[n], 2) + " to " + fx(hi[n], 2) + " K)";
  }
  function automationFinding(years, frac, label) {
    var end = years[years.length - 1], y05 = firstReach(years, frac, 0.5), y10 = firstReach(years, frac, 0.999);
    return "In the " + label + " AI run, automation reaches half of tasks in " + (y05 === null ? "no year before " + end : y05) + " and all tasks in " + (y10 === null ? "no year before " + end : y10);
  }
  /* The assumptions link every chart card carries: where the reader finds what this chart assumes and what was not compared. With climate damage on, a World3 chart points to the coupling. */
  var ASSUME = {
    world3: { href: "methods.html#grids", text: "Assumptions: World3 levers, units and what was compared" },
    w3damage: { href: "methods.html#coupling", text: "Assumptions: the climate-damage coupling" },
    climate: { href: "limitations.html#status-climate", text: "Assumptions and limits: FaIR, prescribed emissions, test A2.1" },
    ai: { href: "limitations.html#status-ai", text: "Assumptions and limits: S3's levels are unvalidated" },
    aidamage: { href: "limitations.html#compared", text: "Assumptions and limits: the damage options and what was not compared" },
    history: { href: "methods.html#history-overlay", text: "Assumptions and limits: a comparison with history, not a validation" },
    map: { href: "methods.html#warming-map", text: "Assumptions and limits: illustrative downscaling, how the map is made" }
  };
  function assumeFor(kind, damage) { var k = kind === "world3" && damage && damage !== "off" ? "w3damage" : kind; return ASSUME[k]; }
  /* Warming stripes: the finding title and the whole chart spec (title, text alternative, caveat, file name) come from the data. */
  function stripesFinding(years, ws) {
    var nums = ws.filter(isNum);
    if (!nums.length) return "The FaIR ensemble mean warming has " + NA + " in every year";
    var lo = Math.min.apply(null, nums), hi = Math.max.apply(null, nums);
    return "FaIR ensemble mean warming runs from " + fx(lo, 2) + " K in " + years[ws.indexOf(lo)] + " to " + fx(hi, 2) + " K in " + years[ws.indexOf(hi)] + ", one stripe per year";
  }
  function stripesSpec(climate, years) {
    var cav = "FaIR starts about 0.04 to 0.07 K below observed (test A2.1 failed); emissions are prescribed. The colour scale is relative to this run (blue lowest, red highest), not to observations. A model run, not observed data.";
    var t = stripesFinding(years, climate.warming);
    return { kind: "stripes", years: years, values: climate.warming, title: t, summary: t + ". " + cav, caveat: cav, file: "f3-warming-stripes", valueName: "FaIR ensemble mean warming above 1850-1900 (K)", fmt: "kelvin", assume: ASSUME.climate };
  }
  function aiDamageFinding(years, dmgByOption) {
    var n = years.length - 1;
    return "Damage takes " + fx(scale(dmgByOption.low[n], 100), 1) + "% to " + fx(scale(dmgByOption.high[n], 100), 1) + "% of S3's own output in " + years[n] + " (low to high option)";
  }
  /* Effect of a damage option on 2100 values, at the same lever settings: fractions (run / damage off - 1). */
  function damageEffect(run, off, n) {
    return { io: chg(run.io[n], off.io[n]), pop: chg(run.pop[n], off.pop[n]), nrfr: chg(run.nrfr[n], off.nrfr[n]), ppolx: chg(run.ppolx[n], off.ppolx[n]) };
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
      { id: "peak", k: "Peak population", v: human(pk[1]), sub: pk[0] === null ? NA : "in " + pk[0] },
      { id: "end", k: "Population in " + end, v: human(run.pop[n]), sub: same ? "same as the standard run" : signedPct(chg(run.pop[n], std.pop[n])) + " vs the standard run" },
      { id: "res", k: "Resources left, " + end, v: fx(run.nrfr[n], 2), sub: "of the starting stock" }
    ];
    if (damage === "off") tiles.push({ id: "dmg", k: "Damage effect on " + end + " industry", v: "n/a", sub: "climate damage is off" });
    else tiles.push({ id: "dmg", k: "Damage effect on " + end + " industry", v: signedPct(chg(run.io[n], off.io[n])), sub: "vs damage off, same settings" });
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
      return { id: m.id, label: m.label, fmt: m.fmt, base: v0, a: va, b: vb, dA: chg(va, v0), dB: chg(vb, v0), bMinusA: diff(vb, va), bMinusAFrac: chg(vb, va), identical: va === vb && va === v0 };
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
    if (!isNum(p.bMinusA) || !isNum(io.bMinusA) || !isNum(p.dA) || !isNum(p.dB)) return "The two scenarios cannot be compared in " + end + ": a population or industrial output value is missing (" + NA + ").";
    if (Math.abs(p.bMinusA) < 1e-9 * Math.abs(p.a) && Math.abs(io.bMinusA) < 1e-9 * Math.abs(io.a)) {
      return names.a + " and " + names.b + " end " + end + " with the same population and industrial output: the settings do not change this run.";
    }
    var more = p.bMinusA > 0;
    return names.b + " ends " + end + " with " + human(Math.abs(p.bMinusA)) + (more ? " more" : " fewer") + " people than " + names.a + " (" + human(p.b) + " against " + human(p.a) +
      ") and " + rel(io.b / io.a - 1) + " industrial output; against the standard run, population is " + rel(p.dA) + " in " + names.a + " and " + rel(p.dB) + " in " + names.b + ".";
  }
  /* A value with an explicit sign in the metric's format: "+1.2 billion", "-0.05". */
  function signedFmt(v, fmtName) { var f = FMT[fmtName]; if (!isNum(v)) return NA; return (v < 0 ? "-" : v > 0 ? "+" : "") + f(Math.abs(v)); }
  function overlayFinding(years, label, fmtName, vals, names) {
    var f = FMT[fmtName], end = years[years.length - 1];
    return label + " in " + end + ": " + names.a + " ends at " + f(vals.a) + ", " + names.b + " at " + f(vals.b) + ", the standard run at " + f(vals.base);
  }
  /* The largest 2100 change against the baseline in either scenario, among rows that differ. */
  function barsFinding(years, rows, names) {
    var end = years[years.length - 1], best = null;
    rows.forEach(function (r) {
      if (r.identical) return;
      [["a", r.dA], ["b", r.dB]].forEach(function (p) { if (!isNum(p[1])) return; if (best === null || Math.abs(p[1]) > Math.abs(best.d)) best = { who: names[p[0]], d: p[1], label: r.label }; });
    });
    if (best === null) return "Both scenarios match the standard run in " + end + " on every measure shown";
    return "Against the standard run, the largest " + end + " change is " + best.label.toLowerCase() + " in " + best.who + " (" + signedPct(best.d) + ")";
  }
  /* ---------- range chart ("tornado") and dumbbell (D-070); readings in docs/site-tornado-dumbbell.md; tests/test_site_tornado_dumbbell.py ---------- */
  var METRIC_UNIT = { pop: "People", io: "Model dollars per year (World3's own constant dollars)", nrfr: "Fraction of starting stock", ppolx: "Pollution index (1 = 1970 level)" };
  var RANGE_CAVEAT = "One setting is changed at a time and the others stay as chosen, so combined effects are not shown (the Compare page shows combinations). " +
    "Each bar is the range among the settings the Explorer offers: not an uncertainty range, not a likelihood and not a sensitivity analysis of the model. " +
    "The climate-damage options are a level-of-output effect and high is not the upper end of the literature. Damage-on runs and runs with changed parameters are not compared with WorldDynamics.jl. " +
    "There is no health or yield effect of warming. Model runs, not a forecast.";
  function plainLabel(s) { return String(s).replace(/ \(.*\)/, ""); }
  function lowerFirst(s) { s = String(s); return s.charAt(0).toLowerCase() + s.slice(1); }
  /* One row per setting of the rail (the World3 levers, then the climate-damage option): the lowest and highest value the measure takes in the last year when that ONE setting
     goes through all its values and every other setting stays as chosen. Rows are sorted by the width of that range, widest first; a row with fewer than two values has no width and goes last. */
  function tornadoSpec(W, levers, damage, metricId) {
    var m = COMPARE_METRICS.filter(function (x) { return x.id === metricId; })[0] || COMPARE_METRICS[0], n = W.years.length - 1, end = W.years[n];
    var fmtName = m.fmt === "fraction" ? "index" : m.fmt, f = FMT[fmtName];          /* three significant figures, so the two ends of a narrow range do not print as the same number */
    var val = function (lv, d) { var r = W.runs[runKey(lv, d)]; return r && isNum(r[m.series][n]) ? r[m.series][n] : null; };
    var here = val(levers, damage);
    var mk = function (id, label, pts, k) {
      var lo = null, hi = null, cnt = 0;
      pts.forEach(function (p) { if (!isNum(p.v)) return; cnt++; if (lo === null || p.v < lo.v) lo = p; if (hi === null || p.v > hi.v) hi = p; });   /* a missing value is left out of the range, never read as zero */
      var ok = cnt >= 2;
      return { id: id, label: label, points: pts, lo: ok ? { setting: lo.setting, v: lo.v } : null, hi: ok ? { setting: hi.setting, v: hi.v } : null, swing: ok ? hi.v - lo.v : null, k: k };
    };
    var rows = W.levers.map(function (l, i) {
      return mk(l.param, l.label, l.values.map(function (x, j) { var lv = levers.slice(); lv[i] = j; return { setting: l.value_labels[j], v: val(lv, damage), chosen: j === levers[i] }; }), i);
    });
    rows.push(mk("damage", "Climate damage to industrial output", (W.damage_states || DMG_STATES).map(function (d) { return { setting: "damage " + d, v: val(levers, d), chosen: d === damage }; }), rows.length));
    rows.sort(function (a, b) {
      var an = isNum(a.swing), bn = isNum(b.swing);
      if (an !== bn) return an ? -1 : 1;
      if (an && a.swing !== b.swing) return b.swing - a.swing;
      return a.k - b.k;                                                               /* equal widths keep the order of the data file */
    });
    rows.forEach(function (r) { delete r.k; });
    var what = lowerFirst(plainLabel(m.label)), top = rows[0], title;
    if (!isNum(top.swing)) title = plainLabel(m.label) + " in " + end + " has " + NA + " for the settings compared";
    else if (top.swing === 0) title = "None of the settings changes " + what + " in " + end + ": it stays at " + f(here);
    else title = "Changing one setting at a time, " + lowerFirst(top.label) + " moves " + end + " " + what + " the most: from " + f(top.lo.v) + " at " + top.lo.setting + " to " + f(top.hi.v) + " at " + top.hi.setting;
    var num = function (v) { return isNum(v) ? v : null; };
    return { kind: "tornado", metric: { id: m.id, label: m.label, fmt: fmtName }, fmt: fmtName, year: end, here: here, rows: rows, title: title, summary: title + ". " + RANGE_CAVEAT, caveat: RANGE_CAVEAT,
      unit: METRIC_UNIT[m.id] + ", " + end, file: "f3-range-" + m.id + "-" + levers.join("") + "-damage-" + damage, assume: assumeFor("world3", damage),
      table: { head: ["Setting changed", "Lowest " + end + " value", "at", "Highest " + end + " value", "at", "Range"],
        rows: rows.map(function (r) { return r.lo ? [r.label, f(r.lo.v), r.lo.setting, f(r.hi.v), r.hi.setting, f(r.swing)] : [r.label, NA, NA, NA, NA, NA]; }) },
      csv: { head: ["setting_changed", "lowest_value", "lowest_at", "highest_value", "highest_at", "range", "chosen_run_value"],
        rows: rows.map(function (r) { return r.lo ? [r.label, r.lo.v, r.lo.setting, r.hi.v, r.hi.setting, r.swing, num(here)] : [r.label, null, null, null, null, null, num(here)]; }) } };
  }
  /* Dumbbell: one row per measure that differs from the baseline; A and B as their change against the standard run (%), the gap in percentage points, rows sorted by the gap, widest first.
     rows are those of compareRows, so every number is the bars' and the table's number. */
  function dumbbellSpec(years, rows, names, descr, caveat) {
    var end = years[years.length - 1];
    var out = rows.filter(function (r) { return !r.identical; }).map(function (r, i) {
      return { id: r.id, label: plainLabel(r.label), a: scale(r.dA, 100), b: scale(r.dB, 100), gap: isNum(r.dA) && isNum(r.dB) ? (r.dB - r.dA) * 100 : null, k: i };
    });
    out.sort(function (p, q) {
      var pn = isNum(p.gap), qn = isNum(q.gap);
      if (pn !== qn) return pn ? -1 : 1;
      if (pn && Math.abs(p.gap) !== Math.abs(q.gap)) return Math.abs(q.gap) - Math.abs(p.gap);
      return p.k - q.k;
    });
    out.forEach(function (r) { delete r.k; });
    var top = out[0], title;
    if (!out.length) title = names.a + " and " + names.b + " match the standard run in " + end + " on every measure shown";
    else if (!isNum(top.gap)) title = names.a + " and " + names.b + " cannot be compared in " + end + ": a value is missing (" + NA + ")";
    else if (Math.abs(top.gap) < 0.05) title = names.a + " and " + names.b + " coincide in " + end + ": the same change against the standard run on every measure shown";
    else title = "In " + end + ", " + names.a + " and " + names.b + " are furthest apart on " + lowerFirst(top.label) + ": " + signedPct(top.a / 100) + " against " + signedPct(top.b / 100) + " relative to the standard run, " + Math.abs(top.gap).toFixed(1) + " percentage points apart";
    var pts = function (g) { return isNum(g) ? (Math.abs(g) < 0.05 ? "0.0" : (g > 0 ? "+" : "") + g.toFixed(1)) + " points" : NA; };
    var cav = (caveat ? caveat + " " : "") + "Changes are relative to the standard run with damage off. The measures have different units, so they are compared as percentages; the order is by the distance between A and B.";
    return { kind: "dumbbell", year: end, rows: out, names: names, title: title, caveat: cav, file: "f3-compare-dumbbell", assume: ASSUME.w3damage, unit: "Change in " + end + " value against the standard run (%)",
      summary: title + ". " + names.a + " is " + descr.a + "; " + names.b + " is " + descr.b + ". Warming is identical in all three and is not drawn. " + cav + " Model runs, not forecasts.",
      gapText: pts,
      table: { head: ["Measure, " + end, names.a + " vs baseline", names.b + " vs baseline", "B minus A"], rows: out.map(function (r) { return [r.label, signedPct(scale(r.a, 0.01)), signedPct(scale(r.b, 0.01)), pts(r.gap)]; }) },
      csv: { head: ["measure", "A_change_pct", "B_change_pct", "B_minus_A_points"], rows: out.map(function (r) { return [r.label, r.a, r.b, r.gap]; }) } };
  }
  /* ---------- observed history and the warming map (D-057); readings in docs/history-comparison.md and docs/warming-map.md; tests/test_site_history.py ---------- */
  /* World3 values sit at 1 January: the calendar-year value is the mean of the value at the start and at the end of the year. */
  function calYear(a, years, y) {
    var i = years.indexOf(y);
    if (i < 0 || i + 1 >= a.length || !isNum(a[i]) || !isNum(a[i + 1])) return null;
    return (a[i] + a[i + 1]) / 2;
  }
  function gapPct(v) { return (v >= 0 ? "+" : "-") + Math.abs(v).toFixed(1) + "%"; }
  function noGap(what) { return { year: null, model: null, obs: null, gapPct: null, within: null, sentence: what + " has " + NA + " in the years compared, so no gap is computed.", title: what + " has " + NA + " in the years compared" }; }
  function historyPopGap(years, pop, Hd) {
    var P = Hd.population, k = -1, i;
    for (i = P.years.length - 1; i >= 0; i--) { if (P.is_estimate[i] && isNum(P.billions[i]) && calYear(pop, years, P.years[i]) !== null) { k = i; break; } }
    if (k < 0) return noGap("World3 population");
    var y = P.years[k], model = calYear(pop, years, y) / 1e9, obs = P.billions[k], g = (model - obs) / obs * 100, within = Math.abs(g) <= 5;
    return { year: y, model: model, obs: obs, gapPct: g, within: within,
      sentence: "In " + y + ", the last year the UN gives as an estimate, the selected World3 run has " + model.toFixed(2) + " billion people against " + obs.toFixed(2) + " billion: " + gapPct(g) + ", " + (within ? "within" : "outside") + " the 5% band set beforehand.",
      title: "World3 population is " + gapPct(g) + " against the UN estimate in " + y + " (" + model.toFixed(2) + " against " + obs.toFixed(2) + " billion), " + (within ? "within" : "outside") + " the 5% band set beforehand" };
  }
  function historyIoGap(years, io, Hd) {
    var G = Hd.gdp, b = G.years.indexOf(1990), base = calYear(io, years, 1990), k = -1, i;
    if (base === null || b < 0 || !isNum(G.trillion_usd_2015[b])) return noGap("World3 industrial output or world GDP");
    for (i = G.years.length - 1; i >= 0; i--) { if (isNum(G.trillion_usd_2015[i]) && calYear(io, years, G.years[i]) !== null) { k = i; break; } }
    if (k < 0) return noGap("World3 industrial output or world GDP");
    var y = G.years[k], model = calYear(io, years, y) / base, obs = G.trillion_usd_2015[k] / G.trillion_usd_2015[b], g = (model - obs) / obs * 100, within = Math.abs(g) <= 25;
    return { year: y, model: model, obs: obs, gapPct: g, within: within,
      sentence: "Indexed to 1990 = 1, in " + y + " World3 industrial output is " + model.toFixed(2) + " and world GDP is " + obs.toFixed(2) + ": " + gapPct(g) + ", " + (within ? "within" : "outside") + " the 25% band set beforehand. These are not the same quantity (industry in model dollars against all output in 2015 US dollars), so the gap is not an error rate.",
      title: "Indexed to 1990 = 1, World3 industrial output is " + gapPct(g) + " against world GDP in " + y + " (" + model.toFixed(2) + " against " + obs.toFixed(2) + "): not the same quantity, so read it as a distance" };
  }
  function historyTempGap(Hd) {
    var T = Hd.temperature, i = T.years.length - 1, y = T.years[i];
    var fair = T.fair_mean[i], obs = T.hadcrut5[i], lo = T.hadcrut5_lower[i], hi = T.hadcrut5_upper[i], p05 = T.fair_p05[i], p95 = T.fair_p95[i];
    if (![fair, obs, lo, hi, p05, p95].every(isNum)) return { year: y, fair: null, obs: null, diff: null, inside: null, obsInBand: null, sentence: "In " + y + " the FaIR or HadCRUT5 temperature has " + NA + ", so no gap is computed.", title: "The FaIR or HadCRUT5 temperature has " + NA + " in " + y };
    var diff = fair - obs, inside = lo <= fair && fair <= hi, obsInBand = p05 <= obs && obs <= p95, sg = (diff >= 0 ? "+" : "-") + Math.abs(diff).toFixed(2) + " K";
    return { year: y, fair: fair, obs: obs, diff: diff, inside: inside, obsInBand: obsInBand,
      sentence: "In " + y + " the FaIR ensemble mean is " + fair.toFixed(2) + " K above 1850-1900 against HadCRUT5's " + obs.toFixed(2) + " K: " + sg + ", " + (inside ? "inside" : "outside") + " HadCRUT5's 95% interval (" + lo.toFixed(2) + " to " + hi.toFixed(2) + " K), the form of test A2.1. HadCRUT5's best estimate is " + (obsInBand ? "inside" : "outside") + " the FaIR 5th to 95th percentile band (" + p05.toFixed(2) + " to " + p95.toFixed(2) + " K).",
      title: "In " + y + " the FaIR mean is " + sg + " against HadCRUT5, " + (inside ? "inside" : "outside") + " HadCRUT5's 95% interval (the form of test A2.1)" };
  }
  var SEQ = [[255, 247, 236], [254, 232, 200], [253, 212, 158], [253, 187, 132], [252, 141, 89], [239, 101, 72], [215, 48, 31], [179, 0, 0], [127, 0, 0]];   /* ColorBrewer OrRd, 9 classes: sequential, colour-blind safe */
  function seqColor(t) {
    t = Math.max(0, Math.min(1, t));
    var x = t * (SEQ.length - 1), i = Math.min(SEQ.length - 2, Math.floor(x)), f = x - i;
    return "rgb(" + SEQ[i].map(function (v, j) { return Math.round(v + (SEQ[i + 1][j] - v) * f); }).join(",") + ")";
  }
  function mapTakeaway(Mp, C, year) {
    var i = C.years.indexOf(year), g = C.warming[i], lo = C.warming_p05[i], hi = C.warming_p95[i];
    if (!isNum(g) || !isNum(lo) || !isNum(hi)) return { global: { mean: null, lo: null, hi: null }, hottest: null, coolest: null, sentence: "The global FaIR warming has " + NA + " in " + year + ", so no regional value is computed.", title: "The global FaIR warming has " + NA + " in " + year };
    var hot = Mp.regions[0], cool = Mp.regions[0];
    Mp.regions.forEach(function (r) { if (r.c > hot.c) hot = r; if (r.c < cool.c) cool = r; });
    var h = { id: hot.id, name: hot.name, value: hot.c * g }, c = { id: cool.id, name: cool.name, value: cool.c * g };
    return { global: { mean: g, lo: lo, hi: hi }, hottest: h, coolest: c,
      sentence: "In " + year + " the global FaIR ensemble mean is " + g.toFixed(2) + " K above 1850-1900 (5th to 95th percentile " + lo.toFixed(2) + " to " + hi.toFixed(2) + " K). Scaled by the pattern, the warmest region is " + h.name + " at " + h.value.toFixed(1) + " K and the coolest is " + c.name + " at " + c.value.toFixed(1) + " K. Only the global uncertainty is shown; pattern uncertainty is not.",
      title: "Pattern-scaled warming in " + year + ": warmest region " + h.name + " at " + h.value.toFixed(1) + " K, coolest " + c.name + " at " + c.value.toFixed(1) + " K, global mean " + g.toFixed(2) + " K" };
  }
  function regionReadout(r, year, g) { return r.name + " (" + r.id + "), " + year + ": " + fx(scale(g, r.c), 2) + " K above 1850-1900 = global " + fx(g, 2) + " K x " + r.c.toFixed(2) + ". Illustrative."; }
  /* The table, and the CSV, of every region for the chosen year: raw numbers (the page formats them). */
  function mapTable(Mp, g, year) {
    return { head: ["Region", "Type", "K per K of global (c)", "Warming in " + year + " (K)"],
      rows: Mp.regions.slice().sort(function (a, b) { return b.c - a.c; }).map(function (r) { return { id: r.id, name: r.name, type: r.type, c: r.c, k: scale(g, r.c) }; }) };
  }
  /* Keyboard model of the map (one tab stop, arrows between regions): where a region is, which region is next in a direction, and reading order for Home/End. Pure: positions come from the region outlines in the data. */
  function regionCentre(r) {
    var best = null, bestArea = -1;
    r.polys.forEach(function (poly) {
      var ring = poly[0], x0 = Infinity, x1 = -Infinity, y0 = Infinity, y1 = -Infinity;
      ring.forEach(function (p) { x0 = Math.min(x0, p[0]); x1 = Math.max(x1, p[0]); y0 = Math.min(y0, p[1]); y1 = Math.max(y1, p[1]); });
      var a = (x1 - x0) * (y1 - y0);
      if (a > bestArea) { bestArea = a; best = { lon: (x0 + x1) / 2, lat: (y0 + y1) / 2 }; }
    });
    return best || { lon: 0, lat: 0 };
  }
  function mapOrder(regions) {                                         /* reading order: north to south in 30-degree bands, west to east inside a band; ties by id */
    var band = 30, pos = regions.map(function (r) { var c = regionCentre(r); return { id: r.id, row: -Math.round(c.lat / band), lon: c.lon }; });
    pos.sort(function (a, b) { return a.row - b.row || a.lon - b.lon || (a.id < b.id ? -1 : a.id > b.id ? 1 : 0); });
    return pos.map(function (p) { return p.id; });
  }
  function mapNeighbour(regions, id, dir) {                            /* nearest region centre inside the 90-degree cone of the arrow direction, or null; dir: left, right, up, down */
    var cs = {}, me = null;
    regions.forEach(function (r) { cs[r.id] = regionCentre(r); });
    me = cs[id]; if (!me) return null;
    var best = null, bestD = Infinity;
    regions.forEach(function (r) {
      if (r.id === id) return;
      var dx = cs[r.id].lon - me.lon, dy = cs[r.id].lat - me.lat;
      var along = dir === "right" ? dx : dir === "left" ? -dx : dir === "up" ? dy : dir === "down" ? -dy : NaN;
      var across = (dir === "left" || dir === "right") ? dy : dx;
      if (!(along > 0) || Math.abs(across) > along) return;
      var d = along * along + 4 * across * across;                       /* off-axis distance counts double, so the arrow prefers the region straight ahead */
      if (d < bestD || (d === bestD && r.id < best)) { bestD = d; best = r.id; }
    });
    return best;
  }
  /* The "View as table" rows: every region, highest warming first, regions with no value last (never as zero). Carries id, type and the coefficient c too (they were in the separate "View data table" this one replaced on the map card, 2026-10-22). */
  function mapValueTable(Mp, g, year) {
    var unit = "K above 1850-1900", rows = Mp.regions.map(function (r) { return { id: r.id, name: r.name, type: r.type, c: isNum(r.c) ? r.c : null, value: isNum(r.c) ? scale(g, r.c) : null }; });
    rows.sort(function (a, b) {
      var an = isNum(a.value), bn = isNum(b.value);
      if (an !== bn) return an ? -1 : 1;
      if (an && a.value !== b.value) return b.value - a.value;
      return a.name < b.name ? -1 : a.name > b.name ? 1 : 0;
    });
    var missing = rows.filter(function (r) { return !isNum(r.value); }).length;
    return { unit: unit, head: ["Region", "ID", "Type", "K per K of global (c)", "Value", "Unit"], rows: rows, missing: missing,
      caption: "Pattern-scaled warming in " + year + ", all " + rows.length + " regions, highest first (" + unit + "). Illustrative." + (missing ? " " + missing + " with " + NA + " are listed last." : "") };
  }
  function mapSpec(Mp, C, years, year) {
    var t = mapTakeaway(Mp, { years: years, warming: C.warming, warming_p05: C.warming_p05, warming_p95: C.warming_p95 }, year);
    var mx = Math.max.apply(null, C.warming.filter(isNum)) * Math.max.apply(null, Mp.regions.map(function (r) { return r.c; }));
    var cav = Mp.meta.label + " Colour scale: 0 K to " + mx.toFixed(1) + " K of regional warming above 1850-1900, the same in every year. Only the global FaIR uncertainty is shown; pattern uncertainty is not. FaIR starts about 0.04 to 0.07 K below observed (test A2.1 failed); emissions are prescribed.";
    return { kind: "map", map: Mp, year: year, global: t.global.mean, max: mx, title: t.title, summary: t.sentence + " " + cav, caveat: cav, file: "f3-warming-map-" + year, assume: ASSUME.map };
  }
  /* ---------- connections map: effect numbers for a link, from the data ---------- */
  function effectTable(kind, D) {
    var W = D.world3, WY = W.years, n = WY.length - 1, AY = D.years, T = D.climate.warming, tEnd = T[T.length - 1] , opts = ["low", "central", "high"];
    if (kind === "w3damage") {
      var std = W.levers.map(function (l) { return l.standard_index; }), off = W.runs[runKey(std, "off")];
      return { head: ["Damage option", "c (% of output per K squared)", "Industrial output, " + WY[n], "Population, " + WY[n]],
        rows: opts.map(function (o) { var e = damageEffect(W.runs[runKey(std, o)], off, n); return [o, W.damage.coeff_pct_per_K2[o].toFixed(3), signedPct(e.io), signedPct(e.pop)]; }),
        note: "Standard lever settings, against the same run with damage off. Driven by FaIR ensemble-mean warming of " + fx(tEnd, 2) + " K in " + AY[AY.length - 1] + "." };
    }
    if (kind === "s3damage") {
      var m = AY.length - 1;
      return { head: ["Damage option", "c (% of output per K squared)", "Share of S3's own output lost, " + AY[m]],
        rows: opts.map(function (o) { return [o, D.meta.damage_coeff_pct_per_K2[o].toFixed(3), fx(scale(D.runs[aiKey("central", o)].damage_fraction[m], 100), 1) + (isNum(D.runs[aiKey("central", o)].damage_fraction[m]) ? "%" : "")]; }),
        note: "Central AI investment setting. Shares of S3's own output, whose level is unvalidated. Driven by FaIR ensemble-mean warming of " + fx(tEnd, 2) + " K in " + AY[m] + "." };
    }
    return null;
  }
  function linksFinding(links) {
    var c = function (s) { return links.filter(function (l) { return l.status === s; }).length; };
    return c("built") + " of " + links.length + " links between the models are built and tested; " + (c("withheld") ? c("withheld") + (c("withheld") === 1 ? " more is" : " more are") + " built with outputs withheld" : "") + (c("not-built") ? (c("withheld") ? ", and " : "") + c("not-built") + " are not built" : "");
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
    NA: NA, isNum: isNum, scale: scale, scaleArr: scaleArr, chg: chg, diff: diff, fx: fx, runs: runs, lastNum: lastNum,
    human: human, FMT: FMT, rel: rel, signedPct: signedPct, peakOf: peakOf, firstReach: firstReach, indexOfYear: indexOfYear, sameSeries: sameSeries, sameRun: sameRun, maxSpread: maxSpread,
    DEF_LEVERS: DEF_LEVERS, DMG_STATES: DMG_STATES, AI_S: AI_S, AI_D: AI_D, PRESETS: PRESETS, runKey: runKey, aiKey: aiKey, encodeState: encodeState, decodeState: decodeState,
    csvOf: csvOf, damageNotice: damageNotice, popFinding: popFinding, industryFinding: industryFinding, resourcesFinding: resourcesFinding, pollutionFinding: pollutionFinding,
    calYear: calYear, historyPopGap: historyPopGap, historyIoGap: historyIoGap, historyTempGap: historyTempGap, SEQ: SEQ, seqColor: seqColor, mapTakeaway: mapTakeaway, regionReadout: regionReadout, mapTable: mapTable, regionCentre: regionCentre, mapOrder: mapOrder, mapNeighbour: mapNeighbour, mapValueTable: mapValueTable, mapSpec: mapSpec,
    ASSUME: ASSUME, assumeFor: assumeFor, temperatureFinding: temperatureFinding, stripesFinding: stripesFinding, stripesSpec: stripesSpec, automationFinding: automationFinding, aiDamageFinding: aiDamageFinding, damageEffect: damageEffect, damageBarsFinding: damageBarsFinding,
    w3Kpis: w3Kpis, COMPARE_METRICS: COMPARE_METRICS, compareRows: compareRows, compareHeadline: compareHeadline, compareState: compareState, effectTable: effectTable, linksFinding: linksFinding, signedFmt: signedFmt, overlayFinding: overlayFinding, barsFinding: barsFinding, encodeCompare: encodeCompare, scenarioName: scenarioName,
    METRIC_UNIT: METRIC_UNIT, RANGE_CAVEAT: RANGE_CAVEAT, tornadoSpec: tornadoSpec, dumbbellSpec: dumbbellSpec
  };
});
