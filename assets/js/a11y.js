(function () {
  "use strict";
  try {
    var prodFont = localStorage.getItem("fontSize");
    if (prodFont && prodFont !== "1") {
      var sizes = ["1em", "1.15em", "1.3em", "1.5em", "2em"];
      var idx = Math.min(Math.max(parseInt(prodFont, 10), 1), sizes.length);
      document.documentElement.style.fontSize = sizes[idx - 1];
    }
    if (localStorage.getItem("darkMode") === "true") {
      document.documentElement.classList.add("rd-dark");
    }
  } catch (ignore) {}
  var KEY = "cko-a11y";
  var FONT = ["Fonte", "Grande", "Maior"];
  var LINE = ["Linha", "Ampla"];
  var LETTER = ["Letra", "Ampla"];
  var defaults = {
    font: 0,
    line: 0,
    letter: 0,
    contrast: false,
    dark: false,
    dyslexia: false,
    focus: "yellow"
  };

  function load() {
    try {
      return Object.assign({}, defaults, JSON.parse(localStorage.getItem(KEY) || "{}"));
    } catch (err) {
      return Object.assign({}, defaults);
    }
  }

  function save(state) {
    try {
      localStorage.setItem(KEY, JSON.stringify(state));
    } catch (err) {
      /* ignore quota / private mode */
    }
  }

  function apply(state) {
    var html = document.documentElement;
    html.classList.toggle("a11y-font-lg", state.font === 1);
    html.classList.toggle("a11y-font-xl", state.font === 2);
    html.classList.toggle("a11y-line-lg", state.line === 1);
    html.classList.toggle("a11y-letter-lg", state.letter === 1);
    html.classList.toggle("contraste-alto", !!state.contrast);
    html.classList.toggle("rd-dark", !!state.dark);
    html.classList.toggle("fonte-dislexia", !!state.dyslexia);
    html.style.setProperty("--a11y-focus", state.focus || "yellow");
    var font = document.getElementById("fontSizeText");
    var line = document.getElementById("lineHeightText");
    var letter = document.getElementById("letterSpacingText");
    if (font) font.textContent = FONT[state.font] || FONT[0];
    if (line) line.textContent = LINE[state.line] || LINE[0];
    if (letter) letter.textContent = LETTER[state.letter] || LETTER[0];
    document.querySelectorAll(".color-option").forEach(function (btn) {
      btn.setAttribute("aria-checked", btn.getAttribute("data-color") === state.focus ? "true" : "false");
    });
  }

  function onReady() {
    var state = load();
    apply(state);
    function bind(id, fn) {
      var el = document.getElementById(id);
      if (el) el.addEventListener("click", fn);
    }
    bind("btnAlternarTamanhoFonte", function () {
      state.font = (state.font + 1) % 3;
      save(state);
      apply(state);
    });
    bind("btnAlternarEspacamentoLinha", function () {
      state.line = state.line ? 0 : 1;
      save(state);
      apply(state);
    });
    bind("btnAlternarEspacamentoLetra", function () {
      state.letter = state.letter ? 0 : 1;
      save(state);
      apply(state);
    });
    bind("btnAlternarContraste", function () {
      state.contrast = !state.contrast;
      save(state);
      apply(state);
    });
    bind("btnAlternarModoEscuro", function () {
      state.dark = !state.dark;
      save(state);
      apply(state);
    });
    bind("btnAlternarFonteDislexia", function () {
      state.dyslexia = !state.dyslexia;
      save(state);
      apply(state);
    });
    bind("btnResetAcessibilidade", function () {
      state = Object.assign({}, defaults);
      save(state);
      apply(state);
    });
    document.querySelectorAll(".color-option").forEach(function (btn) {
      btn.addEventListener("click", function () {
        state.focus = btn.getAttribute("data-color") || "yellow";
        save(state);
        apply(state);
      });
    });
    var toggle = document.getElementById("accessibilityToggleButton");
    var bar = document.getElementById("barraAcessibilidade");
    if (toggle && bar) {
      toggle.addEventListener("click", function () {
        var open = bar.classList.toggle("is-open");
        toggle.setAttribute("aria-expanded", open ? "true" : "false");
      });
    }
    var hamburger = document.getElementById("hamburgerButton");
    var nav = document.getElementById("primary-nav");
    if (hamburger && nav) {
      hamburger.addEventListener("click", function () {
        var open = nav.classList.toggle("is-open");
        hamburger.setAttribute("aria-expanded", open ? "true" : "false");
      });
    }
    var langButton = document.getElementById("langButton");
    var langMenu = document.getElementById("langMenu");
    var langText = document.getElementById("langText");
    var status = document.getElementById("statusMessage");
    if (langButton && langMenu) {
      langButton.addEventListener("click", function (ev) {
        ev.stopPropagation();
        var hidden = langMenu.classList.toggle("hidden");
        langButton.setAttribute("aria-expanded", hidden ? "false" : "true");
      });
      document.addEventListener("click", function (ev) {
        if (!langButton.contains(ev.target) && !langMenu.contains(ev.target)) {
          langMenu.classList.add("hidden");
          langButton.setAttribute("aria-expanded", "false");
        }
      });
      langMenu.querySelectorAll(".lang-option").forEach(function (item) {
        item.addEventListener("click", function () {
          if (langText) langText.textContent = item.querySelector("span") ? item.querySelector("span").textContent : item.textContent;
          langMenu.classList.add("hidden");
          langButton.setAttribute("aria-expanded", "false");
          if (status) status.textContent = "Tradução HOLD. Runtime permanece pt-BR.";
        });
      });
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", onReady);
  } else {
    onReady();
  }
})();
