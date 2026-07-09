(function () {
  "use strict";

  function initReadingProgress() {
    var bar = document.querySelector(".reading-progress");
    if (!bar) return;
    function update() {
      var doc = document.documentElement;
      var h = doc.scrollHeight - window.innerHeight;
      bar.style.width = (h > 0 ? (window.scrollY / h) * 100 : 0) + "%";
    }
    window.addEventListener("scroll", update, { passive: true });
    update();
  }

  function initFaq() {
    document.querySelectorAll(".faq-q").forEach(function (btn) {
      btn.addEventListener("click", function () {
        var item = btn.closest(".faq-item");
        var open = item.classList.contains("open");
        document.querySelectorAll(".faq-item.open").forEach(function (el) {
          el.classList.remove("open");
          el.querySelector(".faq-q").setAttribute("aria-expanded", "false");
        });
        if (!open) {
          item.classList.add("open");
          btn.setAttribute("aria-expanded", "true");
        }
      });
    });
  }

  function initBackTop() {
    var btn = document.getElementById("back-top");
    if (!btn) return;
    window.addEventListener("scroll", function () {
      btn.classList.toggle("visible", window.scrollY > 320);
    }, { passive: true });
    btn.addEventListener("click", function () {
      window.scrollTo({ top: 0, behavior: "smooth" });
    });
  }

  document.addEventListener("partials:ready", function () {
    initReadingProgress();
    initFaq();
    initBackTop();
  });
  if (document.readyState !== "loading") {
    initReadingProgress();
    initFaq();
    initBackTop();
  }
})();
