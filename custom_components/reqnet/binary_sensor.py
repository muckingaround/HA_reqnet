"""Platform for binary_sensor integration."""
from __future__ import annotations

import logging

from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import ReqnetDataCoordinator

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Konfiguracja platformy czujników binarnych Reqnet."""
    coordinator: ReqnetDataCoordinator = hass.data[DOMAIN][config_entry.entry_id]

    binary_sensors = [
        # Indeks 0: Status urządzenia (1 - włączone, 0 - wyłączone)
        ReqnetBinarySensor(
            coordinator,
            0,
            BinarySensorEntityDescription(
                key="device_status",
                translation_key="device_status",
                icon="mdi:power",
            ),
            "mdi:power",
            "mdi:power-off",
        ),
    ]

    async_add_entities(binary_sensors)


class ReqnetBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """Reprezentacja czujnika binarnego Reqnet."""
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: ReqnetDataCoordinator,
        index: int,
        entity_description: BinarySensorEntityDescription,
        on_icon: str | None,
        off_icon: str | None,
    ) -> None:
        """Inicjalizacja czujnika binarnego."""
        super().__init__(coordinator)
        self.entity_description = entity_description
        self._index = index
        self._on_icon = on_icon
        self._off_icon = off_icon

        self._attr_unique_id = f"{coordinator.mac_address.replace(':', '').lower()}_{entity_description.key}"
        # Powiąż encję z urządzeniem (rekuperatorem)
        self._attr_device_info = {
            "identifiers": {(DOMAIN, coordinator.mac_address)},
            "name": f"Reqnet Recuperator ({coordinator.mac_address})",
            "manufacturer": "Reqnet",
            "model": "Recuperator",
        }

    @property
    def is_on(self) -> bool | None:
        """Zwraca true jeśli czujnik binarny jest włączony."""
        if self.coordinator.data is None or self._index >= len(self.coordinator.data):
            return None
        # Zakładamy, że 1 to True (on), a 0 to False (off)
        return bool(self.coordinator.data[self._index])

    @property
    def icon(self):
        """Zwraca ikonę czujnika binarnego."""
        if self.is_on:
            return self._on_icon
        return self._off_icon