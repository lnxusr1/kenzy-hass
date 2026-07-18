"""Kenzy — your household's voice assistant, as a Home Assistant
conversation agent (the second front door: Assist on phone/tablet/watch).

Identity, memory, and skill gating live on the kenzy-server; this integration
maps the HA session to the person entity Kenzy knows and relays one
conversation turn per request.
"""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import KenzyClient
from .const import (
    CONF_HOST,
    CONF_PORT,
    CONF_TOKEN,
    CONF_USE_TLS,
    CONF_VERIFY_TLS,
)

PLATFORMS = [Platform.CONVERSATION]

type KenzyConfigEntry = ConfigEntry[KenzyClient]


async def async_setup_entry(hass: HomeAssistant, entry: KenzyConfigEntry) -> bool:
    session = async_get_clientsession(hass, entry.data.get(CONF_VERIFY_TLS, False))
    entry.runtime_data = KenzyClient(
        session,
        entry.data[CONF_HOST],
        entry.data[CONF_PORT],
        token=entry.data.get(CONF_TOKEN, ""),
        use_tls=entry.data.get(CONF_USE_TLS, True),
    )
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: KenzyConfigEntry) -> bool:
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
