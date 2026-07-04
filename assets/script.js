/**
 * MentorPro — tab routing + accessibility helpers.
 *
 * URLs are shaped like real paths (no hash) via History API:
 *   /                    → first tab (mặc định)
 *   /thong-tin-mentor    → Tab 1
 *   /cau-chuyen-thanh-cong → Tab 2
 *   /lo-trinh-tai-mentorpro → Tab 3
 *   /lien-he             → Tab 4
 *
 * GitHub Pages doesn't do server-side routing, so `docs/404.html` catches
 * unknown paths and redirects them to `/?p=<slug>`. On boot the script
 * reads that ?p= param, restores the pretty URL via replaceState, then
 * activates the matching tab. See build.py::write_404().
 */

(function () {
  "use strict";

  var buttons = Array.prototype.slice.call(document.querySelectorAll(".tab-btn"));
  var panels  = Array.prototype.slice.call(document.querySelectorAll(".tab-panel"));

  // First tab is the "root" — routes to `/` (no path segment).
  var rootSlug = panels.length ? panels[0].id : "";
  var validSlugs = panels.map(function (p) { return p.id; });

  function slugToPath(slug) {
    return (!slug || slug === rootSlug) ? "/" : "/" + slug;
  }

  function pathToSlug() {
    var seg = window.location.pathname.replace(/^\//, "").replace(/\/$/, "");
    // Ignore paths with more than one segment — those aren't tab routes.
    if (seg && seg.indexOf("/") === -1 && validSlugs.indexOf(seg) !== -1) return seg;
    return rootSlug;
  }

  function activate(slug, opts) {
    opts = opts || {};
    var pushURL = opts.pushURL !== false;

    var targetPanel = panels.filter(function (p) { return p.id === slug; })[0];
    if (!targetPanel) return;
    var targetButton = buttons.filter(function (b) { return b.dataset.target === slug; })[0];

    buttons.forEach(function (b) {
      var isActive = b === targetButton;
      b.classList.toggle("is-active", isActive);
      b.setAttribute("aria-selected", isActive ? "true" : "false");
    });
    panels.forEach(function (p) {
      var isActive = p === targetPanel;
      p.classList.toggle("is-active", isActive);
      p.setAttribute("aria-hidden", isActive ? "false" : "true");
    });

    if (pushURL) {
      var newPath = slugToPath(slug);
      if (window.location.pathname !== newPath) {
        history.pushState({ slug: slug }, "", newPath + window.location.search + window.location.hash);
      }
    }
  }

  // Handle 404 redirect handoff: ?p=<slug> means we arrived via GH Pages'
  // 404.html fallback. Restore the pretty URL then continue routing.
  var params = new URLSearchParams(window.location.search);
  var redirected = params.get("p");
  if (redirected !== null) {
    var restored = "/" + redirected.replace(/^\/+/, "").replace(/\/+$/, "");
    params.delete("p");
    var qs = params.toString();
    history.replaceState({ slug: redirected }, "", restored + (qs ? "?" + qs : "") + window.location.hash);
  }

  buttons.forEach(function (btn) {
    btn.addEventListener("click", function () { activate(btn.dataset.target); });
    btn.addEventListener("keydown", function (event) {
      var idx = buttons.indexOf(btn);
      var next = null;
      if (event.key === "ArrowRight") next = buttons[(idx + 1) % buttons.length];
      if (event.key === "ArrowLeft")  next = buttons[(idx - 1 + buttons.length) % buttons.length];
      if (event.key === "Home")       next = buttons[0];
      if (event.key === "End")        next = buttons[buttons.length - 1];
      if (next) {
        event.preventDefault();
        next.focus();
        activate(next.dataset.target);
      }
    });
  });

  // Intercept regular in-page links to tab paths (`href="/lien-he"`) so they
  // switch tab without a full page reload.
  document.addEventListener("click", function (event) {
    var link = event.target.closest && event.target.closest("a[href]");
    if (!link) return;
    var href = link.getAttribute("href");
    if (!href || href.charAt(0) !== "/") return;              // only in-site paths
    if (link.target === "_blank" || event.metaKey || event.ctrlKey || event.shiftKey) return;
    var seg = href.slice(1).split(/[?#]/)[0].replace(/\/$/, "");
    if (validSlugs.indexOf(seg) !== -1) {
      event.preventDefault();
      activate(seg);
    } else if (seg === "") {
      event.preventDefault();
      activate(rootSlug);
    }
  });

  window.addEventListener("popstate", function () { activate(pathToSlug(), { pushURL: false }); });

  // Initial routing based on current pathname.
  activate(pathToSlug(), { pushURL: false });

  var yearEl = document.getElementById("year");
  if (yearEl) yearEl.textContent = String(new Date().getFullYear());
})();
