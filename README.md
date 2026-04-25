# ha-temp.nu

A Home Assistant custom integration for temperatur.nu.

## Features

- Select a temperatur.nu station by search and station identifier
- Exposes current temperature and station information
- Exposes long-term daily summary data for the selected station
- Supports Home Assistant config flow and HACS custom repository installation

## Installation

1. Add this repository to HACS as a custom repository using the category `Integration`.
2. Install the `Temperatur.nu` integration from HACS.
3. Restart Home Assistant.
4. Configure the integration via Settings > Devices & Services > Add Integration > Temperatur.nu.

## Configuration

During setup you can search for a station and then select it from the matching results.

The integration will fetch the latest station observation and daily summary data from `https://api.temperatur.nu/tnu_1.20.php`.

## Notes

- The integration uses a 10-minute polling interval to stay within the temperatur.nu API usage guidelines.
- If you have a signed client key, this integration can be extended with configurable signing support.
