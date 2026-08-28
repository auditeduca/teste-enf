(function () {
  "use strict";

  var cfg = window.CATALOG_CONFIG;
  if (!cfg) return;

  var state = { category: "Todos", query: "", items: [], categories: [], selected: null };

  function esc(s) {
    var d = document.createElement("div");
    d.textContent = s == null ? "" : String(s);
    return d.innerHTML;
  }

  function catName(c) {
    return typeof c === "string" ? c : c.name || c.title || "Todos";
  }

  function itemCategory(item) {
    return item.category || item.domain || item.age || "";
  }

  function itemTitle(item) {
    return item.title || item.name || item.age || "Item";
  }

  function itemDesc(item) {
    return item.description || item.definition || item.fullDescription || "";
  }

  function flattenItems(data) {
    var raw = data[cfg.itemsKey] || [];
    if (cfg.itemsKey === "vaccineSchedule") {
      var flat = [];
      raw.forEach(function (row) {
        (row.vaccines || []).forEach(function (v) {
          flat.push({
            title: v.name,
            category: row.age,
            description: v.disease,
            dose: v.dose,
            ageGroup: row.age,
          });
        });
      });
      return flat;
    }
    return raw;
  }

  function renderFilters() {
    var el = document.getElementById("catalog-filters");
    if (!el) return;
    el.innerHTML = state.categories
      .map(function (c) {
        var n = catName(c);
        return (
          '<button type="button" data-cat="' +
          esc(n) +
          '" class="' +
          (state.category === n ? "active" : "") +
          '">' +
          esc(n) +
          "</button>"
        );
      })
      .join("");
    el.querySelectorAll("button").forEach(function (btn) {
      btn.addEventListener("click", function () {
        state.category = btn.getAttribute("data-cat");
        renderFilters();
        renderGrid();
      });
    });
  }

  function filtered() {
    var q = state.query.toLowerCase();
    return state.items.filter(function (item) {
      var cat = itemCategory(item);
      var matchCat = state.category === "Todos" || cat === state.category || item.ageGroup === state.category;
      if (!matchCat) return false;
      if (!q) return true;
      var blob = [itemTitle(item), itemDesc(item), item.code, item.dose].join(" ").toLowerCase();
      return blob.indexOf(q) !== -1;
    });
  }

  function renderDetail(item) {
    var panel = document.getElementById("catalog-detail");
    if (!panel) return;
    if (!item) {
      panel.hidden = true;
      return;
    }
    panel.hidden = false;
    var html = "<h2>" + esc(itemTitle(item)) + "</h2>";
    html += '<p class="meta">' + esc(itemCategory(item)) + (item.code ? " · Código " + esc(item.code) : "") + "</p>";
    html += "<p>" + esc(itemDesc(item) || item.fullDescription || "") + "</p>";
    if (item.relatedFactors && item.relatedFactors.length) {
      html += "<h3>Fatores relacionados</h3><ul>" + item.relatedFactors.map(function (x) { return "<li>" + esc(x) + "</li>"; }).join("") + "</ul>";
    }
    if (item.symptoms && item.symptoms.length) {
      html += "<h3>Sintomas</h3><ul>" + item.symptoms.map(function (x) { return "<li>" + esc(x) + "</li>"; }).join("") + "</ul>";
    }
    if (item.dose) html += "<p><strong>Dose:</strong> " + esc(item.dose) + "</p>";
    if (item.notifiable) html += "<p><strong>Notificação:</strong> " + esc(item.notifiable) + "</p>";
    if (item.tags) html += "<p>" + item.tags.map(function (t) { return '<span class="cat-badge">' + esc(t) + "</span> "; }).join("") + "</p>";
    panel.innerHTML = html;
    panel.scrollIntoView({ behavior: "smooth", block: "nearest" });
  }

  function renderGrid() {
    var grid = document.getElementById("catalog-grid");
    if (!grid) return;
    var list = filtered();
    if (!list.length) {
      grid.innerHTML = '<p class="catalog-empty">Nenhum resultado encontrado.</p>';
      return;
    }
    grid.innerHTML = list
      .map(function (item, idx) {
        return (
          '<button type="button" class="catalog-card" data-idx="' +
          idx +
          '"><span class="cat-badge">' +
          esc(itemCategory(item)) +
          "</span><h3>" +
          esc(itemTitle(item)) +
          "</h3><p>" +
          esc((itemDesc(item) || "").slice(0, 140)) +
          (itemDesc(item) && itemDesc(item).length > 140 ? "…" : "") +
          "</p></button>"
        );
      })
      .join("");
    grid.querySelectorAll(".catalog-card").forEach(function (card) {
      card.addEventListener("click", function () {
        var item = list[parseInt(card.getAttribute("data-idx"), 10)];
        grid.querySelectorAll(".catalog-card").forEach(function (c) { c.classList.remove("active"); });
        card.classList.add("active");
        renderDetail(item);
      });
    });
  }

  function init() {
    fetch(cfg.dataUrl)
      .then(function (r) { return r.json(); })
      .then(function (data) {
        var cats = data[cfg.categoriesKey] || [];
        state.categories = [{ name: "Todos" }].concat(cats);
        state.items = flattenItems(data);
        renderFilters();
        renderGrid();
      })
      .catch(function (err) {
        console.error("[catalog]", err);
        var grid = document.getElementById("catalog-grid");
        if (grid) grid.innerHTML = "<p>Erro ao carregar dados.</p>";
      });

    var search = document.getElementById("catalog-search");
    if (search) {
      search.addEventListener("input", function () {
        state.query = search.value.trim();
        renderGrid();
      });
    }
  }

  document.addEventListener("partials:ready", init);
  if (document.readyState !== "loading") init();
})();
