(function () {
  "use strict";

  // Scroll-reveal animations, skipped entirely for reduced-motion users
  var prefersReduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var els = document.querySelectorAll(".reveal, .reveal-stag");

  if (prefersReduced || !("IntersectionObserver" in window)) {
    els.forEach(function (el) { el.classList.add("in"); });
    return;
  }

  var io = new IntersectionObserver(
    function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add("in");
          io.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.12, rootMargin: "0px 0px -40px 0px" }
  );

  els.forEach(function (el) { io.observe(el); });
})();

// Chat widget: toggle open/close, auto-open once per browser session
(function () {
  "use strict";
  var launcher = document.getElementById("chatLauncher");
  var panel = document.getElementById("chatPanel");
  if (!launcher || !panel) return;

  function openPanel() {
    panel.classList.add("open");
    launcher.setAttribute("aria-expanded", "true");
  }
  function closePanel() {
    panel.classList.remove("open");
    launcher.setAttribute("aria-expanded", "false");
  }
  function togglePanel() {
    if (panel.classList.contains("open")) { closePanel(); } else { openPanel(); }
  }

  launcher.addEventListener("click", togglePanel);
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") closePanel();
  });
  document.addEventListener("click", function (e) {
    if (!panel.contains(e.target) && e.target !== launcher && !launcher.contains(e.target)) {
      closePanel();
    }
  });

  // Auto-open once per session, after a short delay, so it reads as a
  // greeting rather than an interruption. Silently skipped if storage
  // is unavailable (private browsing, etc).
  try {
    // Only on the home page: on ad landing pages it would cover the headline.
    if (location.pathname === "/" && !sessionStorage.getItem("cabonurse_chat_seen")) {
      setTimeout(function () {
        openPanel();
        sessionStorage.setItem("cabonurse_chat_seen", "1");
      }, 4000);
    }
  } catch (err) { /* storage unavailable — skip auto-open */ }
})();

// Light / dark theme toggle. The initial theme (saved choice, or system
// preference) is already applied by the inline script in <head> before
// paint; this just wires up the button to flip it and remember the choice.
(function () {
  "use strict";
  var toggle = document.getElementById("themeToggle");
  if (!toggle) return;
  var root = document.documentElement;

  function currentTheme() {
    return root.getAttribute("data-theme") === "dark" ? "dark" : "light";
  }
  function applyTheme(theme) {
    root.setAttribute("data-theme", theme);
    toggle.setAttribute("aria-pressed", theme === "dark" ? "true" : "false");
    try { localStorage.setItem("cabonurse_theme", theme); } catch (err) { /* storage unavailable */ }
  }

  toggle.setAttribute("aria-pressed", currentTheme() === "dark" ? "true" : "false");
  toggle.addEventListener("click", function () {
    applyTheme(currentTheme() === "dark" ? "light" : "dark");
  });
})();

// Conversion events for Google Ads / GA4: fires on any WhatsApp or phone link.
(function () {
  "use strict";
  document.addEventListener("click", function (e) {
    var a = e.target.closest && e.target.closest("a[href]");
    if (!a || typeof window.gtag !== "function") return;
    var href = a.getAttribute("href") || "";
    var name = href.indexOf("https://wa.me/") === 0 ? "whatsapp_click"
             : href.indexOf("tel:") === 0 ? "phone_click" : null;
    if (name) window.gtag("event", name, { link_url: href, page_path: location.pathname });
  });
})();
