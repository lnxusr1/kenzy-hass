"""Config flow for the Kenzy integration."""

from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import KenzyApiError, KenzyCannotConnect, KenzyClient
from .const import (
    CONF_HOST,
    CONF_PORT,
    CONF_TOKEN,
    CONF_USE_TLS,
    CONF_VERIFY_TLS,
    DEFAULT_PORT,
    DEFAULT_USE_TLS,
    DEFAULT_VERIFY_TLS,
    DOMAIN,
)

_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Required(CONF_PORT, default=DEFAULT_PORT): int,
        vol.Optional(CONF_TOKEN, default=""): str,
        vol.Required(CONF_USE_TLS, default=DEFAULT_USE_TLS): bool,
        vol.Required(CONF_VERIFY_TLS, default=DEFAULT_VERIFY_TLS): bool,
    }
)


class KenzyConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Point the integration at a kenzy-server (host, port, fleet token)."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            session = async_get_clientsession(self.hass, user_input[CONF_VERIFY_TLS])
            client = KenzyClient(
                session,
                user_input[CONF_HOST],
                user_input[CONF_PORT],
                token=user_input[CONF_TOKEN],
                use_tls=user_input[CONF_USE_TLS],
            )
            try:
                await client.validate()
            except KenzyCannotConnect:
                errors["base"] = "cannot_connect"
            except KenzyApiError as exc:
                errors["base"] = "invalid_auth" if "invalid_auth" in str(exc) else "unknown"
            if not errors:
                await self.async_set_unique_id(
                    f"{user_input[CONF_HOST]}:{user_input[CONF_PORT]}"
                )
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=f"Kenzy ({user_input[CONF_HOST]})", data=user_input
                )
        return self.async_show_form(step_id="user", data_schema=_SCHEMA, errors=errors)
