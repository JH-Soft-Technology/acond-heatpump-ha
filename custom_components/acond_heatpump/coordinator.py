"""Data update coordinator for the Acond heat pump."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, HOLDING_COUNT, INPUT_COUNT
from .modbus import AcondModbusClient, ModbusError, to_int16

_LOGGER = logging.getLogger(__name__)


@dataclass
class AcondData:
    """Raw register snapshot."""

    inputs: list[int]
    holding: list[int]

    def temp(self, index: int, holding: bool = False) -> float:
        """Temperature (int16 x10) as °C."""
        regs = self.holding if holding else self.inputs
        return to_int16(regs[index]) / 10

    def bit(self, index: int, bit: int) -> bool:
        """Bit of an input register."""
        return bool(self.inputs[index] >> bit & 1)


type AcondConfigEntry = ConfigEntry[AcondCoordinator]


class AcondCoordinator(DataUpdateCoordinator[AcondData]):
    """Polls input 30001-30018 and holding 40001-40012 in two requests."""

    config_entry: AcondConfigEntry

    def __init__(
        self,
        hass: HomeAssistant,
        entry: AcondConfigEntry,
        client: AcondModbusClient,
        scan_interval: int,
    ) -> None:
        super().__init__(
            hass,
            _LOGGER,
            config_entry=entry,
            name=DOMAIN,
            update_interval=timedelta(seconds=scan_interval),
        )
        self.client = client

    async def _async_update_data(self) -> AcondData:
        try:
            inputs = await self.client.read_input_registers(0, INPUT_COUNT)
            holding = await self.client.read_holding_registers(0, HOLDING_COUNT)
        except ModbusError as err:
            raise UpdateFailed(str(err)) from err
        return AcondData(inputs=inputs, holding=holding)

    async def async_write(self, address: int, value: int) -> None:
        """Write a holding register, update the snapshot and refresh."""
        try:
            await self.client.write_register(address, value)
        except ModbusError as err:
            raise HomeAssistantError(f"Write of holding register {address} failed: {err}") from err
        if self.data is not None:
            self.data.holding[address] = value & 0xFFFF
            self.async_update_listeners()
        await self.async_request_refresh()
