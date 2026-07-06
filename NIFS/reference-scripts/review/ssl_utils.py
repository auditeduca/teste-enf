"""TLS context for outbound API calls (DeepSeek, Groq, Cursor proxy)."""
from __future__ import annotations

import os
import ssl
import urllib.error
import urllib.request
from pathlib import Path


def ssl_verify_enabled() -> bool:
    flag = os.environ.get("NKP_SSL_VERIFY", os.environ.get("DEEPSEEK_SSL_VERIFY", "1"))
    return flag.strip().lower() not in ("0", "false", "no", "off")


def make_ssl_context() -> ssl.SSLContext:
    """Prefer certifi CA bundle — fixes Windows CERTIFICATE_VERIFY_FAILED on api.deepseek.com."""
    if not ssl_verify_enabled():
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        return ctx

    ctx = ssl.create_default_context()

    cafile = (os.environ.get("SSL_CERT_FILE") or os.environ.get("REQUESTS_CA_BUNDLE") or "").strip()
    if cafile and Path(cafile).is_file():
        ctx.load_verify_locations(cafile=cafile)
        return ctx

    try:
        import certifi

        ctx.load_verify_locations(cafile=certifi.where())
    except ImportError:
        pass

    return ctx


def urlopen_request(req: urllib.request.Request, *, timeout: float = 120):
    return urllib.request.urlopen(req, timeout=timeout, context=make_ssl_context())


def ssl_setup_hint(exc: BaseException) -> str:
    reason = str(getattr(exc, "reason", exc))
    if "CERTIFICATE_VERIFY_FAILED" not in reason and "certificate verify failed" not in reason.lower():
        return ""
    return (
        " Dica: pip install certifi (ou defina SSL_CERT_FILE). "
        "Só dev local: NKP_SSL_VERIFY=0 (inseguro)."
    )
