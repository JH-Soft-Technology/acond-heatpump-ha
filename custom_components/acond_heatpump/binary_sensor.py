"""Binary sensors decoded from TC_status (30007)."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import const as c
from .coordinator import AcondConfigEntry, AcondCoordinator
from .entity import AcondEntity


@dataclass(frozen=True, kw_only=True)
class AcondBinaryDescription(BinarySensorEntityDescription):
    """Status bit description."""

    object_id: str
    bit: int
    option: str | None = None


BINARY_SENSORS: tuple[AcondBinaryDescription, ...] = (
    AcondBinaryDescription(key="on", translation_key="on", object_id="tc_zapnuto", bit=c.BIT_ON),
    AcondBinaryDescription(
        key="running", translation_key="running", object_id="kompresor_bezi",
        bit=c.BIT_RUNNING, device_class=BinarySensorDeviceClass.RUNNING,
    ),
    AcondBinaryDescription(
        key="fault", translation_key="fault", object_id="porucha",
        bit=c.BIT_FAULT, device_class=BinarySensorDeviceClass.PROBLEM,
    ),
    AcondBinaryDescription(
        key="dhw_heating", translation_key="dhw_heating", object_id="ohrev_tuv",
        bit=c.BIT_DHW, device_class=BinarySensorDeviceClass.HEAT,
    ),
    AcondBinaryDescription(
        key="circulation1", translation_key="circulation1", object_id="obeh_okruh_1",
        bit=c.BIT_CIRC1, device_class=BinarySensorDeviceClass.RUNNING,
    ),
    AcondBinaryDescription(
        key="circulation2", translation_key="circulation2", object_id="obeh_okruh_2",
        bit=c.BIT_CIRC2, device_class=BinarySensorDeviceClass.RUNNING, option=c.CONF_CIRCUIT2,
    ),
    AcondBinaryDescription(key="defrost", translation_key="defrost", object_id="odtavani", bit=c.BIT_DEFROST),
    AcondBinaryDescription(
        key="backup_heater", translation_key="backup_heater", object_id="bivalence",
        bit=c.BIT_AUX, device_class=BinarySensorDeviceClass.HEAT,
    ),
    AcondBinaryDescription(key="summer", translation_key="summer", object_id="letni_provoz", bit=c.BIT_SUMMER),
    AcondBinaryDescription(
        key="brine_circulation", translation_key="brine_circulation", object_id="obeh_solanky",
        bit=c.BIT_BRINE, device_class=BinarySensorDeviceClass.RUNNING, option=c.CONF_BRINE,
    ),
    AcondBinaryDescription(
        key="cooling", translation_key="cooling", object_id="chlazeni",
        bit=c.BIT_COOLING, device_class=BinarySensorDeviceClass.COLD,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: AcondConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up binary sensors."""
    coordinator = entry.runtime_data
    opts = {**entry.data, **entry.options}
    async_add_entities(
        AcondBinarySensor(coordinator, desc)
        for desc in BINARY_SENSORS
        if desc.option is None or opts.get(desc.option)
    )


class AcondBinarySensor(AcondEntity, BinarySensorEntity):
    """TC_status bit."""

    entity_description: AcondBinaryDescription

    def __init__(self, coordinator: AcondCoordinator, description: AcondBinaryDescription) -> None:
        super().__init__(coordinator, description.key, description.object_id, "binary_sensor")
        self.entity_description = description

    @property
    def is_on(self) -> bool:
        return self.coordinator.data.bit(c.IN_STATUS, self.entity_description.bit)
