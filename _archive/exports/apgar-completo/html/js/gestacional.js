(function () {
  "use strict";

  var form = document.getElementById("gestForm");
  var dumInput = document.getElementById("dum");
  var dumError = document.getElementById("dumError");
  var resultSection = document.getElementById("gestResult");
  var resIg = document.getElementById("resIg");
  var resDpp = document.getElementById("resDpp");
  var gestDetail = document.getElementById("gestDetail");

  if (!form || !dumInput) return;

  var meses = [
    "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
    "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
  ];

  function formatarDataBR(data) {
    return data.toLocaleDateString("pt-BR", { day: "2-digit", month: "2-digit", year: "numeric" });
  }

  function showError(msg) {
    dumError.textContent = msg;
    dumError.hidden = false;
    dumInput.setAttribute("aria-invalid", "true");
    resultSection.hidden = true;
  }

  function clearError() {
    dumError.hidden = true;
    dumError.textContent = "";
    dumInput.removeAttribute("aria-invalid");
  }

  function calcular() {
    clearError();
    var dumValue = dumInput.value;
    if (!dumValue) {
      showError("Por favor, insira a Data da Última Menstruação (DUM).");
      return;
    }

    var dumDate = new Date(dumValue + "T00:00:00");
    var hoje = new Date();
    hoje.setHours(0, 0, 0, 0);
    dumDate.setHours(0, 0, 0, 0);

    if (dumDate > hoje) {
      showError("A DUM não pode ser uma data no futuro.");
      return;
    }

    var diffMs = hoje.getTime() - dumDate.getTime();
    var diffDias = Math.floor(diffMs / (1000 * 60 * 60 * 24));
    var semanas = Math.floor(diffDias / 7);
    var dias = diffDias % 7;

    var dppDate = new Date(dumDate.getTime());
    dppDate.setDate(dppDate.getDate() + 280);

    var dDum = dumDate.getDate();
    var mDum = dumDate.getMonth() + 1;
    var aDum = dumDate.getFullYear();
    var dNaegele = dDum + 7;
    var explicacaoMes;

    if (mDum >= 1 && mDum <= 3) {
      explicacaoMes =
        "Como o mês da DUM é <strong>" + meses[mDum - 1] +
        "</strong> (entre janeiro e março), <strong>somamos 9</strong> aos meses: " +
        mDum + " + 9 = <strong>" + (mDum + 9) + "</strong>.";
    } else {
      explicacaoMes =
        "Como o mês da DUM é <strong>" + meses[mDum - 1] +
        "</strong> (entre abril e dezembro), <strong>subtraímos 3</strong> dos meses (" +
        mDum + " - 3 = <strong>" + (mDum - 3) + "</strong>) e <strong>somamos 1</strong> ao ano (" +
        aDum + " + 1 = <strong>" + (aDum + 1) + "</strong>).";
    }

    resIg.textContent = semanas + " semanas e " + dias + " dias";
    resDpp.textContent = formatarDataBR(dppDate);

    gestDetail.innerHTML =
      "<h4>1. Regra de Naegele (DPP)</h4>" +
      "<p>A DUM inserida foi <strong>" + formatarDataBR(dumDate) + "</strong>.</p>" +
      "<ul>" +
      "<li><strong>Passo A (dias):</strong> " + dDum + " + 7 + " = <strong>" + dNaegele + "</strong></li>" +
      "<li><strong>Passo B (meses e anos):</strong> " + explicacaoMes + "</li>" +
      "<li><strong>Resultado DPP:</strong> <strong>" + formatarDataBR(dppDate) + "</strong></li>" +
      "</ul>" +
      "<h4>2. Idade gestacional atual</h4>" +
      "<p>Dias corridos desde a DUM (" + formatarDataBR(dumDate) + ") até hoje (" + formatarDataBR(hoje) + "): <strong>" + diffDias + " dias</strong>.</p>" +
      "<p>" + diffDias + " ÷ 7 = <strong>" + semanas + " semanas</strong> e resto de <strong>" + dias + " dias</strong>.</p>";

    resultSection.hidden = false;
    resultSection.scrollIntoView({ behavior: "smooth", block: "nearest" });
  }

  form.addEventListener("submit", function (e) {
    e.preventDefault();
    calcular();
  });

  form.addEventListener("reset", function () {
    clearError();
    resultSection.hidden = true;
    resIg.textContent = "—";
    resDpp.textContent = "—";
    gestDetail.innerHTML = "";
  });
})();
