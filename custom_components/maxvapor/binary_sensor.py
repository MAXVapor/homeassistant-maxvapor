"""Binary sensors: READY, heating, and the coil protection flags."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import MaxVaporCoordinator
from .entity import MaxVaporEntity


@dataclass(frozen=True, kw_only=True)
class MaxVaporBinarySensorDescription(BinarySensorEntityDescription):
    value_fn: Callable[[dict[str, Any]], bool]


SENSORS: tuple[MaxVaporBinarySensorDescription, ...] = (
    MaxVaporBinarySensorDescription(
        key="ready",
        name="Ready",
        icon="mdi:fire-circle",
        value_fn=lambda state: bool(state.get("ready")),
    ),
    MaxVaporBinarySensorDescription(
        key="heating",
        name="Heating",
        device_class=BinarySensorDeviceClass.HEAT,
        value_fn=lambda state: bool(state.get("pid_state")),
    ),
    MaxVaporBinarySensorDescription(
        key="coil_flapping",
        name="Coil fault warning",
        device_class=BinarySensorDeviceClass.PROBLEM,
        value_fn=lambda state: bool(state.get("coil_flapping")),
    ),
    MaxVaporBinarySensorDescription(
        key="coil_runaway",
        name="Coil damage warning",
        device_class=BinarySensorDeviceClass.PROBLEM,
        value_fn=lambda state: bool(state.get("coil_runaway")),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    coordinator: MaxVaporCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        MaxVaporBinarySensor(coordinator, serial, description)
        for serial in coordinator.devices
        for description in SENSORS
    )


class MaxVaporBinarySensor(MaxVaporEntity, BinarySensorEntity):
    entity_description: MaxVaporBinarySensorDescription

    def __init__(
        self,
        coordinator: MaxVaporCoordinator,
        serial: str,
        description: MaxVaporBinarySensorDescription,
    ) -> None:
        super().__init__(coordinator, serial)
        self.entity_description = description
        self._attr_unique_id = f"{serial}_{description.key}"

    @property
    def is_on(self) -> bool:
        return self.entity_description.value_fn(self.state_data)
