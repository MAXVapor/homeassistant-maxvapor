"""Sensors: coil temperature (for history graphs) and auto-off countdown."""
from __future__ import annotations

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature, UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import MaxVaporCoordinator
from .entity import MaxVaporEntity


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    coordinator: MaxVaporCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities: list[SensorEntity] = []
    for serial in coordinator.devices:
        entities.append(MaxVaporTemperatureSensor(coordinator, serial))
        entities.append(MaxVaporAutoOffSensor(coordinator, serial))
    async_add_entities(entities)


class MaxVaporTemperatureSensor(MaxVaporEntity, SensorEntity):
    _attr_name = "Temperature"
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS

    def __init__(self, coordinator: MaxVaporCoordinator, serial: str) -> None:
        super().__init__(coordinator, serial)
        self._attr_unique_id = f"{serial}_temperature"

    @property
    def native_value(self) -> float | None:
        return self.state_data.get("temperature_c")


class MaxVaporAutoOffSensor(MaxVaporEntity, SensorEntity):
    _attr_name = "Auto-off remaining"
    _attr_device_class = SensorDeviceClass.DURATION
    _attr_native_unit_of_measurement = UnitOfTime.SECONDS

    def __init__(self, coordinator: MaxVaporCoordinator, serial: str) -> None:
        super().__init__(coordinator, serial)
        self._attr_unique_id = f"{serial}_auto_off_remain"

    @property
    def native_value(self) -> int | None:
        return self.state_data.get("auto_off_remain")
