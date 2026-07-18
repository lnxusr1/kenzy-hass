"""The Kenzy conversation agent (F3.1)."""

from __future__ import annotations

import logging

from homeassistant.components import conversation
from homeassistant.const import MATCH_ALL
from homeassistant.core import HomeAssistant
from homeassistant.helpers import intent
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import KenzyConfigEntry
from .api import KenzyApiError, KenzyCannotConnect
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: KenzyConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    async_add_entities([KenzyAgent(entry)])


class KenzyAgent(conversation.ConversationEntity):
    """Relays Assist turns to kenzy-server's /assist channel.

    The one job done client-side: map the HA *user* (session uuid) to the HA
    *person entity* — the stable id the household mapped on Kenzy's People
    page (people.yaml ``ha_user``). Kenzy resolves that to the same person
    records the voice channel uses; an unmapped user is served fail-closed
    (no memory, gated skills withheld), exactly like an unrecognized voice.
    """

    _attr_has_entity_name = True
    _attr_name = None
    # The integration TILE icon comes from the brands repo (assets/brands/);
    # this is the conversation entity's own icon, honored locally.
    _attr_icon = "mdi:account-voice"

    def __init__(self, entry: KenzyConfigEntry) -> None:
        self._entry = entry
        self._attr_unique_id = entry.entry_id

    @property
    def supported_languages(self) -> list[str] | str:
        """Kenzy's language handling lives server-side (the configured model)."""
        return MATCH_ALL

    def _person_entity_for(self, user_id: str | None) -> str:
        """HA user uuid → person entity id (e.g. ``person.john_mark``)."""
        if not user_id:
            return ""
        for state in self.hass.states.async_all("person"):
            if state.attributes.get("user_id") == user_id:
                return state.entity_id
        return ""

    async def async_process(
        self, user_input: conversation.ConversationInput
    ) -> conversation.ConversationResult:
        ha_user = self._person_entity_for(user_input.context.user_id)
        response = intent.IntentResponse(language=user_input.language)
        try:
            reply = await self._entry.runtime_data.assist(user_input.text, ha_user)
            response.async_set_speech(reply["text"])
        except KenzyCannotConnect:
            response.async_set_error(
                intent.IntentResponseErrorCode.UNKNOWN,
                "I couldn't reach Kenzy — is the server up?",
            )
        except KenzyApiError as exc:
            _LOGGER.warning("Kenzy assist failed: %s", exc)
            response.async_set_error(
                intent.IntentResponseErrorCode.UNKNOWN,
                "Kenzy couldn't handle that request.",
            )
        return conversation.ConversationResult(
            response=response, conversation_id=user_input.conversation_id
        )
