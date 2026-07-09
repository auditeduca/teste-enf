/* ======================================================================
   global-scripts.js — Scripts globais leves (DELIVERY)
   Fonte acessibilidade + utilitários compartilhados pelo cabeçalho.
   ====================================================================== */
(function () {
  "use strict";

  var savedFontSize = parseInt(localStorage.getItem("fontSize") || "1", 10);
  if (savedFontSize !== 1) {
    var fontSizes = ["1em", "1.15em", "1.3em", "1.5em", "2em"];
    var idx = Math.min(Math.max(savedFontSize, 1), fontSizes.length);
    document.documentElement.style.fontSize = fontSizes[idx - 1];
  }

  if (!window.handleSearch) {
    window.handleSearch = function (event) {
      event.preventDefault();
      var form = event.target;
      var input = form.querySelector('input[name="q"]');
      var query = (input && input.value || "").trim();
      if (!query) return false;
      window.location.href = "busca.html?q=" + encodeURIComponent(query);
      return false;
    };
  }
})();
