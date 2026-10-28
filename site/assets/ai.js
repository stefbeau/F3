/* F3 AI Impact page: progressive enhancement only. The charts are inline SVG written by ai_body.py; this script adds the line draw-in, the fade-in of sections
   and the hover/focus tooltip on the publications chart. Without it (or with reduced motion) everything is visible and every value is in the data table. */
(function () {
  "use strict";
  var root = document.documentElement;
  var reduce = window.matchMedia && matchMedia("(prefers-reduced-motion: reduce)").matches;
  var fmt = function (n) { return Number(n).toLocaleString("en-US"); };

  function drawLines() {
    document.querySelectorAll('[data-animate="line"]').forEach(function (l) {
      requestAnimationFrame(function () { requestAnimationFrame(function () { l.classList.add("drawn"); }); });
    });
  }

  function reveal() {
    var secs = document.querySelectorAll(".ai-section");
    if (!("IntersectionObserver" in window)) { secs.forEach(function (s) { s.classList.add("visible"); }); return; }
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add("visible"); io.unobserve(e.target); } });
    }, { threshold: 0.1 });
    secs.forEach(function (s) { io.observe(s); });
  }

  function tooltip() {
    var wrap = document.querySelector('[data-chart="years"]'), tip = document.getElementById("ai_tip");
    if (!wrap || !tip) return;
    function show(c) {
      var box = wrap.getBoundingClientRect(), r = c.getBoundingClientRect();
      tip.textContent = c.dataset.year + ": " + fmt(c.dataset.count) + " publications";
      tip.hidden = false;
      var x = r.left - box.left + r.width / 2 - tip.offsetWidth / 2;
      tip.style.left = Math.max(0, Math.min(x, box.width - tip.offsetWidth)) + "px";
      tip.style.top = (r.top - box.top - tip.offsetHeight - 8) + "px";
    }
    function hide() { tip.hidden = true; }
    wrap.querySelectorAll("circle.ai-dot").forEach(function (c) {
      c.setAttribute("tabindex", "0");
      c.addEventListener("mouseover", function () { show(c); });
      c.addEventListener("focus", function () { show(c); });
      c.addEventListener("mouseout", hide);
      c.addEventListener("blur", hide);
    });
  }

  document.addEventListener("DOMContentLoaded", function () {
    tooltip();
    if (reduce) return;
    root.classList.add("ai-js");
    drawLines();
    reveal();
  });
})();
