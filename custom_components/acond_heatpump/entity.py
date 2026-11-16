"""Base entity."""

from __future__ import annotations

from homeassistant.const import CONF_HOST
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MANUFACTURER, MODEL
from .coordinator import AcondCoordinator


class AcondEntity(CoordinatorEntity[AcondCoordinator]):
    """Common device info and entity id handling.

    Entity ids are fixed to the `<domain>.acond_<object_id>` form used by the
    bundled dashboard (HA appends _2 etc. if the id is already taken).
    """

    _attr_has_entity_name = True

    def __init__(self, coordinator: AcondCoordinator, key: str, object_id: str, platform: str) -> None:
        super().__init__(coordinator)
        entry = coordinator.config_entry
        self._attr_unique_id = f"{entry.entry_id}_{key}"
        self.entity_id = f"{platform}.acond_{object_id}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="Acond",
            manufacturer=MANUFACTURER,
            model=MODEL,
            configuration_url=f"http://{entry.data[CONF_HOST]}/",
        )
