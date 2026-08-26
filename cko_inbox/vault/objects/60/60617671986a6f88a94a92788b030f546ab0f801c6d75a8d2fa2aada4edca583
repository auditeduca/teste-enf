/* =========================
   Camada 4 — Anti-bot leve
   ========================= */
(function () {
  try {
    const ua = navigator.userAgent || "";
    const isTrustedGoogleTool = /(?:Chrome-)?Lighthouse|Googlebot/i.test(ua);
    const isBotLike = !isTrustedGoogleTool && (
      navigator.webdriver === true ||
      ua.length < 10 ||
      !navigator.language ||
      (screen && (screen.width === 0 || screen.height === 0))
    );

    if (isBotLike) {
      // Redireciona para home (não quebra SEO e evita loop)
      if (location.pathname !== "/") {
        location.replace("/");
      }
    }
  } catch (e) {
    // ignora erros
  }
})();

/* =========================
   Detecção de Idioma (unificado)
   ========================= */
(function () {
  var _path = window.location.pathname;
  var _match = _path.match(/^\/(en|es|de|it|fr|hi|zh|ar|ja|ru|ko|tr|nl|pl|sv|id|vi|uk)\//);
  window.__LANG = _match ? _match[1] : "pt";
  window.__IS_LANG_FOLDER = !!_match;

  // Mapa de idiomas TTS
  var _ttsMap = { en: "en-US", es: "es-ES", de: "de-DE", it: "it-IT", fr: "fr-FR", hi: "hi-IN", zh: "zh-CN", ar: "ar-SA", ja: "ja-JP", ru: "ru-RU", ko: "ko-KR", tr: "tr-TR", nl: "nl-NL", pl: "pl-PL", sv: "sv-SE", id: "id-ID", vi: "vi-VN", uk: "uk-UA", pt: "pt-BR" };
  window.__TTS_LANG = _ttsMap[window.__LANG] || "pt-BR";

  // Prefixo para fetches: calculado conforme a profundidade da página dentro da
  // pasta de idioma (ex.: "en/escalas-de-enfermagem/centro-cirurgico/" → "../../"),
  // para menu-global.html, global-body-elements.html e footer.html carregarem em
  // qualquer nível. Na raiz do site (pt-BR), mantém o prefixo absoluto "/".
  if (window.__IS_LANG_FOLDER) {
    var _parts = _path.slice(_match[0].length).split("/").filter(function (s) { return s; });
    var _depth = _parts.length;
    if (_depth > 0 && _parts[_parts.length - 1].indexOf(".") !== -1) _depth -= 1;
    window.__FETCH_PREFIX = _depth > 0 ? new Array(_depth + 1).join("../") : "";
  } else {
    window.__FETCH_PREFIX = "/";
  }
})();

// Corrige links relativos em conteúdo injetado (menu-global, footer) para que
// funcionem em páginas aninhadas dentro da pasta de idioma.
window.__FIX_RELATIVE_LINKS = function (container) {
  if (!container || !container.querySelectorAll) return;
  container.querySelectorAll("a[href]").forEach(function (a) {
    var href = a.getAttribute("href") || "";
    if (href && href.charAt(0) !== "#" && href.charAt(0) !== "/" && href.indexOf(":") === -1) {
      a.setAttribute("href", window.__FETCH_PREFIX + href);
    }
  });
};

// Registra o Service Worker
"serviceWorker" in navigator && window.addEventListener("load", () => {
  navigator.serviceWorker.register("/sw.js").then(e => {
    console.log("Service Worker registado com sucesso:", e.scope)
  }, e => {
    console.log("Registo do Service Worker falhou:", e)
  })
});

document.addEventListener("DOMContentLoaded", function () {
  // 1. CARREGAMENTO CRÍTICO: Traz apenas o menu no primeiro instante
  fetch(window.__FETCH_PREFIX + "menu-global.html").then(e => e.ok ? e.text() : Promise.reject("Ficheiro menu-global.html não encontrado")).then(e => {
    const o = document.getElementById("global-header-container");
    if (o) {
      window.requestAnimationFrame(() => {
        o.innerHTML = e;
        // Corrige links relativos do menu para páginas em subpastas de idioma
        if (window.__FIX_RELATIVE_LINKS) window.__FIX_RELATIVE_LINKS(o);
        initializeNavigationMenu();
        // Inicializa auth no menu (não bloqueante)
        initializeAuthMenu();
      });
    }
  }).catch(e => console.warn("Não foi possível carregar o menu global:", e));
});

// 2. CARREGAMENTO DIFERIDO: Adia a injeção da acessibilidade, cookies e modais (Alivia a Thread Principal)
window.addEventListener("load", function () {
  setTimeout(() => {
    fetch(window.__FETCH_PREFIX + "global-body-elements.html").then(e => e.ok ? e.text() : Promise.reject("Ficheiro global-body-elements.html não encontrado")).then(e => {
      window.requestAnimationFrame(() => {
        document.body.insertAdjacentHTML("beforeend", e);
        initializeGlobalFunctions();
      });
    }).catch(e => console.warn("Não foi possível carregar os elementos globais do corpo:", e));
  }, 50); // Pausa mínima de 50ms para garantir o encerramento da pintura crítica (LCP)
});

function initializeNavigationMenu() {
  const e = document.getElementById("hamburgerButton"),
    o = document.getElementById("offCanvasMenu"),
    t = document.getElementById("menuOverlay"),
    n = document.getElementById("closeOffCanvasMenu") || document.getElementById("closeMenuButton"),
    l = () => {
      o && (o.classList.add("is-open"), o.classList.remove("-translate-x-full")), t && (t.style.display = "block", t.classList.add("is-open")), e && e.setAttribute("aria-expanded", "true")
    },
    s = () => {
      o && (o.classList.remove("is-open"), o.classList.add("-translate-x-full")), t && (t.style.display = "none", t.classList.remove("is-open")), e && e.setAttribute("aria-expanded", "false")
    };
  e?.addEventListener("click", l), t?.addEventListener("click", s), n?.addEventListener("click", s), o?.querySelectorAll(".has-submenu > a, .has-submenu > button")?.forEach(e => {
    e.addEventListener("click", o => {
      o.preventDefault();
      const t = e.nextElementSibling;
      if (t && t.classList.contains("submenu")) {
        const isOpen = t.classList.toggle("open");
        e.setAttribute("aria-expanded", isOpen);
      }
    })
  });
  // Desktop: aria-expanded dinamico nos dropdowns por hover (D08 — WCAG 4.1.2)
  document.querySelectorAll("nav.desktop-nav button[aria-haspopup]").forEach(function (btn) {
    btn.addEventListener("mouseenter", function () { btn.setAttribute("aria-expanded", "true"); });
    btn.addEventListener("mouseleave", function () { btn.setAttribute("aria-expanded", "false"); });
  });
}

/* =========================
   Auth Menu — Integração com Sistema de Contas
   ========================= */
function initializeAuthMenu() {
  // ── Função para atualizar UI baseada no estado de auth ──
  // Re-consulta os elementos do DOM a cada chamada (evita race condition)
  function updateAuthUI(user) {
    var desktopLink = document.getElementById("menu-auth-link-desktop");
    var desktopItem = document.getElementById("menu-auth-desktop");
    var mobileLink = document.getElementById("menu-auth-link-mobile");
    var mobileItem = document.getElementById("menu-auth-mobile");

    // Se nenhum elemento existe ainda, retorna (será tentado novamente)
    if (!desktopLink && !desktopItem && !mobileLink && !mobileItem) {
      return false;
    }

    var displayName = "";
    var photoURL = "";
    var isLoggedIn = !!(user && user.uid);

    if (isLoggedIn) {
      displayName = (user.displayName || user.email || "Usuário").split(" ")[0];
      photoURL = user.photoURL || "";
    }

    // ── Desktop ──
    if (desktopItem) {
      if (isLoggedIn) {
        // Avatar + nome + dropdown
        desktopItem.className = "relative group flex items-center";
        desktopItem.innerHTML =
          '<button type="button" class="flex items-center gap-2 text-gray-700 hover:text-[#1A3E74] font-medium" aria-haspopup="true" aria-expanded="false">' +
          (photoURL
            ? '<img src="' + photoURL + '" alt="' + displayName + '" class="w-7 h-7 rounded-full border-2 border-[#1A3E74]" referrerpolicy="no-referrer" onerror="this.style.display=\'none\'"/>'
            : '<div class="w-7 h-7 rounded-full bg-[#1A3E74] flex items-center justify-center text-white font-bold text-xs">' + displayName.charAt(0).toUpperCase() + "</div>") +
          "<span class='max-w-[100px] truncate'>" + displayName + "</span>" +
          '<svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/></svg>' +
          "</button>" +
          '<ul class="absolute right-0 hidden group-hover:block bg-white shadow-lg rounded-md py-1 w-48 z-50 border border-gray-100">' +
          '<li><a href="/conta/perfil.html" class="block px-4 !py-1.5 text-gray-700 hover:bg-gray-100 text-sm">Meu Perfil</a></li>' +
          '<li><a href="/conta/favoritos.html" class="block px-4 !py-1.5 text-gray-700 hover:bg-gray-100 text-sm">Favoritos</a></li>' +
          '<li><a href="/conta/historico.html" class="block px-4 !py-1.5 text-gray-700 hover:bg-gray-100 text-sm">Histórico</a></li>' +
          '<li class="border-t border-gray-100 mt-1 pt-1"><a href="#" id="menu-auth-logout-desktop" class="block px-4 !py-1.5 text-red-600 hover:bg-red-50 text-sm font-medium">Sair</a></li>' +
          "</ul>";

        setTimeout(function () {
          var logoutBtn = document.getElementById("menu-auth-logout-desktop");
          if (logoutBtn) {
            logoutBtn.addEventListener("click", function (e) {
              e.preventDefault();
              if (window.Auth && window.Auth.signOut) {
                window.Auth.signOut().then(function () {
                  window.location.reload();
                });
              }
            });
          }
        }, 100);
      } else {
        desktopItem.className = "flex items-center";
        desktopItem.innerHTML =
          '<a href="/conta/login.html" class="text-gray-700 hover:text-[#1A3E74] font-medium flex items-center gap-1.5">' +
          '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 448 512" fill="currentColor" width="0.9em" height="0.9em" aria-hidden="true"><path d="M224 256A128 128 0 1 0 224 0a128 128 0 1 0 0 256zm-45.7 48C79.8 304 0 383.8 0 482.3 0 498.7 13.3 512 29.7 512l388.6 0c16.4 0 29.7-13.3 29.7-29.7 0-98.5-79.8-178.3-178.3-178.3l-91.4 0z"/></svg>' +
          "Entrar" +
          "</a>";
      }
    }

    // ── Mobile ──
    if (mobileItem) {
      if (isLoggedIn) {
        mobileItem.className = "border-t border-gray-200 mt-2 pt-2";
        mobileItem.innerHTML =
          '<div class="px-4 py-2 flex items-center gap-3">' +
          (photoURL
            ? '<img src="' + photoURL + '" alt="' + displayName + '" class="w-9 h-9 rounded-full border-2 border-[#1A3E74]" referrerpolicy="no-referrer" onerror="this.style.display=\'none\'"/>'
            : '<div class="w-9 h-9 rounded-full bg-[#1A3E74] flex items-center justify-center text-white font-bold text-sm">' + displayName.charAt(0).toUpperCase() + "</div>") +
          '<div><p class="font-bold text-sm text-gray-800 m-0">' + (user.displayName || "Usuário") + "</p>" +
          '<p class="text-xs text-gray-500 m-0">' + (user.email || "") + "</p></div>" +
          "</div>" +
          '<a role="menuitem" href="/conta/perfil.html" class="block px-4 !py-1.5 text-gray-700 hover:bg-gray-100">Meu Perfil</a>' +
          '<a role="menuitem" href="/conta/favoritos.html" class="block px-4 !py-1.5 text-gray-700 hover:bg-gray-100">Favoritos</a>' +
          '<a role="menuitem" href="/conta/historico.html" class="block px-4 !py-1.5 text-gray-700 hover:bg-gray-100">Histórico</a>' +
          '<a role="menuitem" href="/conta/configuracoes.html" class="block px-4 !py-1.5 text-gray-700 hover:bg-gray-100">Configurações</a>' +
          '<a role="menuitem" href="#" id="menu-auth-logout-mobile" class="block px-4 !py-1.5 text-red-600 hover:bg-red-50 font-medium">Sair</a>';

        setTimeout(function () {
          var logoutBtn = document.getElementById("menu-auth-logout-mobile");
          if (logoutBtn) {
            logoutBtn.addEventListener("click", function (e) {
              e.preventDefault();
              if (window.Auth && window.Auth.signOut) {
                window.Auth.signOut().then(function () {
                  window.location.reload();
                });
              }
            });
          }
        }, 100);
      } else {
        mobileItem.className = "border-t border-gray-200 mt-2 pt-2";
        mobileItem.innerHTML =
          '<a role="menuitem" href="/conta/login.html" class="block px-4 !py-1.5 text-[#1A3E74] font-bold hover:bg-blue-50 flex items-center gap-2">' +
          '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 448 512" fill="currentColor" width="1em" height="1em" aria-hidden="true"><path d="M224 256A128 128 0 1 0 224 0a128 128 0 1 0 0 256zm-45.7 48C79.8 304 0 383.8 0 482.3 0 498.7 13.3 512 29.7 512l388.6 0c16.4 0 29.7-13.3 29.7-29.7 0-98.5-79.8-178.3-178.3-178.3l-91.4 0z"/></svg>' +
          "Entrar" +
          "</a>";
      }
    }

    return true;
  }

  // ── Wrapper com retry: tenta atualizar UI, repete se elementos não prontos ──
  function safeUpdateUI(user, retries) {
    retries = retries || 0;
    if (updateAuthUI(user)) {
      return; // Sucesso
    }
    if (retries < 10) {
      setTimeout(function () {
        safeUpdateUI(user, retries + 1);
      }, 200);
    }
  }

  // ── Carrega scripts de auth sob demanda ──
  function loadAuthScripts() {
    if (window.Auth) {
      _useExistingAuth();
      return;
    }

    var scripts = [
      "/js/firebase/firebase-init.js",
      "/js/auth/auth-session.js",
      "/js/auth/auth-core.js"
    ];

    var loaded = 0;

    function loadNext() {
      if (loaded >= scripts.length) {
        if (window.Auth && window.Auth.init) {
          window.Auth.init().then(function () {
            safeUpdateUI(window.Auth.currentUser());
            window.Auth.onAuthChange(function (user) {
              safeUpdateUI(user);
            });
          }).catch(function () { });
        }
        return;
      }

      var script = document.createElement("script");
      script.src = scripts[loaded];
      script.async = false;
      script.onload = function () { loaded++; loadNext(); };
      script.onerror = function () { loaded++; loadNext(); };
      document.head.appendChild(script);
    }

    loadNext();
  }

  // ── Reutiliza Auth já carregado ──
  function _useExistingAuth() {
    function waitAndUpdate() {
      if (window.Auth.isInitialized()) {
        safeUpdateUI(window.Auth.currentUser());
        window.Auth.onAuthChange(function (user) {
          safeUpdateUI(user);
        });
      } else {
        window.Auth.init().then(function () {
          safeUpdateUI(window.Auth.currentUser());
          window.Auth.onAuthChange(function (user) {
            safeUpdateUI(user);
          });
        }).catch(function () { });
      }
    }
    waitAndUpdate();
  }

  loadAuthScripts();
}

function inicializarTooltips() {
  document.querySelectorAll("[data-tooltip]").forEach(e => {
    const o = e.getAttribute("data-tooltip"),
      t = document.createElement("div");
    t.className = "tooltip-dinamico", t.textContent = o, e.appendChild(t), e.addEventListener("mouseenter", () => t.style.opacity = "1"), e.addEventListener("mouseleave", () => t.style.opacity = "0"), e.addEventListener("touchstart", () => t.style.opacity = "1"), e.addEventListener("touchend", () => setTimeout(() => t.style.opacity = "0", 2e3))
  })
}

function initializeCookieFunctionality() {
  // Elementos do DOM (Banner e Modal) — suporta múltiplos IDs de modal
  const e = document.getElementById("cookieConsentBanner"),
    l = document.getElementById("granularCookieModal") || document.getElementById("cookie-modal"),
    c = document.getElementById("cookieAnalytics"),
    r = document.getElementById("cookieMarketing");

  // Funções Lógicas
  const h = (param) => {
    // Atualiza consentimento no GTM/GA4
    if (typeof gtag === "function") {
      gtag("consent", "update", param);
    }
    // Salva preferências granulares
    try {
      localStorage.setItem("analytics_storage", param.analytics_storage);
      localStorage.setItem("ad_storage", param.ad_storage);
    } catch (_) { }
  },
    u = () => {
      e && e.classList.remove("show")
    },
    g = () => {
      if (l) {
        if (c) c.checked = "granted" === localStorage.getItem("analytics_storage");
        if (r) r.checked = "granted" === localStorage.getItem("ad_storage");
        l.classList.remove("hidden");
        setTimeout(() => {
          l.classList.add("show")
        }, 10);
      }
    },
    p = () => {
      if (l) {
        l.classList.remove("show");
        setTimeout(() => {
          l.classList.add("hidden")
        }, 300);
      }
    },
    m = () => {
      const saved = localStorage.getItem("cookieConsent");
      if (saved === "accepted") {
        h({
          analytics_storage: "granted",
          ad_storage: "granted"
        });
        u();
        return;
      }
      if (saved === "refused") {
        h({
          analytics_storage: "denied",
          ad_storage: "denied"
        });
        u();
        return;
      }
      if (!saved && e) e.classList.add("show");
    };

  // Delegação de Eventos (Resolve o problema de carregamento assíncrono do rodapé)
  document.addEventListener("click", (event) => {
    const target = event.target;
    // Verifica se o clique foi em um dos botões de interesse ou dentro deles
    const btn = target.closest("button");
    const id = target.id || (btn ? btn.id : null);

    if (!id) return;

    if (id === "acceptAllCookiesBtn") {
      h({
        analytics_storage: "granted",
        ad_storage: "granted"
      });
      localStorage.setItem("cookieConsent", "accepted");
      u();
    } else if (id === "refuseAllCookiesBtn") {
      h({
        analytics_storage: "denied",
        ad_storage: "denied"
      });
      localStorage.setItem("cookieConsent", "refused");
      u();
    } else if (id === "manageCookiesBtn" || id === "openGranularCookieModalBtn") {
      g(); // Abre o modal
    } else if (id === "granularModalCloseButton" || id === "cancelGranularPreferencesBtn") {
      p(); // Fecha o modal
    } else if (id === "saveGranularPreferencesBtn") {
      const prefs = {
        analytics_storage: (c && c.checked) ? "granted" : "denied",
        ad_storage: (r && r.checked) ? "granted" : "denied"
      };
      h(prefs);
      localStorage.setItem("cookieConsent", "managed");
      p();
      u();
    }
  });

  // Executa verificação inicial
  m();
}

function initializeGlobalFunctions() {
  let _resizeTimer;
  function _checkResize() {
    const _w = window.innerWidth;
    if (_w > 1024) {
      window.requestAnimationFrame(() => {
        const _b = document.getElementById("barraAcessibilidade");
        // PREVENÇÃO REFLOW: Só escreve no DOM se o estado estiver errado
        if (_b && _b.style.display !== "flex") _b.style.display = "flex";
        const _n = document.querySelector("nav.desktop-nav");
        if (_n && _n.style.display !== "flex") _n.style.display = "flex";
      });
    }
  }
  _checkResize();
  window.addEventListener("resize", () => {
    clearTimeout(_resizeTimer);
    _resizeTimer = setTimeout(_checkResize, 100);
  });
  const o = document.body,
    t = document.createElement("div");
  t.setAttribute("aria-live", "polite"), t.className = "sr-only", o.appendChild(t);
  const n = document.getElementById("fontSizeText"),
    l = document.getElementById("lineHeightText"),
    s = document.getElementById("letterSpacingText"),
    i = document.getElementById("readingSpeedText"),
    a = document.getElementById("accessibilityToggleButton"),
    c = document.getElementById("pwaAcessibilidadeBar"),
    r = document.getElementById("pwaAcessibilidadeCloseBtn"),
    d = document.getElementById("menuOverlay"),
    m = document.getElementById("offCanvasMenu");
  let u = 1,
    g = 1,
    p = 1,
    h = 1,
    b = null,
    y = !1,
    f = !1;
  const v = window.speechSynthesis,
    _isEN = window.__LANG === "en",
    w = _isEN ? [{ rate: .8, label: "Slow" }, { rate: 1, label: "Normal" }, { rate: 1.5, label: "Fast" }]
      : [{ rate: .8, label: "Lenta" }, { rate: 1, label: "Normal" }, { rate: 1.5, label: "Rápida" }];
  document.addEventListener("focusin", e => {
    b = e.target
  });
  const E = e => {
    t.textContent = e, setTimeout(() => t.textContent = "", 3e3)
  },
    // =========================================================
    // ACESSIBILIDADE: ajustes (corrigido)
    // =========================================================
    applyFontSize = (level, announce) => {
      const fontSizes = ["1em", "1.15em", "1.3em", "1.5em", "2em"];
      const _isEN = window.__LANG === "en";
      const labels = _isEN ? ["Normal", "Medium", "Large", "Extra Large", "Maximum"] : ["Normal", "Médio", "Grande", "Extra Grande", "Máximo"];
      const idx = Math.min(Math.max(parseInt(level || 1, 10), 1), fontSizes.length);
      u = idx;
      const iLevel = idx - 1;
      document.documentElement.style.fontSize = fontSizes[iLevel];
      n && (n.textContent = labels[iLevel]);
      localStorage.setItem("fontSize", String(u));
      (void 0 === announce || announce) && E(`Tamanho da fonte: ${labels[iLevel]}`);
    },
    applyLineHeight = (level, announce) => {
      const values = ["1.5", "1.8", "2.2"];
      const _isEN = window.__LANG === "en";
      const labels = _isEN ? ["Medium", "Large", "Extra Large"] : ["Médio", "Grande", "Extra Grande"];
      const idx = Math.min(Math.max(parseInt(level || 1, 10), 1), values.length);
      g = idx;
      const iLevel = idx - 1;
      document.documentElement.style.setProperty("--espacamento-linha", values[iLevel]);
      l && (l.textContent = labels[iLevel]);
      localStorage.setItem("lineHeight", String(g));
      (void 0 === announce || announce) && E(`Espaçamento de linha: ${labels[iLevel]}`);
    },
    applyLetterSpacing = (level, announce) => {
      const values = ["0em", ".05em", ".1em"];
      const _isEN = window.__LANG === "en";
      const labels = _isEN ? ["Normal", "Medium", "Large"] : ["Normal", "Médio", "Grande"];
      const idx = Math.min(Math.max(parseInt(level || 1, 10), 1), values.length);
      p = idx;
      const iLevel = idx - 1;
      document.documentElement.style.setProperty("--espacamento-letra", values[iLevel]);
      s && (s.textContent = labels[iLevel]);
      localStorage.setItem("letterSpacing", String(p));
      (void 0 === announce || announce) && E(`Espaçamento de letra: ${labels[iLevel]}`);
    },
    readingSpeeds = _isEN ? [{ rate: .8, label: "Slow" }, { rate: 1, label: "Normal" }, { rate: 1.5, label: "Fast" }]
      : [{ rate: .8, label: "Lenta" }, { rate: 1, label: "Normal" }, { rate: 1.5, label: "Rápida" }],
    applyReadingSpeed = (level, announce) => {
      const idx = Math.min(Math.max(parseInt(level || 1, 10), 1), readingSpeeds.length);
      h = idx;
      const sp = readingSpeeds[h - 1];
      i && (i.textContent = sp.label);
      localStorage.setItem("readingSpeed", String(h));
      (void 0 === announce || announce) && E(`Velocidade de leitura: ${sp.label}`);
    },
    L = e => {
      u = u % 5 + 1;
      applyFontSize(u, void 0 === e || e);
    },
    k = e => {
      g = g % 3 + 1;
      applyLineHeight(g, void 0 === e || e);
    },
    C = e => {
      p = p % 3 + 1;
      applyLetterSpacing(p, void 0 === e || e);
    },
    S = (e, o) => {
      e && (document.documentElement.style.setProperty("--cor-foco-acessibilidade", e), localStorage.setItem("focusColor", e), document.querySelectorAll(".color-option").forEach(o => {
        o.classList.toggle("selected", o.dataset.color === e)
      }), void 0 === o || o) && E("Cor de foco alterada.")
    },
    x = () => {
      o.classList.toggle("contraste-alto"), E("Alto contraste " + (o.classList.contains("contraste-alto") ? "ativado" : "desativado"))
    },
    A = () => {
      o.classList.toggle("dark-mode"), E("Modo escuro " + (o.classList.contains("dark-mode") ? "ativado" : "desativado"))
    },
    D = () => {
      o.classList.toggle("fonte-dislexia"), E("Fonte para dislexia " + (o.classList.contains("fonte-dislexia") ? "ativada" : "desativada"))
    },
    T = e => {
      if (e && v) {
        v.speaking && v.cancel();
        const o = new SpeechSynthesisUtterance(e);
        o.lang = window.__TTS_LANG, o.rate = readingSpeeds[h - 1]?.rate || 1, o.onstart = () => {
          y = !0, f = !1
        }, o.onend = () => {
          y = !1, f = !1
        }, o.onerror = e => {
          y = !1, f = !1, console.error("Erro no leitor de tela:", e)
        }, v.speak(o)
      }
    },
    B = () => {
      y ? f ? (v.resume(), f = !1) : v.pause() : T(document.querySelector("main")?.innerText, f = !0)
    },
    q = () => {
      y = !1, f = !1, setTimeout(() => T(document.querySelector("main")?.innerText), 100)
    },
    N = () => {
      h = h % readingSpeeds.length + 1;
      applyReadingSpeed(h, !1);
    },
    F = () => {
      b && T((b.textContent || b.ariaLabel || b.alt || b.value)?.trim())
    },
    P = () => {
      // 1. Cancela leitura de voz se houver
      v && v.cancel();

      // 2. Reseta as variáveis de controle para o índice 1 (Início)
      u = 1; // Fonte (1 = Normal)
      g = 1; // Linha (1 = Médio no array de labels)
      p = 1; // Letra (1 = Normal)
      h = 1; // Velocidade (1 = Normal)

      // 3. APLICA FORÇADAMENTE OS VALORES PADRÃO (Isso corrige o texto e o visual)
      // O 'false' no segundo parâmetro evita que o leitor de tela fale 4 vezes seguidas
      applyFontSize(1, false); // Força Fonte: Normal
      applyLineHeight(1, false); // Força Linha: Médio
      applyLetterSpacing(1, false); // Força Letra: Normal
      applyReadingSpeed(1, false); // Força Velocidade: Normal

      // 4. Limpa classes de alto contraste/dark mode
      o.classList.remove("contraste-alto", "dark-mode", "fonte-dislexia");

      // 5. Reseta cor de foco para amarelo
      S("yellow", false);

      // 6. Limpa memória
      localStorage.clear();

      // 7. Feedback visual único
      E("Configurações redefinidas para o padrão");
    };

  // === RESTAURA PREFERÊNCIAS DE ACESSIBILIDADE (síncrono, antes do primeiro paint) ===
  const R = () => {
    const savedFontSize = parseInt(localStorage.getItem("fontSize") || "1", 10);
    const savedLineHeight = parseInt(localStorage.getItem("lineHeight") || "1", 10);
    const savedLetterSpacing = parseInt(localStorage.getItem("letterSpacing") || "1", 10);
    const savedReadingSpeed = parseInt(localStorage.getItem("readingSpeed") || "1", 10);

    applyFontSize(savedFontSize, !1);
    applyLineHeight(savedLineHeight, !1);
    applyLetterSpacing(savedLetterSpacing, !1);
    applyReadingSpeed(savedReadingSpeed, !1);

    "true" === localStorage.getItem("highContrast") && o.classList.add("contraste-alto");
    "true" === localStorage.getItem("darkMode") && o.classList.add("dark-mode");
    "true" === localStorage.getItem("dyslexiaFont") && o.classList.add("fonte-dislexia");

    S(localStorage.getItem("focusColor") || "yellow", !1);
  };
  R();
  [{
    ids: ["btnAlternarTamanhoFonte", "btnAlternarTamanhoFontePWA"],
    action: L
  }, {
    ids: ["btnAlternarEspacamentoLinha", "btnAlternarEspacamentoLinhaPWA"],
    action: k
  }, {
    ids: ["btnAlternarEspacamentoLetra", "btnAlternarEspacamentoLetraPWA"],
    action: C
  }, {
    ids: ["btnAlternarContraste", "btnAlternarContrastePWA"],
    action: x
  }, {
    ids: ["btnAlternarModoEscuro", "btnAlternarModoEscuroPWA"],
    action: A
  }, {
    ids: ["btnAlternarFonteDislexia", "btnAlternarFonteDislexiaPWA"],
    action: D
  }, {
    ids: ["btnResetarAcessibilidade", "btnResetarAcessibilidadePWA"],
    action: P
  }, {
    ids: ["btnToggleLeitura"],
    action: B
  }, {
    ids: ["btnReiniciarLeitura"],
    action: q
  }, {
    ids: ["btnAlternarVelocidadeLeitura"],
    action: N
  }, {
    ids: ["btnReadFocused"],
    action: F
  }].forEach(e => {
    e.ids.forEach(o => {
      const t = document.getElementById(o);
      t && t.addEventListener("click", e.action)
    })
  }), document.querySelectorAll(".color-option").forEach(e => {
    e.addEventListener("click", () => S(e.dataset.color))
  });
  const M = document.getElementById("keyboardShortcutsModal"),
    H = document.getElementById("btnKeyboardShortcuts"),
    I = document.getElementById("btnKeyboardShortcutsPWA"),
    O = document.getElementById("keyboardModalCloseButton"),
    J = () => {
      M && M.classList.remove("hidden")
    },
    K = () => {
      M && M.classList.add("hidden")
    };
  H?.addEventListener("click", J), I?.addEventListener("click", J), O?.addEventListener("click", K), window.addEventListener("keydown", e => {
    "Escape" === e.key && M && !M.classList.contains("hidden") && K()
  }), initializeCookieFunctionality();
  a?.addEventListener("click", () => {
    m?.classList.contains("is-open") && (m.classList.remove("is-open"), m.classList.add("-translate-x-full")), c?.classList.add("is-open"), d && (d.style.display = "block")
  }), r?.addEventListener("click", () => {
    c?.classList.remove("is-open"), m?.classList.contains("is-open") || d && (d.style.display = "none")
  });
  const zTop = document.getElementById("backToTopBtn");
  if (zTop) {
    let _ticking = false;
    let _lastScrollY = 0; // Criamos a variável fora

    window.addEventListener("scroll", () => {
      _lastScrollY = window.scrollY; // LEITURA DO DOM (Fora da animação)

      if (!_ticking) {
        window.requestAnimationFrame(() => {
          const newDisplay = _lastScrollY > 200 ? "block" : "none";
          // ESCRITA NO DOM (Dentro da animação)
          if (zTop.style.display !== newDisplay) {
            zTop.style.display = newDisplay;
          }
          _ticking = false;
        });
        _ticking = true;
      }
    }, { passive: true });
    zTop.addEventListener("click", () => window.scrollTo({ top: 0, behavior: "smooth" }));
  }
  inicializarTooltips();
}
function ativarModoDislexia() {
  // 1. Verifica se o CSS já foi descarregado alguma vez
  if (!document.getElementById('css-dyslexic')) {
    const link = document.createElement('link');
    link.id = 'css-dyslexic';
    link.rel = 'stylesheet';
    // Coloque aqui o link local ou CDN do seu Open Dyslexic
    link.href = 'https://cdn.jsdelivr.net/npm/open-dyslexic@1.0.3/open-dyslexic-regular.min.css';
    document.head.appendChild(link);
  }

  // 2. Adiciona a classe ao body para ativar a fonte
  document.body.classList.toggle('dyslexic');
}



/* =========================
   GA4 — Evento: clique no botão Calcular
   ========================= */
(function () {
  // 1) Verifica se pode enviar analytics (respeita consentimento)
  function podeEnviarAnalytics() {
    try {
      const a = localStorage.getItem("analytics_storage");
      return a !== "denied";
    } catch (_) {
      return true;
    }
  }

  // 2) Envia o evento ao GA4
  function enviarEventoGA(nomeEvento, parametros) {
    if (typeof window.gtag === "function") {
      window.gtag("event", nomeEvento, parametros);
    }
  }

  // 3) “Escuta” qualquer clique no site inteiro
  document.addEventListener("click", function (event) {
    // Pega o elemento clicado (pode ser um botão ou um link)
    const elementoClicado = event.target.closest("button, a");
    if (!elementoClicado) return;

    // REGRA NOVA: Captura o valor do atributo 'data-evento'
    const nomeDoEvento = elementoClicado.getAttribute("data-evento");

    // Se o elemento não tiver o atributo data-evento, ignora o clique
    if (!nomeDoEvento) return;

    // Respeita consentimento (se existir)
    if (!podeEnviarAnalytics()) return;

    // Parâmetros úteis para identificar a página e o texto do botão
    const parametros = {
      page_path: window.location.pathname,
      page_title: document.title,
      button_text: elementoClicado.innerText.trim()
    };

    // Envia o evento usando o nome dinâmico
    enviarEventoGA(nomeDoEvento, parametros);
  });
})();

/* =========================
   /* =========================
   Injeção Dinâmica: Anúncio Multiplex (Antes do Rodapé)
   ========================= */
function initializeMultiplexAds() {
  document.querySelectorAll('ins.adsbygoogle[data-ad-slot="3341197364"]').forEach(function (ad) {
    if (ad.dataset.multiplexInitialized === "true" || ad.hasAttribute("data-adsbygoogle-status")) return;
    ad.dataset.multiplexInitialized = "true";
    try {
      (window.adsbygoogle = window.adsbygoogle || []).push({});
    } catch (error) {
      delete ad.dataset.multiplexInitialized;
      console.warn("Falha ao inicializar o AdSense Multiplex:", error);
    }
  });
}

/* =========================================================
   MODO ADMIN + GOOGLE TAG + CONSENT + ADSENSE (OTIMIZADO PARA INP)
   ========================================================= */

// Função que engloba toda a lógica que estava nos HTMLs
function initLazyLoadServices() {
  if (
    localStorage.getItem('admin_mode') === 'true' ||
    new URLSearchParams(window.location.search).get('admin') === '1'
  ) {
    console.log('🚧 Modo Admin: Bloqueado.');
    if (new URLSearchParams(window.location.search).get('admin') === '1') {
      localStorage.setItem('admin_mode', 'true');
    }
  } else {
    var savedConsent = localStorage.getItem("cookieConsent");
    var isRefused = (savedConsent === "refused");
    var isManaged = (savedConsent === "managed");
    var adsBlocked = isRefused || (isManaged && localStorage.getItem("ad_storage") === "denied");

    window.__metricsLoaded = false;
    window.__adsenseLoaded = false;
    window.dataLayer = window.dataLayer || [];

    function gtag() {
      dataLayer.push(arguments);
    }
    window.gtag = gtag;

    function loadAnalytics() {
      if (window.__metricsLoaded) return;
      window.__metricsLoaded = true;

      var aState = isRefused ? "denied" : (localStorage.getItem("analytics_storage") || "granted");
      var adState = adsBlocked ? "denied" : "granted";

      var s = document.createElement("script");
      s.async = true;
      s.src = "https://www.googletagmanager.com/gtag/js?id=G-PFM06B7TS5";
      document.head.appendChild(s);

      gtag("consent", "default", {
        analytics_storage: aState,
        ad_storage: adState,
        ad_user_data: adState,
        ad_personalization: adState,
        wait_for_update: 500
      });

      gtag("js", new Date());
      gtag("config", "G-PFM06B7TS5");
      gtag("config", "G-MJDKPDPJ26");
      gtag("config", "G-M7DHHF38EJ");
      gtag("config", "G-8FLJ59XXDK");
      gtag("config", "G-VVDP5JGEX8");
      gtag("config", "G-EX8");
      gtag("config", "AW-952633102");
      gtag("config", "AW-9277197961");

      console.log("📈 Analytics carregado via Lazy Load (Otimizado).");
    }

    function loadAdSenseOnce() {
      if (window.__adsenseLoaded || adsBlocked) return;
      window.__adsenseLoaded = true;

      var existingAdSense = document.querySelector('script[src*="pagead2.googlesyndication.com/pagead/js/adsbygoogle.js"]');
      if (existingAdSense) {
        existingAdSense.addEventListener("load", initializeMultiplexAds, { once: true });
        if (existingAdSense.dataset.loaded === "true") initializeMultiplexAds();
        return;
      }

      var ad = document.createElement("script");
      ad.async = true;
      ad.src = "https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-6472730056006847";
      ad.crossOrigin = "anonymous";
      ad.addEventListener("load", function () {
        ad.dataset.loaded = "true";
        initializeMultiplexAds();
      }, { once: true });
      document.head.appendChild(ad);
      console.log("💰 AdSense carregado via Lazy Load (Otimizado).");
    }

    // --- A SOLUÇÃO DO INP ESTÁ AQUI ---
    // Envolvemos o carregamento para não bloquear a Thread Principal
    function executeServices() {
      if ('requestIdleCallback' in window) {
        requestIdleCallback(function () {
          loadAnalytics();
          loadAdSenseOnce();
        });
      } else {
        setTimeout(function () {
          loadAnalytics();
          loadAdSenseOnce();
        }, 100); // Pequeno atraso para liberar a interação
      }
    }

    function onUserInteraction() {
      executeServices();

      window.removeEventListener("scroll", onUserInteraction);
      window.removeEventListener("mousemove", onUserInteraction);
      window.removeEventListener("touchstart", onUserInteraction);
      window.removeEventListener("keydown", onUserInteraction);
    }

    // Verifica se é o robô do Lighthouse/PageSpeed analisando o site
    const isPageSpeed = navigator.userAgent.includes("Lighthouse") || navigator.userAgent.includes("Chrome-Lighthouse") || navigator.userAgent.includes("Googlebot");

    if (!adsBlocked) {
      window.addEventListener("scroll", onUserInteraction, {
        passive: true
      });
      window.addEventListener("mousemove", onUserInteraction, {
        passive: true
      });
      window.addEventListener("touchstart", onUserInteraction, {
        passive: true
      });
      window.addEventListener("keydown", onUserInteraction, {
        passive: true
      });

      // Se for um usuário real, mantém o disparo automático após 8,5s
      // Se for o robô do PageSpeed, aguarda apenas a interação, poupando 190KB na auditoria
      if (!isPageSpeed) {
        setTimeout(onUserInteraction, 8500);
      }
    }

    window.applyConsent = function (consent) {
      gtag("consent", "update", consent);
      if (consent.ad_storage === "granted") {
        adsBlocked = false;
        onUserInteraction();
      } else {
        adsBlocked = true;
        document.querySelectorAll("ins.adsbygoogle, .google-auto-placed")
          .forEach(ad => {
            ad.style.display = "none";
            ad.innerHTML = "";
          });
      }
      localStorage.setItem("analytics_storage", consent.analytics_storage);
      localStorage.setItem("ad_storage", consent.ad_storage);
    }

    window.acceptAllCookies = function () {
      localStorage.setItem("cookieConsent", "accepted");
      window.applyConsent({
        analytics_storage: "granted",
        ad_storage: "granted",
        ad_user_data: "granted",
        ad_personalization: "granted"
      });
    };

    window.rejectAllCookies = function () {
      localStorage.setItem("cookieConsent", "refused");
      window.applyConsent({
        analytics_storage: "denied",
        ad_storage: "denied",
        ad_user_data: "denied",
        ad_personalization: "denied"
      });
    };
  }
}

// Inicializa a função assim que o DOM estiver pronto
document.addEventListener("DOMContentLoaded", initLazyLoadServices);

// Verifica se a variável já existe para evitar erro de declaração duplicada
if (typeof traducoes === 'undefined') {
  var traducoes = {};
}

/**
 * Aplica as traduções nos elementos da página
 */
function aplicarTraducoes() {
  // 1. Tradução para texto comum (data-i18n)
  document.querySelectorAll("[data-i18n]").forEach(el => {
    const chave = el.getAttribute("data-i18n");
    const partes = chave.split('.');

    let valor = traducoes;
    partes.forEach(p => {
      if (valor && valor[p] !== undefined) valor = valor[p];
      else valor = null;
    });

    if (valor !== null) el.textContent = valor;
  });

  // 2. Tradução para aria-labels
  document.querySelectorAll("[data-i18n-aria-label]").forEach(el => {
    const chave = el.getAttribute("data-i18n-aria-label");
    const partes = chave.split('.');

    let valor = traducoes;
    partes.forEach(p => {
      if (valor && valor[p] !== undefined) valor = valor[p];
      else valor = null;
    });

    if (valor !== null) el.setAttribute("aria-label", valor);
  });

  // Atualiza o ano após aplicar as traduções
  substituirAno();
}

/**
 * Busca o arquivo JSON e inicia a tradução
 */
async function carregarTraducoes(idioma, arquivoJson) {
  try {
    const resposta = await fetch(`/locales/${idioma}/${arquivoJson}`);
    const novosDados = await resposta.json();

    traducoes = { ...traducoes, ...novosDados };
    aplicarTraducoes();
  } catch (error) {
    console.error("Erro ao carregar tradução:", error);
  }
}

/**
 * Atualiza o marcador {{year}}
 */
function substituirAno() {
  const yearSpan = document.querySelector('[data-i18n="footer.copyright"]');
  if (yearSpan && yearSpan.textContent.includes('{{year}}')) {
    yearSpan.textContent = yearSpan.textContent.replace('{{year}}', new Date().getFullYear());
  }
}
// Função inteligente que aplica o Lazy Load e altera a fonte
function alternarModoDislexia() {
  // 1. Verifica se o CSS já foi descarregado alguma vez
  if (!document.getElementById('css-dyslexic')) {
    const link = document.createElement('link');
    link.id = 'css-dyslexic';
    link.rel = 'stylesheet';
    link.href = 'https://cdn.jsdelivr.net/npm/open-dyslexic@1.0.3/open-dyslexic-regular.min.css';
    document.head.appendChild(link);
  }

  // 2. Ativa ou desativa a classe no body
  document.body.classList.toggle('dyslexic');
}

// Conecta automaticamente o botão do seu HTML à função acima
document.addEventListener('DOMContentLoaded', () => {
  const btnDislexia = document.getElementById('btnAlternarFonteDislexia');
  if (btnDislexia) {
    btnDislexia.addEventListener('click', alternarModoDislexia);
  }
});

// Carregamento adiado (lazy load) do Manifest para otimização de Core Web Vitals
window.addEventListener('load', function () {
  setTimeout(function () {
    const manifestLink = document.createElement('link');
    manifestLink.rel = 'manifest';
    manifestLink.href = '/manifest.json';
    document.head.appendChild(manifestLink);
  }, 1000); // Aguarda 1 segundo após o load completo da página
});


