"""Selects: heat pump mode (TC_set 40006) and regulation type (40007)."""

from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import const as c
from .coordinator import AcondConfigEntry, AcondCoordinator
from .entity import AcondEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: AcondConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up selects."""
    coordinator = entry.runtime_data
    async_add_entities([AcondModeSelect(coordinator), AcondRegulationSelect(coordinator)])


class AcondModeSelect(AcondEntity, SelectEntity):
    """Operating mode. Reads rezim_pan (30014), writes TC_set (40006)."""

    _attr_translation_key = "mode"
    _attr_options = list(c.MODE_WRITE_BITS)

    def __init__(self, coordinator: AcondCoordinator) -> None:
        super().__init__(coordinator, "mode_select", "rezim_tc", "select")

    @property
    def current_option(self) -> str | None:
        option = c.MODE_READ.get(self.coordinator.data.inputs[c.IN_MODE])
        return option if option in c.MODE_WRITE_BITS else None

    async def async_select_option(self, option: str) -> None:
        if option not in c.MODE_WRITE_BITS:
            raise ServiceValidationError(f"Unsupported mode {option}")
        keep = self.coordinator.data.holding[c.HR_TC_SET] & c.TC_SET_KEEP_MASK
        await self.coordinator.async_write(c.HR_TC_SET, keep | c.MODE_WRITE_BITS[option])


class AcondRegulationSelect(AcondEntity, SelectEntity):
    """Regulation type. Reads typ_reg_pan (30015), writes TC_set_reg (40007)."""

    _attr_translation_key = "regulation"
    _attr_options = list(c.REGULATION_OPTIONS)

    def __init__(self, coordinator: AcondCoordinator) -> None:
        super().__init__(coordinator, "regulation_select", "typ_regulace", "select")

    @property
    def current_option(self) -> str | None:
        value = self.coordinator.data.inputs[c.IN_REGULATION]
        return c.REGULATION_OPTIONS[value] if value < len(c.REGULATION_OPTIONS) else None

    async def async_select_option(self, option: str) -> None:
        await self.coordinator.async_write(c.HR_REGULATION, c.REGULATION_OPTIONS.index(option))
