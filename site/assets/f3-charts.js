/* F3 charts (D-056): inline SVG line and diverging-bar charts. Every chart gets a finding title, a text alternative, a data table, PNG and CSV download.
   The SVG viewBox is the real pixel size so text is drawn at its real size (13 px minimum). Needs window.F3 (core.js). No model numbers here. */
(function () {
  "use strict";
  /* The data file uses null for "no value": it is never drawn, never read as zero, and a line is broken where a value is missing (F3.runs). */
  var F3 = window.F3, NS = "http://www.w3.org/2000/svg";
  var $ = function (id) { return document.getElementById(id); };
  var tok = function (n) { return getComputedStyle(document.documentElement).getPropertyValue(n).trim(); };
  var esc = function (s) { return String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;"); };
  /* Scenario colours are the same on every chart (design-guidelines 4.1): line colour and a text variant that meets contrast on the card. */
  function scen() {
    return { base: tok("--base"), baseT: tok("--base-t"), a: tok("--sa"), aT: tok("--sa-t"), b: tok("--sb"), bT: tok("--sb-t"),
      acc1: tok("--acc1"), acc2: tok("--acc2"), acc3: tok("--acc3"), heat: tok("--heat") };
  }
  /* Wrap the unit line to the plot width (about 7.4 px per character at 13 px) so it is never cut off on a phone. */
  function wrapText(t, px) {
    var max = Math.max(12, Math.floor(px / 7.4)), words = String(t || "").split(" "), lines = [], cur = "";
    words.forEach(function (w) { var tt = cur ? cur + " " + w : w; if (tt.length > max && cur) { lines.push(cur); cur = w; } else cur = tt; });
    if (cur) lines.push(cur);
    return lines;
  }
  function unitSvg(lines, x, fs, fg) { return lines.map(function (l, i) { return '<text x="' + x + '" y="' + (16 + i * 16) + '" font-size="' + fs + '" font-weight="600" fill="' + fg + '">' + esc(l) + "</text>"; }).join(""); }
  function niceTicks(lo, hi, n) {
    var span = hi - lo || 1, raw = span / n, mag = Math.pow(10, Math.floor(Math.log10(raw))), f = raw / mag;
    var step = (f <= 1 ? 1 : f <= 2 ? 2 : f <= 2.5 ? 2.5 : f <= 5 ? 5 : 10) * mag, t0 = Math.ceil(lo / step - 1e-9) * step, out = [];
    for (var v = t0; v <= hi + step * 1e-9; v += step) out.push(+v.toPrecision(12));
    return out;
  }
  /* ---------- card: title, plot, legend, readout, buttons, data table ---------- */
  function mount(el, o) {
    if (el._c) return el._c;
    o = o || {};
    el.classList.add("chartcard");
    el.innerHTML = (o.title === false ? "" : '<h3 class="ct" data-role="title"></h3>') +
      '<div class="plot" data-role="plot" tabindex="0" role="group"></div><div class="leg" data-role="legend"></div>' +
      '<div class="rd" data-role="rd" aria-live="polite"></div>' +
      '<p class="assume"><a data-role="assume" href="methods.html">Assumptions and limits</a></p><div class="dl"><button type="button" data-dl="table" aria-expanded="false">View data table</button><button type="button" data-dl="png">Download PNG</button><button type="button" data-dl="csv">Download CSV</button></div>' +
      '<div class="dtbox" data-role="dt" hidden><p class="alt" data-role="alt"></p><div class="tblwrap"><table data-role="tbl"></table></div></div>';
    var c = { el: el, spec: null, cur: null };
    ["title", "plot", "legend", "rd", "dt", "alt", "tbl", "assume"].forEach(function (r) { c[r] = el.querySelector('[data-role="' + r + '"]'); });
    c.rd.textContent = "Hover, touch or use the left and right arrow keys to read values.";
    var bt = el.querySelector('[data-dl="table"]');
    bt.onclick = function () { var open = c.dt.hidden; c.dt.hidden = !open; bt.setAttribute("aria-expanded", String(open)); bt.textContent = open ? "Hide data table" : "View data table"; };
    el.querySelector('[data-dl="png"]').onclick = function () { downloadPng(c); };
    el.querySelector('[data-dl="csv"]').onclick = function () { downloadCsv(c); };
    var move = function (e) { if (c.spec && c.spec.kind === "line") showCursor(c, indexAt(c, e)); };
    c.plot.addEventListener("pointerdown", move);
    c.plot.addEventListener("pointermove", function (e) { if (e.pointerType === "mouse" || e.buttons) move(e); });
    c.plot.addEventListener("pointerleave", function (e) { if (e.pointerType === "mouse") clearCursor(c); });
    c.plot.addEventListener("keydown", function (e) {
      if (!c.spec || c.spec.kind !== "line") return;
      var n = c.spec.years.length, i = c.cur;
      if (e.key === "ArrowRight" || e.key === "ArrowLeft") { var d = (e.key === "ArrowRight" ? 1 : -1) * (e.shiftKey ? 10 : 1); i = i === null ? (d > 0 ? 0 : n - 1) : i + d; }
      else if (e.key === "Home") i = 0; else if (e.key === "End") i = n - 1; else if (e.key === "Escape") { clearCursor(c); return; } else return;
      e.preventDefault(); showCursor(c, i);
    });
    el._c = c;
    return c;
  }
  function setText(c, spec) {
    if (c.title) c.title.textContent = spec.title || "";
    c.alt.textContent = "Text alternative: " + (spec.summary || spec.title || "");
    if (spec.assume) { c.assume.href = spec.assume.href; c.assume.textContent = spec.assume.text; }
    c.plot.setAttribute("aria-label", (spec.title || spec.label || "Chart") + (spec.kind === "line" ? ". Use the left and right arrow keys to read values year by year." : ""));
  }
  function legendHtml(c, items) {
    c.legend.innerHTML = items.map(function (i) {
      return '<span><svg viewBox="0 0 34 10" aria-hidden="true"><line x1="0" y1="5" x2="34" y2="5" stroke="' + i.color + '" stroke-width="3"' + (i.dash ? ' stroke-dasharray="' + i.dash + '"' : "") + '/></svg>' + esc(i.name) + "</span>";
    }).join("");
  }
  function tableHtml(c, head, rows) {
    c.tbl.innerHTML = "<tr>" + head.map(function (h) { return "<th>" + esc(h) + "</th>"; }).join("") + "</tr>" +
      rows.map(function (r) { return "<tr>" + r.map(function (x) { return "<td>" + esc(x) + "</td>"; }).join("") + "</tr>"; }).join("");
  }
  /* ---------- line chart ---------- */
  function lineChart(el, spec) {
    var c = mount(el, spec); spec.kind = "line"; c.spec = spec;
    var years = spec.years, series = spec.series, wrap = c.plot;
    var W = Math.max(300, Math.floor(wrap.clientWidth || 340)), narrow = W < 520, H = narrow ? 320 : 300, FS = 13, R = 26, B = 34;
    var ul = wrapText(spec.unit, W - 24), nl = series.filter(function (s) { return s.label; }).length, T = 28 + Math.max(0, nl - 1) * 15 + (ul.length - 1) * 16;
    var xmin = years[0], xmax = years[years.length - 1], ymin = Infinity, ymax = -Infinity;
    series.forEach(function (s) { (s.band ? [s.band[0], s.band[1]] : []).concat([s.y]).forEach(function (a) { a.forEach(function (v) { if (F3.isNum(v)) { ymin = Math.min(ymin, v); ymax = Math.max(ymax, v); } }); }); });
    if (spec.ymin !== undefined) ymin = spec.ymin; if (spec.ymax !== undefined) ymax = spec.ymax;
    var pad = (ymax - ymin) * 0.03 || 1; if (spec.ymin === undefined) ymin -= pad; if (spec.ymax === undefined) ymax += pad;
    var fm = F3.FMT[spec.fmt || "index"], ticks = niceTicks(ymin, ymax, narrow ? 4 : 5), labels = ticks.map(fm);
    var L = Math.min(Math.round(W * 0.34), Math.max(44, Math.ceil(Math.max.apply(null, labels.map(function (s) { return s.length; })) * 7.6) + 14));
    var X = function (x) { return L + (x - xmin) / (xmax - xmin) * (W - L - R); }, Yp = function (v) { return T + (1 - (v - ymin) / (ymax - ymin)) * (H - T - B); };
    var line = tok("--line"), mut = tok("--mut"), fg = tok("--fg"), card = tok("--card"), g = "";
    ticks.forEach(function (v, i) { var yy = Yp(v); g += '<line x1="' + L + '" x2="' + (W - R) + '" y1="' + yy + '" y2="' + yy + '" stroke="' + line + '"/><text x="' + (L - 6) + '" y="' + (yy + 4) + '" text-anchor="end" font-size="' + FS + '" fill="' + mut + '">' + labels[i] + "</text>"; });
    var step = spec.xstep || (narrow ? 25 : 15);
    for (var yr = Math.ceil(xmin / step) * step; yr <= xmax; yr += step) g += '<text x="' + X(yr) + '" y="' + (H - 10) + '" text-anchor="middle" font-size="' + FS + '" fill="' + mut + '">' + yr + "</text>";
    g += unitSvg(ul, 8, FS, fg);
    var ends = [];
    series.forEach(function (s) {
      if (s.band) {
        var both = years.map(function (x, i) { return F3.isNum(s.band[0][i]) && F3.isNum(s.band[1][i]) ? 1 : null; });
        F3.runs(both).forEach(function (r) {
          var idx = years.slice(r[0], r[1] + 1).map(function (x, k) { return r[0] + k; });
          var up = idx.map(function (i) { return X(years[i]) + "," + Yp(s.band[1][i]); }), dn = idx.map(function (i) { return X(years[i]) + "," + Yp(s.band[0][i]); }).reverse();
          g += '<polygon points="' + up.concat(dn).join(" ") + '" fill="' + s.color + '" opacity=".2"/>';
        });
      }
      if (s.dots) {
        years.forEach(function (x, i) {
          if (!F3.isNum(s.y[i])) return;
          var hollow = s.proj && s.proj[i];
          g += '<circle cx="' + X(x) + '" cy="' + Yp(s.y[i]) + '" r="2.8" fill="' + (hollow ? card : s.color) + '" stroke="' + s.color + '" stroke-width="1.4"/>';
        });
      } else F3.runs(s.y).forEach(function (r) {
        var pts = years.slice(r[0], r[1] + 1).map(function (x, k) { return X(x) + "," + Yp(s.y[r[0] + k]); }).join(" ");
        g += '<polyline points="' + pts + '" fill="none" stroke="' + s.color + '" stroke-width="' + (s.width || 2.6) + '"' + (s.dash ? ' stroke-dasharray="' + s.dash + '"' : "") + ' stroke-linejoin="round"/>';
      });
      var last = F3.lastNum(s.y);
      if (s.label && last >= 0) ends.push({ label: s.label, color: s.tcolor || s.color, y: Yp(s.y[last]) - 6 });
    });
    ends.sort(function (a, b) { return b.y - a.y; });
    for (var i = 1; i < ends.length; i++) if (ends[i - 1].y - ends[i].y < 15) ends[i].y = ends[i - 1].y - 15;
    ends.forEach(function (e) { g += '<text x="' + (W - R - 6) + '" y="' + Math.max(e.y, 12) + '" text-anchor="end" font-size="' + FS + '" font-weight="600" fill="' + e.color + '" stroke="' + card + '" stroke-width="3" paint-order="stroke">' + esc(e.label) + "</text>"; });
    (spec.annotations || []).forEach(function (a) {
      var x = X(a.x), y = Yp(a.y), right = x > W * 0.62, tx = right ? x - 10 : x + 10, ty = y - 12;
      if (ty < 14) ty = y + 20;
      g += '<circle cx="' + x + '" cy="' + y + '" r="5" fill="' + (a.color || fg) + '" stroke="' + card + '" stroke-width="2"/>' +
        '<text x="' + tx + '" y="' + ty + '" text-anchor="' + (right ? "end" : "start") + '" font-size="' + FS + '" font-weight="600" fill="' + (a.tcolor || fg) + '" stroke="' + card + '" stroke-width="3" paint-order="stroke">' + esc(a.text) + "</text>";
    });
    wrap.innerHTML = '<svg viewBox="0 0 ' + W + " " + H + '" width="' + W + '" height="' + H + '" role="img" aria-label="' + esc((spec.title || spec.label || "") + ". " + (spec.summary || "")) + '"><title>' + esc(spec.title || spec.label || "") + "</title><desc>" + esc(spec.summary || "") + "</desc>" + g + "</svg>";
    c.m = { X: X, Yp: Yp, T: T, B: B, W: W, H: H, fm: fm };
    setText(c, spec);
    legendHtml(c, series.filter(function (s) { return s.name; }).map(function (s) { return { name: s.name, color: s.color, dash: s.dash }; }));
    var hs = ["Year"], cols = [];
    series.forEach(function (s) { hs.push(s.name || "value"); cols.push(s.y); if (s.band) { hs.push((s.name || "value") + " 5th percentile"); cols.push(s.band[0]); hs.push((s.name || "value") + " 95th percentile"); cols.push(s.band[1]); } });
    var ts = spec.tableStep || 10, rows = [];
    years.forEach(function (y, i) { if ((y - xmin) % ts === 0 || i === years.length - 1) rows.push([y].concat(cols.map(function (a) { return fm(a[i]); }))); });
    tableHtml(c, hs, rows);
    if (c.cur !== null && c.cur < years.length) showCursor(c, c.cur);
  }
  function showCursor(c, i) {
    var s = c.spec, m = c.m, svg = c.plot.querySelector("svg"); if (!svg) return;
    i = Math.max(0, Math.min(s.years.length - 1, i)); c.cur = i;
    svg.querySelectorAll(".cur").forEach(function (e) { e.remove(); });
    var x = m.X(s.years[i]), ln = document.createElementNS(NS, "line");
    ln.setAttribute("class", "cur"); ln.setAttribute("x1", x); ln.setAttribute("x2", x); ln.setAttribute("y1", m.T); ln.setAttribute("y2", m.H - m.B); ln.setAttribute("stroke", tok("--fg")); ln.setAttribute("stroke-width", "1.5"); svg.appendChild(ln);
    s.series.forEach(function (se) {
      if (!F3.isNum(se.y[i])) return;
      var ci = document.createElementNS(NS, "circle"); ci.setAttribute("class", "cur"); ci.setAttribute("cx", x); ci.setAttribute("cy", m.Yp(se.y[i])); ci.setAttribute("r", "4.5"); ci.setAttribute("fill", se.color); ci.setAttribute("stroke", tok("--card")); ci.setAttribute("stroke-width", "1.5"); svg.appendChild(ci);
    });
    c.rd.textContent = s.years[i] + ": " + s.series.map(function (se) { return (se.name || "value") + " " + m.fm(se.y[i]) + (se.band ? " (5 to 95%: " + m.fm(se.band[0][i]) + " to " + m.fm(se.band[1][i]) + ")" : ""); }).join("; ");
  }
  function clearCursor(c) { c.cur = null; c.plot.querySelectorAll(".cur").forEach(function (e) { e.remove(); }); c.rd.textContent = "Hover, touch or use the left and right arrow keys to read values."; }
  function indexAt(c, ev) {
    var m = c.m, svg = c.plot.querySelector("svg"), r = svg.getBoundingClientRect(), k = m.W / r.width, xv = (ev.clientX - r.left) * k, ys = c.spec.years;
    var L = m.X(ys[0]), Rr = m.X(ys[ys.length - 1]);
    return Math.round((xv - L) / (Rr - L) * (ys.length - 1));
  }
  /* ---------- diverging bar chart: categories x series, change against a baseline, a visible zero line ---------- */
  function barChart(el, spec) {
    var c = mount(el, spec); spec.kind = "bar"; c.spec = spec;
    var wrap = c.plot, W = Math.max(300, Math.floor(wrap.clientWidth || 340)), FS = 13, ns = spec.series.length, bh = 18, gap = 5, catH = 22 + ns * (bh + gap) + 10, ul = wrapText(spec.unit, W - 24), T = 26 + (ul.length - 1) * 16, B = 34;
    var H = T + spec.categories.length * catH + B, vals = [0];
    spec.categories.forEach(function (k) { k.values.forEach(function (v) { if (F3.isNum(v)) vals.push(v); }); });
    var lo = Math.min.apply(null, vals), hi = Math.max.apply(null, vals), room = 74, L = 12 + (lo < 0 ? room : 0), Rr = W - 12 - (hi > 0 ? room : 0);
    if (hi === lo) { hi = lo + 1; }
    var X = function (v) { return L + (v - lo) / (hi - lo) * (Rr - L); }, zx = X(0), fm = spec.fmt, fg = tok("--fg"), mut = tok("--mut"), line = tok("--line"), card = tok("--card"), g = "";
    niceTicks(lo, hi, 4).forEach(function (v) {
      var x = X(v); g += '<line x1="' + x + '" x2="' + x + '" y1="' + T + '" y2="' + (H - B) + '" stroke="' + line + '"/><text x="' + x + '" y="' + (H - 12) + '" text-anchor="middle" font-size="' + FS + '" fill="' + mut + '">' + esc(spec.tickFmt ? spec.tickFmt(v) : fm(v)) + "</text>";
    });
    g += unitSvg(ul, 8, FS, fg);
    spec.categories.forEach(function (k, ci) {
      var y0 = T + ci * catH;
      g += '<text x="' + Math.max(8, Math.min(zx, W - 8)) + '" y="' + (y0 + 16) + '" text-anchor="' + (zx > W * 0.66 ? "end" : "start") + '" font-size="' + FS + '" font-weight="600" fill="' + fg + '">' + esc(k.label) + "</text>";
      k.values.forEach(function (v, si) {
        var s = spec.series[si], y = y0 + 22 + si * (bh + gap);
        if (!F3.isNum(v)) {                                               /* no value: no bar, a label saying so, never a zero-length bar read as zero */
          g += '<text x="' + (zx + 6) + '" y="' + (y + 13.5) + '" text-anchor="start" font-size="' + FS + '" font-weight="600" fill="' + (s.tcolor || s.color) + '">' + esc((s.short ? s.short + " " : "") + F3.NA) + "</text>";
          return;
        }
        var x1 = Math.min(zx, X(v)), w = Math.max(Math.abs(X(v) - zx), 1.5), dim = s.dim && s.dim(ci);
        g += '<rect x="' + x1 + '" y="' + y + '" width="' + w + '" height="' + bh + '" rx="2" fill="' + s.color + '"' + (dim ? ' opacity=".45"' : "") + "/>";
        var lab = (s.short ? s.short + " " : "") + fm(v), right = v >= 0;
        g += '<text x="' + (right ? X(v) + 6 : X(v) - 6) + '" y="' + (y + 13.5) + '" text-anchor="' + (right ? "start" : "end") + '" font-size="' + FS + '" font-weight="600" fill="' + (s.tcolor || s.color) + '" stroke="' + card + '" stroke-width="3" paint-order="stroke">' + esc(lab) + "</text>";
      });
    });
    g += '<line x1="' + zx + '" x2="' + zx + '" y1="' + (T - 4) + '" y2="' + (H - B) + '" stroke="' + fg + '" stroke-width="2.2"/>';
    wrap.innerHTML = '<svg viewBox="0 0 ' + W + " " + H + '" width="' + W + '" height="' + H + '" role="img" aria-label="' + esc((spec.title || "") + ". " + (spec.summary || "")) + '"><title>' + esc(spec.title || "") + "</title><desc>" + esc(spec.summary || "") + "</desc>" + g + "</svg>";
    setText(c, spec);
    c.rd.textContent = spec.zeroNote || "The vertical line is zero: no change.";
    legendHtml(c, spec.series.map(function (s) { return { name: s.name, color: s.color }; }));
    var hs = [spec.catHead || "Measure"].concat(spec.series.map(function (s) { return s.name; }));
    tableHtml(c, hs, spec.categories.map(function (k) { return [k.label].concat(k.values.map(function (v) { return F3.isNum(v) ? fm(v) : F3.NA; })); }));
  }
  /* ---------- warming stripes: one stripe per year, same card tools as the other charts (data table, PNG, CSV, text alternative) ---------- */
  var RAMP = { lo: [33, 102, 172], mid: [247, 247, 247], hi: [178, 24, 43] };
  function mixc(p, q, t) { return p.map(function (v, i) { return Math.round(v + (q[i] - v) * t); }); }
  /* The static <svg id="ig_stripes"> in the page (title, desc and 13 px labels) is adopted as the plot, so it is also the fallback before the script runs. */
  function stripes(el, spec) {
    if (!el._svg) el._svg = el.querySelector("svg");
    var svg = el._svg, c = mount(el, spec), vals = spec.values, years = spec.years, n = vals.length, w = 320 / n, nums = vals.filter(F3.isNum);
    spec.kind = "stripes"; c.spec = spec;
    var lo = Math.min.apply(null, nums), hi = Math.max.apply(null, nums);
    var col = function (v) { var t = (v - lo) / ((hi - lo) || 1), k = t < 0.5 ? mixc(RAMP.lo, RAMP.mid, t * 2) : mixc(RAMP.mid, RAMP.hi, (t - 0.5) * 2); return "rgb(" + k.join(",") + ")"; };
    svg.querySelector("#stripes_g").innerHTML = vals.map(function (v, i) {
      return '<rect x="' + (i * w).toFixed(2) + '" y="0" width="' + (w + 0.6).toFixed(2) + '" height="84" ' + (F3.isNum(v) ? 'fill="' + col(v) + '"' : 'style="fill:var(--line)"') + "/>";
    }).join("");
    svg.querySelector("#stripes_l").textContent = years[0] + ": " + F3.fx(lo, 2) + " K"; svg.querySelector("#stripes_r").textContent = years[n - 1] + ": " + F3.fx(hi, 2) + " K";
    svg.querySelector("#ig_stripes_t").textContent = spec.title; svg.querySelector("#ig_stripes_d").textContent = spec.summary;
    c.plot.innerHTML = ""; c.plot.appendChild(svg); c.plot.removeAttribute("tabindex");
    setText(c, spec);
    c.plot.setAttribute("aria-label", spec.title);
    c.legend.innerHTML = '<span><i class="sw" style="background:' + col(lo) + '"></i>Blue: the lowest mean in the period (' + F3.fx(lo, 2) + ' K)</span><span><i class="sw" style="background:' + col(hi) + '"></i>Red: the highest (' + F3.fx(hi, 2) + ' K)</span>' +
      (nums.length < n ? '<span><i class="sw" style="background:var(--line)"></i>Grey: no value</span>' : "");
    c.rd.textContent = "Colour is relative to this run, not to observations. Read every year in the data table.";
    tableHtml(c, ["Year", spec.valueName], years.map(function (y, i) { return [y, F3.FMT[spec.fmt](vals[i])]; }));
    c.dt.classList.add("long");
  }
  /* ---------- warming map: 58 AR6 regions coloured by pattern-scaled warming for the chosen year (D-057); same card tools as the other charts ---------- */
  function ringPath(r) { return "M" + r.map(function (p) { return (p[0] + 180).toFixed(1) + "," + (90 - p[1]).toFixed(1); }).join("L") + "Z"; }
  function mapScale(c, W, mx) {
    var n = 9, bw = W - 24, every = W < 460 ? 2 : 1, st = "", ticks = "", k, v;
    for (k = 0; k <= n; k++) st += '<stop offset="' + k / n + '" stop-color="' + F3.seqColor(k / n) + '"/>';
    for (v = 0; v <= mx; v += every) { var x = 12 + v / mx * bw; ticks += '<line x1="' + x + '" x2="' + x + '" y1="14" y2="20" stroke="' + tok("--mut") + '"/><text x="' + x + '" y="36" font-size="13" text-anchor="middle" fill="' + tok("--mut") + '">' + v + " K</text>"; }
    c.legend.innerHTML = '<svg class="cscale" viewBox="0 0 ' + W + ' 42" width="' + W + '" height="42" role="img" aria-label="Colour scale from 0 K to ' + mx.toFixed(0) + ' K of regional warming above 1850-1900"><defs><linearGradient id="mapgrad">' + st +
      '</linearGradient></defs><rect x="12" y="2" width="' + bw + '" height="12" fill="url(#mapgrad)" stroke="' + tok("--line") + '"/>' + ticks + "</svg>";
  }
  function regionMap(el, spec) {
    var c = mount(el, spec), M = spec.map, g = spec.global, mx = spec.max, key = tok("--card") + tok("--mut") + tok("--line");
    spec.kind = "map"; c.spec = spec;
    if (!c.order) { c.order = F3.mapOrder(M.regions); c.tab = c.order[0]; }                   /* roving tabindex: exactly one region is a tab stop; arrows, Home and End move it */
    if (c.mapKey !== key) {                                                       /* build the regions once per theme; later calls only recolour */
      var order = { "Ocean": 0, "Land-Ocean": 1, "Land": 2 }, regs = M.regions.slice().sort(function (a, b) { return order[a.type] - order[b.type]; }), bg = tok("--card"), s = "";
      s += '<rect x="0" y="0" width="360" height="180" fill="' + tok("--line") + '" opacity=".25"/><g role="group" aria-label="Regions. One tab stop: use the arrow keys to move between regions, Home and End for the first and last, Escape to leave.">';
      regs.forEach(function (r) { s += '<path class="reg" data-id="' + r.id + '" tabindex="' + (r.id === c.tab ? "0" : "-1") + '" role="img" aria-label="' + esc(r.name) + '" d="' + r.polys.map(function (poly) { return poly.map(ringPath).join(""); }).join("") + '" fill-rule="evenodd" stroke="' + bg + '" stroke-width=".35"/>'; });
      s += '</g><path d="' + M.coast.map(ringPath).join("") + '" fill="none" stroke="' + tok("--mut") + '" stroke-width=".25" pointer-events="none"/>';
      s += '<path class="ringhalo" d="" fill="none" stroke="' + bg + '" stroke-width="5" vector-effect="non-scaling-stroke" pointer-events="none"/><path class="ring" d="" fill="none" stroke="' + tok("--focus") + '" stroke-width="2.5" vector-effect="non-scaling-stroke" pointer-events="none"/>';
      c.plot.innerHTML = '<svg viewBox="0 0 360 180" width="100%" role="img" aria-label="' + esc(spec.title) + '"><title>' + esc(spec.title) + "</title><desc>" + esc(spec.summary) + "</desc>" + s + "</svg>";
      c.plot.removeAttribute("tabindex"); c.sel = null;
      var regEls = function () { return c.plot.querySelectorAll("path.reg"); };
      var rove = function (id) {                                                  /* make id the one tab stop and move focus to it */
        regEls().forEach(function (q) { q.setAttribute("tabindex", q.dataset.id === id ? "0" : "-1"); });
        c.tab = id; var el2 = c.plot.querySelector('path.reg[data-id="' + id + '"]'); if (el2) el2.focus();
      };
      regEls().forEach(function (p) {
        var pick = function () { c.sel = p.dataset.id; mapRead(c); };
        var rest = function () { var f = document.activeElement; c.sel = f && f.classList && f.classList.contains("reg") && c.plot.contains(f) ? f.dataset.id : null; mapRead(c); };
        p.addEventListener("mouseenter", pick); p.addEventListener("click", pick);
        p.addEventListener("focus", function () {
          regEls().forEach(function (q) { q.setAttribute("tabindex", q === p ? "0" : "-1"); }); c.tab = p.dataset.id; pick();
        });
        p.addEventListener("mouseleave", rest);
        p.addEventListener("blur", function () { setTimeout(rest, 0); });          /* after the move: focus lands on another region or leaves the map */
      });
      c.plot.addEventListener("keydown", function (e) {
        if (e.ctrlKey || e.altKey || e.metaKey || !e.target.classList || !e.target.classList.contains("reg")) return;
        var id = e.target.dataset.id, dirs = { ArrowLeft: "left", ArrowRight: "right", ArrowUp: "up", ArrowDown: "down" }, to = null;
        if (dirs[e.key]) to = F3.mapNeighbour(c.spec.map.regions, id, dirs[e.key]) || id;
        else if (e.key === "Home") to = c.order[0]; else if (e.key === "End") to = c.order[c.order.length - 1];
        else if (e.key === "Escape") { e.preventDefault(); c.sel = null; mapRead(c); e.target.blur(); return; } else return;
        e.preventDefault(); rove(to);
      });
      c.mapKey = key;
    }
    if (!c.vt) {                                                                   /* the "View as table" control and its table, built once */
      var base = (el.id || "map") + "_vt";
      c.rd.insertAdjacentHTML("afterend", '<div class="mapview"><button type="button" class="mapbtn" id="' + base + '_btn" aria-expanded="false" aria-controls="' + base + '">View as table</button>' +
        '<div class="maptblbox" id="' + base + '" role="region" aria-label="Warming by region as a table" tabindex="0" hidden><table class="maptable" data-role="vt"></table></div></div>');
      c.vt = el.querySelector('[data-role="vt"]'); c.vtBox = el.querySelector(".maptblbox"); c.vtBtn = el.querySelector(".mapbtn");
      c.vtBtn.onclick = function () { var open = c.vtBox.hidden; c.vtBox.hidden = !open; c.vtBtn.setAttribute("aria-expanded", String(open)); c.vtBtn.textContent = open ? "Hide table" : "View as table"; };
    }
    var vt = F3.mapValueTable(M, g, spec.year);
    c.vt.innerHTML = "<caption>" + esc(vt.caption) + "</caption><thead><tr>" + vt.head.map(function (h) { return '<th scope="col">' + esc(h) + "</th>"; }).join("") + "</tr></thead><tbody>" +
      vt.rows.map(function (r) { return '<tr><th scope="row">' + esc(r.name) + "</th><td>" + (F3.isNum(r.value) ? r.value.toFixed(2) : F3.NA) + "</td><td>" + esc(vt.unit) + "</td></tr>"; }).join("") + "</tbody>";
    c.plot.querySelectorAll("path.reg").forEach(function (p) {
      var r = M.regions.filter(function (x) { return x.id === p.dataset.id; })[0], v = F3.scale(g, r.c);
      p.setAttribute("fill", F3.isNum(v) ? F3.seqColor(v / mx) : tok("--line"));
      p.setAttribute("aria-label", r.name + ": " + F3.fx(v, 2) + " K above 1850-1900 in " + spec.year);
    });
    var svg = c.plot.querySelector("svg"); svg.setAttribute("aria-label", spec.title); svg.querySelector("title").textContent = spec.title; svg.querySelector("desc").textContent = spec.summary;
    setText(c, spec); c.plot.setAttribute("aria-label", spec.title);
    mapScale(c, Math.max(280, Math.floor(c.legend.clientWidth || 320)), mx);
    var tb = F3.mapTable(M, g, spec.year);
    tableHtml(c, tb.head, tb.rows.map(function (r) { return [r.name + " (" + r.id + ")", r.type, r.c.toFixed(2), F3.fx(r.k, 2)]; }));
    c.dt.classList.add("long"); mapRead(c);
  }
  function mapRead(c) {
    var s = c.spec, r = c.sel ? s.map.regions.filter(function (x) { return x.id === c.sel; })[0] : null;
    c.rd.textContent = r ? F3.regionReadout(r, s.year, s.global) : "Hover or tap a region, or tab to the map and use the arrow keys, to read its value.";
    var src = c.sel ? c.plot.querySelector('path.reg[data-id="' + c.sel + '"]') : null, d = src ? src.getAttribute("d") : "";
    c.plot.querySelectorAll("path.ring, path.ringhalo").forEach(function (q) { q.setAttribute("d", d); });
  }
  /* ---------- downloads ---------- */
  function download(blob, name) { var a = document.createElement("a"); a.href = URL.createObjectURL(blob); a.download = name; document.body.appendChild(a); a.click(); a.remove(); setTimeout(function () { URL.revokeObjectURL(a.href); }, 2000); }
  function csvFor(c) {
    var s = c.spec, notes = ["F3 Explorer v0.2: a conditional scenario, not a forecast."]; if (s.caveat) notes.push(s.caveat);
    if (s.kind === "map") {
      var tb = F3.mapTable(s.map, s.global, s.year), q2 = function (x) { return /[",\n]/.test(x) ? '"' + x.replace(/"/g, '""') + '"' : x; };
      var out = ["region_id,region,type,coefficient_K_per_K," + "warming_K_" + s.year];
      tb.rows.forEach(function (r) { out.push([r.id, q2(r.name), r.type, r.c, F3.isNum(r.k) ? r.k : ""].join(",")); });
      notes.forEach(function (x) { out.push("# " + x); });
      if (tb.rows.some(function (r) { return !F3.isNum(r.k); })) out.push("# An empty cell means no value, not zero.");
      return out.join("\n") + "\n";
    }
    if (s.kind === "stripes") return F3.csvOf(s.years, [{ name: s.valueName, y: s.values }], notes);
    if (s.kind === "line") {
      var cols = []; s.series.forEach(function (se) { cols.push({ name: se.name || "value", y: se.y }); if (se.band) { cols.push({ name: (se.name || "value") + " 5th percentile", y: se.band[0] }); cols.push({ name: (se.name || "value") + " 95th percentile", y: se.band[1] }); } });
      return F3.csvOf(s.years, cols, notes);
    }
    var q = function (t) { return /[",\n]/.test(t) ? '"' + t.replace(/"/g, '""') + '"' : t; }, lines = [[s.catHead || "Measure"].concat(s.series.map(function (x) { return x.name; })).map(q).join(",")];
    s.categories.forEach(function (k) { lines.push([q(k.label)].concat(k.values.map(function (v) { return F3.isNum(v) ? String(v) : ""; })).join(",")); });
    notes.forEach(function (t) { lines.push("# " + t); });
    if (s.categories.some(function (k) { return k.values.some(function (v) { return !F3.isNum(v); }); })) lines.push("# An empty cell means no value, not zero.");
    return lines.join("\n") + "\n";
  }
  function downloadCsv(c) { download(new Blob([csvFor(c)], { type: "text/csv;charset=utf-8" }), (c.spec.file || "f3-chart") + ".csv"); }
  function downloadPng(c) {
    var svg = c.plot.querySelector("svg").cloneNode(true), vb = svg.viewBox.baseVal, W = vb.width, H = vb.height;
    svg.querySelectorAll(".cur").forEach(function (e) { e.remove(); }); svg.setAttribute("xmlns", NS); svg.setAttribute("font-family", "Work Sans, system-ui, Segoe UI, Roboto, sans-serif");
    var lines = [c.spec.title || ""].concat(["F3 Explorer v0.2: a conditional scenario, not a forecast."], c.spec.caveat ? [c.spec.caveat] : []).filter(Boolean);
    var S = 2, pad = 8, lh = 17, cv = document.createElement("canvas"), ctx = cv.getContext("2d"), wrapped = [];
    ctx.font = "13px system-ui, Segoe UI, Roboto, sans-serif";
    lines.forEach(function (t) { var cur = ""; t.split(" ").forEach(function (w) { var tt = cur ? cur + " " + w : w; if (ctx.measureText(tt).width > W - 2 * pad && cur) { wrapped.push(cur); cur = w; } else cur = tt; }); wrapped.push(cur); });
    var extra = wrapped.length * lh + pad * 2; cv.width = W * S; cv.height = (H + extra) * S;
    var img = new Image();
    img.onload = function () {
      var k = cv.getContext("2d"); k.scale(S, S); k.fillStyle = tok("--card"); k.fillRect(0, 0, W, H + extra); k.drawImage(img, 0, 0, W, H);
      k.fillStyle = tok("--mut"); k.font = "13px system-ui, Segoe UI, Roboto, sans-serif"; wrapped.forEach(function (t, i) { k.fillText(t, pad, H + pad + 13 + i * lh); });
      cv.toBlob(function (b) { download(b, (c.spec.file || "f3-chart") + ".png"); }, "image/png");
    };
    img.src = "data:image/svg+xml;charset=utf-8," + encodeURIComponent(new XMLSerializer().serializeToString(svg));
  }
  window.F3C = { tok: tok, scen: scen, mount: mount, lineChart: lineChart, barChart: barChart, stripes: stripes, regionMap: regionMap, esc: esc, csvFor: csvFor };
})();
