(function () {
  "use strict";

  var tools = [];
  var filter = "todos";
  var query = "";

  var input = document.getElementById("searchInput");
  var form = document.getElementById("searchForm");
  var results = document.getElementById("searchResults");
  var empty = document.getElementById("searchEmpty");
  var meta = document.getElementById("searchMeta");
  var filters = document.getElementById("searchFilters");

  var categoryLabels = {
    calculadora: "Calculadora",
    escala: "Escala",
    catalogo: "Catálogo",
    simulado: "Simulado",
    ferramenta: "Ferramenta"
  };

  function normalize(str) {
    return (str || "")
      .toLowerCase()
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "");
  }

  function getQueryFromUrl() {
    var params = new URLSearchParams(window.location.search);
    return (params.get("q") || "").trim();
  }

  function render() {
    var q = normalize(query);
    var list = tools.filter(function (tool) {
      if (filter !== "todos" && tool.category !== filter) return false;
      if (!q) return true;
      var hay = normalize(tool.title + " " + tool.description + " " + tool.slug);
      return hay.indexOf(q) !== -1;
    });

    results.innerHTML = list
      .map(function (tool) {
        var badge = categoryLabels[tool.category] || "Ferramenta";
        return (
          '<a class="search-card" href="' +
          tool.url +
          '"><span class="badge">' +
          badge +
          "</span><h2>" +
          tool.title +
          "</h2><p>" +
          (tool.description || "") +
          "</p></a>"
        );
      })
      .join("");

    empty.hidden = list.length > 0;
    results.hidden = list.length === 0;
    meta.hidden = false;
    meta.innerHTML =
      "<span><strong>" +
      list.length +
      "</strong> resultado(s)" +
      (query ? ' para "<strong>' + query.replace(/</g, "&lt;") + "</strong>\"" : "") +
      "</span>";
  }

  function setFilter(next) {
    filter = next;
    filters.querySelectorAll("button").forEach(function (btn) {
      btn.classList.toggle("active", btn.getAttribute("data-filter") === filter);
    });
    render();
  }

  function updateUrl() {
    var url = "busca.html";
    if (query) url += "?q=" + encodeURIComponent(query);
    history.replaceState(null, "", url);
  }

  fetch("js/tools-index.json")
    .then(function (res) {
      return res.json();
    })
    .then(function (data) {
      tools = data;
      query = getQueryFromUrl();
      if (input) input.value = query;
      render();
    })
    .catch(function () {
      results.innerHTML = '<p class="search-empty">Não foi possível carregar o índice de busca.</p>';
    });

  if (form) {
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      query = (input && input.value || "").trim();
      updateUrl();
      render();
    });
  }

  if (input) {
    input.addEventListener("input", function () {
      query = input.value.trim();
      updateUrl();
      render();
    });
  }

  if (filters) {
    filters.addEventListener("click", function (e) {
      var btn = e.target.closest("button[data-filter]");
      if (!btn) return;
      setFilter(btn.getAttribute("data-filter"));
    });
  }
})();
