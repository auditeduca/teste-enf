(function () {
  "use strict";
  var FONT_SIZES = ["1em", "1.15em", "1.3em", "1.5em", "2em"];
  var FONT_LABELS = ["Normal", "Médio", "Grande", "Extra Grande", "Máximo"];
  var LINE_VALUES = ["1.5", "1.8", "2.2"];
  var LINE_LABELS = ["Médio", "Grande", "Extra Grande"];
  var LETTER_VALUES = ["0em", ".05em", ".1em"];
  var LETTER_LABELS = ["Normal", "Médio", "Grande"];
  var SPEEDS = [
    { rate: 0.8, label: "Lenta" },
    { rate: 1, label: "Normal" },
    { rate: 1.5, label: "Rápida" }
  ];
  var KEYS = {
    font: "fontSize",
    line: "lineHeight",
    letter: "letterSpacing",
    speed: "readingSpeed",
    contrast: "highContrast",
    dark: "darkMode",
    dyslexia: "dyslexiaFont",
    focus: "focusColor"
  };

  var fontLevel = 1;
  var lineLevel = 1;
  var letterLevel = 1;
  var speedLevel = 1;
  var lastFocus = null;
  var speaking = false;
  var paused = false;
  var synth = window.speechSynthesis || null;

  function readInt(key, fallback) {
    try {
      var raw = parseInt(localStorage.getItem(key) || String(fallback), 10);
      return isNaN(raw) ? fallback : raw;
    } catch (ignore) {
      return fallback;
    }
  }

  function readFlag(key) {
    try {
      return localStorage.getItem(key) === "true";
    } catch (ignore) {
      return false;
    }
  }

  function write(key, value) {
    try {
      localStorage.setItem(key, String(value));
    } catch (ignore) {
      /* quota / private mode */
    }
  }

  function removeKey(key) {
    try {
      localStorage.removeItem(key);
    } catch (ignore) {}
  }

  function announce(message) {
    var status = document.getElementById("statusMessage");
    if (status) {
      status.textContent = message;
      window.setTimeout(function () {
        if (status.textContent === message) status.textContent = "";
      }, 3000);
    }
  }

  function setText(id, value) {
    var el = document.getElementById(id);
    if (el) el.textContent = value;
  }

  function clamp(level, max) {
    var n = parseInt(level, 10);
    if (isNaN(n) || n < 1) return 1;
    return n > max ? max : n;
  }

  function applyFont(level, speak) {
    fontLevel = clamp(level, FONT_SIZES.length);
    var idx = fontLevel - 1;
    document.documentElement.style.fontSize = FONT_SIZES[idx];
    setText("fontSizeText", FONT_LABELS[idx]);
    setText("fontSizeTextPWA", FONT_LABELS[idx]);
    write(KEYS.font, fontLevel);
    if (speak) announce("Tamanho da fonte: " + FONT_LABELS[idx]);
  }

  function applyLine(level, speak) {
    lineLevel = clamp(level, LINE_VALUES.length);
    var idx = lineLevel - 1;
    document.documentElement.style.setProperty("--espacamento-linha", LINE_VALUES[idx]);
    setText("lineHeightText", LINE_LABELS[idx]);
    setText("lineHeightTextPWA", LINE_LABELS[idx]);
    write(KEYS.line, lineLevel);
    if (speak) announce("Espaçamento de linha: " + LINE_LABELS[idx]);
  }

  function applyLetter(level, speak) {
    letterLevel = clamp(level, LETTER_VALUES.length);
    var idx = letterLevel - 1;
    document.documentElement.style.setProperty("--espacamento-letra", LETTER_VALUES[idx]);
    setText("letterSpacingText", LETTER_LABELS[idx]);
    setText("letterSpacingTextPWA", LETTER_LABELS[idx]);
    write(KEYS.letter, letterLevel);
    if (speak) announce("Espaçamento de letra: " + LETTER_LABELS[idx]);
  }

  function applySpeed(level, speak) {
    speedLevel = clamp(level, SPEEDS.length);
    var sp = SPEEDS[speedLevel - 1];
    setText("readingSpeedText", sp.label);
    write(KEYS.speed, speedLevel);
    if (speak) announce("Velocidade de leitura: " + sp.label);
  }

  function applyFocus(color, speak) {
    var value = color || "yellow";
    document.documentElement.style.setProperty("--cor-foco-acessibilidade", value);
    document.documentElement.style.setProperty("--a11y-focus", value);
    write(KEYS.focus, value);
    document.querySelectorAll(".color-option").forEach(function (btn) {
      var on = btn.getAttribute("data-color") === value;
      btn.classList.toggle("selected", on);
      btn.setAttribute("aria-checked", on ? "true" : "false");
    });
    if (speak) announce("Cor de foco alterada.");
  }

  function setBodyClass(name, on) {
    document.body.classList.toggle(name, !!on);
    document.documentElement.classList.toggle(name, !!on);
    if (name === "dark-mode") {
      document.documentElement.classList.toggle("rd-dark", !!on);
    }
  }

  function speakText(text) {
    if (!text || !synth) {
      announce("Leitura HOLD neste navegador.");
      return;
    }
    synth.cancel();
    var utter = new SpeechSynthesisUtterance(text);
    utter.lang = "pt-BR";
    utter.rate = (SPEEDS[speedLevel - 1] || SPEEDS[1]).rate;
    utter.onstart = function () {
      speaking = true;
      paused = false;
    };
    utter.onend = function () {
      speaking = false;
      paused = false;
    };
    utter.onerror = function () {
      speaking = false;
      paused = false;
    };
    synth.speak(utter);
  }

  function toggleReadMain() {
    if (!synth) {
      announce("Leitura HOLD neste navegador.");
      return;
    }
    if (speaking) {
      if (paused) {
        synth.resume();
        paused = false;
      } else {
        synth.pause();
        paused = true;
      }
      return;
    }
    var main = document.querySelector("main");
    speakText(main ? main.innerText : document.body.innerText);
  }

  function restartRead() {
    if (synth) synth.cancel();
    speaking = false;
    paused = false;
    window.setTimeout(function () {
      var main = document.querySelector("main");
      speakText(main ? main.innerText : document.body.innerText);
    }, 80);
  }

  function readFocused() {
    if (!lastFocus) return;
    var text = (lastFocus.textContent || lastFocus.getAttribute("aria-label") || lastFocus.alt || lastFocus.value || "").trim();
    speakText(text);
  }

  function restore() {
    applyFont(readInt(KEYS.font, 1), false);
    applyLine(readInt(KEYS.line, 1), false);
    applyLetter(readInt(KEYS.letter, 1), false);
    applySpeed(readInt(KEYS.speed, 1), false);
    setBodyClass("contraste-alto", readFlag(KEYS.contrast));
    setBodyClass("dark-mode", readFlag(KEYS.dark));
    setBodyClass("fonte-dislexia", readFlag(KEYS.dyslexia));
    var focus = "yellow";
    try {
      focus = localStorage.getItem(KEYS.focus) || "yellow";
    } catch (ignore) {}
    applyFocus(focus, false);
  }

  function resetAll() {
    if (synth) synth.cancel();
    speaking = false;
    paused = false;
    applyFont(1, false);
    applyLine(1, false);
    applyLetter(1, false);
    applySpeed(1, false);
    setBodyClass("contraste-alto", false);
    setBodyClass("dark-mode", false);
    setBodyClass("fonte-dislexia", false);
    applyFocus("yellow", false);
    Object.keys(KEYS).forEach(function (k) {
      removeKey(KEYS[k]);
    });
    try {
      localStorage.removeItem("cko-a11y");
    } catch (ignore) {}
    announce("Configurações redefinidas para o padrão");
  }

  function bindIds(ids, fn) {
    ids.forEach(function (id) {
      var el = document.getElementById(id);
      if (el) el.addEventListener("click", fn);
    });
  }

  function closePwa() {
    var bar = document.getElementById("pwaAcessibilidadeBar");
    var overlay = document.getElementById("menuOverlay");
    var toggle = document.getElementById("accessibilityToggleButton");
    if (bar) bar.classList.remove("is-open");
    if (overlay) overlay.classList.remove("is-open");
    if (toggle) toggle.setAttribute("aria-expanded", "false");
  }

  function openPwa() {
    var bar = document.getElementById("pwaAcessibilidadeBar");
    var overlay = document.getElementById("menuOverlay");
    var toggle = document.getElementById("accessibilityToggleButton");
    if (bar) bar.classList.add("is-open");
    if (overlay) overlay.classList.add("is-open");
    if (toggle) toggle.setAttribute("aria-expanded", "true");
  }

  function onReady() {
    restore();
    document.addEventListener("focusin", function (ev) {
      lastFocus = ev.target;
    });
    bindIds(["btnAlternarTamanhoFonte", "btnAlternarTamanhoFontePWA"], function () {
      applyFont(fontLevel % FONT_SIZES.length + 1, true);
    });
    bindIds(["btnAlternarEspacamentoLinha", "btnAlternarEspacamentoLinhaPWA"], function () {
      applyLine(lineLevel % LINE_VALUES.length + 1, true);
    });
    bindIds(["btnAlternarEspacamentoLetra", "btnAlternarEspacamentoLetraPWA"], function () {
      applyLetter(letterLevel % LETTER_VALUES.length + 1, true);
    });
    bindIds(["btnAlternarContraste", "btnAlternarContrastePWA"], function () {
      var on = !document.body.classList.contains("contraste-alto");
      setBodyClass("contraste-alto", on);
      write(KEYS.contrast, on);
      announce("Alto contraste " + (on ? "ativado" : "desativado"));
    });
    bindIds(["btnAlternarModoEscuro", "btnAlternarModoEscuroPWA"], function () {
      var on = !document.body.classList.contains("dark-mode");
      setBodyClass("dark-mode", on);
      write(KEYS.dark, on);
      announce("Modo escuro " + (on ? "ativado" : "desativado"));
    });
    bindIds(["btnAlternarFonteDislexia", "btnAlternarFonteDislexiaPWA"], function () {
      var on = !document.body.classList.contains("fonte-dislexia");
      setBodyClass("fonte-dislexia", on);
      write(KEYS.dyslexia, on);
      announce("Fonte para dislexia " + (on ? "ativada" : "desativada"));
    });
    bindIds(["btnResetarAcessibilidade", "btnResetarAcessibilidadePWA"], resetAll);
    bindIds(["btnToggleLeitura"], toggleReadMain);
    bindIds(["btnReiniciarLeitura"], restartRead);
    bindIds(["btnAlternarVelocidadeLeitura"], function () {
      applySpeed(speedLevel % SPEEDS.length + 1, true);
    });
    bindIds(["btnReadFocused"], readFocused);
    document.querySelectorAll(".color-option").forEach(function (btn) {
      btn.addEventListener("click", function () {
        applyFocus(btn.getAttribute("data-color") || "yellow", true);
      });
    });

    var modal = document.getElementById("keyboardShortcutsModal");
    function openModal() {
      if (modal) modal.classList.add("show");
    }
    function closeModal() {
      if (modal) modal.classList.remove("show");
    }
    bindIds(["btnKeyboardShortcuts", "btnKeyboardShortcutsPWA"], openModal);
    bindIds(["keyboardModalCloseButton"], closeModal);

    var toggle = document.getElementById("accessibilityToggleButton");
    var closeBtn = document.getElementById("pwaAcessibilidadeCloseBtn");
    var overlay = document.getElementById("menuOverlay");
    if (toggle) toggle.addEventListener("click", function () {
      var bar = document.getElementById("pwaAcessibilidadeBar");
      if (bar && bar.classList.contains("is-open")) closePwa();
      else openPwa();
    });
    if (closeBtn) closeBtn.addEventListener("click", closePwa);
    if (overlay) overlay.addEventListener("click", closePwa);

    window.addEventListener("keydown", function (ev) {
      if (ev.key !== "Escape") return;
      closeModal();
      closePwa();
    });

    var topBtn = document.getElementById("backToTopBtn");
    if (topBtn) {
      var ticking = false;
      var lastY = 0;
      window.addEventListener("scroll", function () {
        lastY = window.scrollY;
        if (ticking) return;
        ticking = true;
        window.requestAnimationFrame(function () {
          var mobile = window.innerWidth <= 768;
          var show = !mobile && lastY > 200;
          topBtn.style.display = show ? "block" : "none";
          ticking = false;
        });
      }, { passive: true });
      topBtn.addEventListener("click", function () {
        window.scrollTo({ top: 0, behavior: "smooth" });
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
          announce("Tradução HOLD. Runtime permanece pt-BR.");
        });
      });
    }
  }

  try {
    var prodFont = localStorage.getItem("fontSize");
    if (prodFont && prodFont !== "1") {
      var idx = Math.min(Math.max(parseInt(prodFont, 10), 1), FONT_SIZES.length);
      document.documentElement.style.fontSize = FONT_SIZES[idx - 1];
    }
    if (localStorage.getItem("darkMode") === "true") {
      document.documentElement.classList.add("rd-dark", "dark-mode");
    }
  } catch (ignore) {}

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", onReady);
  } else {
    onReady();
  }
})();
