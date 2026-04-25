from __future__ import annotations

import logging

from aiohttp import ClientError, ClientTimeout
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import API_BASE_URL, CONF_LONG_TERM_SPAN, CONF_STATION_ID, DEFAULT_CLI, SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)

_REQUEST_TIMEOUT = ClientTimeout(total=30)


class TemperaturNuApi:
    def __init__(self, session):
        self._session = session

    async def async_get_json(self, params: dict[str, str]) -> dict:
        try:
            async with self._session.get(
                API_BASE_URL,
                params={**params, "cli": DEFAULT_CLI},
                timeout=_REQUEST_TIMEOUT,
            ) as response:
                if response.status != 200:
                    raise UpdateFailed("Unexpected status code %s from temperatur.nu API" % response.status)
                return await response.json()
        except ClientError as err:
            raise UpdateFailed("Unable to fetch data from temperatur.nu: %s" % err) from err

    async def async_search_stations(self, query: str) -> dict:
        return await self.async_get_json({"search": query, "verbose": ""})

    async def async_get_station(self, station_id: str) -> dict:
        return await self.async_get_json({"p": station_id, "verbose": ""})

    async def async_get_daily(self, station_id: str, span: str) -> dict:
        return await self.async_get_json({"p": station_id, "daily": "1", "span": span})


class TemperatureNuDataUpdateCoordinator(DataUpdateCoordinator):
    def __init__(self, hass: HomeAssistant, session, config_data: dict[str, str]) -> None:
        self.api = TemperaturNuApi(session)
        self.station_id = config_data[CONF_STATION_ID]
        self.long_term_span = config_data.get(CONF_LONG_TERM_SPAN, "1week")

        super().__init__(
            hass,
            _LOGGER,
            name="Temperatur.nu",
            update_interval=SCAN_INTERVAL,
        )

    async def _async_update_data(self) -> dict[str, object]:
        station_response = await self.api.async_get_station(self.station_id)
        stations = station_response.get("stations") or []
        if not stations:
            raise UpdateFailed("No station data received from temperatur.nu")

        station = stations[0]
        daily_data: list[dict[str, object]] = []
        try:
            daily_response = await self.api.async_get_daily(self.station_id, self.long_term_span)
            daily_stations = daily_response.get("stations") or []
            if daily_stations:
                daily_data = daily_stations[0].get("daily", []) or []
        except UpdateFailed as err:
            _LOGGER.debug("Daily data request failed: %s", err)

        return {
            "station": station,
            "daily": daily_data,
        }
