#!/usr/bin/env python3
"""Generate example datapackage assets for all four supported storage backends.

Creates two parallel sets of examples — one for each major revision of the
Frictionless Data Package specification — each containing the same
weather-station dataset (5 stations, 30 daily readings) stored as:

  v1/csv/     — tabular-data-package with tabular-data-resource (fully spec-compliant)
  v1/parquet/ — data-package with community Parquet extension pattern
  v1/duckdb/  — data-package with community duckdb_table extension pattern
  v1/sqlite/  — data-package with community sqlite_table extension pattern

  v2/csv/     — $schema v2 descriptor with CSV resources
  v2/parquet/ — $schema v2 descriptor with Parquet resources
  v2/duckdb/  — $schema v2 descriptor with duckdb_table extension
  v2/sqlite/  — $schema v2 descriptor with sqlite_table extension

The data files are identical across versions; only the descriptor structure and
content differ, illustrating the key breaking changes between v1 and v2:

  - Package-level identifier: v1 uses "profile", v2 uses "$schema"
  - Contributors: v1 uses "role" (string), v2 uses "roles" (array)
  - Resource profile: v1 CSV resources declare "profile": "tabular-data-resource"
  - Version field: v1 spec doesn't define "version"; v2 does (we omit it from v1)
  - Non-CSV backends: not defined in either spec; community patterns apply to both

Run from the skill root:

    python scripts/generate_examples.py

Requires: pandas, pyarrow, duckdb (all available in the agent-skills pixi env).
SQLite is in the Python stdlib.
"""

import hashlib
import json
import random
import sqlite3
from functools import cache
from pathlib import Path
from typing import Any, TypedDict

import duckdb
import pandas as pd
from duckdb import DuckDBPyConnection


class Station(TypedDict):
    station_id: str
    station_name: str
    latitude: float
    longitude: float
    elevation_m: int
    active: bool
    commissioned_date: str


class ClimateParams(TypedDict):
    min: float
    max: float
    precip_chance: float


class Reading(TypedDict):
    station_id: str
    date: str
    temp_min_c: float
    temp_max_c: float
    precipitation_mm: float | None
    wind_speed_avg_ms: float


class FileStats(TypedDict):
    bytes: int
    hash: str


# ---------------------------------------------------------------------------
# Sample data (identical for both spec versions)
# ---------------------------------------------------------------------------

