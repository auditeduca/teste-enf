(function () {
  "use strict";

  var DECK_URL = "/data/quiz-deck.json";
  var LETTERS = ["A", "B", "C", "D"];
  var RELATED = [
    { label: "Flashcards SRS", href: "/flashcards-srs.html" },
    { label: "Carrinho de Emergência", href: "/biblioteca-carinho-de-emergencia.html" },
    { label: "Mapa do site", href: "/mapa-do-site.html" }
  ];

  function $(sel, root) {
    return (root || document).querySelector(sel);
  }

  function $$(sel, root) {
    return Array.prototype.slice.call((root || document).querySelectorAll(sel));
  }

  function shuffle(arr) {
    var a = arr.slice();
    for (var i = a.length - 1; i > 0; i--) {
      var j = Math.floor(Math.random() * (i + 1));
      var t = a[i];
      a[i] = a[j];
      a[j] = t;
    }
    return a;
  }

  function CkoQuiz(root) {
    this.root = root;
    this.data = null;
    this.step = 1;
    this.area = "all";
    this.diff = "all";
    this.qty = 10;
    this.deck = [];
    this.answers = [];
    this.index = 0;
    this.flipped = false;
    this.paused = false;
    this.soundOn = true;
    this.seconds = 0;
    this.timer = null;
    this.resourcesOpen = false;
    this.synth = window.speechSynthesis || null;
    this.audioCtx = null;
    this.icon = "/iconpages-calculadoras-de-enfermagem.webp";
  }

  CkoQuiz.prototype.init = function () {
    var self = this;
    fetch(DECK_URL, { credentials: "same-origin" })
      .then(function (r) {
        if (!r.ok) throw new Error("deck");
        return r.json();
      })
      .then(function (data) {
        self.data = data;
        self.icon = data.icon || self.icon;
        self.bind();
        self.renderSetup();
        self.showView("setup");
        self.goStep(1);
      })
      .catch(function () {
        self.toast("Não foi possível carregar o quiz.", "bad");
      });
  };

  CkoQuiz.prototype.bind = function () {
    var self = this;
    var next = $("[data-q-next]", this.root);
    var back = $("[data-q-back]", this.root);
    var start = $("[data-q-start]", this.root);
    var qty = $("[data-q-qty]", this.root);

    if (next) next.addEventListener("click", function () { self.nextStep(); });
    if (back) back.addEventListener("click", function () { self.prevStep(); });
    if (start) start.addEventListener("click", function () { self.startSession(); });
    if (qty) {
      qty.addEventListener("change", function () {
        self.qty = Math.max(3, Math.min(30, parseInt(qty.value, 10) || 10));
        qty.value = String(self.qty);
      });
    }

    $$("[data-q-tool]", this.root).forEach(function (btn) {
      btn.addEventListener("click", function () {
        var action = btn.getAttribute("data-q-tool");
        if (action === "speak") self.speak();
        if (action === "pause") self.togglePause(btn);
        if (action === "sound") self.toggleSound(btn);
        if (action === "help") self.openResources();
        if (action === "exit") self.exitSession();
      });
    });

    var flip = $("[data-q-flip]", this.root);
    if (flip) {
      flip.addEventListener("click", function (e) {
        if (e.target.closest("[data-q-opt]") || e.target.closest("[data-q-face-action]")) return;
        self.toggleFlip();
      });
    }

    var closeRes = $("[data-q-close-res]", this.root);
    if (closeRes) closeRes.addEventListener("click", function () { self.closeResources(); });

    var openRes = $("[data-q-open-res]", this.root);
    if (openRes) openRes.addEventListener("click", function () { self.openResources(true); });

    var nextQ = $("[data-q-next-q]", this.root);
    if (nextQ) nextQ.addEventListener("click", function () { self.nextQuestion(); });

    var restart = $("[data-q-restart]", this.root);
    if (restart) restart.addEventListener("click", function () { self.resetToSetup(); });
  };

  CkoQuiz.prototype.showView = function (name) {
    $$("[data-q-view]", this.root).forEach(function (el) {
      el.classList.toggle("is-active", el.getAttribute("data-q-view") === name);
    });
  };

  CkoQuiz.prototype.goStep = function (n) {
    this.step = n;
    $$("[data-q-step-panel]", this.root).forEach(function (el) {
      el.hidden = Number(el.getAttribute("data-q-step-panel")) !== n;
    });
    $$("[data-q-step-dot]", this.root).forEach(function (el) {
      var s = Number(el.getAttribute("data-q-step-dot"));
      el.classList.toggle("is-active", s === n);
      el.classList.toggle("is-done", s < n);
    });
    var next = $("[data-q-next]", this.root);
    var start = $("[data-q-start]", this.root);
    var back = $("[data-q-back]", this.root);
    if (back) back.hidden = n === 1;
    if (next) next.hidden = n === 3;
    if (start) start.hidden = n !== 3;
  };

  CkoQuiz.prototype.nextStep = function () {
    if (this.step === 1 && !this.area) {
      this.toast("Selecione uma área de conhecimento.", "bad");
      return;
    }
    if (this.step === 2 && !this.diff) {
      this.toast("Selecione a dificuldade.", "bad");
      return;
    }
    if (this.step < 3) this.goStep(this.step + 1);
  };

  CkoQuiz.prototype.prevStep = function () {
    if (this.step > 1) this.goStep(this.step - 1);
  };

  CkoQuiz.prototype.renderSetup = function () {
    var self = this;
    var areaBox = $("[data-q-areas]", this.root);
    var diffBox = $("[data-q-diffs]", this.root);
    if (!areaBox || !this.data) return;

    var cats = this.data.categories || {};
    var html =
      '<button type="button" class="cko-quiz__choice is-selected" data-area="all">Todas as áreas</button>';
    Object.keys(cats).forEach(function (key) {
      html +=
        '<button type="button" class="cko-quiz__choice" data-area="' +
        key +
        '">' +
        cats[key].label +
        "</button>";
    });
    areaBox.innerHTML = html;
    areaBox.onclick = function (e) {
      var btn = e.target.closest("[data-area]");
      if (!btn) return;
      self.area = btn.getAttribute("data-area");
      $$("[data-area]", areaBox).forEach(function (el) {
        el.classList.toggle("is-selected", el === btn);
      });
    };

    var diffs = this.data.difficulties || {};
    var dhtml =
      '<button type="button" class="cko-quiz__choice is-selected" data-diff="all">Todas</button>';
    Object.keys(diffs).forEach(function (key) {
      dhtml +=
        '<button type="button" class="cko-quiz__choice" data-diff="' +
        key +
        '">' +
        diffs[key] +
        "</button>";
    });
    diffBox.innerHTML = dhtml;
    diffBox.onclick = function (e) {
      var btn = e.target.closest("[data-diff]");
      if (!btn) return;
      self.diff = btn.getAttribute("data-diff");
      $$("[data-diff]", diffBox).forEach(function (el) {
        el.classList.toggle("is-selected", el === btn);
      });
    };

    $$("img[data-q-icon]", this.root).forEach(function (img) {
      img.src = self.icon;
    });
  };

  CkoQuiz.prototype.startSession = function () {
    var pool = (this.data.questions || []).filter(function (q) {
      if (this.area !== "all" && q.cat !== this.area) return false;
      if (this.diff !== "all" && q.diff !== this.diff) return false;
      return true;
    }, this);

    if (!pool.length) {
      this.toast("Nenhuma questão para esses filtros.", "bad");
      return;
    }

    var qty = Math.max(3, Math.min(30, this.qty || 10));
    if (pool.length < qty) qty = pool.length;
    this.deck = shuffle(pool).slice(0, qty);
    this.answers = new Array(this.deck.length).fill(null);
    this.index = 0;
    this.flipped = false;
    this.paused = false;
    this.resourcesOpen = false;
    this.seconds = 0;
    this.showView("session");
    this.startTimer();
    this.renderMinis();
    this.loadQuestion();
    this.closeResources();
    this.updateScore();
  };

  CkoQuiz.prototype.startTimer = function () {
    var self = this;
    if (this.timer) clearInterval(this.timer);
    this.timer = setInterval(function () {
      if (self.paused) return;
      self.seconds++;
      var el = $("[data-q-timer]", self.root);
      if (!el) return;
      var m = Math.floor(self.seconds / 60);
      var s = self.seconds % 60;
      el.textContent =
        String(m).padStart(2, "0") + ":" + String(s).padStart(2, "0");
    }, 1000);
  };

  CkoQuiz.prototype.togglePause = function (btn) {
    this.paused = !this.paused;
    if (btn) btn.classList.toggle("is-on", this.paused);
    if (this.paused && this.synth) this.synth.cancel();
    this.toast(this.paused ? "Quiz pausado." : "Quiz retomado.");
  };

  CkoQuiz.prototype.toggleSound = function (btn) {
    this.soundOn = !this.soundOn;
    if (btn) btn.classList.toggle("is-on", this.soundOn);
    this.toast(this.soundOn ? "Sons ativados." : "Sons desativados.");
  };

  CkoQuiz.prototype.beep = function (ok) {
    if (!this.soundOn) return;
    try {
      var Ctx = window.AudioContext || window.webkitAudioContext;
      if (!Ctx) return;
      if (!this.audioCtx) this.audioCtx = new Ctx();
      var ctx = this.audioCtx;
      var o = ctx.createOscillator();
      var g = ctx.createGain();
      o.type = "sine";
      o.frequency.value = ok ? 880 : 220;
      g.gain.value = 0.04;
      o.connect(g);
      g.connect(ctx.destination);
      o.start();
      setTimeout(function () {
        o.stop();
      }, ok ? 140 : 220);
    } catch (e) {
      /* ignore */
    }
  };

  CkoQuiz.prototype.speak = function () {
    if (!this.synth || !this.deck.length) return;
    this.synth.cancel();
    var q = this.deck[this.index];
    var text = this.flipped
      ? "Resposta: " + q.opts[q.ans] + ". " + (q.interpretation || "")
      : "Pergunta: " + q.q;
    var u = new SpeechSynthesisUtterance(text);
    u.lang = "pt-BR";
    u.rate = 1.05;
    this.synth.speak(u);
  };

  CkoQuiz.prototype.renderMinis = function () {
    var wrap = $("[data-q-minis]", this.root);
    if (!wrap) return;
    var self = this;
    wrap.innerHTML = "";
    this.deck.forEach(function (q, i) {
      var btn = document.createElement("button");
      btn.type = "button";
      btn.className = "cko-quiz__mini";
      if (i === self.index) btn.classList.add("is-current");
      if (self.answers[i] !== null) {
        btn.classList.add(self.answers[i] === q.ans ? "is-correct" : "is-wrong");
      }
      btn.innerHTML =
        '<img src="' +
        self.icon +
        '" alt="" width="18" height="18"/><b>' +
        (i + 1) +
        "</b>";
      btn.addEventListener("click", function () {
        self.index = i;
        self.loadQuestion();
      });
      wrap.appendChild(btn);
    });
  };

  CkoQuiz.prototype.updateScore = function () {
    var ok = 0;
    var bad = 0;
    var self = this;
    this.answers.forEach(function (a, i) {
      if (a === null) return;
      if (a === self.deck[i].ans) ok++;
      else bad++;
    });
    var cur = $("[data-q-score-cur]", this.root);
    var okEl = $("[data-q-score-ok]", this.root);
    var badEl = $("[data-q-score-bad]", this.root);
    if (cur) cur.textContent = this.index + 1 + "/" + this.deck.length;
    if (okEl) okEl.textContent = String(ok);
    if (badEl) badEl.textContent = String(bad);
  };

  CkoQuiz.prototype.loadQuestion = function () {
    var q = this.deck[this.index];
    var cat = (this.data.categories && this.data.categories[q.cat]) || {};
    var answered = this.answers[this.index] !== null;
    this.flipped = answered;

    var inner = $("[data-q-flip]", this.root);
    if (inner) inner.classList.toggle("is-flipped", this.flipped);

    var qEl = $("[data-q-text]", this.root);
    var catEl = $("[data-q-cat]", this.root);
    if (qEl) qEl.textContent = q.q;
    if (catEl) catEl.textContent = cat.label || q.cat;

    var opts = $("[data-q-opts]", this.root);
    if (opts) {
      opts.innerHTML = "";
      var self = this;
      q.opts.forEach(function (opt, i) {
        var btn = document.createElement("button");
        btn.type = "button";
        btn.className = "cko-quiz__opt";
        btn.setAttribute("data-q-opt", String(i));
        btn.innerHTML = "<strong>" + LETTERS[i] + ")</strong> " + opt;
        if (answered) {
          btn.disabled = true;
          if (i === q.ans) btn.classList.add("is-correct");
          if (i === self.answers[self.index] && i !== q.ans) btn.classList.add("is-wrong");
        } else {
          btn.addEventListener("click", function (e) {
            e.stopPropagation();
            self.answer(i);
          });
        }
        opts.appendChild(btn);
      });
    }

    var ansEl = $("[data-q-answer]", this.root);
    if (ansEl) ansEl.textContent = q.opts[q.ans];

    this.renderMinis();
    this.updateScore();
    if (answered) this.fillResources(true);
    else {
      this.closeResources();
      this.fillResources(false);
    }
  };

  CkoQuiz.prototype.toggleFlip = function () {
    this.flipped = !this.flipped;
    var inner = $("[data-q-flip]", this.root);
    if (inner) inner.classList.toggle("is-flipped", this.flipped);
  };

  CkoQuiz.prototype.answer = function (idx) {
    if (this.answers[this.index] !== null || this.paused) return;
    var q = this.deck[this.index];
    this.answers[this.index] = idx;
    var ok = idx === q.ans;
    this.beep(ok);
    this.toast(
      ok ? "Você acertou! Veja os recursos ao lado." : "Resposta incorreta. Confira o painel de dúvidas.",
      ok ? "ok" : "bad"
    );
    this.flipped = true;
    var inner = $("[data-q-flip]", this.root);
    if (inner) inner.classList.add("is-flipped");
    this.loadQuestion();
    this.openResources();
  };

  CkoQuiz.prototype.fillResources = function (answered) {
    var q = this.deck[this.index];
    if (!q) return;
    var cat = (this.data.categories && this.data.categories[q.cat]) || {};
    var banner = $("[data-q-banner]", this.root);
    var concept = $("[data-q-concept]", this.root);
    var normative = $("[data-q-normative]", this.root);
    var interpretation = $("[data-q-interpretation]", this.root);
    var related = $("[data-q-related]", this.root);
    var empty = $("[data-q-res-empty]", this.root);
    var body = $("[data-q-res-body]", this.root);

    if (concept) concept.textContent = cat.concept || "—";
    if (normative) normative.textContent = cat.normative || "—";
    if (interpretation) interpretation.textContent = q.interpretation || "—";

    if (related) {
      related.innerHTML = "";
      RELATED.forEach(function (link) {
        var a = document.createElement("a");
        a.href = link.href;
        a.textContent = link.label;
        related.appendChild(a);
      });
    }

    if (!answered) {
      if (banner) {
        banner.hidden = true;
        banner.className = "cko-quiz__banner";
        banner.textContent = "";
      }
      if (empty) empty.hidden = this.resourcesOpen;
      if (body) body.hidden = !this.resourcesOpen;
      return;
    }

    var ok = this.answers[this.index] === q.ans;
    if (banner) {
      banner.hidden = false;
      banner.className = "cko-quiz__banner " + (ok ? "cko-quiz__banner--ok" : "cko-quiz__banner--bad");
      banner.textContent = ok
        ? "Você acertou! Acesse os recursos relacionados abaixo."
        : "Resposta incorreta. Revise conceito, normativo e interpretação.";
    }
    if (empty) empty.hidden = true;
    if (body) body.hidden = false;
  };

  CkoQuiz.prototype.openResources = function () {
    this.resourcesOpen = true;
    var panel = $("[data-q-resources]", this.root);
    if (panel) panel.classList.remove("is-closed");
    this.fillResources(this.answers[this.index] !== null);
    var empty = $("[data-q-res-empty]", this.root);
    var body = $("[data-q-res-body]", this.root);
    if (empty) empty.hidden = true;
    if (body) body.hidden = false;
  };

  CkoQuiz.prototype.closeResources = function () {
    this.resourcesOpen = false;
    var panel = $("[data-q-resources]", this.root);
    if (panel) panel.classList.add("is-closed");
    var empty = $("[data-q-res-empty]", this.root);
    var body = $("[data-q-res-body]", this.root);
    if (this.answers[this.index] === null) {
      if (empty) empty.hidden = false;
      if (body) body.hidden = true;
    }
  };

  CkoQuiz.prototype.nextQuestion = function () {
    if (this.index < this.deck.length - 1) {
      this.index++;
      this.loadQuestion();
      return;
    }
    this.finish();
  };

  CkoQuiz.prototype.finish = function () {
    if (this.timer) clearInterval(this.timer);
    if (this.synth) this.synth.cancel();
    var ok = 0;
    var self = this;
    this.answers.forEach(function (a, i) {
      if (a === self.deck[i].ans) ok++;
    });
    var bad = this.deck.length - ok;
    var pct = Math.round((ok / this.deck.length) * 100);
    var okEl = $("[data-q-result-ok]", this.root);
    var badEl = $("[data-q-result-bad]", this.root);
    var pctEl = $("[data-q-result-pct]", this.root);
    if (okEl) okEl.textContent = String(ok);
    if (badEl) badEl.textContent = String(bad);
    if (pctEl) pctEl.textContent = pct + "%";
    this.showView("result");
    this.beep(pct >= 70);
    this.toast("Quiz finalizado: " + pct + "% de aproveitamento.", pct >= 70 ? "ok" : "bad");
  };

  CkoQuiz.prototype.exitSession = function () {
    if (!window.confirm("Encerrar o quiz atual e voltar à seleção?")) return;
    this.resetToSetup();
  };

  CkoQuiz.prototype.resetToSetup = function () {
    if (this.timer) clearInterval(this.timer);
    if (this.synth) this.synth.cancel();
    this.deck = [];
    this.answers = [];
    this.index = 0;
    this.showView("setup");
    this.goStep(1);
  };

  CkoQuiz.prototype.toast = function (msg, kind) {
    var el = $("[data-q-toast]") || document.querySelector("[data-q-toast]");
    if (!el) return;
    el.textContent = msg;
    el.classList.remove("is-ok", "is-bad");
    if (kind === "ok") el.classList.add("is-ok");
    if (kind === "bad") el.classList.add("is-bad");
    el.classList.add("is-show");
    clearTimeout(this._toastTimer);
    this._toastTimer = setTimeout(function () {
      el.classList.remove("is-show");
    }, 2800);
  };

  document.addEventListener("DOMContentLoaded", function () {
    var root = document.querySelector("[data-cko-quiz]");
    if (!root) return;
    var app = new CkoQuiz(root);
    app.init();
    window.ckoQuiz = app;
  });
})();
