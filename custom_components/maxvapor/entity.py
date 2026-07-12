"""Shared entity base: device registry info and per-serial state access."""
from __future__ import annotations

from typing import Any

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import MaxVaporCoordinator


class MaxVaporEntity(CoordinatorEntity[MaxVaporCoordinator]):
    """One entity bound to one device serial."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: MaxVaporCoordinator, serial: str) -> None:
        super().__init__(coordinator)
        self._serial = serial

    @property
    def state_data(self) -> dict[str, Any]:
        return self.coordinator.data.get(self._serial, {})

    @property
    def available(self) -> bool:
        return super().available and bool(self.state_data.get("online"))

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self._serial)},
            name=self.coordinator.devices[self._serial]["name"],
            manufacturer="MaxVapor",
            model="MaxVapor BT",
            serial_number=self._serial,
            sw_version=self.state_data.get("firmware"),
        )
