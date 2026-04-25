from __future__ import annotations

import logging

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription, SensorStateClass
from homeassistant.const import TEMP_CELSIUS
from homeassistant.helpers.entity import CoordinatorEntity

from .const import ATTRIBUTION, DOMAIN
from .coordinator import TemperatureNuDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


SENSOR_TYPES: tuple[SensorEntityDescription, ...] = (
    SensorEntityDescription(
        key="temperature",
        name="Current temperature",
        native_unit_of_measurement=TEMP_CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="daily_average",
        name="Daily average temperature",
        native_unit_of_measurement=TEMP_CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="daily_min",
        name="Daily minimum temperature",
        native_unit_of_measurement=TEMP_CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="daily_max",
        name="Daily maximum temperature",
        native_unit_of_measurement=TEMP_CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="last_update",
        name="Station last update",
    ),
    SensorEntityDescription(
        key="source_info",
        name="Source information",
    ),
)


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator: TemperatureNuDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities = [TemperaturNuSensor(coordinator, description) for description in SENSOR_TYPES]
    async_add_entities(entities)


class TemperaturNuSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator: TemperatureNuDataUpdateCoordinator, description: SensorEntityDescription) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        station_title = coordinator.data.get("station", {}).get("title", "Temperatur.nu")
        self._attr_name = f"{station_title} {description.name}"
        self._attr_unique_id = f"temperaturnu_{coordinator.station_id}_{description.key}"
        self._attr_attribution = ATTRIBUTION

    @property
    def native_value(self):
        station = self.coordinator.data.get("station", {})
        daily = self.coordinator.data.get("daily", [])
        key = self.entity_description.key

        if key == "temperature":
            temp = station.get("temp")
            try:
                return float(temp)
            except (TypeError, ValueError):
                return None

        if key == "daily_average":
            values = [float(day.get("average")) for day in daily if day.get("average") not in (None, "")]
            return sum(values) / len(values) if values else None

        if key == "daily_min":
            values = [float(day.get("min")) for day in daily if day.get("min") not in (None, "")]
            return min(values) if values else None

        if key == "daily_max":
            values = [float(day.get("max")) for day in daily if day.get("max") not in (None, "")]
            return max(values) if values else None

        if key == "last_update":
            return station.get("lastUpdate")

        if key == "source_info":
            return station.get("sourceInfo")

        return None
