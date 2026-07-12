"""The e-nail as a thermostat: current temp, target temp, heat on/off."""
from __future__ import annotations

from typing import Any

from homeassistant.components.climate import (
    ClimateEntity,
    ClimateEntityFeature,
    HVACAction,
    HVACMode,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PRECISION_TENTHS, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, MAX_TEMP_C
from .coordinator import MaxVaporCoordinator
from .entity import MaxVaporEntity


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    coordinator: MaxVaporCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        MaxVaporClimate(coordinator, serial) for serial in coordinator.devices
    )


class MaxVaporClimate(MaxVaporEntity, ClimateEntity):
    _attr_name = None  # takes the device name
    _attr_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_precision = PRECISION_TENTHS
    _attr_target_temperature_step = PRECISION_TENTHS
    _attr_min_temp = 0.0
    _attr_max_temp = MAX_TEMP_C
    _attr_hvac_modes = [HVACMode.HEAT, HVACMode.OFF]
    _attr_supported_features = (
        ClimateEntityFeature.TARGET_TEMPERATURE
        | ClimateEntityFeature.TURN_ON
        | ClimateEntityFeature.TURN_OFF
    )

    def __init__(self, coordinator: MaxVaporCoordinator, serial: str) -> None:
        super().__init__(coordinator, serial)
        self._attr_unique_id = f"{serial}_climate"

    @property
    def current_temperature(self) -> float | None:
        return self.state_data.get("temperature_c")

    @property
    def target_temperature(self) -> float | None:
        return self.state_data.get("setpoint_c")

    @property
    def hvac_mode(self) -> HVACMode:
        return HVACMode.HEAT if self.state_data.get("pid_state") else HVACMode.OFF

    @property
    def hvac_action(self) -> HVACAction:
        if not self.state_data.get("pid_state"):
            return HVACAction.OFF
        # In-band and holding reads as idle; climbing reads as heating.
        return HVACAction.IDLE if self.state_data.get("ready") else HVACAction.HEATING

    async def async_set_temperature(self, **kwargs: Any) -> None:
        temperature = kwargs.get("temperature")
        if temperature is None:
            return
        await self.coordinator.api.set_setpoint(self._serial, round(temperature, 2))
        await self.coordinator.async_request_refresh()

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        await self.coordinator.api.set_heat(self._serial, hvac_mode == HVACMode.HEAT)
        await self.coordinator.async_request_refresh()
