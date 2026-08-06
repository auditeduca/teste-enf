/* ==========================================================
   CE - Calculadora Padrão (SEM eval)
   Arquivo: /ce-calculadora-padrao.js
   Suporta: + - * / ( ) e decimais (vírgula/ponto)
   HTML esperado:
     [data-ce-calc]
       [data-ce-expr]
       [data-ce-result]
       [data-ce-keys] com botões data-ce-key ou data-ce-action
   ========================================================== */

(function () {
  "use strict";

  function isOp(t) { return t === "+" || t === "-" || t === "*" || t === "/"; }
  function prec(op) { return (op === "*" || op === "/") ? 2 : 1; }
  function isNumberToken(t) { return typeof t === "number" && Number.isFinite(t); }

  // Tokeniza expressão: números, operadores, parênteses
  // Trata "-" unário (ex.: -2, 5*-2, -(3+1))
  function tokenize(input) {
    const s = String(input).replace(/\s+/g, "");
    const tokens = [];
    let i = 0;

    function peekLast() { return tokens.length ? tokens[tokens.length - 1] : null; }
    function isUnaryMinusPosition() {
      const last = peekLast();
      return (
        last === null ||
        (typeof last === "string" && (isOp(last) || last === "("))
      );
    }

    while (i < s.length) {
      const ch = s[i];

      // números (inteiro/decimal)
      if ((ch >= "0" && ch <= "9") || ch === ".") {
        let numStr = "";
        while (i < s.length) {
          const c = s[i];
          if ((c >= "0" && c <= "9") || c === ".") {
            numStr += c;
            i++;
          } else break;
        }
        if (numStr === "." || numStr.split(".").length > 2) throw new Error("Número inválido");
        const n = Number(numStr);
        if (!Number.isFinite(n)) throw new Error("Número inválido");
        tokens.push(n);
        continue;
      }

      // parênteses
      if (ch === "(" || ch === ")") {
        tokens.push(ch);
        i++;
        continue;
      }

      // operadores
      if (isOp(ch)) {
        // trata "-" unário
        if (ch === "-" && isUnaryMinusPosition()) {
          // se for "-(" => vira "0 - ("
          if (s[i + 1] === "(") {
            tokens.push(0);
            tokens.push("-");
            i++;
            continue;
          }
          // se for "-<numero>" => número negativo
          // consome o número logo após
          let j = i + 1;
          let numStr = "-";
          let hasDigit = false;

          while (j < s.length) {
            const c = s[j];
            if ((c >= "0" && c <= "9") || c === ".") {
              if (c >= "0" && c <= "9") hasDigit = true;
              numStr += c;
              j++;
            } else break;
          }

          if (!hasDigit) {
            // "-" sozinho em posição unária não é válido
            throw new Error("Sinal inválido");
          }
          if (numStr === "-" || numStr === "-." || numStr.split(".").length > 2) throw new Error("Número inválido");

          const n = Number(numStr);
          if (!Number.isFinite(n)) throw new Error("Número inválido");
          tokens.push(n);
          i = j;
          continue;
        }

        tokens.push(ch);
        i++;
        continue;
      }

      throw new Error("Caractere inválido");
    }

    return tokens;
  }

  // Shunting-yard -> RPN
  function toRPN(tokens) {
    const out = [];
    const stack = [];

    for (const t of tokens) {
      if (isNumberToken(t)) {
        out.push(t);
        continue;
      }

      if (t === "(") {
        stack.push(t);
        continue;
      }

      if (t === ")") {
        while (stack.length && stack[stack.length - 1] !== "(") {
          out.push(stack.pop());
        }
        if (!stack.length) throw new Error("Parênteses inválidos");
        stack.pop(); // remove "("
        continue;
      }

      if (isOp(t)) {
        while (
          stack.length &&
          isOp(stack[stack.length - 1]) &&
          prec(stack[stack.length - 1]) >= prec(t)
        ) {
          out.push(stack.pop());
        }
        stack.push(t);
        continue;
      }

      throw new Error("Token inválido");
    }

    while (stack.length) {
      const op = stack.pop();
      if (op === "(" || op === ")") throw new Error("Parênteses inválidos");
      out.push(op);
    }

    return out;
  }

  // Avalia RPN
  function evalRPN(rpn) {
    const st = [];
    for (const t of rpn) {
      if (isNumberToken(t)) {
        st.push(t);
        continue;
      }
      if (!isOp(t)) throw new Error("RPN inválida");

      if (st.length < 2) throw new Error("Expressão incompleta");
      const b = st.pop();
      const a = st.pop();

      let r;
      if (t === "+") r = a + b;
      else if (t === "-") r = a - b;
      else if (t === "*") r = a * b;
      else if (t === "/") {
        if (b === 0) throw new Error("Divisão por zero");
        r = a / b;
      }

      if (!Number.isFinite(r)) throw new Error("Resultado inválido");
      st.push(r);
    }
    if (st.length !== 1) throw new Error("Expressão inválida");
    return st[0];
  }

  // Formata resultado (vírgula PT-BR) com limite de casas para evitar números gigantes
  function formatResult(n) {
    // limita casas decimais sem “comer” precisão à toa
    const rounded = Math.round((n + Number.EPSILON) * 1e10) / 1e10;
    let s = String(rounded);

    // notação científica: mantém (é raro em uso normal, mas evita bug)
    if (s.includes("e") || s.includes("E")) return s.replace(".", ",");

    // remove zeros finais de decimal
    if (s.includes(".")) {
      s = s.replace(/0+$/, "").replace(/\.$/, "");
    }
    return s.replace(".", ",");
  }

  function initCalc(root) {
    const exprEl = root.querySelector("[data-ce-expr]");
    const resEl  = root.querySelector("[data-ce-result]");
    const keysEl = root.querySelector("[data-ce-keys]");
    if (!exprEl || !resEl || !keysEl) return;

    let expr = "0";

    function render() { exprEl.textContent = expr; }
    function setExpr(v) { expr = (v && v.length) ? v : "0"; render(); }

    function lastChar() { return expr.length ? expr[expr.length - 1] : ""; }

    function append(ch) {
      // vírgula vira ponto internamente
      if (ch === ",") ch = ".";

      if (expr === "0") expr = "";

      // evita começar com + * / (mas permite "-" e "(")
      if ((ch === "+" || ch === "*" || ch === "/") && expr === "") return;

      // evita repetir operador: troca o último
      if (isOp(ch)) {
        const lc = lastChar();
        if (isOp(lc)) {
          expr = expr.slice(0, -1) + ch;
          render();
          return;
        }
        // se está vazio, não coloca operador (exceto -)
        if (expr === "" && ch !== "-") return;
      }

      // ponto decimal: não permite dois no mesmo “número atual”
      if (ch === ".") {
        const chunk = expr.split(/[+\-*/()]/).pop();
        if (chunk.includes(".")) return;
        if (chunk === "" || chunk === "-") expr += "0";
      }

      // fecha parênteses só se fizer sentido
      if (ch === ")") {
        const lc = lastChar();
        if (expr === "" || isOp(lc) || lc === "(") return;
        // checa balanceamento
        const opens = (expr.match(/\(/g) || []).length;
        const closes = (expr.match(/\)/g) || []).length;
        if (closes >= opens) return;
      }

      // abre parênteses: se antes for número ou ")", insere "*("
      if (ch === "(") {
        const lc = lastChar();
        if ((lc >= "0" && lc <= "9") || lc === ")" || lc === ".") {
          expr += "*";
        }
      }

      expr += ch;
      render();
    }

    function backspace() {
      if (expr.length <= 1) return setExpr("0");
      setExpr(expr.slice(0, -1));
    }

    function clearAll() {
      expr = "0";
      resEl.textContent = "";
      render();
    }

    function calculate() {
      try {
        const clean = expr.replace(/\s+/g, "");
        const tokens = tokenize(clean);
        const rpn = toRPN(tokens);
        const out = evalRPN(rpn);
        resEl.textContent = formatResult(out);
      } catch (e) {
        resEl.textContent = "Erro";
      }
    }

    keysEl.addEventListener("click", function (ev) {
      const btn = ev.target.closest("button");
      if (!btn) return;

      const key = btn.getAttribute("data-ce-key");
      const action = btn.getAttribute("data-ce-action");

      if (key) append(key);
      else if (action === "back") backspace();
      else if (action === "clear") clearAll();
      else if (action === "equals") calculate();
    });

    render();
  }

  function boot() {
    document.querySelectorAll("[data-ce-calc]").forEach(initCalc);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})();
