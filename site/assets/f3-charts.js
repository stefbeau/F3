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
      '<div class="dl"><button type="button" data-dl="table" aria-expanded="false">View data table</button><button type="button" data-dl="png">Download PNG</button><button type="button" data-dl="csv">Download CSV</button></div>' +
      '<div class="dtbox" data-role="dt" hidden><p class="alt" data-role="alt"></p><div class="tblwrap"><table data-role="tbl"></table></div></div>';
    var c = { el: el, spec: null, cur: null };
    ["title", "plot", "legend", "rd", "dt", "alt", "tbl"].forEach(function (r) { c[r] = el.querySelector('[data-role="' + r + '"]'); });
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
      F3.runs(s.y).forEach(function (r) {
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
  /* ---------- downloads ---------- */
  function download(blob, name) { var a = document.createElement("a"); a.href = URL.createObjectURL(blob); a.download = name; document.body.appendChild(a); a.click(); a.remove(); setTimeout(function () { URL.revokeObjectURL(a.href); }, 2000); }
  function csvFor(c) {
    var s = c.spec, notes = ["F3 Explorer v0.2: a conditional scenario, not a forecast."]; if (s.caveat) notes.push(s.caveat);
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
  window.F3C = { tok: tok, scen: scen, mount: mount, lineChart: lineChart, barChart: barChart, esc: esc, csvFor: csvFor };
})();
