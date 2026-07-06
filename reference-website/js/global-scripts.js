/* =========================
   Camada 4 — Anti-bot leve
   ========================= */
(function () {
  try {
    const ua = navigator.userAgent || "";
    const isBotLike =
      navigator.webdriver === true ||
      ua.length < 10 ||
      !navigator.language ||
      (screen && (screen.width === 0 || screen.height === 0));

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
  var _ttsMap = { en:"en-US", es:"es-ES", de:"de-DE", it:"it-IT", fr:"fr-FR", hi:"hi-IN", zh:"zh-CN", ar:"ar-SA", ja:"ja-JP", ru:"ru-RU", ko:"ko-KR", tr:"tr-TR", nl:"nl-NL", pl:"pl-PL", sv:"sv-SE", id:"id-ID", vi:"vi-VN", uk:"uk-UA", pt:"pt-BR" };
  window.__TTS_LANG = _ttsMap[window.__LANG] || "pt-BR";

  // Prefixo para fetches (relativo na pasta de idioma, absoluto na raiz)
  window.__FETCH_PREFIX = window.__IS_LANG_FOLDER ? "" : "/";
})();

// Executar IMEDIATAMENTE para evitar flash de tamanho de fonte
(function () {
  const savedFontSize = parseInt(localStorage.getItem("fontSize") || "1", 10);
  // PREVENÇÃO DE CLS: Só reescreve o tamanho da fonte se o usuário realmente tiver alterado o padrão
  if (savedFontSize !== 1) {
    const fontSizes = ["1em", "1.15em", "1.3em", "1.5em", "2em"];
    const idx = Math.min(Math.max(savedFontSize, 1), fontSizes.length);
    document.documentElement.style.fontSize = fontSizes[idx - 1];
  }
})();
// Registra o Service Worker
"serviceWorker" in navigator && window.addEventListener("load", () => {
  navigator.serviceWorker.register("/sw.js").then(e => {
    console.log("Service Worker registado com sucesso:", e.scope)
  }, e => {
    console.log("Registo do Service Worker falhou:", e)
  })
});

document.addEventListener("DOMContentLoaded", function () {
  fetch(window.__FETCH_PREFIX + "menu-global.html").then(e => e.ok ? e.text() : Promise.reject("Ficheiro menu-global.html não encontrado")).then(e => {
    const o = document.getElementById("global-header-container");
    if (o) {
      window.requestAnimationFrame(() => {
        o.innerHTML = e;
        initializeNavigationMenu();
      });
    }
  }).catch(e => console.warn("Não foi possível carregar o menu global:", e));

  fetch(window.__FETCH_PREFIX + "global-body-elements.html").then(e => e.ok ? e.text() : Promise.reject("Ficheiro global-body-elements.html não encontrado")).then(e => {
    window.requestAnimationFrame(() => {
      document.body.insertAdjacentHTML("beforeend", e);
      initializeGlobalFunctions();
    });
  }).catch(e => console.warn("Não foi possível carregar os elementos globais do corpo:", e));

// Função para carregar o Seletor de Idiomas (consolidado e com fallback)

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
  })
}

function inicializarTooltips() {
  document.querySelectorAll("[data-tooltip]").forEach(e => {
    const o = e.getAttribute("data-tooltip"),
      t = document.createElement("div");
    t.className = "tooltip-dinamico", t.innerText = o, e.appendChild(t), e.addEventListener("mouseenter", () => t.style.opacity = "1"), e.addEventListener("mouseleave", () => t.style.opacity = "0"), e.addEventListener("touchstart", () => t.style.opacity = "1"), e.addEventListener("touchend", () => setTimeout(() => t.style.opacity = "0", 2e3))
  })
}

function initializeCookieFunctionality() {
  // Elementos do DOM (Banner e Modal)
  const e = document.getElementById("cookieConsentBanner"),
    l = document.getElementById("granularCookieModal"),
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
      } catch (_) {}
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
    window.addEventListener("scroll", () => {
      if (!_ticking) {
        window.requestAnimationFrame(() => {
          const _lastScrollY = window.scrollY; 
          const newDisplay = _lastScrollY > 200 ? "block" : "none";
          // PREVENÇÃO REFLOW: Só escreve se o estilo realmente for mudar
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
  // 1) Verifica se pode enviar analytics (respeita consentimento, se você usar)
  function podeEnviarAnalytics() {
    try {
      const a = localStorage.getItem("analytics_storage");
      return a !== "denied"; // se estiver denied, não envia
    } catch (_) {
      return true; // se não conseguir ler, permite
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
    // pega o elemento clicado e procura o botão mais próximo
    const botao = event.target.closest("button");
    if (!botao) return;

    // regra: só dispara se for o botão Calcular padrão
    if (botao.id !== "btnCalcular") return;

    // respeita consentimento (se existir)
    if (!podeEnviarAnalytics()) return;

    // parâmetros úteis para identificar a página
    const parametros = {
      page_path: window.location.pathname,
      page_title: document.title
    };

    // envia o evento
    enviarEventoGA("calcular_click", parametros);
  });
})();

/* =========================
   Injeção Dinâmica: Anúncio Multiplex (Antes do Rodapé)
   ========================= */
document.addEventListener("DOMContentLoaded", function () {
  // 1. Localiza a âncora exata do rodapé na página atual
  const footerPlaceholder = document.getElementById("footer-placeholder");

  // Se a página não tiver rodapé por algum motivo, aborta para evitar erros
  if (!footerPlaceholder) return;

  // 2. Cria o container do anúncio
  const adContainer = document.createElement("div");

  // Usamos exatamente as mesmas classes do seu footer.html para alinhar perfeitamente
  // A classe my-10 adiciona margem superior e inferior para não colar no texto
  adContainer.className = "max-w-7xl mx-auto px-4 my-10";
  
  // ==========================================
  // ANTI-CLS: Reserva de espaço dinâmica para o AdSense Multiplex
  // ==========================================
  adContainer.style.minHeight = window.innerWidth >= 768 ? "90px" : "250px";

  // 3. Monta a tag do anúncio (sem a tag <script> que é bloqueada via innerHTML)
  adContainer.innerHTML = `
    <ins class="adsbygoogle"
         style="display:block"
         data-ad-format="autorelaxed"
         data-ad-client="ca-pub-6472730056006847"
         data-ad-slot="5401011816"></ins>
  `;

  // 4. Injeta o anúncio no DOM, exatamente ANTES da div do rodapé
  footerPlaceholder.parentNode.insertBefore(adContainer, footerPlaceholder);

  // 5. Solicita ao AdSense que preencha o bloco de forma segura
  // Como você usa lazy load, o array window.adsbygoogle guardará o pedido
  // até que o usuário interaja com a página e o AdSense seja ativado.
  setTimeout(() => {
    try {
      (window.adsbygoogle = window.adsbygoogle || []).push({});
    } catch (e) {
      console.warn("Falha ao inicializar o AdSense Multiplex:", e);
    }
  }, 300);
});

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
      var ad = document.createElement("script");
      ad.async = true;
      ad.src = "https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-6472730056006847";
      ad.crossOrigin = "anonymous";
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

      setTimeout(onUserInteraction, 8500);
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

