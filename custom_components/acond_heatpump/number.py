"""Number: return water target for manual regulation (40008)."""

from __future__ import annotations

from homeassistant.components.number import NumberDeviceClass, NumberEntity, NumberMode
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import const as c
from .coordinator import AcondConfigEntry, AcondCoordinator
from .entity import AcondEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: AcondConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up numbers."""
    async_add_entities([AcondReturnTarget(entry.runtime_data)])


class AcondReturnTarget(AcondEntity, NumberEntity):
    """Manual-mode return water target."""

    _attr_translation_key = "return_manual"
    _attr_device_class = NumberDeviceClass.TEMPERATURE
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_native_min_value = 20
    _attr_native_max_value = 55
    _attr_native_step = 0.5
    _attr_mode = NumberMode.BOX

    def __init__(self, coordinator: AcondCoordinator) -> None:
        super().__init__(coordinator, "return_manual", "zpatecka_manual", "number")

    @property
    def native_value(self) -> float:
        return self.coordinator.data.temp(c.IN_T_SET_RETURN)

    async def async_set_native_value(self, value: float) -> None:
        await self.coordinator.async_write(c.HR_T_SET_RETURN, round(value * 10))
