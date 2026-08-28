/* ======================================================================
   i18n-loader.js — Carregamento de dicionários via JSON (i18n/*.json)
   Calculadoras de Enfermagem — Global Platform

   Este arquivo é um carregador OPCIONAL, complementar ao lang-selector.js
   existente (que já contém TRANSLATIONS.en/.es embutidos no próprio JS).
   Ele não substitui nem altera lang-selector.js — serve para a próxima
   fase da migração, quando os dicionários passarem a viver em
   i18n/{lang}.json em vez de hardcoded no JS.

   Cadeia de fallback: idioma solicitado → en → pt (nativo, já no HTML,
   portanto nunca precisa de fetch: se nada for encontrado, o texto
   original do HTML permanece como está).
   ====================================================================== */
(function () {
  "use strict";

  var cache = {};

  function fetchDict(lang) {
    if (cache[lang]) return Promise.resolve(cache[lang]);
    if (lang === "pt") return Promise.resolve(null); // nativo, sem arquivo
    return fetch("i18n/" + lang + ".json")
      .then(function (res) {
        if (!res.ok) throw new Error("HTTP " + res.status);
        return res.json();
      })
      .then(function (json) {
        cache[lang] = json;
        return json;
      })
      .catch(function (err) {
        console.warn("[i18n-loader] Não foi possível carregar", lang, err);
        return null;
      });
  }

  /**
   * Carrega o dicionário do idioma pedido, com fallback para 'en' e
   * depois 'pt' (nulo = mantém o HTML nativo).
   * Retorna uma Promise<Object|null>.
   */
  function loadDictionaryWithFallback(lang) {
    return fetchDict(lang).then(function (dict) {
      if (dict) return dict;
      if (lang !== "en") {
        return fetchDict("en");
      }
      return null;
    });
  }

  window.I18N_LOADER = {
    loadDictionaryWithFallback: loadDictionaryWithFallback,
    fetchDict: fetchDict
  };
})();
