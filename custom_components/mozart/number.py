"""Number entities for the Bang & Olufsen Mozart integration."""
from __future__ import annotations

from mozart_api.models import Bass, SoundSettings, Treble

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity import DeviceInfo, EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    CONNECTION_STATUS,
    HASS_NUMBERS,
    MOZART_DOMAIN,
    SOUND_SETTINGS_NOTIFICATION,
    MozartVariables,
)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Mozart number entities from config entry."""
    entities = []

    # Add number entities.
    for number in hass.data[MOZART_DOMAIN][config_entry.unique_id][HASS_NUMBERS]:
        entities.append(number)

    async_add_entities(new_entities=entities, update_before_add=True)


class MozartNumber(MozartVariables, NumberEntity):
    """Number for Mozart settings."""

    def __init__(self, entry: ConfigEntry) -> None:
        """Init the Mozart number."""
        super().__init__(entry)

        self._attr_entity_category = EntityCategory.CONFIG
        self._attr_available = True
        self._attr_should_poll = False
        self._attr_mode = NumberMode.AUTO
        self._attr_device_info = DeviceInfo(
            identifiers={(MOZART_DOMAIN, self._unique_id)}
        )
        self._attr_native_value = 0.0

    async def async_added_to_hass(self) -> None:
        """Turn on the dispatchers."""
        connection_dispatcher = async_dispatcher_connect(
            self.hass,
            f"{self._unique_id}_{CONNECTION_STATUS}",
            self._update_connection_state,
        )

        self._dispatchers.append(connection_dispatcher)

    async def async_will_remove_from_hass(self) -> None:
        """Turn off the dispatchers."""
        for dispatcher in self._dispatchers:
            dispatcher()

    async def _update_connection_state(self, connection_state: bool) -> None:
        """Update entity connection state."""
        self._attr_available = connection_state

        self.async_write_ha_state()


class MozartNumberTreble(MozartNumber):
    """Treble number for Mozart settings."""

    def __init__(self, entry: ConfigEntry) -> None:
        """Init the treble number."""
        super().__init__(entry)

        number_range: range = range(-6, 6, 1)
        self._attr_native_min_value = float(number_range.start)
        self._attr_native_max_value = float(number_range.stop)
        self._attr_name = f"{self._name} Treble"
        self._attr_unique_id = f"{self._unique_id}-treble"
        self._attr_icon = "mdi:equalizer"
        self._attr_mode = NumberMode.SLIDER

    async def async_set_native_value(self, value: float) -> None:
        """Set the treble value."""
        self._mozart_client.set_sound_settings_adjustments_treble(
            treble=Treble(value=value), async_req=True
        )

    async def async_added_to_hass(self) -> None:
        """Turn on the dispatchers."""
        sound_settings_dispatcher = async_dispatcher_connect(
            self.hass,
            f"{self._unique_id}_{SOUND_SETTINGS_NOTIFICATION}",
            self._update_sound_settings,
        )

        connection_dispatcher = async_dispatcher_connect(
            self.hass,
            f"{self._unique_id}_{CONNECTION_STATUS}",
            self._update_connection_state,
        )

        self._dispatchers.append(sound_settings_dispatcher)
        self._dispatchers.append(connection_dispatcher)

    async def _update_sound_settings(self, data: SoundSettings) -> None:
        """Update sound settings."""
        self._sound_settings = data
        self._attr_native_value = self._sound_settings.adjustments.treble

        self.async_write_ha_state()


class MozartNumberBass(MozartNumber):
    """Bass number for Mozart settings."""

    def __init__(self, entry: ConfigEntry) -> None:
        """Init the bass number."""
        super().__init__(entry)

        number_range: range = range(-6, 6, 1)
        self._attr_native_min_value = float(number_range.start)
        self._attr_native_max_value = float(number_range.stop)
        self._attr_name = f"{self._name} Bass"
        self._attr_unique_id = f"{self._unique_id}-bass"
        self._attr_icon = "mdi:equalizer"
        self._attr_mode = NumberMode.SLIDER

    async def async_set_native_value(self, value: float) -> None:
        """Set the bass value."""
        self._mozart_client.set_sound_settings_adjustments_bass(
            bass=Bass(value=value), async_req=True
        )

    async def async_added_to_hass(self) -> None:
        """Turn on the dispatchers."""
        sound_settings_dispatcher = async_dispatcher_connect(
            self.hass,
            f"{self._unique_id}_{SOUND_SETTINGS_NOTIFICATION}",
            self._update_sound_settings,
        )

        connection_dispatcher = async_dispatcher_connect(
            self.hass,
            f"{self._unique_id}_{CONNECTION_STATUS}",
            self._update_connection_state,
        )

        self._dispatchers.append(sound_settings_dispatcher)
        self._dispatchers.append(connection_dispatcher)

    async def _update_sound_settings(self, data: SoundSettings) -> None:
        """Update sound settings."""
        self._sound_settings = data
        self._attr_native_value = self._sound_settings.adjustments.bass

        self.async_write_ha_state()
