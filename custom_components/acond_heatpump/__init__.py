"""Acond heat pump integration (Modbus TCP)."""

from __future__ import annotations

from pathlib import Path

from homeassistant.components.http import StaticPathConfig
from homeassistant.const import CONF_HOST, CONF_PORT, Platform
from homeassistant.core import HomeAssistant

from .const import (
    CONF_DEVICE_ID,
    CONF_SCAN_INTERVAL,
    DEFAULT_DEVICE_ID,
    DEFAULT_PORT,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    STATIC_URL,
)
from .coordinator import AcondConfigEntry, AcondCoordinator
from .modbus import AcondModbusClient

PLATFORMS: list[Platform] = [
    Platform.BINARY_SENSOR,
    Platform.CLIMATE,
    Platform.NUMBER,
    Platform.SELECT,
    Platform.SENSOR,
]


async def _async_register_static(hass: HomeAssistant) -> None:
    """Serve the dashboard SVGs at /acond_heatpump/... (once per HA run)."""
    key = f"{DOMAIN}_static"
    if hass.data.get(key):
        return
    hass.data[key] = True
    await hass.http.async_register_static_paths(
        [StaticPathConfig(STATIC_URL, str(Path(__file__).parent / "www"), True)]
    )


async def async_setup_entry(hass: HomeAssistant, entry: AcondConfigEntry) -> bool:
    """Set up from a config entry."""
    conf = {**entry.data, **entry.options}
    client = AcondModbusClient(
        conf[CONF_HOST],
        conf.get(CONF_PORT, DEFAULT_PORT),
        conf.get(CONF_DEVICE_ID, DEFAULT_DEVICE_ID),
    )
    coordinator = AcondCoordinator(
        hass, entry, client, conf.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
    )
    try:
        await coordinator.async_config_entry_first_refresh()
    except Exception:
        await client.close()
        raise

    entry.runtime_data = coordinator
    if hass.http is not None:
        await _async_register_static(hass)

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(_async_reload))
    return True


async def _async_reload(hass: HomeAssistant, entry: AcondConfigEntry) -> None:
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: AcondConfigEntry) -> bool:
    """Unload a config entry."""
    unloaded = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unloaded:
        await entry.runtime_data.client.close()
    return unloaded
