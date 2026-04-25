from __future__ import annotations

import logging

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import CONF_STATION_ID, CONF_STATION_SEARCH, DOMAIN
from .coordinator import TemperaturNuApi

_LOGGER = logging.getLogger(__name__)

_USER_STEP_SCHEMA = vol.Schema({vol.Required(CONF_STATION_SEARCH): str})
_STATION_SELECT_SCHEMA_FACTORY = lambda options: vol.Schema({vol.Required(CONF_STATION_ID): vol.In(options)})


class StationNotFoundError(HomeAssistantError):
    pass


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    def __init__(self) -> None:
        self._station_options: dict[str, str] = {}

    async def async_step_user(self, user_input: dict[str, str] | None = None):
        errors = {}

        if user_input is None:
            return self.async_show_form(step_id="user", data_schema=_USER_STEP_SCHEMA)

        station_search = user_input[CONF_STATION_SEARCH].strip()

        if not station_search:
            errors[CONF_STATION_SEARCH] = "required"
            return self.async_show_form(step_id="user", data_schema=_USER_STEP_SCHEMA, errors=errors)

        try:
            session = async_get_clientsession(self.hass)
            api = TemperaturNuApi(session)
            result = await api.async_search_stations(station_search)
            stations = result.get("stations") or []
            if not stations:
                raise StationNotFoundError

            self._station_options = {station["id"]: station.get("title", station["id"]) for station in stations}

            return await self.async_step_station_select()
        except StationNotFoundError:
            errors[CONF_STATION_SEARCH] = "station_not_found"
        except HomeAssistantError:
            _LOGGER.exception("Error searching for Temperatur.nu stations")
            errors["base"] = "cannot_connect"

        return self.async_show_form(step_id="user", data_schema=_USER_STEP_SCHEMA, errors=errors)

    async def async_step_station_select(
        self, user_input: dict[str, str] | None = None
    ):
        if user_input is None:
            return self.async_show_form(
                step_id="station_select",
                data_schema=_STATION_SELECT_SCHEMA_FACTORY(self._station_options),
            )

        station_id = user_input[CONF_STATION_ID]
        session = async_get_clientsession(self.hass)
        api = TemperaturNuApi(session)

        try:
            result = await api.async_get_station(station_id)
            stations = result.get("stations") or []
            if not stations:
                raise StationNotFoundError
        except StationNotFoundError:
            return self.async_show_form(
                step_id="station_select",
                data_schema=_STATION_SELECT_SCHEMA_FACTORY(self._station_options),
                errors={CONF_STATION_ID: "station_not_found"},
            )
        except HomeAssistantError:
            _LOGGER.exception("Error validating selected station")
            return self.async_show_form(
                step_id="station_select",
                data_schema=_STATION_SELECT_SCHEMA_FACTORY(self._station_options),
                errors={"base": "cannot_connect"},
            )

        return self.async_create_entry(
            title=f"Temperatur.nu {station_id}",
            data={
                CONF_STATION_ID: station_id,
            },
        )
