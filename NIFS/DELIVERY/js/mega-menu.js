/* ======================================================================
   mega-menu.js — Comportamento do cabeçalho com mega-menus
   Calculadoras de Enfermagem — Global Platform
   Menu mobile (hamburger), fechamento por ESC/clique, aria-expanded no
   hover dos itens de mega-menu e função global de busca.
   ====================================================================== */
(function () {
  var wired = false;
  function wire() {
    if (wired) return;
    if (!document.getElementById("gh-hamburger-btn")) return;
    wired = true;
    bindMegaMenu();
  }

  function bindMegaMenu() {
  var hamburger = document.getElementById("gh-hamburger-btn");
  var mobileMenu = document.getElementById("gh-mobile-menu");

  function closeMobileMenu() {
    if (!mobileMenu || !hamburger) return;
    mobileMenu.classList.remove("open");
    hamburger.setAttribute("aria-expanded", "false");
    hamburger.innerHTML = '<i class="fa-solid fa-bars" aria-hidden="true"></i>';
  }

  if (hamburger && mobileMenu) {
    hamburger.addEventListener("click", function () {
      var isOpen = mobileMenu.classList.toggle("open");
      hamburger.setAttribute("aria-expanded", isOpen);
      hamburger.innerHTML = isOpen
        ? '<i class="fa-solid fa-xmark" aria-hidden="true"></i>'
        : '<i class="fa-solid fa-bars" aria-hidden="true"></i>';
    });
  }

  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") {
      if (mobileMenu) {
        mobileMenu.querySelectorAll("details[open]").forEach(function (d) { d.removeAttribute("open"); });
      }
      closeMobileMenu();
    }
  });

  if (mobileMenu) {
    mobileMenu.addEventListener("click", function (e) {
      var target = e.target.closest("a[href]");
      if (!target) return;
      setTimeout(closeMobileMenu, 150);
    });
  }

  // Atualiza aria-expanded nos botões de mega-menu/mini-dropdown no hover (desktop)
  document.querySelectorAll(".gh-menu-list > li > button").forEach(function (btn) {
    var li = btn.closest("li");
    if (!li) return;
    li.addEventListener("mouseenter", function () { btn.setAttribute("aria-expanded", "true"); });
    li.addEventListener("mouseleave", function () { btn.setAttribute("aria-expanded", "false"); });
  });

  // Busca global — redireciona para busca.html?q=...
  window.handleSearch = function (event) {
    var form = event.target;
    var input = form.querySelector('input[name="q"]');
    var query = (input && input.value || "").trim();
    event.preventDefault();
    if (!query) return false;
    window.location.href = "busca.html?q=" + encodeURIComponent(query);
    return false;
  };
  }

  document.addEventListener("partials:ready", wire);
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", wire);
  } else {
    wire();
  }
})();
