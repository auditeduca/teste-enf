/* ======================================================================
   site-widgets.js — Módulo do rodapé: cookies (banner/modal/FAB) e
   botão voltar ao topo. Calculadoras de Enfermagem — Global Platform.
   ====================================================================== */
(function () {
  var STORAGE_KEY = "cookie-consent";

  function getConsent() {
    try {
      var raw = localStorage.getItem(STORAGE_KEY);
      return raw ? JSON.parse(raw) : null;
    } catch (e) {
      return null;
    }
  }

  function setConsent(prefs) {
    var payload = Object.assign({ essential: true, timestamp: Date.now() }, prefs);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(payload));
    return payload;
  }

  function initCookies() {
    var banner = document.getElementById("ck-banner");
    var overlay = document.getElementById("ck-modal-overlay");
    var fab = document.getElementById("ck-fab");
    if (!banner || !overlay || !fab) return;

    var chkPerformance = document.getElementById("ck-performance");
    var chkFunctionality = document.getElementById("ck-functionality");
    var chkAnalytics = document.getElementById("ck-analytics");

    function paintToggles(prefs) {
      if (chkPerformance) chkPerformance.checked = !!(prefs && prefs.performance);
      if (chkFunctionality) chkFunctionality.checked = !!(prefs && prefs.functionality);
      if (chkAnalytics) chkAnalytics.checked = !!(prefs && prefs.analytics);
    }

    function showBanner() { banner.classList.add("show"); }
    function hideBanner() { banner.classList.remove("show"); }
    function openModal() { overlay.classList.add("show"); document.body.style.overflow = "hidden"; }
    function closeModal() { overlay.classList.remove("show"); document.body.style.overflow = ""; }
    function showFab() { fab.classList.add("show"); }

    var existing = getConsent();
    if (existing) {
      paintToggles(existing);
      showFab();
    } else {
      setTimeout(showBanner, 600);
    }

    var accept = document.getElementById("ck-accept");
    var reject = document.getElementById("ck-reject");
    var customize = document.getElementById("ck-customize");
    var reject2 = document.getElementById("ck-reject-2");
    var save = document.getElementById("ck-save");
    var closeBtn = document.getElementById("ck-modal-close");

    if (accept) accept.addEventListener("click", function () {
      var prefs = setConsent({ performance: true, functionality: true, analytics: true });
      paintToggles(prefs);
      hideBanner();
      showFab();
    });

    if (reject) reject.addEventListener("click", function () {
      var prefs = setConsent({ performance: false, functionality: false, analytics: false });
      paintToggles(prefs);
      hideBanner();
      showFab();
    });

    if (customize) customize.addEventListener("click", function () {
      paintToggles(getConsent());
      openModal();
    });

    if (reject2) reject2.addEventListener("click", function () {
      var prefs = setConsent({ performance: false, functionality: false, analytics: false });
      paintToggles(prefs);
      closeModal();
      hideBanner();
      showFab();
    });

    if (save) save.addEventListener("click", function () {
      var prefs = setConsent({
        performance: !!(chkPerformance && chkPerformance.checked),
        functionality: !!(chkFunctionality && chkFunctionality.checked),
        analytics: !!(chkAnalytics && chkAnalytics.checked)
      });
      paintToggles(prefs);
      closeModal();
      hideBanner();
      showFab();
    });

    if (closeBtn) closeBtn.addEventListener("click", closeModal);
    overlay.addEventListener("click", function (e) { if (e.target === overlay) closeModal(); });
    document.addEventListener("keydown", function (e) { if (e.key === "Escape") closeModal(); });

    fab.addEventListener("click", function () {
      paintToggles(getConsent());
      openModal();
    });
  }

  function initBackToTop() {
    var btn = document.getElementById("bt-top");
    if (!btn) return;
    function toggle() {
      if (window.scrollY > 420) btn.classList.add("show");
      else btn.classList.remove("show");
    }
    window.addEventListener("scroll", toggle, { passive: true });
    toggle();
    btn.addEventListener("click", function () {
      window.scrollTo({ top: 0, behavior: "smooth" });
    });
  }

  /* ====================================================================
     TEMA (modo escuro) — switch dentro do modal de Preferências
     ==================================================================== */
  function initTheme() {
    var checkbox = document.getElementById("theme-toggle");
    if (!checkbox) return;

    function paint(isDark) {
      document.documentElement.classList.toggle("rd-dark", isDark);
      checkbox.checked = isDark;
    }

    var saved = localStorage.getItem("site-theme");
    paint(saved === "dark");

    checkbox.addEventListener("change", function () {
      paint(checkbox.checked);
      localStorage.setItem("site-theme", checkbox.checked ? "dark" : "light");
    });
  }

  /* ====================================================================
     TOASTER — window.showToast(message, type)
     ==================================================================== */
  var TOAST_ICONS = {
    success: "fa-solid fa-circle-check",
    error: "fa-solid fa-circle-exclamation",
    info: "fa-solid fa-circle-info"
  };
  window.showToast = function (message, type) {
    var container = document.getElementById("toast-container");
    if (!container) return;
    type = type && TOAST_ICONS[type] ? type : "info";
    var toast = document.createElement("div");
    toast.className = "toast toast-" + type;
    toast.setAttribute("role", "status");
    toast.innerHTML = '<i class="' + TOAST_ICONS[type] + '" aria-hidden="true"></i><span></span>';
    toast.querySelector("span").textContent = message;
    container.appendChild(toast);
    requestAnimationFrame(function () { toast.classList.add("show"); });
    setTimeout(function () {
      toast.classList.remove("show");
      setTimeout(function () { toast.remove(); }, 260);
    }, 3600);
  };

  /* ====================================================================
     SPINNER — estado de carregamento em botões
     ==================================================================== */
  function setButtonLoading(btn, isLoading) {
    if (!btn) return;
    var label = btn.querySelector(".btn-label") || btn;
    if (isLoading) {
      btn.dataset.originalHtml = label.innerHTML;
      label.innerHTML = '<span class="spinner"></span>';
      btn.disabled = true;
    } else {
      if (btn.dataset.originalHtml) label.innerHTML = btn.dataset.originalHtml;
      btn.disabled = false;
    }
  }

  /* ====================================================================
     NEWSLETTER — main + rodapé (consentimento + spinner + toaster)
     ==================================================================== */
  function initNewsletterForms() {
    ["rd-newsletter-form-main", "rd-newsletter-form-footer"].forEach(function (id) {
      var form = document.getElementById(id);
      if (!form) return;
      form.addEventListener("submit", function (e) {
        e.preventDefault();
        var checkbox = form.querySelector('input[type="checkbox"]');
        var email = form.querySelector('input[type="email"]');
        if (checkbox && !checkbox.checked) {
          window.showToast("Confirme o consentimento para receber comunicações.", "error");
          return;
        }
        if (email && !email.value) {
          window.showToast("Informe um e-mail válido.", "error");
          return;
        }
        var submitBtn = form.querySelector('button[type="submit"]');
        setButtonLoading(submitBtn, true);
        setTimeout(function () {
          setButtonLoading(submitBtn, false);
          window.showToast("Inscrição confirmada! Verifique seu e-mail.", "success");
          form.reset();
        }, 900);
      });
    });
  }

  /* ====================================================================
     FAIXA 3 — PREFERÊNCIAS (acessibilidade/utilitários, estilo Handtalk)
     Painel único com todos os recursos. A faixa some no topo da página
     e aparece após o início da rolagem (mesmo padrão do voltar ao topo).
     ==================================================================== */
  function initUtilityBarReveal() {
    var bar = document.getElementById("barraAcessibilidade");
    if (!bar) return;
    function toggle() {
      if (window.scrollY > 80) bar.classList.add("is-scrolled");
      else bar.classList.remove("is-scrolled");
    }
    window.addEventListener("scroll", toggle, { passive: true });
    toggle();
  }

  function initAccessibility() {
    var root = document.documentElement;
    var FONT_STEPS = [100, 110, 120, 130, 140];
    var fontIndex = 0;
    var fontLabel = document.getElementById("a11y-font-label");

    function bind(id, fn) {
      var el = document.getElementById(id);
      if (el) el.addEventListener("click", fn);
    }

    function applyFontScale() {
      root.style.fontSize = FONT_STEPS[fontIndex] + "%";
      localStorage.setItem("a11y-font-index", String(fontIndex));
      if (fontLabel) fontLabel.textContent = FONT_STEPS[fontIndex] + "%";
    }
    function incFont() { fontIndex = Math.min(fontIndex + 1, FONT_STEPS.length - 1); applyFontScale(); }
    function decFont() { fontIndex = Math.max(fontIndex - 1, 0); applyFontScale(); }

    function setPressed(id, pressed) {
      var el = document.getElementById(id);
      if (el) el.setAttribute("aria-pressed", String(pressed));
    }

    // Alto contraste e fonte para dislexia — agora são switches (checkbox)
    // dentro do modal de Preferências.
    var contrastSwitch = document.getElementById("a11y-contrast");
    var dyslexiaSwitch = document.getElementById("a11y-dyslexia");

    function applyContrast(on) {
      root.classList.toggle("contraste-alto", on);
      localStorage.setItem("a11y-contrast", on ? "1" : "0");
      if (contrastSwitch) contrastSwitch.checked = on;
    }
    function applyDyslexia(on) {
      root.classList.toggle("fonte-dislexia", on);
      localStorage.setItem("a11y-dyslexia", on ? "1" : "0");
      if (dyslexiaSwitch) dyslexiaSwitch.checked = on;
    }
    if (contrastSwitch) contrastSwitch.addEventListener("change", function () { applyContrast(contrastSwitch.checked); });
    if (dyslexiaSwitch) dyslexiaSwitch.addEventListener("change", function () { applyDyslexia(dyslexiaSwitch.checked); });

    // Ouvir esta página (Web Speech API) — ação visível inline na faixa 3
    function toggleRead() {
      if (!("speechSynthesis" in window)) {
        window.showToast("Leitura em voz alta não é suportada neste navegador.", "error");
        return;
      }
      if (window.speechSynthesis.speaking) {
        window.speechSynthesis.cancel();
        setPressed("a11y-read", false);
        return;
      }
      var main = document.getElementById("main-content");
      var text = main ? main.innerText : document.body.innerText;
      var utter = new SpeechSynthesisUtterance(text.slice(0, 6000));
      utter.lang = document.documentElement.lang || "pt-BR";
      utter.onend = function () { setPressed("a11y-read", false); };
      utter.onerror = function () { setPressed("a11y-read", false); };
      window.speechSynthesis.speak(utter);
      setPressed("a11y-read", true);
      window.showToast("Lendo o conteúdo da página...", "info");
    }

    // Compartilhar
    function share() {
      var url = window.location.href;
      var title = document.title;
      if (navigator.share) {
        navigator.share({ title: title, url: url }).catch(function () {});
      } else if (navigator.clipboard) {
        navigator.clipboard.writeText(url).then(function () {
          window.showToast("Link copiado para a área de transferência.", "success");
        }).catch(function () {
          window.showToast("Não foi possível copiar o link.", "error");
        });
      }
    }

    // Salvar página (lista local de favoritos)
    function toggleSave() {
      var key = "saved-pages";
      var url = window.location.href;
      var saved = [];
      try { saved = JSON.parse(localStorage.getItem(key) || "[]"); } catch (e) {}
      var idx = saved.indexOf(url);
      var isSaved;
      if (idx === -1) {
        saved.push(url);
        isSaved = true;
        window.showToast("Página salva nos seus favoritos.", "success");
      } else {
        saved.splice(idx, 1);
        isSaved = false;
        window.showToast("Página removida dos favoritos.", "info");
      }
      localStorage.setItem(key, JSON.stringify(saved));
      setPressed("a11y-save", isSaved);
    }

    function restoreSaved() {
      var key = "saved-pages";
      var saved = [];
      try { saved = JSON.parse(localStorage.getItem(key) || "[]"); } catch (e) {}
      setPressed("a11y-save", saved.indexOf(window.location.href) !== -1);
    }

    function printPage() { window.print(); }

    function resetAll() {
      fontIndex = 0;
      applyFontScale();
      applyContrast(false);
      applyDyslexia(false);
      window.showToast("Preferências redefinidas.", "info");
    }

    // Restaura preferências salvas
    var savedIndex = parseInt(localStorage.getItem("a11y-font-index"), 10);
    if (!isNaN(savedIndex) && FONT_STEPS[savedIndex] !== undefined) fontIndex = savedIndex;
    applyFontScale();
    applyContrast(localStorage.getItem("a11y-contrast") === "1");
    applyDyslexia(localStorage.getItem("a11y-dyslexia") === "1");
    restoreSaved();

    bind("a11y-font-inc", incFont);
    bind("a11y-font-dec", decFont);
    bind("a11y-read", toggleRead);
    bind("a11y-share", share);
    bind("a11y-save", toggleSave);
    bind("a11y-print", printPage);
    bind("a11y-reset", resetAll);

    // Modal de Preferências — abrir/fechar (mesmo padrão do modal de cookies)
    var trigger = document.getElementById("a11y-trigger");
    var modalOverlay = document.getElementById("a11y-modal-overlay");
    function openA11yModal() {
      if (!modalOverlay) return;
      modalOverlay.classList.add("show");
      document.body.style.overflow = "hidden";
      if (trigger) trigger.setAttribute("aria-expanded", "true");
    }
    function closeA11yModal() {
      if (!modalOverlay) return;
      modalOverlay.classList.remove("show");
      document.body.style.overflow = "";
      if (trigger) trigger.setAttribute("aria-expanded", "false");
    }
    if (trigger) trigger.addEventListener("click", openA11yModal);
    bind("a11y-modal-close", closeA11yModal);
    if (modalOverlay) modalOverlay.addEventListener("click", function (e) { if (e.target === modalOverlay) closeA11yModal(); });

    // Modal de atalhos de teclado (aberto a partir do modal de Preferências)
    var shortcutsModal = document.getElementById("keyboardShortcutsModal");
    function openShortcuts() { closeA11yModal(); if (shortcutsModal) shortcutsModal.classList.add("show"); }
    function closeShortcuts() { if (shortcutsModal) shortcutsModal.classList.remove("show"); }
    bind("a11y-shortcuts", openShortcuts);
    bind("a11y-shortcuts-close", closeShortcuts);
    if (shortcutsModal) shortcutsModal.addEventListener("click", function (e) { if (e.target === shortcutsModal) closeShortcuts(); });

    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape") { closeShortcuts(); closeA11yModal(); }
    });
  }

  /* ====================================================================
     AVALIAÇÃO (estrelas) — "Avalie este conteúdo", igual privacidade.html
     ==================================================================== */
  function initRating() {
    var wrap = document.getElementById("a11y-stars");
    if (!wrap) return;
    var buttons = Array.prototype.slice.call(wrap.querySelectorAll("button"));
    var key = "content-rating:" + window.location.pathname;

    function paint(value) {
      buttons.forEach(function (btn) {
        var star = parseInt(btn.getAttribute("data-star"), 10);
        btn.classList.toggle("on", star <= value);
      });
    }

    var saved = parseInt(localStorage.getItem(key), 10);
    if (!isNaN(saved) && saved > 0) {
      wrap.classList.add("rated");
      paint(saved);
    }

    buttons.forEach(function (btn) {
      btn.addEventListener("click", function () {
        var value = parseInt(btn.getAttribute("data-star"), 10);
        localStorage.setItem(key, String(value));
        wrap.classList.add("rated");
        paint(value);
        window.showToast("Obrigado pela sua avaliação!", "success");
      });
    });
  }

  function initDecorativeStarRatings() {
    document.querySelectorAll(".tool-rating .stars").forEach(function (el) {
      var label = el.getAttribute("aria-label") || "";
      var match = label.match(/([\d.]+)\s*de\s*5/i);
      if (!match) return;
      var rating = parseFloat(match[1]);
      if (isNaN(rating)) return;
      el.classList.add("decorative");
      var buttons = Array.prototype.slice.call(el.querySelectorAll("button"));
      buttons.forEach(function (btn, index) {
        var starValue = buttons.length - index;
        btn.classList.remove("on", "half");
        if (rating >= starValue) btn.classList.add("on");
        else if (rating >= starValue - 0.5) btn.classList.add("half");
      });
    });
  }

  var inited = false;
  function init() {
    if (inited) return;
    if (!document.getElementById("barraAcessibilidade") && !document.querySelector("#site-header .rd-header")) {
      return;
    }
    inited = true;
    initCookies();
    initBackToTop();
    initTheme();
    initAccessibility();
    initUtilityBarReveal();
    initNewsletterForms();
    initRating();
    initDecorativeStarRatings();
  }

  document.addEventListener("partials:ready", init);
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
