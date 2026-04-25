from __future__ import annotations

from datetime import timedelta

DOMAIN = "temperaturnu"
DEFAULT_CLI = "home_assistant_temperaturnu"
SCAN_INTERVAL = timedelta(minutes=10)
API_BASE_URL = "https://api.temperatur.nu/tnu_1.20.php"
CONF_STATION_ID = "station_id"
CONF_LONG_TERM_SPAN = "long_term_span"
CONF_STATION_SEARCH = "station_search"
LONG_TERM_SPAN_OPTIONS = ["1day", "1week", "1month", "1year"]
ATTRIBUTION = "Data provided by temperatur.nu"
