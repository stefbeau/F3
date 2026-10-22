/* F3 shell: theme toggle. The initial theme is set by a tiny inline script in <head> (saved choice, else the page kind's default; reading pages follow
   prefers-color-scheme). The saved choice is a per-viewer convenience: every access is in try/catch and the page works without it. */
(function () {
  var root = document.documentElement, btn = document.getElementById("themeToggle");
  function label() {
    var dark = root.getAttribute("data-theme") === "dark";
    if (btn) { btn.textContent = dark ? "Light theme" : "Dark theme"; btn.setAttribute("aria-pressed", String(dark)); btn.setAttribute("aria-label", dark ? "Switch to the light reading theme" : "Switch to the dark dashboard theme"); }
  }
  label();
  if (btn) btn.addEventListener("click", function () {
    var next = root.getAttribute("data-theme") === "dark" ? "light" : "dark";
    root.setAttribute("data-theme", next);
    try { localStorage.setItem("f3-theme", next); } catch (e) { /* storage may be blocked */ }
    label();
    window.dispatchEvent(new Event("f3theme"));
  });
})();
/* Definitions on touch and keyboard (the title attribute alone does not work on a phone). */
(function () {
  function close() { document.querySelectorAll(".defpop").forEach(function (x) { x.remove(); }); }
  document.querySelectorAll("abbr[title]").forEach(function (a) {
    a.tabIndex = 0;
    function toggle() { var open = a._pop && a._pop.isConnected; close(); if (open) return; var p = document.createElement("span"); p.className = "defpop"; p.setAttribute("role", "status"); p.textContent = a.getAttribute("title"); a.after(p); a._pop = p; }
    a.addEventListener("click", function (e) { e.stopPropagation(); toggle(); });
    a.addEventListener("keydown", function (e) { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); toggle(); } else if (e.key === "Escape") close(); });
  });
  document.addEventListener("click", function (e) { if (!e.target.closest("abbr")) close(); });
})();
