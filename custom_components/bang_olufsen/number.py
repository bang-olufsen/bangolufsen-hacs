"""Number entities for the Bang & Olufsen integration."""

from __future__ import annotations

from mozart_api.models import Bass, SoundSettings, Treble

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import BangOlufsenConfigEntry, set_platform_initialized
from .const import BASS_TREBLE_RANGE, CONNECTION_STATUS, WebsocketNotification
from .entity import BangOlufsenEntity


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: BangOlufsenConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Number entities from config entry."""
    entities: list[BangOlufsenEntity] = [
        BangOlufsenNumberBass(config_entry),
        BangOlufsenNumberTreble(config_entry),
    ]

    async_add_entities(new_entities=entities)

    set_platform_initialized(config_entry.runtime_data)


class BangOlufsenNumber(BangOlufsenEntity, NumberEntity):
    """Base Number class."""

    _attr_mode = NumberMode.AUTO

    def __init__(self, config_entry: BangOlufsenConfigEntry) -> None:
        """Init the Number."""
        super().__init__(config_entry)

        self._attr_entity_category = EntityCategory.CONFIG
        self._attr_native_value = 0.0


class BangOlufsenNumberTreble(BangOlufsenNumber):
    """Treble Number."""

    _attr_icon = "mdi:equalizer"
    _attr_native_max_value = float(BASS_TREBLE_RANGE.stop)
    _attr_native_min_value = float(BASS_TREBLE_RANGE.start)
    _attr_translation_key = "treble"

    def __init__(self, config_entry: BangOlufsenConfigEntry) -> None:
        """Init the treble Number."""
        super().__init__(config_entry)

        self._attr_mode = NumberMode.SLIDER
        self._attr_unique_id = f"{self._unique_id}-treble"

    async def async_set_native_value(self, value: float) -> None:
        """Set the treble value."""
        await self._client.set_sound_settings_adjustments_treble(
            treble=Treble(value=int(value))
        )

    async def async_added_to_hass(self) -> None:
        """Turn on the dispatchers."""
        self.async_on_remove(
            async_dispatcher_connect(
                self.hass,
                f"{self._unique_id}_{CONNECTION_STATUS}",
                self._async_update_connection_state,
            )
        )
        self.async_on_remove(
            async_dispatcher_connect(
                self.hass,
                f"{self._unique_id}_{WebsocketNotification.SOUND_SETTINGS}",
                self._update_sound_settings,
            )
        )

    async def _update_sound_settings(self, data: SoundSettings) -> None:
        """Update sound settings."""
        if data.adjustments and data.adjustments.treble is not None:
            self._attr_native_value = data.adjustments.treble
            self.async_write_ha_state()


class BangOlufsenNumberBass(BangOlufsenNumber):
    """Bass Number."""

    _attr_icon = "mdi:equalizer"
    _attr_native_max_value = float(BASS_TREBLE_RANGE.stop)
    _attr_native_min_value = float(BASS_TREBLE_RANGE.start)
    _attr_translation_key = "bass"

    def __init__(self, config_entry: BangOlufsenConfigEntry) -> None:
        """Init the bass Number."""
        super().__init__(config_entry)

        self._attr_mode = NumberMode.SLIDER
        self._attr_unique_id = f"{self._unique_id}-bass"

    async def async_set_native_value(self, value: float) -> None:
        """Set the bass value."""
        await self._client.set_sound_settings_adjustments_bass(
            bass=Bass(value=int(value))
        )

    async def async_added_to_hass(self) -> None:
        """Turn on the dispatchers."""
        self.async_on_remove(
            async_dispatcher_connect(
                self.hass,
                f"{self._unique_id}_{CONNECTION_STATUS}",
                self._async_update_connection_state,
            )
        )
        self.async_on_remove(
            async_dispatcher_connect(
                self.hass,
                f"{self._unique_id}_{WebsocketNotification.SOUND_SETTINGS}",
                self._update_sound_settings,
            )
        )

    async def _update_sound_settings(self, data: SoundSettings) -> None:
        """Update sound settings."""
        if data.adjustments and data.adjustments.bass is not None:
            self._attr_native_value = data.adjustments.bass
            self.async_write_ha_state()
