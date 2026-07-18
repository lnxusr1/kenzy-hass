"""Minimal client for kenzy-server's always-on HTTP endpoints.

Talks to the ``/assist`` channel (F3): text + the HA person entity id in,
Kenzy's reply out. Identity, memory, and skill gating all live server-side —
this client is deliberately dumb.

Auth: the fleet's shared service token, sent as a KENZY-HMAC signature
(``X-Kenzy-Auth``) so the token itself never travels the wire — a ~10-line
reimplementation of kenzy's scheme rather than a dependency on the kenzy
package. A tokenless Kenzy (auth disabled) works with no token configured.
"""

from __future__ import annotations

import hashlib
import hmac
import time
from typing import Any
from urllib.parse import urlencode

import aiohttp


def _sign(token: str, method: str, path: str) -> str:
    """kenzy.serviceauth.sign_service_request, reimplemented byte-for-byte
    (key = sha256("kenzy-svc-hmac\\0" + token); material =
    "req"\\0 ts \\0 METHOD \\0 path). Covered by a fixed-vector test so drift
    against the kenzy wire format is caught."""
    ts = int(time.time())
    key = hashlib.sha256(b"kenzy-svc-hmac\x00" + token.encode()).digest()
    material = b"\x00".join([b"req", str(ts).encode(), method.upper().encode(), path.encode()])
    sig = hmac.new(key, material, hashlib.sha256).hexdigest()
    return f"KENZY-HMAC ts={ts}, sig={sig}"


class KenzyApiError(Exception):
    """The server was reached but refused or failed the request."""


class KenzyCannotConnect(Exception):
    """The server was not reachable at all."""


class KenzyClient:
    def __init__(
        self,
        session: aiohttp.ClientSession,
        host: str,
        port: int,
        *,
        token: str = "",
        use_tls: bool = True,
    ) -> None:
        self._session = session
        self._base = f"{'https' if use_tls else 'http'}://{host}:{port}"
        self._token = token

    def _headers(self, method: str, path: str) -> dict[str, str]:
        if not self._token:
            return {}
        return {"X-Kenzy-Auth": _sign(self._token, method, path)}

    async def _get(self, path_qs: str, *, timeout: float) -> tuple[int, dict[str, Any]]:
        path = path_qs.split("?", 1)[0]
        try:
            async with self._session.get(
                self._base + path_qs,
                headers=self._headers("GET", path),
                timeout=aiohttp.ClientTimeout(total=timeout),
            ) as resp:
                try:
                    body = await resp.json()
                except Exception:
                    body = {}
                return resp.status, body if isinstance(body, dict) else {}
        except aiohttp.ClientError as exc:
            raise KenzyCannotConnect(str(exc)) from exc
        except TimeoutError as exc:
            raise KenzyCannotConnect("timeout") from exc

    async def validate(self) -> None:
        """Config-flow check: prove the server is reachable and the token is
        accepted WITHOUT running the pipeline — /assist with no text answers
        400 exactly when connectivity + auth are good."""
        status, _ = await self._get("/assist", timeout=10)
        if status == 401:
            raise KenzyApiError("invalid_auth")
        if status != 400:
            raise KenzyApiError(f"unexpected status {status}")

    async def assist(self, text: str, ha_user: str) -> dict[str, Any]:
        """One conversation turn. Returns {text, speaker, recognized, fast}."""
        qs = urlencode({"text": text, "ha_user": ha_user})
        status, body = await self._get(f"/assist?{qs}", timeout=60)
        if status == 401:
            raise KenzyApiError("invalid_auth")
        if status != 200 or "text" not in body:
            raise KenzyApiError(body.get("error", f"status {status}"))
        return body