STATIONS: list[Station] = [
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
_STATION_CLIMATE: dict[str, ClimateParams] = {
    "WS-0001": {"min": 1.0, "max": 9.0, "precip_chance": 0.65},
    "WS-0002": {"min": -6.0, "max": 0.0, "precip_chance": 0.70},
    "WS-0003": {"min": -10.0, "max": -2.0, "precip_chance": 0.50},
    "WS-0004": {"min": 2.0, "max": 8.0, "precip_chance": 0.75},
    "WS-0005": {"min": -4.0, "max": 5.0, "precip_chance": 0.25},
}

SAMPLE_START_DATE = "2024-01-01"
SAMPLE_PERIODS = 30


def generate_readings(
    stations: list[Station],
    climate_by_station: dict[str, ClimateParams],
    dates: list[str],
    seed: int = 42,
) -> list[Reading]:
    """Generate deterministic daily readings for the example stations."""
    rng = random.Random(seed)
    readings: list[Reading] = []

    for station in stations:
        station_id = station["station_id"]
        climate = climate_by_station[station_id]
        for date in dates:
            temp_min = round(climate["min"] + rng.gauss(0, 1.5), 1)
            temp_max = round(climate["max"] + rng.gauss(0, 1.5), 1)
            if temp_max < temp_min:
                temp_min, temp_max = temp_max, temp_min

            if rng.random() < climate["precip_chance"]:
                precipitation_mm: float | None = round(rng.uniform(0.5, 25.0), 1)
            else:
                precipitation_mm = None  # station did not report

            readings.append(
                {
                    "station_id": station_id,
                    "date": date,
                    "temp_min_c": temp_min,
                    "temp_max_c": temp_max,
                    "precipitation_mm": precipitation_mm,
                    "wind_speed_avg_ms": round(rng.uniform(0.5, 8.0), 1),
                }
            )

    return readings


@cache
def build_sample_dataframes() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Build the example station and reading tables on first use."""
    dates = (
        pd.date_range(SAMPLE_START_DATE, periods=SAMPLE_PERIODS)
        .strftime("%Y-%m-%d")
        .tolist()
    )
    readings = generate_readings(STATIONS, _STATION_CLIMATE, dates)
    return pd.DataFrame(STATIONS), pd.DataFrame(readings)


# ---------------------------------------------------------------------------
# Shared field and schema definitions (same logical content for both versions)
# ---------------------------------------------------------------------------

STATIONS_FIELDS = [
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
]

READINGS_FIELDS = [
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
        "warning": (
            "Null values indicate the station did not report precipitation for that day"
            " — not zero precipitation. Do not substitute 0 for null in analysis."
            " A value of 0.0 means the station reported and confirmed trace or no precipitation."
        ),
    },
    {
        "name": "wind_speed_avg_ms",
        "type": "number",
        "description": "Average wind speed over the calendar day.",
        "unit": "meters per second",
    },
]

STATIONS_SCHEMA = {
    "fields": STATIONS_FIELDS,
    "primaryKey": ["station_id"],
}

READINGS_SCHEMA = {
    "fields": READINGS_FIELDS,
    "primaryKey": ["station_id", "date"],
    "foreignKeys": [
        {
            "fields": ["station_id"],
            "reference": {"resource": "stations", "fields": ["station_id"]},
        }
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
    "description": (
        "Daily summary observations from each station.\n\n"
        "Note: readings before 2010-01-01 were collected using an older instrument"
        " calibration standard and may differ systematically by 0.3–0.5 °C from"
        " post-2010 readings. Do not combine pre- and post-2010 data in a single"
        " analysis without applying the calibration correction described in the"
        " methodology notes."
    ),
    "schema": READINGS_SCHEMA,
}

ASSETS = Path(__file__).parent.parent / "assets" / "examples"


# ---------------------------------------------------------------------------
# Spec-version-specific package metadata
# ---------------------------------------------------------------------------
# The two versions differ in:
#   1. How the spec version is declared (profile vs $schema)
#   2. How contributors are structured (role string vs roles array)
#   3. The "version" field (v1 spec doesn't define it; we omit it from v1)
#   4. The "created" field (v1 spec doesn't define it; we omit it from v1)

V1_PACKAGE_META_BASE: dict[str, Any] = {
    # "profile" is the v1 way to declare the package type.
    # "tabular-data-package" is the strictest standard-compliant profile for CSV.
    # Non-CSV backends use "data-package" since their resources are not tabular-CSV.
    # (profile is set per-backend in the generator functions below)
    "name": "weather-stations",
    "title": "Example Weather Station Dataset",
    "description": (
        "A demonstration datapackage containing two related tables: station metadata"
        " and daily temperature readings. Illustrates Frictionless Data Package v1"
        " structure including field types, constraints, foreign keys, and common"
        " non-standard extensions (unit, warning)."
    ),
    # v1 spec doesn't define "version" — omitted intentionally
    # v1 spec doesn't define "created" — omitted intentionally
    "licenses": [
        {"name": "CC-BY-4.0", "path": "https://creativecommons.org/licenses/by/4.0/"}
    ],
    "contributors": [
        # v1: "role" is a singular string (default: "contributor")
        {"title": "Example Organization", "email": "data@example.org", "role": "author"}
    ],
    "sources": [
        {"title": "National Weather Service", "path": "https://www.weather.gov/"}
    ],
}

V2_PACKAGE_META: dict[str, Any] = {
    # "$schema" is the v2 way to declare the spec version.
    "$schema": "https://datapackage.org/profiles/2.0/datapackage.json",
    "name": "weather-stations",
    "title": "Example Weather Station Dataset",
    "description": (
        "A demonstration datapackage containing two related tables: station metadata"
        " and daily temperature readings. Illustrates Frictionless Data Package v2"
        " structure including field types, constraints, foreign keys, and common"
        " non-standard extensions (unit, warning)."
    ),
    "version": "1.0.0",  # v2 defines a "version" field
    "created": "2025-01-01T00:00:00Z",  # v2 recommends ISO 8601 datetime
    "licenses": [
        {"name": "CC-BY-4.0", "path": "https://creativecommons.org/licenses/by/4.0/"}
    ],
    "contributors": [
        # v2: "roles" is an array (breaking change from v1's singular "role")
        {
            "title": "Example Organization",
            "email": "data@example.org",
            "roles": ["author"],
        }
    ],
    "sources": [
        {"title": "National Weather Service", "path": "https://www.weather.gov/"}
    ],
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def file_stats(path: Path) -> FileStats:
    """Return bytes and MD5 hash for a file — useful for integrity checking."""
    data = path.read_bytes()
    return {"bytes": len(data), "hash": "md5:" + hashlib.md5(data).hexdigest()}


def write_descriptor(
    directory: Path, package_meta: dict[str, Any], resources: list[dict[str, Any]]
) -> None:
    descriptor = {**package_meta, "resources": resources}
    (directory / "datapackage.json").write_text(
        json.dumps(descriptor, indent=2, ensure_ascii=False) + "\n"
    )


def write_data_files(out: Path) -> None:
    """Write the data files to the output directory (CSV, Parquet, DuckDB, SQLite).

    This is separated so that data files are shared / written once regardless of
    how many descriptor variants we generate against them.
    """
    out.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# V1 generators
#
# Key v1-specific choices:
#   CSV:     profile="tabular-data-package" at package level;
#            profile="tabular-data-resource" on each resource.
#            This is the most standards-compliant form of a v1 package.
#   Others:  profile="data-package" at package level (non-CSV resources are not
#            tabular-data-resources by spec). Community extension fields
#            (duckdb_table, sqlite_table) are used exactly as in v2 — they are
#            publisher conventions, not spec features, in both versions.
# ---------------------------------------------------------------------------


def generate_v1_csv(out: Path) -> None:
    stations_df, readings_df = build_sample_dataframes()
    out.mkdir(parents=True, exist_ok=True)
    stations_df.to_csv(out / "stations.csv", index=False)
    readings_df.to_csv(out / "daily-readings.csv", index=False)

    package_meta = {
        "profile": "tabular-data-package",
        **V1_PACKAGE_META_BASE,
    }
    write_descriptor(
        out,
        package_meta,
        [
            {
                # "tabular-data-resource" is the v1 profile for a CSV resource with a schema.
                "profile": "tabular-data-resource",
                **STATIONS_RESOURCE_BASE,
                "path": "stations.csv",
                "format": "csv",
                "mediatype": "text/csv",
                **file_stats(out / "stations.csv"),
            },
            {
                "profile": "tabular-data-resource",
                **READINGS_RESOURCE_BASE,
                "path": "daily-readings.csv",
                "format": "csv",
                "mediatype": "text/csv",
                **file_stats(out / "daily-readings.csv"),
            },
        ],
    )
    print(f"v1 CSV example written to {out}")


def generate_v1_parquet(out: Path) -> None:
    stations_df, readings_df = build_sample_dataframes()
    out.mkdir(parents=True, exist_ok=True)
    stations_df.to_parquet(out / "stations.parquet", index=False)
    readings_df.to_parquet(out / "daily-readings.parquet", index=False)

    # Community pattern for v1 Parquet resources:
    # - Use "data-package" profile (not "tabular-data-package" — these aren't CSV)
    # - Declare mediatype "application/parquet" and format "parquet"
    # - Keep the "schema" field — it documents the logical schema even though
    #   v1 strictly defines schema for CSV. Publishers commonly include it for
    #   documentation purposes and it is valid as a custom extension.
    package_meta = {
        "profile": "data-package",
        **V1_PACKAGE_META_BASE,
    }
    write_descriptor(
        out,
        package_meta,
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
    print(f"v1 Parquet example written to {out}")


def generate_v1_duckdb(out: Path) -> None:
    stations_df, readings_df = build_sample_dataframes()
    out.mkdir(parents=True, exist_ok=True)
    db_path = out / "weather.duckdb"
    db_path.unlink(missing_ok=True)
    con: DuckDBPyConnection = duckdb.connect(str(db_path))
    con.execute("CREATE TABLE stations AS SELECT * FROM stations_df")
    con.execute('CREATE TABLE "daily-readings" AS SELECT * FROM readings_df')
    con.close()

    # Community pattern for v1 DuckDB resources:
    # - Use "data-package" profile
    # - Both resources share the same "path" (the .duckdb file)
    # - The non-standard "duckdb_table" key identifies which table inside the DB
    # - No "bytes"/"hash" since both resources share one file; including stats
    #   on the shared file on the first resource and omitting from the second
    #   is a common publisher convention.
    db_stats = file_stats(db_path)
    package_meta = {
        "profile": "data-package",
        **V1_PACKAGE_META_BASE,
    }
    write_descriptor(
        out,
        package_meta,
        [
            {
                **STATIONS_RESOURCE_BASE,
                "path": "weather.duckdb",
                "format": "duckdb",
                "mediatype": "application/octet-stream",
                "duckdb_table": "stations",
                **db_stats,
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
    print(f"v1 DuckDB example written to {out}")


def generate_v1_sqlite(out: Path) -> None:
    stations_df, readings_df = build_sample_dataframes()
    out.mkdir(parents=True, exist_ok=True)
    db_path = out / "weather.sqlite"
    db_path.unlink(missing_ok=True)
    con: sqlite3.Connection = sqlite3.connect(str(db_path))
    stations_df.to_sql("stations", con, index=False, if_exists="replace")
    readings_df.to_sql("daily-readings", con, index=False, if_exists="replace")
    con.close()

    db_stats = file_stats(db_path)
    package_meta = {
        "profile": "data-package",
        **V1_PACKAGE_META_BASE,
    }
    write_descriptor(
        out,
        package_meta,
        [
            {
                **STATIONS_RESOURCE_BASE,
                "path": "weather.sqlite",
                "format": "sqlite",
                "mediatype": "application/vnd.sqlite3",
                "sqlite_table": "stations",
                **db_stats,
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
    print(f"v1 SQLite example written to {out}")


# ---------------------------------------------------------------------------
# V2 generators
#
# V2 uses "$schema" to declare the spec version and "roles" (array) for
# contributors. Everything else is structurally similar to v1; Parquet/DuckDB/
# SQLite backends use the same community extension fields in both versions.
# ---------------------------------------------------------------------------


def generate_v2_csv(out: Path) -> None:
    stations_df, readings_df = build_sample_dataframes()
    out.mkdir(parents=True, exist_ok=True)
    stations_df.to_csv(out / "stations.csv", index=False)
    readings_df.to_csv(out / "daily-readings.csv", index=False)
    write_descriptor(
        out,
        V2_PACKAGE_META,
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
    print(f"v2 CSV example written to {out}")


def generate_v2_parquet(out: Path) -> None:
    stations_df, readings_df = build_sample_dataframes()
    out.mkdir(parents=True, exist_ok=True)
    stations_df.to_parquet(out / "stations.parquet", index=False)
    readings_df.to_parquet(out / "daily-readings.parquet", index=False)
    write_descriptor(
        out,
        V2_PACKAGE_META,
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
    print(f"v2 Parquet example written to {out}")


def generate_v2_duckdb(out: Path) -> None:
    stations_df, readings_df = build_sample_dataframes()
    out.mkdir(parents=True, exist_ok=True)
    db_path = out / "weather.duckdb"
    db_path.unlink(missing_ok=True)
    con: DuckDBPyConnection = duckdb.connect(str(db_path))
    con.execute("CREATE TABLE stations AS SELECT * FROM stations_df")
    con.execute('CREATE TABLE "daily-readings" AS SELECT * FROM readings_df')
    con.close()
    db_stats = file_stats(db_path)
    write_descriptor(
        out,
        V2_PACKAGE_META,
        [
            {
                **STATIONS_RESOURCE_BASE,
                "path": "weather.duckdb",
                "format": "duckdb",
                "mediatype": "application/octet-stream",
                "duckdb_table": "stations",
                **db_stats,
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
    print(f"v2 DuckDB example written to {out}")


def generate_v2_sqlite(out: Path) -> None:
    stations_df, readings_df = build_sample_dataframes()
    out.mkdir(parents=True, exist_ok=True)
    db_path = out / "weather.sqlite"
    db_path.unlink(missing_ok=True)
    con: sqlite3.Connection = sqlite3.connect(str(db_path))
    stations_df.to_sql("stations", con, index=False, if_exists="replace")
    readings_df.to_sql("daily-readings", con, index=False, if_exists="replace")
    con.close()
    db_stats = file_stats(db_path)
    write_descriptor(
        out,
        V2_PACKAGE_META,
        [
            {
                **STATIONS_RESOURCE_BASE,
                "path": "weather.sqlite",
                "format": "sqlite",
                "mediatype": "application/vnd.sqlite3",
                "sqlite_table": "stations",
                **db_stats,
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
    print(f"v2 SQLite example written to {out}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("Generating v1 examples...")
    generate_v1_csv(ASSETS / "v1" / "csv")
    generate_v1_parquet(ASSETS / "v1" / "parquet")
    generate_v1_duckdb(ASSETS / "v1" / "duckdb")
    generate_v1_sqlite(ASSETS / "v1" / "sqlite")

    print("\nGenerating v2 examples...")
    generate_v2_csv(ASSETS / "v2" / "csv")
    generate_v2_parquet(ASSETS / "v2" / "parquet")
    generate_v2_duckdb(ASSETS / "v2" / "duckdb")
    generate_v2_sqlite(ASSETS / "v2" / "sqlite")

    print("\nDone.")
