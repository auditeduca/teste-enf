/**
 * lang-selector.js
 * Injeta o seletor de idiomas na faixa 1 do header (#header-lang-slot),
 * com fallback para #language-selector-placeholder.
 */

(function () {
  "use strict";

  var mounted = false;

  function ensureHeaderToolsAssets() {
    if (!document.querySelector('link[href="/css/cko-header-tools.css"]')) {
      var link = document.createElement("link");
      link.rel = "stylesheet";
      link.href = "/css/cko-header-tools.css";
      document.head.appendChild(link);
    }
    if (!document.querySelector('script[src="/js/cko-global-search.js"]')) {
      var s = document.createElement("script");
      s.src = "/js/cko-global-search.js";
      s.defer = true;
      document.head.appendChild(s);
    }
  }

  function hideLegacyPlaceholder() {
    document.body.classList.add("cko-lang-in-header");
    var ph = document.getElementById("language-selector-placeholder");
    if (ph) {
      ph.innerHTML = "";
      ph.setAttribute("hidden", "");
      ph.style.display = "none";
      ph.style.minHeight = "0";
    }
  }

  function mountInto(container, inHeader) {
    if (!container || mounted) return;
    fetch("/_language_selector.html")
      .then(function (response) {
        if (!response.ok) throw new Error("Ficheiro _language_selector.html não encontrado");
        return response.text();
      })
      .then(function (data) {
        if (mounted) return;
        container.innerHTML = data;
        mounted = true;
        if (inHeader) hideLegacyPlaceholder();
        langSelectorInit();
        if (window.CKOGlobalSearch && typeof window.CKOGlobalSearch.init === "function") {
          window.CKOGlobalSearch.init();
        }
      })
      .catch(function (err) {
        console.error("Erro ao carregar seletor de idiomas:", err);
      });
  }

  function tryMount() {
    ensureHeaderToolsAssets();
    var headerSlot = document.getElementById("header-lang-slot");
    if (headerSlot) {
      mountInto(headerSlot, true);
      return true;
    }
    return false;
  }

  function boot() {
    ensureHeaderToolsAssets();
    if (tryMount()) return;

    var header = document.getElementById("global-header-container");
    if (header) {
      var obs = new MutationObserver(function () {
        if (tryMount()) obs.disconnect();
      });
      obs.observe(header, { childList: true, subtree: true });
      // Fallback após menu demorar
      setTimeout(function () {
        if (mounted) return;
        obs.disconnect();
        var legacy = document.getElementById("language-selector-placeholder");
        if (legacy) mountInto(legacy, false);
      }, 4000);
      return;
    }

    var legacy = document.getElementById("language-selector-placeholder");
    if (legacy) mountInto(legacy, false);
  }

  document.addEventListener("cko-header:ready", function () {
    tryMount();
  });

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})();

function langSelectorInit() {
  var button = document.getElementById("langButton");
  var menu = document.getElementById("langMenu");
  var langFlag = document.getElementById("langFlag");
  var langText = document.getElementById("langText");

  if (!button || !menu) return;

  var pathName = window.location.pathname;
  var fileNameMatch = pathName.match(/[^/]*\.html$/i);
  var currentFileName = fileNameMatch ? fileNameMatch[0] : "";

  button.addEventListener("click", function () {
    menu.classList.toggle("hidden");
    button.setAttribute("aria-expanded", menu.classList.contains("hidden") ? "false" : "true");
  });

  document.addEventListener("click", function (e) {
    if (!button.contains(e.target) && !menu.contains(e.target)) {
      menu.classList.add("hidden");
      button.setAttribute("aria-expanded", "false");
    }
  });

  document.querySelectorAll("#langMenu [data-value]").forEach(function (item) {
    item.addEventListener("click", function () {
      var value = item.dataset.value;
      var flag = item.dataset.flag;
      var text = item.textContent.trim();

      langFlag.src = flag;
      langText.textContent = text;
      menu.classList.add("hidden");
      button.setAttribute("aria-expanded", "false");

      var newPath = "/";
      var map = {
        en: "/en/",
        es: "/es/",
        de: "/de/",
        it: "/it/",
        fr: "/fr/",
        hi: "/hi/",
        zh: "/zh/",
        ar: "/ar/",
        ja: "/ja/",
        ru: "/ru/",
        ko: "/ko/",
        tr: "/tr/",
        nl: "/nl/",
        pl: "/pl/",
        sv: "/sv/",
        id: "/id/",
        vi: "/vi/",
        uk: "/uk/"
      };
      if (map[value]) newPath = map[value];

      if (currentFileName && currentFileName !== "index.html") {
        newPath += currentFileName;
      }
      window.location.href = newPath;
    });
  });

  var path = window.location.pathname;
  var current = document.querySelector('[data-value="pt"]');
  var langs = ["en", "es", "de", "it", "fr", "hi", "zh", "ar", "ja", "ru", "ko", "tr", "nl", "pl", "sv", "id", "vi", "uk"];
  for (var i = 0; i < langs.length; i++) {
    if (path.indexOf("/" + langs[i] + "/") === 0) {
      current = document.querySelector('[data-value="' + langs[i] + '"]');
      break;
    }
  }

  if (current) {
    langFlag.src = current.dataset.flag;
    langText.textContent = current.textContent.trim();
  }
}
