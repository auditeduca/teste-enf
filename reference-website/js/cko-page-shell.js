/**
 * CKO page shell — modular breadcrumb, nav, hero, actions, aside.
 * Pages declare mounts only; content comes from /data/cko-shell-pages.json.
 *
 * <div data-cko-page="cirurgica" data-cko-slot="chrome"></div>
 * <div data-cko-page="cirurgica" data-cko-slot="hero"></div>
 * ... page body ...
 * <div data-cko-page="cirurgica" data-cko-slot="aside"></div>
 */
(function () {
  "use strict";

  var CATALOG_PATH = "/data/cko-shell-pages.json";
  var catalogCache = null;

  function siteUrl(absPath) {
    var path = String(absPath || "").replace(/^\//, "");
    try {
      var base = document.querySelector("base");
      if (base && base.href) return new URL(path, base.href).href;
      var parts = window.location.pathname.replace(/\\/g, "/").split("/").filter(Boolean);
      if (parts.length && /\.[a-z0-9]+$/i.test(parts[parts.length - 1])) parts.pop();
      var prefix = parts.map(function () { return ".."; }).join("/");
      return (prefix ? prefix + "/" : "") + path;
    } catch (e) {
      return "/" + path;
    }
  }

  function escapeHtml(str) {
    return String(str == null ? "" : str)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#39;");
  }

  function renderBreadcrumb(items) {
    if (!items || !items.length) return "";
    var html = '<nav class="cko-breadcrumb no-print" aria-label="Breadcrumb"><ol class="cko-breadcrumb__list">';
    items.forEach(function (item, idx) {
      var last = idx === items.length - 1;
      if (idx > 0) html += '<li class="cko-breadcrumb__sep" aria-hidden="true">›</li>';
      if (last || !item.href) {
        html +=
          '<li class="cko-breadcrumb__item' +
          (last ? " is-current" : "") +
          '"' +
          (last ? ' aria-current="page"' : "") +
          ">" +
          escapeHtml(item.label) +
          "</li>";
      } else {
        html +=
          '<li class="cko-breadcrumb__item"><a class="cko-breadcrumb__link" href="' +
          escapeHtml(item.href) +
          '">' +
          escapeHtml(item.label) +
          "</a></li>";
      }
    });
    html += "</ol></nav>";
    return html;
  }

  function renderNavSet(catalog, page) {
    // Off: page.navSet false/null, navSetEnabled false, or defaults.hideNavSet
    if (page.navSet === false || page.navSet === null) return "";
    if (page.navSetEnabled === false) return "";
    if (catalog.defaults && catalog.defaults.hideNavSet && page.navSetEnabled !== true) {
      return "";
    }
    var setId = page.navSet;
    if (!setId || !catalog.navSets || !catalog.navSets[setId]) return "";
    var active = page.activeNav || "";
    var items = catalog.navSets[setId];
    var label =
      page.navLabel ||
      (setId === "protocolos" ? "Protocolos relacionados" : "Bibliotecas de materiais");
    var html =
      '<div class="ce-actionbar cko-shell-nav no-print" role="group" aria-label="' +
      escapeHtml(label) +
      '">';
    items.forEach(function (item) {
      var primary = item.id === active;
      html +=
        '<a class="cko-btn ' +
        (primary ? "cko-btn--primary" : "cko-btn--ghost") +
        '" href="' +
        escapeHtml(item.href) +
        '"' +
        (primary ? ' aria-current="page"' : "") +
        ">" +
        escapeHtml(item.label) +
        "</a>";
    });
    html += "</div>";
    return html;
  }

  function renderActions(actions) {
    if (!actions || !actions.length) return "";
    var html =
      '<div class="ce-actionbar cko-shell-actions no-print" role="group" aria-label="Ações da página">';
    actions.forEach(function (item) {
      var primary = !!item.primary;
      html +=
        '<a class="cko-btn ' +
        (primary ? "cko-btn--primary" : "cko-btn--ghost") +
        '" href="' +
        escapeHtml(item.href) +
        '">' +
        escapeHtml(item.label) +
        "</a>";
    });
    html += "</div>";
    return html;
  }

  function renderHero(hero) {
    if (!hero) return "";
    var chips = "";
    (hero.chips || []).forEach(function (c) {
      chips += '<span class="cko-cart-chip">' + escapeHtml(c) + "</span>";
    });
    return (
      '<section class="cko-cart-hero no-print" aria-label="Introdução">' +
      (hero.eyebrow
        ? '<p class="cko-cart-hero__eyebrow">' + escapeHtml(hero.eyebrow) + "</p>"
        : "") +
      '<h1 class="cko-cart-hero__title">' +
      escapeHtml(hero.title || "") +
      "</h1>" +
      (hero.lead
        ? '<p class="cko-cart-hero__lead">' + escapeHtml(hero.lead) + "</p>"
        : "") +
      (chips ? '<div class="cko-cart-chips">' + chips + "</div>" : "") +
      "</section>"
    );
  }

  function renderAside(catalog, page) {
    // Off: page.aside false/null, aside.enabled false, or defaults.hideAside (unless enabled:true)
    if (page.aside === false || page.aside === null) return "";
    var aside = page.aside && typeof page.aside === "object" ? page.aside : {};
    if (aside.enabled === false) return "";
    if (catalog.defaults && catalog.defaults.hideAside && aside.enabled !== true) return "";
    var notice = aside.notice || (catalog.defaults && catalog.defaults.notice) || "";
    var copyright =
      aside.copyright || (catalog.defaults && catalog.defaults.copyright) || "";
    if (!notice && !copyright) return "";
    return (
      '<aside class="cko-cart-section cko-shell-aside no-print">' +
      (notice
        ? '<p class="cko-shell-aside__notice"><strong>Aviso:</strong> ' +
          escapeHtml(notice) +
          "</p>"
        : "") +
      (copyright
        ? '<p class="cko-copyright cko-shell-aside__copy">' +
          escapeHtml(copyright) +
          "</p>"
        : "") +
      "</aside>"
    );
  }

  function renderSidebar(catalog, page) {
    var side = page.sidebar || {};
    var tools = side.tools || page.actions || [];
    var toc = side.toc || [];
    var showFeedback = side.feedback !== false;
    var html = "";

    html += '<div class="cko-side-card no-print" data-cko-side-toc>';
    html += '<h2 class="cko-side-card__title">Nesta página</h2>';
    if (toc.length) {
      html += '<ol class="cko-side-toc">';
      toc.forEach(function (item) {
        html +=
          '<li><a href="#' +
          escapeHtml(item.id) +
          '">' +
          escapeHtml(item.label) +
          "</a></li>";
      });
      html += "</ol>";
    } else {
      html +=
        '<p class="cko-shell-aside__notice" style="margin:0">Índice gerado automaticamente das seções.</p>';
      html += '<ol class="cko-side-toc" data-cko-toc-auto></ol>';
    }
    html += "</div>";

    if (tools.length) {
      html += '<div class="cko-side-card no-print">';
      html += '<h2 class="cko-side-card__title">Recursos úteis</h2>';
      html += '<div class="cko-side-tools">';
      tools.forEach(function (item) {
        var primary = !!item.primary;
        html +=
          '<a class="cko-btn ' +
          (primary ? "cko-btn--primary" : "cko-btn--ghost") +
          '" href="' +
          escapeHtml(item.href) +
          '">' +
          escapeHtml(item.label) +
          "</a>";
      });
      html +=
        '<button type="button" class="cko-btn cko-btn--ghost" data-cko-print>Imprimir / PDF do navegador</button>';
      html += "</div></div>";
    }

    if (showFeedback) {
      html +=
        '<div class="cko-side-card no-print cko-feedback" data-cko-feedback>' +
        '<h2 class="cko-side-card__title">Feedback</h2>' +
        '<p class="cko-shell-aside__notice" style="margin:0 0 .5rem">Esta página foi útil para sua prática?</p>' +
        '<form data-cko-feedback-form>' +
        '<label for="cko-fb-rating">Avaliação</label>' +
        '<select id="cko-fb-rating" name="rating" required>' +
        '<option value="">Selecione</option>' +
        '<option value="5">Muito útil</option>' +
        '<option value="4">Útil</option>' +
        '<option value="3">Razoável</option>' +
        '<option value="2">Pouco útil</option>' +
        '<option value="1">Não ajudou</option>' +
        "</select>" +
        '<label for="cko-fb-note">Comentário (opcional)</label>' +
        '<textarea id="cko-fb-note" name="note" maxlength="500" placeholder="O que melhorar neste conteúdo?"></textarea>' +
        '<div class="cko-feedback__actions">' +
        '<button type="submit" class="cko-btn cko-btn--primary">Enviar feedback</button>' +
        "</div>" +
        '<p class="cko-feedback__msg" data-cko-feedback-msg role="status">Obrigado — feedback registrado neste dispositivo.</p>' +
        "</form></div>";
    }

    return html;
  }

  function bindSidebar(root) {
    var scope = root || document;
    var printBtn = scope.querySelector("[data-cko-print]");
    if (printBtn) {
      printBtn.addEventListener("click", function () {
        window.print();
      });
    }
    var form = scope.querySelector("[data-cko-feedback-form]");
    if (form) {
      form.addEventListener("submit", function (e) {
        e.preventDefault();
        var rating = form.querySelector('[name="rating"]');
        var note = form.querySelector('[name="note"]');
        var payload = {
          page: window.location.pathname,
          rating: rating ? rating.value : "",
          note: note ? note.value : "",
          at: new Date().toISOString()
        };
        try {
          var key = "cko-feedback:" + window.location.pathname;
          var prev = JSON.parse(localStorage.getItem(key) || "[]");
          if (!Array.isArray(prev)) prev = [];
          prev.push(payload);
          localStorage.setItem(key, JSON.stringify(prev.slice(-20)));
        } catch (err) {}
        var msg = scope.querySelector("[data-cko-feedback-msg]");
        if (msg) msg.classList.add("is-visible");
        form.reset();
      });
    }
  }

  function fillAutoToc() {
    var lists = document.querySelectorAll("[data-cko-toc-auto]");
    Array.prototype.forEach.call(lists, function (ol) {
      var main =
        document.querySelector(".cko-layout__main") ||
        document.getElementById("main-content");
      if (!main) return;
      var heads = main.querySelectorAll("h2[id], section.cko-ds-section > h2, .cko-ds-section h2");
      if (!heads.length) {
        ol.innerHTML =
          '<li><span class="cko-shell-aside__notice">Sem seções com id ainda.</span></li>';
        return;
      }
      var html = "";
      var seen = {};
      Array.prototype.forEach.call(heads, function (h) {
        if (!h.id) {
          var slug = (h.textContent || "")
            .toLowerCase()
            .replace(/[^a-z0-9]+/g, "-")
            .replace(/^-|-$/g, "")
            .slice(0, 40);
          if (slug) h.id = slug;
        }
        if (!h.id || seen[h.id]) return;
        seen[h.id] = true;
        html +=
          '<li><a href="#' +
          escapeHtml(h.id) +
          '">' +
          escapeHtml(h.textContent.replace(/^\d+\.\s*/, "").trim()) +
          "</a></li>";
      });
      ol.innerHTML = html;
    });
  }

  function renderSlot(catalog, page, slot) {
    if (slot === "breadcrumb") return renderBreadcrumb(page.breadcrumb);
    if (slot === "nav") return renderNavSet(catalog, page);
    if (slot === "actions") return renderActions(page.actions);
    if (slot === "hero") return renderHero(page.hero);
    if (slot === "aside") return renderAside(catalog, page);
    if (slot === "sidebar") return renderSidebar(catalog, page);
    if (slot === "chrome") {
      return (
        renderBreadcrumb(page.breadcrumb) +
        renderNavSet(catalog, page) +
        renderActions(page.actions)
      );
    }
    if (slot === "full") {
      return (
        renderBreadcrumb(page.breadcrumb) +
        renderNavSet(catalog, page) +
        renderActions(page.actions) +
        renderHero(page.hero)
      );
    }
    return "";
  }

  function isInsideSlot(el, mount) {
    if (!el) return false;
    if (mount && (el === mount || mount.contains(el))) return true;
    return Boolean(el.closest("[data-cko-slot]"));
  }

  function hasStaticBreadcrumb(mount) {
    var nodes = document.querySelectorAll(
      '[data-cko-static="breadcrumb"], nav.tpl-breadcrumb, nav.crumbs, nav[aria-label="Breadcrumb"]'
    );
    for (var i = 0; i < nodes.length; i += 1) {
      if (!isInsideSlot(nodes[i], mount)) return true;
    }
    return false;
  }

  function hasStaticHero(mount) {
    // Only intentional static chrome wins. Local navy cards and loose H1s
    // are forbidden by PADRAO_PAGINAS / identity v10 — they must not suppress the shell.
    var marked = document.querySelectorAll(
      '[data-cko-static="hero"], .tool-header, section.hero, .cko-home-hero'
    );
    for (var i = 0; i < marked.length; i += 1) {
      if (!isInsideSlot(marked[i], mount)) return true;
    }
    return false;
  }

  function hideLegacyLocalHeroes() {
    var slots = document.querySelectorAll('[data-cko-slot="hero"]');
    var hasShellHero = false;
    Array.prototype.forEach.call(slots, function (slot) {
      if (slot.querySelector(".cko-cart-hero") && slot.getAttribute("data-cko-deduped") !== "hero") {
        hasShellHero = true;
      }
    });
    if (!hasShellHero) return;
    document.querySelectorAll('[class*="-card-navy"]').forEach(function (el) {
      if (isInsideSlot(el)) return;
      if (el.closest("#resultado-section, [data-cko-scale-score], .print-area")) return;
      if (!el.querySelector("h1")) return;
      el.setAttribute("data-cko-legacy-hero", "1");
      el.hidden = true;
    });
    var main = document.getElementById("main-content") || document.querySelector("main");
    if (!main) return;
    var titles = main.querySelectorAll("h1");
    for (var i = 0; i < titles.length; i += 1) {
      var h1 = titles[i];
      if (isInsideSlot(h1)) continue;
      if (h1.closest("[data-cko-static='hero'], .tool-header, section.hero, .cko-home-hero")) continue;
      if (h1.closest(".cko-calc-workspace, [data-cko-scale-items], #resultado-section, .print-area")) continue;
      var wrap = h1.closest("section") || h1.parentElement;
      if (!wrap || isInsideSlot(wrap)) continue;
      wrap.setAttribute("data-cko-legacy-hero", "1");
      wrap.hidden = true;
      break;
    }
  }

  function fillMounts(catalog) {
    var mounts = document.querySelectorAll("[data-cko-page]");
    Array.prototype.forEach.call(mounts, function (el) {
      var id = el.getAttribute("data-cko-page");
      var slot = el.getAttribute("data-cko-slot") || "full";
      var page = catalog.pages && catalog.pages[id];
      if (!page) {
        el.innerHTML =
          '<p class="cko-shell-error">Shell: página desconhecida (' +
          escapeHtml(id) +
          ").</p>";
        return;
      }
      var skipBreadcrumb = slot === "chrome" || slot === "breadcrumb" || slot === "full" ? hasStaticBreadcrumb(el) : false;
      var skipHero = slot === "hero" || slot === "full" ? hasStaticHero(el) : false;
      if ((slot === "hero" && skipHero) || (slot === "breadcrumb" && skipBreadcrumb)) {
        el.innerHTML = "";
        el.setAttribute("data-cko-deduped", slot);
        el.setAttribute("data-cko-ready", "1");
        return;
      }
      if (slot === "chrome" && skipBreadcrumb) {
        var rest = renderNavSet(catalog, page) + renderActions(page.actions);
        el.innerHTML = rest;
        if (!rest) el.setAttribute("data-cko-deduped", "breadcrumb");
        el.setAttribute("data-cko-ready", "1");
        return;
      }
      if (slot === "full" && (skipBreadcrumb || skipHero)) {
        el.innerHTML =
          (skipBreadcrumb ? "" : renderBreadcrumb(page.breadcrumb)) +
          renderNavSet(catalog, page) +
          renderActions(page.actions) +
          (skipHero ? "" : renderHero(page.hero));
        el.setAttribute("data-cko-deduped", [skipBreadcrumb ? "breadcrumb" : "", skipHero ? "hero" : ""].filter(Boolean).join(","));
        el.setAttribute("data-cko-ready", "1");
        return;
      }
      el.innerHTML = renderSlot(catalog, page, slot);
      el.setAttribute("data-cko-ready", "1");
      if (slot === "sidebar") bindSidebar(el);
    });
    hideLegacyLocalHeroes();
    fillAutoToc();
  }

  function boot() {
    var mounts = document.querySelectorAll("[data-cko-page]");
    if (!mounts.length) return;

    var run = function (catalog) {
      catalogCache = catalog;
      fillMounts(catalog);
      try {
        document.dispatchEvent(
          new CustomEvent("cko-shell:ready", { detail: { catalog: catalog } })
        );
      } catch (e) {}
    };

    if (catalogCache) {
      run(catalogCache);
      return;
    }

    fetch(siteUrl(CATALOG_PATH), { credentials: "same-origin" })
      .then(function (r) {
        if (!r.ok) throw new Error("Shell catalog HTTP " + r.status);
        return r.json();
      })
      .then(run)
      .catch(function (err) {
        Array.prototype.forEach.call(mounts, function (el) {
          el.innerHTML =
            '<p class="cko-shell-error">Falha ao carregar shell modular.</p>';
        });
        console.error(err);
      });
  }

  window.CKOPageShell = {
    boot: boot,
    siteUrl: siteUrl,
    refreshToc: fillAutoToc,
    getCatalog: function () {
      return catalogCache;
    }
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})();
