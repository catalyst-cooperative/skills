#!/usr/bin/env python3
"""Generate example datapackage assets for all four supported storage backends.

Creates four parallel example packages containing the same weather-station dataset
(5 stations, 150 daily readings) stored as:
  - CSV      → assets/examples/csv/
  - Parquet  → assets/examples/parquet/
  - DuckDB   → assets/examples/duckdb/
  - SQLite   → assets/examples/sqlite/

Each directory contains a datapackage.json descriptor and the corresponding data
file(s). Run from the skill root:

    python scripts/generate_examples.py

Requires: pandas, pyarrow, duckdb (all available in the agent-skills pixi env).
SQLite is in the Python stdlib.
"""

import hashlib
import json
import sqlite3
from pathlib import Path

import duckdb
import pandas as pd

# ---------------------------------------------------------------------------
# Sample data
# ---------------------------------------------------------------------------

STATIONS = [
    {
        "station_id": "WS-0001",
        "station_name": "Portland Airport",
        "latitude": 45.587,
        "longitude": -122.597,
        "elevation_m": 9,
        "active": True,
        "commissioned_date": "1978-01-01",
    },
    {
        "station_id": "WS-0002",
        "station_name": "Mount Hood Meadows",
        "latitude": 45.331,
        "longitude": -121.669,
        "elevation_m": 1706,
        "active": True,
        "commissioned_date": "1958-06-01",
    },
    {
        "station_id": "WS-0003",
        "station_name": "Crater Lake NPS",
        "latitude": 42.944,
        "longitude": -122.109,
        "elevation_m": 2135,
        "active": True,
        "commissioned_date": "1931-07-01",
    },
    {
        "station_id": "WS-0004",
        "station_name": "Astoria Regional Airport",
        "latitude": 46.158,
        "longitude": -123.879,
        "elevation_m": 3,
        "active": False,
        "commissioned_date": "1948-02-01",
    },
    {
        "station_id": "WS-0005",
        "station_name": "Burns Municipal Airport",
        "latitude": 43.592,
        "longitude": -118.955,
        "elevation_m": 1262,
        "active": True,
        "commissioned_date": "1954-09-01",
    },
]

# Base temps (°C) and precipitation frequency per station (Jan 2024 approximations)
_STATION_CLIMATE = {
    "WS-0001": {"min": 1.0, "max": 9.0, "precip_chance": 0.65},
    "WS-0002": {"min": -6.0, "max": 0.0, "precip_chance": 0.70},
    "WS-0003": {"min": -10.0, "max": -2.0, "precip_chance": 0.50},
    "WS-0004": {"min": 2.0, "max": 8.0, "precip_chance": 0.75},
    "WS-0005": {"min": -4.0, "max": 5.0, "precip_chance": 0.25},
}

import random  # noqa: E402

random.seed(42)

DATES = pd.date_range("2024-01-01", periods=30).strftime("%Y-%m-%d").tolist()

READINGS = []
for station in STATIONS:
    sid = station["station_id"]
    climate = _STATION_CLIMATE[sid]
    for date in DATES:
        tmin = round(climate["min"] + random.gauss(0, 1.5), 1)
        tmax = round(climate["max"] + random.gauss(0, 1.5), 1)
        if tmax < tmin:
            tmin, tmax = tmax, tmin
        if random.random() < climate["precip_chance"]:
            precip = round(random.uniform(0.5, 25.0), 1)
        else:
            precip = None  # station did not report
        READINGS.append(
            {
                "station_id": sid,
                "date": date,
                "temp_min_c": tmin,
                "temp_max_c": tmax,
                "precipitation_mm": precip,
                "wind_speed_avg_ms": round(random.uniform(0.5, 8.0), 1),
            }
        )

stations_df = pd.DataFrame(STATIONS)
readings_df = pd.DataFrame(READINGS)

# ---------------------------------------------------------------------------
# Shared descriptor schema (same for all four backends, path/format differ)
# ---------------------------------------------------------------------------

