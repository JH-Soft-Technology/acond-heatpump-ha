"""Thermostats: circuit 1, optional circuit 2 and DHW.

Current temperature comes from the input register (sensor), target is the
holding register the heat pump reads (written by HA).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from homeassistant.components.climate import (
    ClimateEntity,
    ClimateEntityDescription,
    ClimateEntityFeature,
    HVACAction,
    HVACMode,
)
from homeassistant.const import ATTR_TEMPERATURE, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import const as c
from .coordinator import AcondConfigEntry, AcondCoordinator
from .entity import AcondEntity


@dataclass(frozen=True, kw_only=True)
class AcondClimateDescription(ClimateEntityDescription):
    """Thermostat description."""

    object_id: str
    current_reg: int  # input
    target_reg: int  # holding
    activity_bit: int  # TC_status bit meaning "this circuit is being heated"
    min_temp: float
    max_temp: float
    step: float
    option: str | None = None


CLIMATES: tuple[AcondClimateDescription, ...] = (
    AcondClimateDescription(
        key="circuit1", translation_key="circuit1", object_id="okruh_1",
        current_reg=c.IN_T_ACT_INDOOR1, target_reg=c.HR_T_SET_INDOOR1,
        activity_bit=c.BIT_CIRC1, min_temp=10, max_temp=30, step=0.5,
    ),
    AcondClimateDescription(
        key="circuit2", translation_key="circuit2", object_id="okruh_2",
        current_reg=c.IN_T_ACT_INDOOR2, target_reg=c.HR_T_SET_INDOOR2,
        activity_bit=c.BIT_CIRC2, min_temp=10, max_temp=30, step=0.5, option=c.CONF_CIRCUIT2,
    ),
    AcondClimateDescription(
        key="dhw", translation_key="dhw", object_id="tuv",
        current_reg=c.IN_T_ACT_DHW, target_reg=c.HR_T_SET_DHW,
        activity_bit=c.BIT_DHW, min_temp=10, max_temp=46, step=1,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: AcondConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up thermostats."""
    coordinator = entry.runtime_data
    opts = {**entry.data, **entry.options}
    async_add_entities(
        AcondClimate(coordinator, desc)
        for desc in CLIMATES
        if desc.option is None or opts.get(desc.option)
    )


class AcondClimate(AcondEntity, ClimateEntity):
    """Target temperature thermostat."""

    entity_description: AcondClimateDescription
    _attr_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_hvac_modes = [HVACMode.HEAT]
    _attr_hvac_mode = HVACMode.HEAT
    _attr_supported_features = ClimateEntityFeature.TARGET_TEMPERATURE

    def __init__(self, coordinator: AcondCoordinator, description: AcondClimateDescription) -> None:
        super().__init__(coordinator, description.key, description.object_id, "climate")
        self.entity_description = description
        self._attr_min_temp = description.min_temp
        self._attr_max_temp = description.max_temp
        self._attr_target_temperature_step = description.step

    @property
    def current_temperature(self) -> float | None:
        return self.coordinator.data.temp(self.entity_description.current_reg)

    @property
    def target_temperature(self) -> float | None:
        value = self.coordinator.data.temp(self.entity_description.target_reg, holding=True)
        # 0 = never written / out of range -> unknown
        return value if value >= self.entity_description.min_temp else None

    @property
    def hvac_action(self) -> HVACAction:
        data = self.coordinator.data
        if not data.bit(c.IN_STATUS, c.BIT_ON):
            return HVACAction.OFF
        if data.bit(c.IN_STATUS, self.entity_description.activity_bit) and data.bit(
            c.IN_STATUS, c.BIT_RUNNING
        ):
            return HVACAction.HEATING
        return HVACAction.IDLE

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """Only HEAT is supported; mode switching is done by the mode select."""

    async def async_set_temperature(self, **kwargs: Any) -> None:
        """Write target temperature (x10)."""
        if (temp := kwargs.get(ATTR_TEMPERATURE)) is None:
            return
        temp = min(max(float(temp), self.min_temp), self.max_temp)
        await self.coordinator.async_write(self.entity_description.target_reg, round(temp * 10))
