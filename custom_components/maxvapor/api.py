"""Async client for the MaxVapor dashboard REST API (/api/v1/)."""
from __future__ import annotations

import asyncio
from typing import Any

import aiohttp

TIMEOUT = aiohttp.ClientTimeout(total=10)


class MaxVaporApiError(Exception):
    """The API was unreachable or answered with an error."""


class MaxVaporAuthError(MaxVaporApiError):
    """The API token was rejected."""


class MaxVaporApi:
    """Thin wrapper over the endpoints the integration uses."""

    def __init__(self, session: aiohttp.ClientSession, token: str, base_url: str) -> None:
        self._session = session
        self._headers = {"Authorization": f"Token {token}"}
        self._base_url = base_url.rstrip("/")

    async def _request(self, method: str, path: str, **kwargs: Any) -> Any:
        url = f"{self._base_url}/{path}"
        try:
            async with self._session.request(
                method, url, headers=self._headers, timeout=TIMEOUT, **kwargs
            ) as response:
                if response.status in (401, 403):
                    raise MaxVaporAuthError(f"{response.status} for {path}")
                if response.status >= 400:
                    raise MaxVaporApiError(f"HTTP {response.status} for {path}")
                return await response.json()
        except (aiohttp.ClientError, asyncio.TimeoutError) as err:
            raise MaxVaporApiError(f"request to {path} failed: {err}") from err

    async def list_devices(self) -> list[dict[str, Any]]:
        """The caller's linked devices (plain array)."""
        return await self._request("GET", "devices/")

    async def get_state(self, serial: str) -> dict[str, Any]:
        """Live device state from the telemetry cache."""
        return await self._request("GET", f"devices/{serial}/state/")

    async def set_setpoint(self, serial: str, setpoint_c: float) -> None:
        await self._request(
            "PUT", f"devices/{serial}/setpoint/", json={"setpoint_c": setpoint_c}
        )

    async def set_heat(self, serial: str, enabled: bool) -> None:
        await self._request(
            "PUT", f"devices/{serial}/pid/", json={"enabled": enabled}
        )
