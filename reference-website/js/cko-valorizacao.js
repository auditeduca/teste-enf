(function () {
  "use strict";

  var ICON_URL = "/iconpages-calculadoras-de-enfermagem.webp";
  var W = 1080;
  var H = 1350;

  var TEMPLATES = {
    formatura: {
      eyebrow: "FORMAÇÃO EM ENFERMAGEM",
      headline: "FORMADO(A)!",
      body: function (nome, meta) {
        return (
          "Tenho orgulho de compartilhar: " +
          nome +
          " concluiu a formação em Enfermagem" +
          (meta ? " — " + meta : "") +
          ". Um marco de dedicação ao cuidado e à ciência do cuidar."
        );
      },
      badge: "ENFERMAGEM",
      badgeSub: "FORMAÇÃO"
    },
    coren: {
      eyebrow: "REGISTRO PROFISSIONAL",
      headline: "INSCRITO(A)!",
      body: function (nome, meta) {
        return (
          "Compartilho com alegria: " +
          nome +
          " está com o registro profissional ativo" +
          (meta ? " (" + meta + ")" : "") +
          ". Pronto(a) para exercer a enfermagem com ética e responsabilidade."
        );
      },
      badge: "COREN",
      badgeSub: "ATIVO"
    },
    especializacao: {
      eyebrow: "QUALIFICAÇÃO PROFISSIONAL",
      headline: "ESPECIALISTA!",
      body: function (nome, meta) {
        return (
          "Celebrando a conquista de " +
          nome +
          ": especialização concluída" +
          (meta ? " em " + meta : "") +
          ". Mais conhecimento a serviço do paciente e da equipe."
        );
      },
      badge: "ESPECIALISTA",
      badgeSub: "ENFERMAGEM"
    },
    concurso: {
      eyebrow: "CONCURSO / SELEÇÃO",
      headline: "APROVADO(A)!",
      body: function (nome, meta) {
        return (
          "Tenho a alegria de anunciar: " +
          nome +
          " foi aprovado(a)" +
          (meta ? " — " + meta : "") +
          ". Persistência e estudo fazendo a diferença na carreira de enfermagem."
        );
      },
      badge: "APROVADO",
      badgeSub: "ENFERMAGEM"
    },
    certificacao: {
      eyebrow: "CERTIFICAÇÃO",
      headline: "CERTIFICADO(A)!",
      body: function (nome, meta) {
        return (
          nome +
          " concluiu com sucesso a certificação" +
          (meta ? " " + meta : "") +
          ". Valorizar a enfermagem também é investir em competência e segurança do paciente."
        );
      },
      badge: "CERTIFICADO",
      badgeSub: "CKO"
    },
    marco: {
      eyebrow: "VALORIZAÇÃO PROFISSIONAL",
      headline: "ORGULHO!",
      body: function (nome, meta) {
        return (
          "Celebramos " +
          nome +
          (meta ? ": " + meta : " e sua trajetória na enfermagem") +
          ". Cuidar é ciência, ética e presença — e merece ser reconhecido."
        );
      },
      badge: "ENFERMAGEM",
      badgeSub: "VALOR"
    }
  };

  function $(sel, root) {
    return (root || document).querySelector(sel);
  }

  function wrapText(ctx, text, x, y, maxWidth, lineHeight) {
    var words = text.split(" ");
    var line = "";
    var yy = y;
    for (var n = 0; n < words.length; n++) {
      var test = line + words[n] + " ";
      if (ctx.measureText(test).width > maxWidth && n > 0) {
        ctx.fillText(line.trim(), x, yy);
        line = words[n] + " ";
        yy += lineHeight;
      } else {
        line = test;
      }
    }
    ctx.fillText(line.trim(), x, yy);
    return yy;
  }

  function loadImage(src) {
    return new Promise(function (resolve) {
      var img = new Image();
      img.crossOrigin = "anonymous";
      img.onload = function () {
        resolve(img);
      };
      img.onerror = function () {
        resolve(null);
      };
      img.src = src;
    });
  }

  function ValorizacaoApp(root) {
    this.root = root;
    this.canvas = $("[data-vp-canvas]", root) || document.createElement("canvas");
    this.ctx = this.canvas.getContext("2d");
    this.icon = null;
    this.lastUrl = "";
  }

  ValorizacaoApp.prototype.init = function () {
    var self = this;
    loadImage(ICON_URL).then(function (img) {
      self.icon = img;
    });

    var gen = $("[data-vp-generate]", this.root);
    var dl = $("[data-vp-download]", this.root);
    var type = $("[data-vp-type]", this.root);

    if (gen) gen.addEventListener("click", function () { self.generate(); });
    if (type) {
      type.addEventListener("change", function () {
        self.syncMetaPlaceholder();
      });
      this.syncMetaPlaceholder();
    }
    if (dl) {
      dl.addEventListener("click", function () {
        if (!self.lastUrl) return;
      });
    }
  };

  ValorizacaoApp.prototype.syncMetaPlaceholder = function () {
    var type = ($("[data-vp-type]", this.root) || {}).value || "marco";
    var meta = $("[data-vp-meta]", this.root);
    if (!meta) return;
    var map = {
      formatura: "Ex.: Turma 2026 · Universidade X",
      coren: "Ex.: COREN-SP",
      especializacao: "Ex.: UTI / Enfermagem Obstétrica",
      concurso: "Ex.: Prefeitura · Enfermeiro 2026",
      certificacao: "Ex.: BLS · ACLS · Protocolo X",
      marco: "Ex.: 10 anos de profissão"
    };
    meta.placeholder = map[type] || map.marco;
  };

  ValorizacaoApp.prototype.toast = function (msg) {
    var el = $("[data-vp-toast]") || document.querySelector("[data-vp-toast]");
    if (!el) return;
    el.textContent = msg;
    el.classList.add("is-show");
    clearTimeout(this._t);
    this._t = setTimeout(function () {
      el.classList.remove("is-show");
    }, 2600);
  };

  ValorizacaoApp.prototype.generate = function () {
    var self = this;
    var run = function () {
      var nome = (($("[data-vp-name]", self.root) || {}).value || "").trim();
      var type = ($("[data-vp-type]", self.root) || {}).value || "marco";
      var meta = (($("[data-vp-meta]", self.root) || {}).value || "").trim();
      var theme = ($("[data-vp-theme]", self.root) || {}).value || "dark";
      var custom = (($("[data-vp-custom]", self.root) || {}).value || "").trim();
      var tpl = TEMPLATES[type] || TEMPLATES.marco;

      if (!nome) {
        self.toast("Digite o nome para gerar o banner.");
        return;
      }

      self.canvas.width = W;
      self.canvas.height = H;
      var ctx = self.ctx;
      var dark = theme === "dark";

      self.drawBackground(ctx, dark);
      self.drawConfetti(ctx, dark);
      self.drawContent(ctx, dark, nome, tpl, meta, custom);
      self.drawBadge(ctx, tpl);
      if (self.icon) self.drawLogo(ctx, dark);

      var url = self.canvas.toDataURL("image/png");
      self.lastUrl = url;
      var frame = $("[data-vp-frame]", self.root);
      if (frame) {
        frame.innerHTML =
          '<img src="' + url + '" alt="Pré-visualização do banner de valorização profissional">';
      }
      var dl = $("[data-vp-download]", self.root);
      if (dl) {
        dl.hidden = false;
        dl.href = url;
        var safe = nome.replace(/[^\w\u00C0-\u024f\-]+/g, "_").slice(0, 40);
        dl.setAttribute("download", "valorizacao-" + safe + ".png");
      }
      self.toast("Banner gerado. Você já pode baixar.");
    };

    if (document.fonts && document.fonts.ready) {
      document.fonts.ready.then(run).catch(run);
    } else {
      run();
    }
  };

  ValorizacaoApp.prototype.drawBackground = function (ctx, dark) {
    if (dark) {
      var g = ctx.createLinearGradient(0, 0, W, H);
      g.addColorStop(0, "#1A3E74");
      g.addColorStop(0.55, "#1E4D8C");
      g.addColorStop(1, "#122a4f");
      ctx.fillStyle = g;
      ctx.fillRect(0, 0, W, H);

      ctx.save();
      ctx.strokeStyle = "rgba(255,255,255,0.06)";
      ctx.lineWidth = 140;
      ctx.beginPath();
      ctx.moveTo(-80, H * 0.18);
      ctx.lineTo(W + 80, H * 0.78);
      ctx.stroke();
      ctx.restore();

      ctx.fillStyle = "#ffffff";
      ctx.beginPath();
      ctx.moveTo(W, H);
      ctx.lineTo(W - 380, H);
      ctx.lineTo(W, H - 380);
      ctx.closePath();
      ctx.fill();

      ctx.fillStyle = "#3B82F6";
      ctx.beginPath();
      ctx.moveTo(W, H - 380);
      ctx.lineTo(W - 380, H);
      ctx.lineTo(W - 400, H);
      ctx.lineTo(W, H - 400);
      ctx.fill();
    } else {
      ctx.fillStyle = "#ffffff";
      ctx.fillRect(0, 0, W, H);

      ctx.save();
      ctx.strokeStyle = "rgba(26, 62, 116, 0.05)";
      ctx.lineWidth = 140;
      ctx.beginPath();
      ctx.moveTo(-80, H * 0.18);
      ctx.lineTo(W + 80, H * 0.78);
      ctx.stroke();
      ctx.restore();

      ctx.fillStyle = "#1A3E74";
      ctx.beginPath();
      ctx.moveTo(W, H);
      ctx.lineTo(W - 380, H);
      ctx.lineTo(W, H - 380);
      ctx.closePath();
      ctx.fill();

      ctx.fillStyle = "#3B82F6";
      ctx.beginPath();
      ctx.moveTo(W, H - 380);
      ctx.lineTo(W - 380, H);
      ctx.lineTo(W - 400, H);
      ctx.lineTo(W, H - 400);
      ctx.fill();
    }
  };

  ValorizacaoApp.prototype.drawConfetti = function (ctx, dark) {
    var colors = dark
      ? ["#93C5FD", "#BFDBFE", "#FFFFFF", "#60A5FA"]
      : ["#1A3E74", "#3B82F6", "#60A5FA", "#93C5FD"];
    ctx.save();
    for (var i = 0; i < 160; i++) {
      ctx.fillStyle = colors[Math.floor(Math.random() * colors.length)];
      ctx.globalAlpha = Math.random() * 0.45 + 0.25;
      var x = Math.random() * W;
      var y = Math.random() * H * 0.72;
      var size = Math.random() * 9 + 4;
      var rot = Math.random() * Math.PI;
      ctx.translate(x, y);
      ctx.rotate(rot);
      ctx.fillRect(0, 0, i % 2 === 0 ? size : size * 0.55, i % 2 === 0 ? size : size * 1.4);
      ctx.rotate(-rot);
      ctx.translate(-x, -y);
    }
    ctx.restore();
  };

  ValorizacaoApp.prototype.drawLogo = function (ctx, dark) {
    var size = 72;
    var x = 56;
    var y = 48;
    ctx.save();
    ctx.fillStyle = dark ? "rgba(255,255,255,0.12)" : "rgba(26,62,116,0.08)";
    ctx.beginPath();
    ctx.roundRect(x - 10, y - 10, size + 20, size + 20, 16);
    ctx.fill();
    ctx.drawImage(this.icon, x, y, size, size);
    ctx.restore();
  };

  ValorizacaoApp.prototype.drawContent = function (ctx, dark, nome, tpl, meta, custom) {
    var colorEyebrow = dark ? "#BFDBFE" : "#64748B";
    var colorTitle = dark ? "#FFFFFF" : "#1A3E74";
    var colorName = dark ? "#FFFFFF" : "#1A3E74";
    var colorBody = dark ? "#E2E8F0" : "#334155";
    var colorHash = dark ? "#94A3B8" : "#1A3E74";

    ctx.textAlign = "center";
    ctx.fillStyle = colorEyebrow;
    ctx.font = "700 32px Inter, Nunito Sans, sans-serif";
    ctx.fillText(tpl.eyebrow, W / 2, 170);

    ctx.fillStyle = colorTitle;
    ctx.font = "900 92px Nunito Sans, Inter, sans-serif";
    if (dark) {
      ctx.shadowColor = "rgba(0,0,0,0.28)";
      ctx.shadowBlur = 12;
      ctx.shadowOffsetY = 4;
    }
    ctx.fillText(tpl.headline, W / 2, 280);
    ctx.shadowColor = "transparent";
    ctx.shadowBlur = 0;
    ctx.shadowOffsetY = 0;

    var yName = 520;
    var nomeUpper = nome.toUpperCase();
    ctx.fillStyle = colorName;
    ctx.font = "900 78px Nunito Sans, Inter, sans-serif";
    if (nomeUpper.length > 18) {
      var words = nomeUpper.split(" ");
      var half = Math.ceil(words.length / 2) || 1;
      ctx.fillText(words.slice(0, half).join(" "), W / 2, yName - 48);
      ctx.fillText(words.slice(half).join(" "), W / 2, yName + 42);
      yName += 70;
    } else {
      ctx.fillText(nomeUpper, W / 2, yName);
    }

    var body = custom || tpl.body(nome, meta);
    ctx.fillStyle = colorBody;
    ctx.font = "500 34px Inter, Nunito Sans, sans-serif";
    wrapText(ctx, body, W / 2, yName + 120, 860, 48);

    ctx.textAlign = "left";
    ctx.fillStyle = colorHash;
    ctx.font = "italic 700 24px Inter, Nunito Sans, sans-serif";
    ctx.fillText("#Enfermagem #ValorizacaoProfissional", 56, H - 92);
    ctx.fillText("#Cuidado #COREN #CalculadorasDeEnfermagem", 56, H - 52);
  };

  ValorizacaoApp.prototype.drawBadge = function (ctx, tpl) {
    var cx = W - 170;
    var cy = H - 170;
    var r = 96;

    ctx.save();
    ctx.shadowColor = "rgba(0,0,0,0.35)";
    ctx.shadowBlur = 18;
    ctx.shadowOffsetY = 8;

    var grad = ctx.createLinearGradient(cx - r, cy - r, cx + r, cy + r);
    grad.addColorStop(0, "#60A5FA");
    grad.addColorStop(0.5, "#3B82F6");
    grad.addColorStop(1, "#1E4D8C");
    ctx.fillStyle = grad;
    ctx.beginPath();
    ctx.arc(cx, cy, r, 0, Math.PI * 2);
    ctx.fill();

    ctx.shadowColor = "transparent";
    ctx.strokeStyle = "#ffffff";
    ctx.lineWidth = 4;
    ctx.beginPath();
    ctx.arc(cx, cy, r - 8, 0, Math.PI * 2);
    ctx.stroke();

    ctx.fillStyle = "#1A3E74";
    ctx.beginPath();
    ctx.arc(cx, cy, r - 14, 0, Math.PI * 2);
    ctx.fill();

    // mini bars icon
    ctx.fillStyle = "#93C5FD";
    ctx.fillRect(cx - 22, cy - 18, 10, 40);
    ctx.fillRect(cx - 5, cy - 32, 10, 54);
    ctx.fillRect(cx + 12, cy - 10, 10, 32);

    ctx.textAlign = "center";
    ctx.fillStyle = "#fff";
    ctx.font = "800 15px Inter, Nunito Sans, sans-serif";
    ctx.fillText(tpl.badge, cx, cy + 42);
    ctx.font = "700 12px Inter, Nunito Sans, sans-serif";
    ctx.fillStyle = "#BFDBFE";
    ctx.fillText(tpl.badgeSub, cx, cy + 60);
    ctx.restore();
  };

  // roundRect polyfill for older browsers
  if (!CanvasRenderingContext2D.prototype.roundRect) {
    CanvasRenderingContext2D.prototype.roundRect = function (x, y, w, h, r) {
      var radius = typeof r === "number" ? r : 8;
      this.beginPath();
      this.moveTo(x + radius, y);
      this.arcTo(x + w, y, x + w, y + h, radius);
      this.arcTo(x + w, y + h, x, y + h, radius);
      this.arcTo(x, y + h, x, y, radius);
      this.arcTo(x, y, x + w, y, radius);
      this.closePath();
      return this;
    };
  }

  document.addEventListener("DOMContentLoaded", function () {
    var root = document.querySelector("[data-cko-valorizacao]");
    if (!root) return;
    var app = new ValorizacaoApp(root);
    app.init();
    window.ckoValorizacao = app;
  });
})();
