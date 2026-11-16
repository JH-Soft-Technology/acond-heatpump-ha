"""Sensors (input registers 30001-30018)."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import EntityCategory, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import const as c
from .coordinator import AcondConfigEntry, AcondCoordinator, AcondData
from .entity import AcondEntity


@dataclass(frozen=True, kw_only=True)
class AcondSensorDescription(SensorEntityDescription):
    """Sensor description."""

    object_id: str
    value_fn: Callable[[AcondData], float | int | str | None]
    option: str | None = None  # CONF_CIRCUIT2 / CONF_BRINE when optional


def _temp(key: str, object_id: str, index: int, *, measurement: bool = True, option: str | None = None) -> AcondSensorDescription:
    return AcondSensorDescription(
        key=key,
        translation_key=key,
        object_id=object_id,
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT if measurement else None,
        suggested_display_precision=1,
        value_fn=lambda d, i=index: d.temp(i),
        option=option,
    )


SENSORS: tuple[AcondSensorDescription, ...] = (
    _temp("circuit1_target", "okruh_1_zadana", c.IN_T_SET_INDOOR1, measurement=False),
    _temp("circuit1_actual", "okruh_1_aktualni", c.IN_T_ACT_INDOOR1),
    _temp("circuit2_target", "okruh_2_zadana", c.IN_T_SET_INDOOR2, measurement=False, option=c.CONF_CIRCUIT2),
    _temp("circuit2_actual", "okruh_2_aktualni", c.IN_T_ACT_INDOOR2, option=c.CONF_CIRCUIT2),
    _temp("dhw_target", "tuv_zadana", c.IN_T_SET_DHW, measurement=False),
    _temp("dhw_actual", "tuv_aktualni", c.IN_T_ACT_DHW),
    _temp("return_target", "zpatecka_zadana", c.IN_T_SET_RETURN, measurement=False),
    _temp("return_actual", "zpatecka_aktualni", c.IN_T_ACT_RETURN),
    _temp("outdoor", "venkovni_teplota", c.IN_T_AIR),
    _temp("brine", "solanka", c.IN_T_BRINE, option=c.CONF_BRINE),
    _temp("flow", "vystupni_voda", c.IN_T_OUTLET),
    AcondSensorDescription(
        key="mode",
        translation_key="mode",
        object_id="rezim",
        device_class=SensorDeviceClass.ENUM,
        options=c.MODE_OPTIONS,
        value_fn=lambda d: c.MODE_READ.get(d.inputs[c.IN_MODE]),
    ),
    AcondSensorDescription(
        key="regulation",
        translation_key="regulation",
        object_id="typ_regulace",
        device_class=SensorDeviceClass.ENUM,
        options=c.REGULATION_OPTIONS,
        value_fn=lambda d: c.REGULATION_OPTIONS[d.inputs[c.IN_REGULATION]]
        if d.inputs[c.IN_REGULATION] < len(c.REGULATION_OPTIONS)
        else None,
    ),
    AcondSensorDescription(
        key="status",
        translation_key="status",
        object_id="tc_status",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda d: d.inputs[c.IN_STATUS],
    ),
    AcondSensorDescription(
        key="tc_set",
        translation_key="tc_set",
        object_id="tc_set_raw",
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
        value_fn=lambda d: d.holding[c.HR_TC_SET],
    ),
    AcondSensorDescription(
        key="heartbeat",
        translation_key="heartbeat",
        object_id="heartbeat",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda d: d.inputs[c.IN_HEARTBEAT],
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: AcondConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up sensors."""
    coordinator = entry.runtime_data
    opts = {**entry.data, **entry.options}
    async_add_entities(
        AcondSensor(coordinator, desc)
        for desc in SENSORS
        if desc.option is None or opts.get(desc.option)
    )


class AcondSensor(AcondEntity, SensorEntity):
    """Register backed sensor."""

    entity_description: AcondSensorDescription

    def __init__(self, coordinator: AcondCoordinator, description: AcondSensorDescription) -> None:
        super().__init__(coordinator, description.key, description.object_id, "sensor")
        self.entity_description = description

    @property
    def native_value(self) -> float | int | str | None:
        return self.entity_description.value_fn(self.coordinator.data)
