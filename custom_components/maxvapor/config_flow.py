"""Config flow: one account per entry, authenticated with an API token."""
from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_API_TOKEN
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import MaxVaporApi, MaxVaporApiError, MaxVaporAuthError
from .const import DEFAULT_BASE_URL, DOMAIN

STEP_USER_SCHEMA = vol.Schema({vol.Required(CONF_API_TOKEN): str})


class MaxVaporConfigFlow(ConfigFlow, domain=DOMAIN):
    """Ask for the dashboard API token and validate it."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            api = MaxVaporApi(
                async_get_clientsession(self.hass),
                user_input[CONF_API_TOKEN].strip(),
                DEFAULT_BASE_URL,
            )
            try:
                devices = await api.list_devices()
            except MaxVaporAuthError:
                errors["base"] = "invalid_auth"
            except MaxVaporApiError:
                errors["base"] = "cannot_connect"
            else:
                await self.async_set_unique_id(DOMAIN)
                self._abort_if_unique_id_configured()
                title = devices[0]["name"] if devices else "MaxVapor"
                return self.async_create_entry(
                    title=title,
                    data={CONF_API_TOKEN: user_input[CONF_API_TOKEN].strip()},
                )

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_SCHEMA, errors=errors
        )
