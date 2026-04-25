from __future__ import annotations

from datetime import datetime
import logging

from homeassistant.components.weather import WeatherEntity
from homeassistant.const import TEMP_CELSIUS
from homeassistant.helpers import entity_platform
from homeassistant.util import dt as dt_util

from .const import ATTRIBUTION, DOMAIN
from .coordinator import TemperatureNuDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator: TemperatureNuDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([TemperaturNuWeather(coordinator)])


class TemperaturNuWeather(WeatherEntity):
    def __init__(self, coordinator: TemperatureNuDataUpdateCoordinator) -> None:
        self.coordinator = coordinator

    @property
    def unique_id(self) -> str:
        return f"temperaturnu_{self.coordinator.station_id}"

    @property
    def name(self) -> str:
        station = self.coordinator.data["station"]
        return station.get("title", "Temperatur.nu")

    @property
    def native_temperature(self) -> float | None:
        station = self.coordinator.data["station"]
        try:
            return float(station.get("temp"))
        except (TypeError, ValueError):
            return None

    @property
    def temperature_unit(self) -> str:
        return TEMP_CELSIUS

    @property
    def condition(self) -> str:
        return "unknown"

    @property
    def attribution(self) -> str:
        return ATTRIBUTION

    @property
    def available(self) -> bool:
        return self.coordinator.last_update_success

    @property
    def extra_state_attributes(self) -> dict[str, object]:
        station = self.coordinator.data["station"]
        return {
            "station_id": self.coordinator.station_id,
            "last_update": station.get("lastUpdate"),
            "source_info": station.get("sourceInfo"),
            "sensor_type": station.get("sensorType"),
            "station_url": station.get("url"),
        }

    @property
    def native_forecast(self) -> list[dict[str, object]]:
        forecast_data = []
        for day in self.coordinator.data.get("daily", []):
            date_value = day.get("date")
            if not date_value:
                continue

            try:
                date = datetime.fromisoformat(date_value)
            except ValueError:
                try:
                    date = dt_util.parse_date(date_value)
                except ValueError:
                    continue

            try:
                average = float(day.get("average"))
            except (TypeError, ValueError):
                average = None
            try:
                low = float(day.get("min"))
            except (TypeError, ValueError):
                low = None
            try:
                high = float(day.get("max"))
            except (TypeError, ValueError):
                high = None

            forecast_data.append(
                {
                    "datetime": dt_util.as_utc(dt_util.as_datetime(date)),
                    "temperature": average,
                    "templow": low,
                    "temperature_high": high,
                    "condition": "unknown",
                }
            )

        return forecast_data
