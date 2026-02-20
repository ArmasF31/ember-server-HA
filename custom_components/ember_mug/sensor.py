"""Sensor entities for Ember Mug."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory, PERCENTAGE, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CONF_DEVICE_TYPE, DEFAULT_DEVICE_TYPE, DEVICE_TYPE_TUMBLER, DOMAIN
from .coordinator import EmberMugCoordinator


@dataclass(frozen=True, kw_only=True)
class EmberSensorDescription(SensorEntityDescription):
    value_key: str


SENSORS: tuple[EmberSensorDescription, ...] = (
    EmberSensorDescription(
        key="current_temp_c",
        name="Current Temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        value_key="current_temp_c",
    ),
    EmberSensorDescription(
        key="target_temp_c",
        name="Target Temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        value_key="target_temp_c",
    ),
    EmberSensorDescription(
        key="battery_percent",
        name="Battery",
        device_class=SensorDeviceClass.BATTERY,
        native_unit_of_measurement=PERCENTAGE,
        value_key="battery_percent",
    ),
    EmberSensorDescription(
        key="charging",
        name="Charging",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_key="charging",
    ),
    EmberSensorDescription(
        key="liquid_state",
        name="Liquid State",
        value_key="liquid_state",
    ),
    EmberSensorDescription(
        key="liquid_level",
        name="Liquid Level",
        value_key="liquid_level",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: EmberMugCoordinator = hass.data[DOMAIN]["coordinator"]
    async_add_entities(EmberMugSensor(coordinator, entry, description) for description in SENSORS)


class EmberMugSensor(CoordinatorEntity[EmberMugCoordinator], SensorEntity):
    """Coordinator-backed sensor."""

    entity_description: EmberSensorDescription

    def __init__(
        self,
        coordinator: EmberMugCoordinator,
        entry: ConfigEntry,
        description: EmberSensorDescription,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"
        self._attr_has_entity_name = True

        device_type = entry.options.get(CONF_DEVICE_TYPE, entry.data.get(CONF_DEVICE_TYPE, DEFAULT_DEVICE_TYPE))
        model = "Ember Tumbler" if device_type == DEVICE_TYPE_TUMBLER else "Ember Mug"

        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": entry.title,
            "manufacturer": "Ember",
            "model": model,
        }

    @property
    def native_value(self):
        if self.coordinator.data is None:
            return None
        return getattr(self.coordinator.data, self.entity_description.value_key)
