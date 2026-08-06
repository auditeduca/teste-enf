/**
 * CKO Content Engine — renders standardized modules A–F from JSON manifests.
 *
 * Mount:
 *   <div data-cko-content="trr" data-cko-modules="tools,faq,related,references,media"></div>
 *
 * Manifest: /data/content/<pageId>.json (schema: schemas/cko-content-page.schema.json)
 * Identity: /data/cko-content-identity.json
 */
(function () {
  "use strict";

  var IDENTITY_PATH = "/data/cko-content-identity.json";
  var CONTENT_DIR = "/data/content/";
  var identityCache = null;
  var manifestCache = {};

  function siteUrl(absPath) {
    if (window.CKOPageShell && typeof window.CKOPageShell.siteUrl === "function") {
      return window.CKOPageShell.siteUrl(absPath);
    }
    var path = String(absPath || "").replace(/^\//, "");
    try {
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

  function parseModules(el) {
    var raw = el.getAttribute("data-cko-modules") || "faq,related,references,media";
    return raw
      .split(",")
      .map(function (s) {
        return s.trim().toLowerCase();
      })
      .filter(Boolean);
  }

  function renderToc(manifest) {
    var toc = manifest.toc || [];
    if (!toc.length) return "";
    var html =
      '<section class="cko-mod cko-mod--toc" aria-labelledby="cko-mod-toc-title">' +
      '<h2 id="cko-mod-toc-title" class="cko-mod__title">Nesta página</h2>' +
      '<ol class="cko-side-toc">';
    toc.forEach(function (item) {
      html +=
        '<li><a href="#' +
        escapeHtml(item.id) +
        '">' +
        escapeHtml(item.label) +
        "</a></li>";
    });
    html += "</ol></section>";
    return html;
  }

  function renderTools(manifest) {
    var tools = manifest.tools || [];
    if (!tools.length) return "";
    var html =
      '<section class="cko-mod cko-mod--tools" aria-labelledby="cko-mod-tools-title">' +
      '<h2 id="cko-mod-tools-title" class="cko-mod__title">Ferramentas úteis</h2>' +
      '<p class="cko-mod__lead">Atalhos clínicos do mesmo ecossistema — use no fluxo de trabalho.</p>' +
      '<div class="cko-mod-tools">';
    tools.forEach(function (item) {
      html +=
        '<a class="cko-btn ' +
        (item.primary ? "cko-btn--primary" : "cko-btn--ghost") +
        '" href="' +
        escapeHtml(item.href) +
        '">' +
        escapeHtml(item.label) +
        "</a>";
    });
    html += "</div></section>";
    return html;
  }

  function renderFaq(manifest) {
    var faq = manifest.faq || [];
    if (!faq.length) return "";
    var html =
      '<section class="cko-mod cko-mod--faq" aria-labelledby="cko-mod-faq-title">' +
      '<h2 id="cko-mod-faq-title" class="cko-mod__title">Dúvidas frequentes</h2>' +
      '<div class="cko-faq">';
    faq.forEach(function (item, idx) {
      html +=
        "<details" +
        (idx === 0 ? " open" : "") +
        ">" +
        "<summary>" +
        escapeHtml(item.q) +
        "</summary>" +
        '<p class="cko-faq__a">' +
        escapeHtml(item.a) +
        "</p>" +
        "</details>";
    });
    html += "</div></section>";
    return html;
  }

  function renderRelated(manifest) {
    var related = manifest.related || [];
    if (!related.length) return "";
    var html =
      '<section class="cko-mod cko-mod--related" aria-labelledby="cko-mod-related-title">' +
      '<h2 id="cko-mod-related-title" class="cko-mod__title">Conteúdos relacionados</h2>' +
      '<ul class="cko-related">';
    related.forEach(function (item) {
      html +=
        '<li><a class="cko-related__item" href="' +
        escapeHtml(item.href) +
        '">' +
        '<span class="cko-related__kind">' +
        escapeHtml(item.kind || "guia") +
        "</span>" +
        '<span class="cko-related__title">' +
        escapeHtml(item.title) +
        "</span>" +
        (item.blurb
          ? '<span class="cko-related__blurb">' + escapeHtml(item.blurb) + "</span>"
          : "") +
        "</a></li>";
    });
    html += "</ul></section>";
    return html;
  }

  function renderReferences(manifest) {
    var refs = manifest.references || [];
    if (!refs.length) return "";
    var html =
      '<section class="cko-mod cko-mod--refs" aria-labelledby="cko-mod-refs-title">' +
      '<h2 id="cko-mod-refs-title" class="cko-mod__title">Referências</h2>' +
      '<ul class="cko-refs">';
    refs.forEach(function (item) {
      html += '<li class="cko-refs__item">';
      if (item.type) {
        html +=
          '<span class="cko-refs__type">' + escapeHtml(item.type) + "</span>";
      }
      if (item.href) {
        html +=
          '<a href="' +
          escapeHtml(item.href) +
          '" target="_blank" rel="noopener noreferrer">' +
          escapeHtml(item.label) +
          "</a>";
      } else {
        html += escapeHtml(item.label);
      }
      html += "</li>";
    });
    html += "</ul></section>";
    return html;
  }

  function renderMedia(manifest) {
    var media = manifest.media || [];
    if (!media.length) return "";
    var html =
      '<section class="cko-mod cko-mod--media" aria-labelledby="cko-mod-media-title">' +
      '<h2 id="cko-mod-media-title" class="cko-mod__title">Créditos de mídia</h2>' +
      '<ul class="cko-media-credits">';
    media.forEach(function (item) {
      html +=
        '<li class="cko-media-credits__item">' +
        '<span class="cko-media-credits__role">' +
        escapeHtml(item.role || "illustrative") +
        "</span> · " +
        escapeHtml(item.file || "") +
        (item.source ? " — " + escapeHtml(item.source) : "") +
        (item.license ? " (" + escapeHtml(item.license) + ")" : "") +
        (item.mobile ? " · mobile: " + escapeHtml(item.mobile) : "") +
        "</li>";
    });
    html += "</ul></section>";
    return html;
  }

  var RENDERERS = {
    toc: renderToc,
    tools: renderTools,
    faq: renderFaq,
    related: renderRelated,
    references: renderReferences,
    media: renderMedia
  };

  function renderManifest(manifest, modules) {
    var html = "";
    modules.forEach(function (name) {
      var fn = RENDERERS[name];
      if (fn) html += fn(manifest);
    });
    return html;
  }

  function validateManifest(manifest, identity) {
    var issues = [];
    if (!manifest || typeof manifest !== "object") {
      return [{ severity: "error", code: "manifest-missing", message: "Manifesto ausente" }];
    }
    if (!manifest.pageId) {
      issues.push({ severity: "error", code: "pageId", message: "pageId obrigatório" });
    }
    var req = (identity && identity.requiredModules) || ["faq", "related", "references"];
    req.forEach(function (mod) {
      var arr = manifest[mod];
      if (!Array.isArray(arr) || !arr.length) {
        issues.push({
          severity: "error",
          code: "module-" + mod,
          message: "Módulo " + mod + " vazio ou ausente"
        });
      }
    });
    if (Array.isArray(manifest.faq) && manifest.faq.length < 4) {
      issues.push({
        severity: "warn",
        code: "faq-min",
        message: "FAQ com menos de 4 itens (padrão ≥ 4)"
      });
    }
    if (Array.isArray(manifest.related) && manifest.related.length < 3) {
      issues.push({
        severity: "warn",
        code: "related-min",
        message: "Relacionados com menos de 3 itens (padrão ≥ 3)"
      });
    }
    (manifest.media || []).forEach(function (m, i) {
      if (m.role === "protocol-figure" && !m.mobile) {
        issues.push({
          severity: "warn",
          code: "media-mobile",
          message: "protocol-figure[" + i + "] sem variante mobile"
        });
      }
      if (!m.source) {
        issues.push({
          severity: "warn",
          code: "media-source",
          message: "mídia[" + i + "] sem source declarada"
        });
      }
    });
    return issues;
  }

  function validateDom(identity) {
    var issues = [];
    var body = document.body;
    var reqClass = (identity && identity.requiredBodyClass) || "cko-cart-page";
    if (!body || body.className.indexOf(reqClass) === -1) {
      issues.push({
        severity: "error",
        code: "body-class",
        message: "body sem classe " + reqClass
      });
    }
    var layout = document.querySelector(".cko-layout");
    if (!layout) {
      issues.push({ severity: "error", code: "layout", message: "cko-layout ausente" });
    } else {
      if (!layout.querySelector(".cko-layout__main")) {
        issues.push({ severity: "error", code: "layout-main", message: "cko-layout__main ausente" });
      }
      if (!layout.querySelector('.cko-layout__side, [data-cko-slot="sidebar"]')) {
        issues.push({ severity: "error", code: "layout-side", message: "sidebar ausente" });
      }
    }
    ["chrome", "hero", "sidebar"].forEach(function (slot) {
      if (!document.querySelector('[data-cko-slot="' + slot + '"]')) {
        issues.push({
          severity: "error",
          code: "slot-" + slot,
          message: "slot " + slot + " ausente"
        });
      }
    });
    if (!document.querySelector("[data-cko-content]")) {
      issues.push({
        severity: "warn",
        code: "content-mount",
        message: "mount data-cko-content ausente (módulos A–F)"
      });
    }
    var h1s = document.querySelectorAll("h1");
    var articleH1 = 0;
    Array.prototype.forEach.call(h1s, function (h) {
      if (!h.closest(".cko-cart-hero")) articleH1 += 1;
    });
    if (articleH1 > 0) {
      issues.push({
        severity: "warn",
        code: "duplicate-h1",
        message: "H1 fora do hero shell (deve haver só o H1 do hero)"
      });
    }
    return issues;
  }

  function fillMount(el, manifest, identity) {
    var modules = parseModules(el);
    var issues = validateManifest(manifest, identity);
    el.innerHTML = renderManifest(manifest, modules);
    el.setAttribute("data-cko-ready", "1");
    el.setAttribute("data-cko-page-id", manifest.pageId || "");
    if (issues.length) {
      el.setAttribute(
        "data-cko-issues",
        issues
          .map(function (i) {
            return i.code;
          })
          .join(",")
      );
    }
    return issues;
  }

  function loadJson(url) {
    return fetch(siteUrl(url), { credentials: "same-origin" }).then(function (r) {
      if (!r.ok) throw new Error("HTTP " + r.status + " " + url);
      return r.json();
    });
  }

  function boot() {
    var mounts = document.querySelectorAll("[data-cko-content]");
    if (!mounts.length) return;

    var identityPromise = identityCache
      ? Promise.resolve(identityCache)
      : loadJson(IDENTITY_PATH).then(function (id) {
          identityCache = id;
          return id;
        }).catch(function () {
          return null;
        });

    identityPromise.then(function (identity) {
      Array.prototype.forEach.call(mounts, function (el) {
        var pageId = el.getAttribute("data-cko-content");
        if (!pageId) {
          el.innerHTML = '<p class="cko-content-error">Content engine: data-cko-content vazio.</p>';
          return;
        }
        var cached = manifestCache[pageId];
        var p = cached
          ? Promise.resolve(cached)
          : loadJson(CONTENT_DIR + pageId + ".json").then(function (m) {
              manifestCache[pageId] = m;
              return m;
            });

        p.then(function (manifest) {
          fillMount(el, manifest, identity);
          try {
            document.dispatchEvent(
              new CustomEvent("cko-content:ready", {
                detail: { pageId: pageId, manifest: manifest }
              })
            );
          } catch (e) {}
        }).catch(function (err) {
          el.innerHTML =
            '<p class="cko-content-error">Falha ao carregar manifesto de conteúdo (' +
            escapeHtml(pageId) +
            ").</p>";
          console.error(err);
        });
      });
    });
  }

  window.CKOContentEngine = {
    boot: boot,
    siteUrl: siteUrl,
    validateManifest: validateManifest,
    validateDom: function () {
      return validateDom(identityCache);
    },
    getIdentity: function () {
      return identityCache;
    },
    getManifest: function (pageId) {
      return manifestCache[pageId] || null;
    }
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})();
