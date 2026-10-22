/* F3 connections map (D-056 stage 5): select a numbered link to open the inspector. The map, buttons and list are static markup (connections_body.py); this script wires
   selection, keyboard operation, the URL hash and the effect numbers, which are computed from window.F3DATA by core.js. No model numbers here. */
(function () {
  "use strict";
  var D = window.F3DATA, F3 = window.F3, C = window.F3C;
  var $ = function (id) { return document.getElementById(id); };
  var DATA = JSON.parse($("linksdata").textContent), LINKS = DATA.links, NODE = {};
  DATA.nodes.forEach(function (n) { NODE[n.id] = n; });
  var STATUS = { built: "Built and tested", "not-built": "Not built", withheld: "Built, outputs withheld" };
  var sel = null;

  function byN(n) { return LINKS.filter(function (l) { return l.n === n; })[0]; }
  function list(title, items, empty) {
    return "<h4>" + title + "</h4>" + (items.length ? "<ul>" + items.map(function (t) { return "<li>" + C.esc(t) + "</li>"; }).join("") + "</ul>" : '<p class="note">' + empty + "</p>");
  }
  function effectHtml(l) {
    var t = l.effect ? F3.effectTable(l.effect, D) : null;
    if (!t) return '<h4>Effect numbers</h4><p class="note">' + (l.status === "withheld" ? "Withheld: the outputs of this link leave any plausible range until the S3 compute path is validated (awaiting Epoch AI)." : "None: this link is not built, so it has no effect in any Explorer run.") + "</p>";
    return "<h4>Effect numbers (computed from the data)</h4><div class=\"tblwrap\" tabindex=\"0\" role=\"region\" aria-label=\"Effect numbers\"><table class=\"efx\"><tr>" + t.head.map(function (h) { return "<th scope=\"col\">" + C.esc(h) + "</th>"; }).join("") + "</tr>" +
      t.rows.map(function (r) { return "<tr><th scope=\"row\">" + C.esc(r[0]) + "</th>" + r.slice(1).map(function (c) { return "<td>" + C.esc(c) + "</td>"; }).join("") + "</tr>"; }).join("") + "</table></div><p class=\"note\">" + C.esc(t.note) + "</p>";
  }
  function inspectorHtml(l) {
    var dash = { built: "", "not-built": ' stroke-dasharray="7 5"', withheld: ' stroke-dasharray="1 6" stroke-linecap="round"' }[l.status];
    return '<h3>Link ' + l.n + ": " + C.esc(NODE[l.from].label + " to " + NODE[l.to].label) + "</h3>" +
      '<p><span class="lbadge ' + l.status + '"><svg viewBox="0 0 44 10" aria-hidden="true" class="samp ' + l.status + '"><line x1="2" y1="5" x2="42" y2="5" stroke-width="3.4"' + dash + "/></svg> " + STATUS[l.status] + "</span></p>" +
      "<h4>What it does</h4><p>" + C.esc(l.what) + "</p>" + effectHtml(l) +
      list("Tests met", l.met, "No test applies: the link is not built.") + list("Tests failed", l.failed, "None recorded for this link.") + list("Not compared", l.notcompared, "Nothing recorded.") +
      '<p><a href="' + l.methods + '">Methods and records for this link</a> &middot; <a href="limitations.html">Limitations</a></p>';
  }
  function select(n, focus) {
    sel = n;
    var l = byN(n);
    $("insp_body").innerHTML = inspectorHtml(l);
    document.querySelectorAll(".nbtn").forEach(function (b) { b.setAttribute("aria-pressed", String(+b.dataset.n === n)); });
    document.querySelectorAll(".ln").forEach(function (p) { p.classList.toggle("sel", +p.dataset.n === n); });
    document.querySelectorAll(".lbtn").forEach(function (b) {
      var open = +b.dataset.n === n; b.setAttribute("aria-expanded", String(open));
      var box = $("insp_l" + b.dataset.n); box.hidden = !open; box.innerHTML = open ? inspectorHtml(l) : "";
    });
    try { history.replaceState(null, "", "#link=" + n); } catch (e) { /* hash is a convenience */ }
    if (focus) { var t = document.querySelector('.nbtn[data-n="' + n + '"]'); if (t && t.offsetParent !== null) t.focus(); }
  }
  function fromHash() { var m = /link=([1-7])/.exec(location.hash); return m ? +m[1] : 1; }
  $("headline").textContent = F3.linksFinding(LINKS);
  document.querySelectorAll(".nbtn").forEach(function (b) {
    b.addEventListener("click", function () { select(+b.dataset.n); });
    b.addEventListener("keydown", function (e) {
      var n = +b.dataset.n, k = e.key, nx = null;
      if (k === "ArrowRight" || k === "ArrowDown") nx = n % LINKS.length + 1; else if (k === "ArrowLeft" || k === "ArrowUp") nx = (n + LINKS.length - 2) % LINKS.length + 1; else if (k === "Home") nx = 1; else if (k === "End") nx = LINKS.length;
      if (nx !== null) { e.preventDefault(); var t = document.querySelector('.nbtn[data-n="' + nx + '"]'); if (t) t.focus(); }
    });
  });
  document.querySelectorAll("path.hit").forEach(function (p) { p.addEventListener("click", function () { select(+p.dataset.hit); }); });
  document.querySelectorAll(".lbtn").forEach(function (b) { b.addEventListener("click", function () { if (sel === +b.dataset.n && b.getAttribute("aria-expanded") === "true") { sel = null; b.setAttribute("aria-expanded", "false"); $("insp_l" + b.dataset.n).hidden = true; } else select(+b.dataset.n); }); });
  window.addEventListener("hashchange", function () { select(fromHash()); });
  select(fromHash());
})();
