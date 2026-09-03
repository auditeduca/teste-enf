/**
 * HOLD-HUMAN-COPY-RATINGS — gate star/rating copy at runtime.
 * Does not authorize ratings. Does not close the human hold.
 */
(function () {
  if (document.documentElement.getAttribute("data-cko-ratings") === "authorized") {
    return;
  }
  function holdBox() {
    var p = document.createElement("p");
    p.className = "cko-ratings-hold";
    p.setAttribute("data-cko-hold", "HOLD-HUMAN-COPY-RATINGS");
    p.textContent = "Avaliações e estrelas em HOLD — texto não autorizado.";
    return p;
  }
  function gate() {
    document.querySelectorAll(".tool-rating, .stars").forEach(function (el) {
      if (el.getAttribute("data-cko-ratings-hold-done") === "1") return;
      var box = el.classList.contains("tool-rating") ? el : el.closest(".tool-rating") || el;
      if (box.getAttribute("data-cko-ratings-hold-done") === "1") return;
      box.setAttribute("data-cko-ratings-hold-done", "1");
      box.replaceWith(holdBox());
    });
  }
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", gate);
  } else {
    gate();
  }
  document.addEventListener("partials:ready", gate);
  if (typeof MutationObserver === "function") {
    new MutationObserver(gate).observe(document.documentElement, { childList: true, subtree: true });
  }
})();