STATIONS_SCHEMA = {
    "fields": [
        {
            "name": "station_id",
            "type": "string",
            "description": "Unique identifier assigned by the network operator. Stable across all dataset versions.",
            "constraints": {
                "required": True,
                "unique": True,
                "pattern": "^WS-[0-9]{4}$",
            },
        },
        {
            "name": "station_name",
            "type": "string",
            "description": "Human-readable name of the station location (e.g. 'Portland Airport').",
        },
        {
            "name": "latitude",
            "type": "number",
            "description": "Geographic latitude of the station in decimal degrees (WGS84 datum). Positive values are north of the equator.",
            "unit": "degrees",
            "constraints": {"minimum": -90, "maximum": 90},
        },
        {
            "name": "longitude",
            "type": "number",
            "description": "Geographic longitude of the station in decimal degrees (WGS84 datum). Positive values are east of the prime meridian.",
            "unit": "degrees",
            "constraints": {"minimum": -180, "maximum": 180},
        },
        {
            "name": "elevation_m",
            "type": "integer",
            "description": "Elevation of the station above mean sea level.",
            "unit": "meters",
        },
        {
            "name": "active",
            "type": "boolean",
            "description": "Whether the station is currently operational and reporting data.",
        },
        {
            "name": "commissioned_date",
            "type": "date",
            "description": "Date the station began continuous operation.",
        },
    ],
    "primaryKey": ["station_id"],
}

READINGS_SCHEMA = {
    "fields": [
        {
            "name": "station_id",
            "type": "string",
            "description": "References stations.station_id. Every reading must belong to a known station.",
            "constraints": {"required": True},
        },
        {
            "name": "date",
            "type": "date",
            "description": "Calendar date of the observation (local time at the station).",
            "constraints": {"required": True},
        },
        {
            "name": "temp_min_c",
            "type": "number",
            "description": "Minimum air temperature recorded during the 24-hour calendar day.",
            "unit": "degrees Celsius",
        },
        {
            "name": "temp_max_c",
            "type": "number",
            "description": "Maximum air temperature recorded during the 24-hour calendar day.",
            "unit": "degrees Celsius",
        },
        {
            "name": "precipitation_mm",
            "type": "number",
            "description": "Total liquid-equivalent precipitation accumulated during the calendar day.",
            "unit": "millimeters",
            "warning": "Null values indicate the station did not report precipitation for that day — not zero precipitation. Do not substitute 0 for null in analysis. A value of 0.0 means the station reported and confirmed trace or no precipitation.",
        },
        {
            "name": "wind_speed_avg_ms",
            "type": "number",
            "description": "Average wind speed over the calendar day.",
            "unit": "meters per second",
        },
    ],
    "primaryKey": ["station_id", "date"],
    "foreignKeys": [
        {
            "fields": ["station_id"],
            "reference": {"resource": "stations", "fields": ["station_id"]},
        }
    ],
}

PACKAGE_META = {
    "name": "weather-stations",
    "title": "Example Weather Station Dataset",
    "description": "A demonstration datapackage containing two related tables: station metadata and daily temperature readings. Illustrates standard Frictionless Data Package structure including field types, constraints, foreign keys, and common non-standard extensions (unit, warning).",
    "version": "1.0.0",
    "created": "2025-01-01",
    "licenses": [
        {"name": "CC-BY-4.0", "path": "https://creativecommons.org/licenses/by/4.0/"}
    ],
    "contributors": [
        {"title": "Example Organization", "email": "data@example.org", "role": "author"}
    ],
    "sources": [
        {"title": "National Weather Service", "path": "https://www.weather.gov/"}
    ],
}

STATIONS_RESOURCE_BASE = {
    "name": "stations",
    "title": "Weather Stations",
    "description": "One row per weather monitoring station. The station_id is the stable join key used in all other tables.",
    "schema": STATIONS_SCHEMA,
}

READINGS_RESOURCE_BASE = {
    "name": "daily-readings",
    "title": "Daily Temperature and Precipitation Readings",
    "description": "Daily summary observations from each station. Note: readings before 2010-01-01 were collected using an older instrument calibration standard and may differ systematically by 0.3–0.5 °C from post-2010 readings. Do not combine pre- and post-2010 data in a single analysis without applying the calibration correction described in the methodology notes.",
    "schema": READINGS_SCHEMA,
}

ASSETS = Path(__file__).parent.parent / "assets" / "examples"


def file_stats(path: Path) -> dict:
    """Return bytes and MD5 hash for a file — useful for integrity checking."""
    data = path.read_bytes()
    return {"bytes": len(data), "hash": "md5:" + hashlib.md5(data).hexdigest()}


