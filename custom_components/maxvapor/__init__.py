"""MaxVapor e-nail integration: cloud polling over the dashboard REST API."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_API_TOKEN, Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed, ConfigEntryNotReady
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import MaxVaporApi, MaxVaporApiError, MaxVaporAuthError
from .const import DEFAULT_BASE_URL, DOMAIN
from .coordinator import MaxVaporCoordinator

PLATFORMS = [Platform.BINARY_SENSOR, Platform.CLIMATE, Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    api = MaxVaporApi(
        async_get_clientsession(hass), entry.data[CONF_API_TOKEN], DEFAULT_BASE_URL
    )
    try:
        devices = await api.list_devices()
    except MaxVaporAuthError as err:
        raise ConfigEntryAuthFailed("API token rejected") from err
    except MaxVaporApiError as err:
        raise ConfigEntryNotReady(str(err)) from err

    coordinator = MaxVaporCoordinator(hass, api, devices)
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
