"""End-to-end tests against the fake heat pump."""

from __future__ import annotations

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.acond_heatpump.const import (
    CONF_BRINE,
    CONF_CIRCUIT2,
    CONF_DEVICE_ID,
    CONF_SCAN_INTERVAL,
    DOMAIN,
)


def _data(port: int) -> dict:
    return {
        CONF_HOST: "127.0.0.1",
        CONF_PORT: port,
        CONF_DEVICE_ID: 1,
        CONF_SCAN_INTERVAL: 10,
        CONF_CIRCUIT2: False,
        CONF_BRINE: False,
    }


async def _setup(hass: HomeAssistant, port: int) -> MockConfigEntry:
    entry = MockConfigEntry(domain=DOMAIN, data=_data(port), unique_id="x")
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    return entry


async def test_config_flow(hass: HomeAssistant, fake_acond) -> None:
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] is FlowResultType.FORM
    result = await hass.config_entries.flow.async_configure(result["flow_id"], _data(fake_acond.port))
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["title"] == "Acond (127.0.0.1)"


async def test_config_flow_cannot_connect(hass: HomeAssistant, socket_enabled) -> None:
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(result["flow_id"], _data(1))
    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": "cannot_connect"}


async def test_entities(hass: HomeAssistant, fake_acond) -> None:
    await _setup(hass, fake_acond.port)

    s = hass.states.get("sensor.acond_okruh_1_aktualni")
    assert s.state == "20.8"
    assert s.attributes["friendly_name"] == "Acond Circuit 1 actual"
    assert hass.states.get("sensor.acond_venkovni_teplota").state == "-3.5"
    assert hass.states.get("sensor.acond_tuv_aktualni").state == "44.1"
    assert hass.states.get("sensor.acond_vystupni_voda").state == "33.1"
    assert hass.states.get("sensor.acond_rezim").state == "auto"
    assert hass.states.get("sensor.acond_typ_regulace").state == "acondtherm"
    assert hass.states.get("sensor.acond_heartbeat").state == "42"
    # optional entities are not created
    assert hass.states.get("sensor.acond_okruh_2_aktualni") is None
    assert hass.states.get("sensor.acond_solanka") is None

    assert hass.states.get("binary_sensor.acond_kompresor_bezi").state == "on"
    assert hass.states.get("binary_sensor.acond_porucha").state == "off"
    assert hass.states.get("binary_sensor.acond_chlazeni").state == "on"
    assert hass.states.get("binary_sensor.acond_ohrev_tuv").state == "off"

    climate = hass.states.get("climate.acond_okruh_1")
    assert climate.attributes["current_temperature"] == 20.8
    assert climate.attributes["temperature"] == 21.5
    assert climate.attributes["hvac_action"] == "heating"
    assert hass.states.get("climate.acond_tuv").attributes["hvac_action"] == "idle"

    assert hass.states.get("select.acond_rezim_tc").state == "auto"
    assert hass.states.get("select.acond_typ_regulace").state == "acondtherm"
    assert hass.states.get("number.acond_zpatecka_manual").state == "30.0"


async def test_writes(hass: HomeAssistant, fake_acond) -> None:
    await _setup(hass, fake_acond.port)

    await hass.services.async_call(
        "climate", "set_temperature",
        {"entity_id": "climate.acond_okruh_1", "temperature": 22.5}, blocking=True,
    )
    assert fake_acond.writes[-1] == (0, 225)
    assert hass.states.get("climate.acond_okruh_1").attributes["temperature"] == 22.5

    await hass.services.async_call(
        "climate", "set_temperature",
        {"entity_id": "climate.acond_tuv", "temperature": 50}, blocking=False,
    )
    await hass.async_block_till_done()

    # mode keeps summer bit 8, replaces mode bits
    await hass.services.async_call(
        "select", "select_option",
        {"entity_id": "select.acond_rezim_tc", "option": "off"}, blocking=True,
    )
    assert fake_acond.writes[-1] == (5, 0b1_0000_1000)

    await hass.services.async_call(
        "select", "select_option",
        {"entity_id": "select.acond_typ_regulace", "option": "equitherm"}, blocking=True,
    )
    assert fake_acond.writes[-1] == (6, 1)

    await hass.services.async_call(
        "number", "set_value",
        {"entity_id": "number.acond_zpatecka_manual", "value": 35.5}, blocking=True,
    )
    assert fake_acond.writes[-1] == (7, 355)


async def test_options_add_circuit2(hass: HomeAssistant, fake_acond) -> None:
    entry = await _setup(hass, fake_acond.port)
    result = await hass.config_entries.options.async_init(entry.entry_id)
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {CONF_SCAN_INTERVAL: 15, CONF_CIRCUIT2: True, CONF_BRINE: True}
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY
    await hass.async_block_till_done()
    assert hass.states.get("climate.acond_okruh_2") is not None
    assert hass.states.get("sensor.acond_solanka") is not None


async def test_unload(hass: HomeAssistant, fake_acond) -> None:
    entry = await _setup(hass, fake_acond.port)
    assert await hass.config_entries.async_unload(entry.entry_id)
    await hass.async_block_till_done()
