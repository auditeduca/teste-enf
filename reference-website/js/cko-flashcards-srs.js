(function () {
  "use strict";

  var ROOT_SEL = "[data-cko-flashcards]";
  var DECK_URL = "/data/flashcards-deck.json";

  function $(sel, root) {
    return (root || document).querySelector(sel);
  }

  function $$(sel, root) {
    return Array.prototype.slice.call((root || document).querySelectorAll(sel));
  }

  function formatDays(days) {
    if (days < 1) return "< 1 d";
    if (days >= 30) return Math.round(days / 30) + " m";
    return days + " d";
  }

  function createSrs() {
    return {
      reps: 0,
      interval: 0,
      ease: 2.5,
      nextReview: Date.now()
    };
  }

  function CkoFlashcards(root) {
    this.root = root;
    this.categories = {};
    this.baseCards = [];
    this.deck = [];
    this.reviewQueue = [];
    this.currentCard = null;
    this.isFlipped = false;
    this.storageKey = "cko-flashcards-srs-v1";
    this.activeCats = new Set();
    this.synth = window.speechSynthesis || null;
    this.touchStartX = 0;
    this.ratingLock = false;
  }

  CkoFlashcards.prototype.init = function () {
    var self = this;
    fetch(DECK_URL, { credentials: "same-origin" })
      .then(function (res) {
        if (!res.ok) throw new Error("Deck HTTP " + res.status);
        return res.json();
      })
      .then(function (data) {
        self.storageKey = data.storageKey || self.storageKey;
        self.categories = data.categories || {};
        self.baseCards = data.cards || [];
        self.mergeProgress();
        self.renderFilters();
        self.bindUi();
        self.showView("dashboard");
        self.updateDashboard();
      })
      .catch(function () {
        self.toast("Não foi possível carregar o deck de flashcards.");
      });
  };

  CkoFlashcards.prototype.mergeProgress = function () {
    var saved = null;
    try {
      saved = JSON.parse(localStorage.getItem(this.storageKey) || "null");
    } catch (e) {
      saved = null;
    }

    var map = {};
    if (Array.isArray(saved)) {
      saved.forEach(function (c) {
        if (c && c.id) map[c.id] = c.srs;
      });
    }

    this.deck = this.baseCards.map(function (card) {
      return {
        id: card.id,
        cat: card.cat,
        q: card.q,
        a: card.a,
        sub: card.sub || "",
        srs: map[card.id] ? Object.assign(createSrs(), map[card.id]) : createSrs()
      };
    });

    this.save();
  };

  CkoFlashcards.prototype.save = function () {
    var payload = this.deck.map(function (c) {
      return { id: c.id, srs: c.srs };
    });
    try {
      localStorage.setItem(this.storageKey, JSON.stringify(payload));
    } catch (e) {
      /* ignore quota */
    }
  };

  CkoFlashcards.prototype.filteredDeck = function () {
    var cats = this.activeCats;
    if (!cats.size) return this.deck.slice();
    return this.deck.filter(function (c) {
      return cats.has(c.cat);
    });
  };

  CkoFlashcards.prototype.renderFilters = function () {
    var wrap = $("[data-fc-filters]", this.root);
    if (!wrap) return;
    var self = this;
    var html = '<button type="button" class="cko-fc__chip is-active" data-cat="all">Todos</button>';
    Object.keys(this.categories).forEach(function (key) {
      html +=
        '<button type="button" class="cko-fc__chip" data-cat="' +
        key +
        '">' +
        self.categories[key] +
        "</button>";
    });
    wrap.innerHTML = html;
  };

  CkoFlashcards.prototype.bindUi = function () {
    var self = this;
    var startBtn = $("[data-fc-start]", this.root);
    var resetBtn = $("[data-fc-reset]", this.root);
    var homeBtn = $("[data-fc-home]", this.root);
    var speakBtn = $("[data-fc-speak]", this.root);
    var cardInner = $("[data-fc-inner]", this.root);
    var filters = $("[data-fc-filters]", this.root);

    if (startBtn) startBtn.addEventListener("click", function () { self.startStudy(); });
    if (resetBtn) resetBtn.addEventListener("click", function () { self.resetData(); });
    if (homeBtn) homeBtn.addEventListener("click", function () { self.showView("dashboard"); });
    if (speakBtn) speakBtn.addEventListener("click", function () { self.readAloud(); });
    if (cardInner) cardInner.addEventListener("click", function () { self.flipCard(); });

    $$("[data-fc-rate]", this.root).forEach(function (btn) {
      btn.addEventListener("click", function () {
        self.rateCard(Number(btn.getAttribute("data-fc-rate")));
      });
    });

    if (filters) {
      filters.addEventListener("click", function (ev) {
        var btn = ev.target.closest("[data-cat]");
        if (!btn) return;
        var cat = btn.getAttribute("data-cat");
        if (cat === "all") {
          self.activeCats.clear();
          $$(".cko-fc__chip", filters).forEach(function (el) {
            el.classList.toggle("is-active", el.getAttribute("data-cat") === "all");
          });
        } else {
          if (self.activeCats.has(cat)) self.activeCats.delete(cat);
          else self.activeCats.add(cat);
          $$(".cko-fc__chip", filters).forEach(function (el) {
            var c = el.getAttribute("data-cat");
            if (c === "all") el.classList.toggle("is-active", self.activeCats.size === 0);
            else el.classList.toggle("is-active", self.activeCats.has(c));
          });
        }
        self.updateDashboard();
      });
    }

    this.setupTouch();
    this.setupKeyboard();
  };

  CkoFlashcards.prototype.showView = function (name) {
    $$("[data-fc-view]", this.root).forEach(function (el) {
      el.classList.toggle("is-active", el.getAttribute("data-fc-view") === name);
    });
    if (name === "dashboard") this.updateDashboard();
  };

  CkoFlashcards.prototype.updateDashboard = function () {
    var now = Date.now();
    var due = 0;
    this.filteredDeck().forEach(function (c) {
      if (c.srs.nextReview <= now) due++;
    });

    var startBtn = $("[data-fc-start]", this.root);
    if (startBtn) {
      if (due === 0) {
        startBtn.textContent = "Tudo revisado por hoje";
      } else {
        startBtn.textContent = "Iniciar revisão (" + due + ")";
      }
    }
  };

  CkoFlashcards.prototype.startStudy = function () {
    var now = Date.now();
    this.reviewQueue = this.filteredDeck()
      .filter(function (c) { return c.srs.nextReview <= now; })
      .sort(function (a, b) { return a.srs.nextReview - b.srs.nextReview; });

    if (!this.reviewQueue.length) {
      this.toast("Você já revisou todas as cartas selecionadas.");
      return;
    }

    this.showView("study");
    this.loadNextCard();
  };

  CkoFlashcards.prototype.loadNextCard = function () {
    var stage = $("[data-fc-stage]", this.root);
    var inner = $("[data-fc-inner]", this.root);
    var srs = $("[data-fc-srs]", this.root);

    if (!this.reviewQueue.length) {
      this.toast("Sessão finalizada!");
      this.showView("dashboard");
      return;
    }

    this.ratingLock = false;
    this.currentCard = this.reviewQueue[0];
    this.isFlipped = false;

    if (stage) stage.classList.remove("is-out-left", "is-out-right");
    if (inner) {
      inner.style.transform = "";
      inner.classList.remove("is-flipped");
    }
    if (srs) srs.classList.remove("is-visible");

    var catLabel = this.categories[this.currentCard.cat] || this.currentCard.cat;
    var catEl = $("[data-fc-cat]", this.root);
    var qEl = $("[data-fc-q]", this.root);
    var aEl = $("[data-fc-a]", this.root);
    var subEl = $("[data-fc-sub]", this.root);
    var leftEl = $("[data-fc-left]", this.root);

    if (catEl) catEl.textContent = catLabel;
    if (qEl) qEl.textContent = this.currentCard.q;
    if (aEl) aEl.textContent = this.currentCard.a;
    if (subEl) subEl.textContent = this.currentCard.sub || "";
    if (leftEl) leftEl.textContent = String(this.reviewQueue.length);

    this.updateRateLabels();
  };

  CkoFlashcards.prototype.flipCard = function () {
    if (this.isFlipped || !this.currentCard) return;
    this.isFlipped = true;
    var inner = $("[data-fc-inner]", this.root);
    var srs = $("[data-fc-srs]", this.root);
    if (inner) inner.classList.add("is-flipped");
    if (srs) srs.classList.add("is-visible");
  };

  CkoFlashcards.prototype.updateRateLabels = function () {
    var srs = this.currentCard.srs;
    var intHard = srs.reps > 0 ? Math.round(srs.interval * 1.2) || 1 : 1;
    var intGood = srs.reps === 0 ? 1 : srs.reps === 1 ? 6 : Math.round(srs.interval * srs.ease) || 1;
    var intEasy = srs.reps === 0 ? 4 : Math.round(srs.interval * srs.ease * 1.3) || 1;

    var hard = $("[data-fc-time-hard]", this.root);
    var good = $("[data-fc-time-good]", this.root);
    var easy = $("[data-fc-time-easy]", this.root);
    if (hard) hard.textContent = formatDays(intHard);
    if (good) good.textContent = formatDays(intGood);
    if (easy) easy.textContent = formatDays(intEasy);
  };

  CkoFlashcards.prototype.rateCard = function (quality) {
    if (!this.isFlipped || !this.currentCard || this.ratingLock) return;
    this.ratingLock = true;

    var srs = this.currentCard.srs;

    if (quality === 1) {
      srs.reps = 0;
      srs.interval = 0;
      srs.ease = Math.max(1.3, srs.ease - 0.2);
    } else {
      if (srs.reps === 0) srs.interval = quality === 4 ? 4 : 1;
      else if (srs.reps === 1) srs.interval = 6;
      else {
        var multiplier = quality === 2 ? 1.2 : quality === 4 ? srs.ease * 1.3 : srs.ease;
        srs.interval = Math.round(srs.interval * multiplier) || 1;
      }
      srs.reps++;
      if (quality === 2) srs.ease = Math.max(1.3, srs.ease - 0.15);
      if (quality === 4) srs.ease += 0.15;
    }

    var delay = quality === 1 ? 60 * 1000 : srs.interval * 24 * 60 * 60 * 1000;
    srs.nextReview = Date.now() + delay;
    this.save();

    var stage = $("[data-fc-stage]", this.root);
    if (stage) {
      stage.classList.add(quality <= 2 ? "is-out-left" : "is-out-right");
    }

    this.reviewQueue.shift();
    if (quality === 1) this.reviewQueue.push(this.currentCard);

    var self = this;
    setTimeout(function () {
      self.loadNextCard();
    }, 380);
  };

  CkoFlashcards.prototype.setupTouch = function () {
    var stage = $("[data-fc-stage]", this.root);
    if (!stage) return;
    var self = this;

    stage.addEventListener(
      "touchstart",
      function (e) {
        self.touchStartX = e.changedTouches[0].screenX;
      },
      { passive: true }
    );

    stage.addEventListener(
      "touchend",
      function (e) {
        if (!self.isFlipped) return;
        var diff = e.changedTouches[0].screenX - self.touchStartX;
        if (diff < -80) self.rateCard(1);
        else if (diff > 80) self.rateCard(3);
      },
      { passive: true }
    );
  };

  CkoFlashcards.prototype.setupKeyboard = function () {
    var self = this;
    document.addEventListener("keydown", function (e) {
      var study = $('[data-fc-view="study"]', self.root);
      if (!study || !study.classList.contains("is-active")) return;
      if (e.code === "Space" || e.code === "Enter") {
        e.preventDefault();
        self.flipCard();
      }
      if (!self.isFlipped) return;
      if (e.key === "1") self.rateCard(1);
      if (e.key === "2") self.rateCard(2);
      if (e.key === "3") self.rateCard(3);
      if (e.key === "4") self.rateCard(4);
    });
  };

  CkoFlashcards.prototype.readAloud = function () {
    if (!this.synth || !this.currentCard) return;
    this.synth.cancel();
    var text = this.isFlipped
      ? "Resposta: " + this.currentCard.a + ". " + (this.currentCard.sub || "")
      : "Pergunta: " + this.currentCard.q;
    var utter = new SpeechSynthesisUtterance(text);
    utter.lang = "pt-BR";
    utter.rate = 1.05;
    this.synth.speak(utter);
  };

  CkoFlashcards.prototype.resetData = function () {
    if (!window.confirm("Apagar todo o progresso deste deck?")) return;
    try {
      localStorage.removeItem(this.storageKey);
    } catch (e) {
      /* ignore */
    }
    this.mergeProgress();
    this.updateDashboard();
    this.toast("Progresso reiniciado.");
  };

  CkoFlashcards.prototype.toast = function (msg) {
    var el = $("[data-fc-toast]", this.root) || document.querySelector("[data-fc-toast]");
    if (!el) return;
    el.textContent = msg;
    el.classList.add("is-show");
    clearTimeout(this._toastTimer);
    this._toastTimer = setTimeout(function () {
      el.classList.remove("is-show");
    }, 2800);
  };

  document.addEventListener("DOMContentLoaded", function () {
    var root = document.querySelector(ROOT_SEL);
    if (!root) return;
    var app = new CkoFlashcards(root);
    app.init();
    window.ckoFlashcards = app;
  });
})();
