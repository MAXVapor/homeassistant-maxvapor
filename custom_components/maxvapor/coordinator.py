"""Polling coordinator: one cloud round-trip per cycle for all devices."""
from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import MaxVaporApi, MaxVaporApiError
from .const import DOMAIN, READY_BAND_C, UPDATE_INTERVAL_S

_LOGGER = logging.getLogger(__name__)


class MaxVaporCoordinator(DataUpdateCoordinator[dict[str, dict[str, Any]]]):
    """Fetches per-device state; data is a dict keyed by serial."""

    def __init__(
        self,
        hass: HomeAssistant,
        api: MaxVaporApi,
        devices: list[dict[str, Any]],
    ) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=UPDATE_INTERVAL_S),
        )
        self.api = api
        # serial -> device record from /devices/ (name etc.), fixed at setup;
        # reload the config entry to pick up newly linked devices.
        self.devices = {d["serial"]: d for d in devices}

    async def _async_update_data(self) -> dict[str, dict[str, Any]]:
        data: dict[str, dict[str, Any]] = {}
        for serial in self.devices:
            try:
                state = await self.api.get_state(serial)
            except MaxVaporApiError as err:
                raise UpdateFailed(str(err)) from err
            state["ready"] = _is_ready(state)
            data[serial] = state
        return data


def _is_ready(state: dict[str, Any]) -> bool:
    """Mirror the firmware's READY chip: in-band while heating."""
    if not state.get("pid_state"):
        return False
    temperature = state.get("temperature_c")
    setpoint = state.get("setpoint_c")
    if temperature is None or setpoint is None:
        return False
    return abs(temperature - setpoint) <= READY_BAND_C
