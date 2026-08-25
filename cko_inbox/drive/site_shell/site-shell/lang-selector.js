/**
 * lang-selector.js
 * Responsável por injetar e gerir o seletor de idiomas dinâmico.
 */

document.addEventListener("DOMContentLoaded", () => {
  const container = document.getElementById("language-selector-placeholder");
  if (!container) return;

  // O próprio script gere o seu HTML (Encapsulamento perfeito)
  fetch("/_language_selector.html")
    .then(response => {
      if (!response.ok) throw new Error("Ficheiro _language_selector.html não encontrado");
      return response.text();
    })
    .then(data => {
      container.innerHTML = data;
      langSelectorInit(); // Inicializa a lógica apenas após o HTML estar no DOM
    })
    .catch(err => console.error("Erro ao carregar seletor de idiomas:", err));
});

function langSelectorInit() {
  const button = document.getElementById("langButton");
  const menu = document.getElementById("langMenu");
  const langFlag = document.getElementById("langFlag");
  const langText = document.getElementById("langText");

  // Encerra a execução se os elementos não existirem
  if (!button || !menu) return;

  const pathName = window.location.pathname;
  const fileNameMatch = pathName.match(/[^/]*.html$/i);
  const currentFileName = fileNameMatch ? fileNameMatch[0] : "";

  // Abrir/fechar menu
  button.addEventListener("click", () => {
    menu.classList.toggle("hidden");
    button.setAttribute("aria-expanded", !menu.classList.contains("hidden"));
  });

  // Fechar ao clicar fora
  document.addEventListener("click", (e) => {
    if (!button.contains(e.target) && !menu.contains(e.target)) {
      menu.classList.add("hidden");
      button.setAttribute("aria-expanded", "false");
    }
  });

  // --- LÓGICA DE REDIRECIONAMENTO ---
  document.querySelectorAll("#langMenu div").forEach((item) => {
    item.addEventListener("click", () => {
      const value = item.dataset.value;
      const flag = item.dataset.flag;
      // Usa textContent em vez de innerText (evita reflow forçado)
      const text = item.textContent.trim();

      langFlag.src = flag;
      langText.textContent = text;
      menu.classList.add("hidden");
      button.setAttribute("aria-expanded", "false");

      let newPath = "";
      switch (value) {
        case "en": newPath = "/en/"; break;
        case "es": newPath = "/es/"; break;
        case "de": newPath = "/de/"; break;
        case "it": newPath = "/it/"; break;
        case "fr": newPath = "/fr/"; break;
        case "hi": newPath = "/hi/"; break;
        case "zh": newPath = "/zh/"; break;
        case "ar": newPath = "/ar/"; break;
        case "ja": newPath = "/ja/"; break;
        case "ru": newPath = "/ru/"; break;
        case "ko": newPath = "/ko/"; break;
        case "tr": newPath = "/tr/"; break;
        case "nl": newPath = "/nl/"; break;
        case "pl": newPath = "/pl/"; break;
        case "sv": newPath = "/sv/"; break;
        case "id": newPath = "/id/"; break;
        case "vi": newPath = "/vi/"; break;
        case "uk": newPath = "/uk/"; break;
        default: newPath = "/";
      }

      if (currentFileName && currentFileName !== "index.html") {
        newPath += currentFileName;
      }
      window.location.href = newPath;
    });
  });

  // --- DETECÇÃO DO IDIOMA ATUAL ---
  const path = window.location.pathname;
  let current = document.querySelector('[data-value="pt"]');

  // Lógica otimizada de deteção
  const langs = ["en", "es", "de", "it", "fr", "hi", "zh", "ar", "ja", "ru", "ko", "tr", "nl", "pl", "sv", "id", "vi", "uk"];
  for (const lang of langs) {
    if (path.startsWith(`/${lang}/`)) {
      current = document.querySelector(`[data-value="${lang}"]`);
      break;
    }
  }

  if (current) {
    // Usa textContent em vez de innerText (evita reflow forçado)
    langFlag.src = current.dataset.flag;
    langText.textContent = current.textContent.trim();
  }
}