def write_descriptor(directory: Path, resources: list[dict]) -> None:
    descriptor = {**PACKAGE_META, "resources": resources}
    (directory / "datapackage.json").write_text(
        json.dumps(descriptor, indent=2, ensure_ascii=False) + "\n"
    )


# ---------------------------------------------------------------------------
# CSV
# ---------------------------------------------------------------------------


def generate_csv(out: Path) -> None:
    out.mkdir(parents=True, exist_ok=True)
    stations_df.to_csv(out / "stations.csv", index=False)
    readings_df.to_csv(out / "daily-readings.csv", index=False)
    write_descriptor(
        out,
        [
            {
                **STATIONS_RESOURCE_BASE,
                "path": "stations.csv",
                "format": "csv",
                "mediatype": "text/csv",
                **file_stats(out / "stations.csv"),
            },
            {
                **READINGS_RESOURCE_BASE,
                "path": "daily-readings.csv",
                "format": "csv",
                "mediatype": "text/csv",
                **file_stats(out / "daily-readings.csv"),
            },
        ],
    )
    print(f"CSV example written to {out}")


# ---------------------------------------------------------------------------
# Parquet
# ---------------------------------------------------------------------------


def generate_parquet(out: Path) -> None:
    out.mkdir(parents=True, exist_ok=True)
    stations_df.to_parquet(out / "stations.parquet", index=False)
    readings_df.to_parquet(out / "daily-readings.parquet", index=False)
    write_descriptor(
        out,
        [
            {
                **STATIONS_RESOURCE_BASE,
                "path": "stations.parquet",
                "format": "parquet",
                "mediatype": "application/parquet",
                **file_stats(out / "stations.parquet"),
            },
            {
                **READINGS_RESOURCE_BASE,
                "path": "daily-readings.parquet",
                "format": "parquet",
                "mediatype": "application/parquet",
                **file_stats(out / "daily-readings.parquet"),
            },
        ],
    )
    print(f"Parquet example written to {out}")


# ---------------------------------------------------------------------------
# DuckDB (single database file, one table per resource)
# ---------------------------------------------------------------------------


def generate_duckdb(out: Path) -> None:
    out.mkdir(parents=True, exist_ok=True)
    db_path = out / "weather.duckdb"
    db_path.unlink(missing_ok=True)
    con = duckdb.connect(str(db_path))
    con.execute("CREATE TABLE stations AS SELECT * FROM stations_df")
    con.execute('CREATE TABLE "daily-readings" AS SELECT * FROM readings_df')
    con.close()
    write_descriptor(
        out,
        [
            {
                **STATIONS_RESOURCE_BASE,
                "path": "weather.duckdb",
                "format": "duckdb",
                "mediatype": "application/octet-stream",
                "duckdb_table": "stations",
            },
            {
                **READINGS_RESOURCE_BASE,
                "path": "weather.duckdb",
                "format": "duckdb",
                "mediatype": "application/octet-stream",
                "duckdb_table": "daily-readings",
            },
        ],
    )
    print(f"DuckDB example written to {out}")


# ---------------------------------------------------------------------------
# SQLite (single database file)
# ---------------------------------------------------------------------------


def generate_sqlite(out: Path) -> None:
    out.mkdir(parents=True, exist_ok=True)
    db_path = out / "weather.sqlite"
    db_path.unlink(missing_ok=True)
    con = sqlite3.connect(str(db_path))
    stations_df.to_sql("stations", con, index=False, if_exists="replace")
    readings_df.to_sql("daily-readings", con, index=False, if_exists="replace")
    con.close()
    write_descriptor(
        out,
        [
            {
                **STATIONS_RESOURCE_BASE,
                "path": "weather.sqlite",
                "format": "sqlite",
                "mediatype": "application/vnd.sqlite3",
                "sqlite_table": "stations",
            },
            {
                **READINGS_RESOURCE_BASE,
                "path": "weather.sqlite",
                "format": "sqlite",
                "mediatype": "application/vnd.sqlite3",
                "sqlite_table": "daily-readings",
            },
        ],
    )
    print(f"SQLite example written to {out}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    generate_csv(ASSETS / "csv")
    generate_parquet(ASSETS / "parquet")
    generate_duckdb(ASSETS / "duckdb")
    generate_sqlite(ASSETS / "sqlite")
    print("Done.")
