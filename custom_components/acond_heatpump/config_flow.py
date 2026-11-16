"""Config flow for the Acond heat pump."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry, ConfigFlow, ConfigFlowResult, OptionsFlow
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.core import callback
from homeassistant.helpers import selector

from .const import (
    CONF_BRINE,
    CONF_CIRCUIT2,
    CONF_DEVICE_ID,
    CONF_SCAN_INTERVAL,
    DEFAULT_DEVICE_ID,
    DEFAULT_PORT,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    IN_HEARTBEAT,
    MAX_SCAN_INTERVAL,
    MIN_SCAN_INTERVAL,
)
from .modbus import AcondModbusClient, ModbusError

_LOGGER = logging.getLogger(__name__)


def _options_schema(defaults: dict[str, Any]) -> dict:
    return {
        vol.Required(
            CONF_SCAN_INTERVAL, default=defaults.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
        ): selector.NumberSelector(
            selector.NumberSelectorConfig(
                min=MIN_SCAN_INTERVAL,
                max=MAX_SCAN_INTERVAL,
                step=1,
                unit_of_measurement="s",
                mode=selector.NumberSelectorMode.BOX,
            )
        ),
        vol.Required(CONF_CIRCUIT2, default=defaults.get(CONF_CIRCUIT2, False)): bool,
        vol.Required(CONF_BRINE, default=defaults.get(CONF_BRINE, False)): bool,
    }


async def _async_test(host: str, port: int, unit: int) -> None:
    client = AcondModbusClient(host, port, unit)
    try:
        await client.read_input_registers(IN_HEARTBEAT, 1)
    finally:
        await client.close()


class AcondConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow."""

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        """Ask for host / port / Modbus ID."""
        errors: dict[str, str] = {}
        if user_input is not None:
            user_input[CONF_PORT] = int(user_input[CONF_PORT])
            user_input[CONF_DEVICE_ID] = int(user_input[CONF_DEVICE_ID])
            user_input[CONF_SCAN_INTERVAL] = int(user_input[CONF_SCAN_INTERVAL])
            await self.async_set_unique_id(
                f"{user_input[CONF_HOST]}:{user_input[CONF_PORT]}:{user_input[CONF_DEVICE_ID]}"
            )
            self._abort_if_unique_id_configured()
            try:
                await _async_test(
                    user_input[CONF_HOST], user_input[CONF_PORT], user_input[CONF_DEVICE_ID]
                )
            except ModbusError as err:
                _LOGGER.debug("Connection test failed: %s", err)
                errors["base"] = "cannot_connect"
            except Exception:
                _LOGGER.exception("Unexpected error")
                errors["base"] = "unknown"
            else:
                return self.async_create_entry(
                    title=f"Acond ({user_input[CONF_HOST]})", data=user_input
                )

        defaults = user_input or {}
        schema = vol.Schema(
            {
                vol.Required(CONF_HOST, default=defaults.get(CONF_HOST, "")): str,
                vol.Required(CONF_PORT, default=defaults.get(CONF_PORT, DEFAULT_PORT)): vol.Coerce(int),
                vol.Required(
                    CONF_DEVICE_ID, default=defaults.get(CONF_DEVICE_ID, DEFAULT_DEVICE_ID)
                ): vol.Coerce(int),
                **_options_schema(defaults),
            }
        )
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> AcondOptionsFlow:
        """Options flow."""
        return AcondOptionsFlow()


class AcondOptionsFlow(OptionsFlow):
    """Scan interval and optional circuits."""

    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        """Manage options."""
        if user_input is not None:
            user_input[CONF_SCAN_INTERVAL] = int(user_input[CONF_SCAN_INTERVAL])
            return self.async_create_entry(data=user_input)
        current = {**self.config_entry.data, **self.config_entry.options}
        return self.async_show_form(step_id="init", data_schema=vol.Schema(_options_schema(current)))
