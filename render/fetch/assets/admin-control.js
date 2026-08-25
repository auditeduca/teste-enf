/* CKO admin control plane client. First-party. No canonical writes. */
(function () {
  "use strict";

  function outEl() {
    return document.getElementById("admin-action-out");
  }

  function show(data) {
    var el = outEl();
    if (!el) return;
    el.hidden = false;
    el.textContent = typeof data === "string" ? data : JSON.stringify(data, null, 2);
  }

  function rootPrefix() {
    var script = document.querySelector("[data-admin-root]");
    return script ? script.getAttribute("data-admin-root") || "" : "";
  }

  async function call(method, path) {
    var url = rootPrefix() + path;
    var res;
    try {
      res = await fetch(url, {
        method: method,
        headers: { Accept: "application/json" }
      });
    } catch (err) {
      show({
        status: "HOLD",
        reason: "Control plane indisponível. Sirva com python3 -m engine.cli serve — não abra o HTML como arquivo.",
        error: String(err)
      });
      return;
    }
    var body = await res.text();
    try {
      show(JSON.parse(body));
    } catch (err) {
      show({ http: res.status, body: body.slice(0, 2000) });
    }
  }

  document.addEventListener("click", function (event) {
    var btn = event.target.closest("[data-admin-action]");
    if (!btn) return;
    event.preventDefault();
    var action = btn.getAttribute("data-admin-action");
    if (action === "git-status") call("GET", "/__admin/git-status");
    if (action === "render") call("POST", "/__admin/render");
    if (action === "deploy-prepare") call("POST", "/__admin/deploy-prepare");
  });
})();
