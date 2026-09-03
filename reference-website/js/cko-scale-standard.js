/**
 * Align scale pages to identity v10 + PADRAO cluster.
 * Does not authorize clinical promotion. CKO-POL-UT-001 remains PAUSED.
 */
(function () {
  "use strict";

  var SCALE_HINT =
    /escala|braden|aldrete|glasgow|morse|norton|waterlow|meows|pews|nips|flacc|wong|zarit|fugulin|apache|sofa|qsofa|news|moca|katz|barthel|berg|tinetti|ramsay|richmond|painad|cries|bishop|apgar|capurro|cam\b|asa\b|bps\b|gds\b|lachs|lawton|johns|jouvet|hamilton|humpty|hendrich|gosnell|elpo|four|downton|curb|cincinnati|cornell|nanda|prism|saps|pelod|silverman|tinetti|rancholosamigos|ofras|lanss|perroca|escalanumerica/i;

  function pageId() {
    var mount = document.querySelector("[data-cko-page]");
    if (mount) return mount.getAttribute("data-cko-page") || "";
    var path = (window.location.pathname || "").split("/").pop() || "";
    return path.replace(/\.html$/i, "");
  }

  function looksLikeScale() {
    var body = document.body;
    if (!body) return false;
    if (body.getAttribute("data-cko-template") === "scale") return true;
    if (body.classList.contains("cko-tpl-scale")) return true;
    if (document.querySelector("[data-cko-scale-items], .cko-scale-grid, .item-card")) return true;
    return SCALE_HINT.test(pageId()) || SCALE_HINT.test(document.title || "");
  }

  function applyTemplate() {
    var body = document.body;
    if (!body || !looksLikeScale()) return;
    body.setAttribute("data-cko-template", "scale");
    body.classList.add("cko-cart-page", "cko-tpl-scale");
    if (!body.getAttribute("data-cko-theme")) {
      body.setAttribute("data-cko-theme", "clinical");
    }
  }

  function bindPatient() {
    var btn = document.querySelector("[data-cko-scale-patient-toggle]");
    var body = document.querySelector(".cko-scale-patient__body");
    if (!btn || !body) return;
    btn.addEventListener("click", function () {
      var open = btn.getAttribute("aria-expanded") === "true";
      btn.setAttribute("aria-expanded", open ? "false" : "true");
      body.hidden = open;
    });
  }

  function boot() {
    applyTemplate();
    bindPatient();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }

  document.addEventListener("cko-shell:ready", applyTemplate);
  document.addEventListener("partials:ready", applyTemplate);
})();
