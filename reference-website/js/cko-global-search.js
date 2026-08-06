/**
 * CKO Global Search — botão na faixa 1 do header + modal de busca.
 * Índice: links do menu-global + páginas do catálogo shell.
 */
(function () {
  "use strict";

  var index = [];
  var ready = false;

  function esc(s) {
    return String(s == null ? "" : s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function normalize(s) {
    return String(s || "")
      .toLowerCase()
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "");
  }

  function collectFromMenu() {
    var header = document.getElementById("global-header-container");
    if (!header) return [];
    var seen = {};
    var items = [];
    header.querySelectorAll('a[href]').forEach(function (a) {
      var href = a.getAttribute("href") || "";
      if (!href || href === "#" || href.indexOf("javascript:") === 0) return;
      if (href.charAt(0) !== "/" && href.indexOf("http") !== 0) {
        if (!/\.html/i.test(href)) return;
        href = "/" + href.replace(/^\.\//, "");
      }
      try {
        var u = new URL(href, window.location.origin);
        href = u.pathname;
      } catch (e) {
        return;
      }
      if (seen[href]) return;
      var label = (a.textContent || "").replace(/\s+/g, " ").trim();
      if (!label || label.length < 2) return;
      seen[href] = true;
      items.push({ title: label, href: href, source: "menu" });
    });
    return items;
  }

  function mergeShellCatalog(base, catalog) {
    var seen = {};
    base.forEach(function (i) {
      seen[i.href] = true;
    });
    var sets = (catalog && catalog.navSets) || {};
    Object.keys(sets).forEach(function (sk) {
      (sets[sk] || []).forEach(function (item) {
        if (!item || !item.href || seen[item.href]) return;
        seen[item.href] = true;
        base.push({
          title: item.label || item.id,
          href: item.href,
          source: "shell"
        });
      });
    });
    var pages = (catalog && catalog.pages) || {};
    Object.keys(pages).forEach(function (id) {
      var p = pages[id];
      var title =
        (p.hero && p.hero.title) ||
        (p.breadcrumb && p.breadcrumb.length && p.breadcrumb[p.breadcrumb.length - 1].label) ||
        id;
      var href = null;
      Object.keys(sets).forEach(function (sk) {
        (sets[sk] || []).forEach(function (item) {
          if (item.id === id && item.href) href = item.href;
        });
      });
      if (!href) return;
      if (seen[href]) {
        // enrich title if menu label was shorter
        base.forEach(function (i) {
          if (i.href === href && title && title.length > i.title.length) i.title = title;
        });
        return;
      }
      seen[href] = true;
      base.push({ title: title, href: href, source: "shell" });
    });
    return base;
  }

  function buildIndex(cb) {
    var items = collectFromMenu();
    fetch("/data/cko-shell-pages.json", { credentials: "same-origin" })
      .then(function (r) {
        return r.ok ? r.json() : null;
      })
      .then(function (catalog) {
        if (catalog) items = mergeShellCatalog(items, catalog);
        // Extras frequentes
        [
          { title: "Mapa do site", href: "/mapa-do-site.html" },
          { title: "Time de Resposta Rápida (TRR)", href: "/time-de-resposta-rapida.html" },
          { title: "Escala NEWS", href: "/news.html" },
          { title: "Carrinho de Emergência", href: "/biblioteca-carinho-de-emergencia.html" }
        ].forEach(function (x) {
          if (!items.some(function (i) {
            return i.href === x.href;
          })) {
            items.push(x);
          }
        });
        items.sort(function (a, b) {
          return a.title.localeCompare(b.title, "pt");
        });
        index = items;
        ready = true;
        if (cb) cb();
      })
      .catch(function () {
        index = items;
        ready = true;
        if (cb) cb();
      });
  }

  function ensureModal() {
    var el = document.getElementById("cko-global-search");
    if (el) return el;
    el = document.createElement("div");
    el.id = "cko-global-search";
    el.className = "cko-gsearch";
    el.setAttribute("hidden", "");
    el.innerHTML =
      '<div class="cko-gsearch__backdrop" data-cko-gsearch-close></div>' +
      '<div class="cko-gsearch__panel" role="dialog" aria-modal="true" aria-label="Pesquisa global">' +
      '<div class="cko-gsearch__bar">' +
      '<svg class="cko-gsearch__icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" aria-hidden="true"><circle cx="11" cy="11" r="7" stroke-width="2"/><path d="M20 20l-3.5-3.5" stroke-width="2" stroke-linecap="round"/></svg>' +
      '<input id="ckoGlobalSearchInput" type="search" class="cko-gsearch__input" placeholder="Buscar calculadoras, escalas, protocolos…" autocomplete="off" />' +
      '<button type="button" class="cko-gsearch__close" data-cko-gsearch-close aria-label="Fechar">✕</button>' +
      "</div>" +
      '<p class="cko-gsearch__hint">Digite para filtrar o site. Enter abre o primeiro resultado.</p>' +
      '<ul id="ckoGlobalSearchResults" class="cko-gsearch__results" role="listbox"></ul>' +
      "</div>";
    document.body.appendChild(el);

    el.addEventListener("click", function (e) {
      if (e.target.closest("[data-cko-gsearch-close]")) close();
    });
    var input = el.querySelector("#ckoGlobalSearchInput");
    input.addEventListener("input", function () {
      renderResults(input.value);
    });
    input.addEventListener("keydown", function (e) {
      if (e.key === "Escape") {
        e.preventDefault();
        close();
      }
      if (e.key === "Enter") {
        var first = el.querySelector(".cko-gsearch__item");
        if (first) {
          e.preventDefault();
          window.location.href = first.getAttribute("href");
        }
      }
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && !el.hasAttribute("hidden")) close();
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "k") {
        e.preventDefault();
        open();
      }
    });
    return el;
  }

  function renderResults(q) {
    var list = document.getElementById("ckoGlobalSearchResults");
    if (!list) return;
    var nq = normalize(q).trim();
    var hits = !nq
      ? index.slice(0, 12)
      : index
          .filter(function (item) {
            return normalize(item.title).indexOf(nq) !== -1 || normalize(item.href).indexOf(nq) !== -1;
          })
          .slice(0, 40);
    if (!hits.length) {
      list.innerHTML = '<li class="cko-gsearch__empty">Nenhum resultado para “' + esc(q) + '”.</li>';
      return;
    }
    list.innerHTML = hits
      .map(function (item) {
        return (
          '<li><a class="cko-gsearch__item" href="' +
          esc(item.href) +
          '" role="option">' +
          '<span class="cko-gsearch__title">' +
          esc(item.title) +
          "</span>" +
          '<span class="cko-gsearch__href">' +
          esc(item.href) +
          "</span></a></li>"
        );
      })
      .join("");
  }

  function open() {
    var modal = ensureModal();
    if (!ready) {
      buildIndex(function () {
        renderResults("");
      });
    } else {
      renderResults("");
    }
    modal.removeAttribute("hidden");
    document.body.classList.add("cko-gsearch-open");
    var input = document.getElementById("ckoGlobalSearchInput");
    if (input) {
      input.value = "";
      setTimeout(function () {
        input.focus();
      }, 10);
    }
  }

  function close() {
    var modal = document.getElementById("cko-global-search");
    if (modal) modal.setAttribute("hidden", "");
    document.body.classList.remove("cko-gsearch-open");
  }

  function bindButton() {
    var btn = document.getElementById("ckoGlobalSearchBtn");
    if (!btn || btn.getAttribute("data-cko-bound") === "1") return;
    btn.setAttribute("data-cko-bound", "1");
    btn.addEventListener("click", function (e) {
      e.preventDefault();
      open();
    });
  }

  function init() {
    bindButton();
    ensureModal();
    buildIndex();
  }

  window.CKOGlobalSearch = { init: init, open: open, close: close };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", function () {
      document.addEventListener("cko-header:ready", init);
      // retry if header already there
      if (document.getElementById("ckoGlobalSearchBtn")) init();
    });
  } else {
    document.addEventListener("cko-header:ready", init);
    if (document.getElementById("ckoGlobalSearchBtn")) init();
  }
})();
