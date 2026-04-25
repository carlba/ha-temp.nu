from __future__ import annotations

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorEntityDescription, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import ATTRIBUTION, DOMAIN
from .coordinator import TemperatureNuDataUpdateCoordinator

_SENSOR_ICONS: dict[str, str] = {
    "temperature": "mdi:thermometer",
    "daily_average": "mdi:thermometer-lines",
    "daily_min": "mdi:thermometer-lines",
    "daily_max": "mdi:thermometer-lines",
}

SENSOR_TYPES: tuple[SensorEntityDescription, ...] = (
    SensorEntityDescription(
        key="temperature",
        name="Current temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="daily_average",
        name="Daily average temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="daily_min",
        name="Daily minimum temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="daily_max",
        name="Daily maximum temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
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


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: TemperatureNuDataUpdateCoordinator = entry.runtime_data
    async_add_entities(TemperaturNuSensor(coordinator, description) for description in SENSOR_TYPES)


class TemperaturNuSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator: TemperatureNuDataUpdateCoordinator, description: SensorEntityDescription) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        station_title = coordinator.data.get("station", {}).get("title", "Temperatur.nu")
        self._attr_name = f"{station_title} {description.name}"
        self._attr_unique_id = f"{DOMAIN}_{coordinator.station_id}_{description.key}"
        self._attr_attribution = ATTRIBUTION
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.station_id)},
            name=station_title,
            manufacturer="temperatur.nu",
            entry_type=DeviceEntryType.SERVICE,
        )

    @property
    def icon(self) -> str | None:
        return _SENSOR_ICONS.get(self.entity_description.key)

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
