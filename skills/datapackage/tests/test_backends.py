"""Tests for data loading patterns documented in references/storage-backends.md.

Verifies that each backend (Parquet, CSV, SQLite, DuckDB file) loads correctly
using the tools recommended in the reference: DuckDB SQL, polars, pandas, and
the Python sqlite3 stdlib module.

A key goal is to confirm that:
  1. Reading the duckdb_table / sqlite_table extension fields from the descriptor
     is the correct way to identify which table to query (documented in the
     "Finding the correct table name" section of storage-backends.md).
  2. Date columns are stored with a proper date type (date32) — not as strings —
     in typed backends (Parquet, DuckDB, SQLite).

Run:  pixi run pytest skills/datapackage/tests/test_backends.py -v
"""

import json
import sqlite3

import duckdb
import pandas as pd
import polars as pl
import pyarrow.parquet as pq
import pytest
from conftest import (
    DATE_COLUMNS,
    EXAMPLES,
    READING_COLUMNS,
    READING_COUNT,
    STATION_COLUMNS,
    STATION_COUNT,
)

# ---------------------------------------------------------------------------
# Helper: load a descriptor
# ---------------------------------------------------------------------------


def load_descriptor(version: str, backend: str) -> dict:
    path = EXAMPLES / version / backend / "datapackage.json"
    return json.loads(path.read_text())


def resource_by_name(descriptor: dict, name: str) -> dict:
    return next(r for r in descriptor["resources"] if r["name"] == name)


# ---------------------------------------------------------------------------
# DuckDB — read_parquet
# Reference: "DuckDB" section, "SELECT * FROM read_parquet(...)"
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("version", ["v1", "v2"])
def test_duckdb_read_parquet_stations(version):
    """read_parquet returns 5 rows and the correct columns for stations."""
    path = str(EXAMPLES / version / "parquet" / "stations.parquet")
    con = duckdb.connect()
    df = con.execute(f"SELECT * FROM read_parquet('{path}')").df()
    assert df.shape == (STATION_COUNT, len(STATION_COLUMNS)), (
        f"{version}/parquet/stations: expected shape ({STATION_COUNT}, {len(STATION_COLUMNS)}), "
        f"got {df.shape}"
    )
    assert list(df.columns) == STATION_COLUMNS


@pytest.mark.parametrize("version", ["v1", "v2"])
def test_duckdb_read_parquet_readings(version):
    """read_parquet returns 150 rows (5×30) for daily-readings."""
    path = str(EXAMPLES / version / "parquet" / "daily-readings.parquet")
    con = duckdb.connect()
    count = con.execute(f"SELECT count(*) FROM read_parquet('{path}')").fetchall()[0][0]
    assert count == READING_COUNT, (
        f"{version}/parquet/daily-readings: expected {READING_COUNT} rows, got {count}"
    )


@pytest.mark.parametrize("version", ["v1", "v2"])
def test_duckdb_parquet_date_columns(version):
    """Parquet date columns have DuckDB type DATE, not VARCHAR or TIMESTAMP."""
    for resource_name, date_cols in DATE_COLUMNS.items():
        filename = f"{resource_name}.parquet"
        path = str(EXAMPLES / version / "parquet" / filename)
        con = duckdb.connect()
        schema = {
            row[0]: row[1]
            for row in con.execute(
                f"DESCRIBE SELECT * FROM read_parquet('{path}')"
            ).fetchall()
        }
        for col in date_cols:
            assert schema[col] == "DATE", (
                f"{version}/parquet/{filename}: column '{col}' has type '{schema[col]}', "
                f"expected 'DATE'. The generate_examples.py script should write "
                f"datetime.date objects, which pyarrow encodes as date32."
            )


# ---------------------------------------------------------------------------
# DuckDB — .df() shorthand for pandas output
# Reference: "Getting a pandas DataFrame from DuckDB" section
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("version", ["v1", "v2"])
def test_duckdb_sql_df_stations(version):
    """duckdb.sql(...).df() returns a pandas DataFrame for a Parquet file."""
    path = str(EXAMPLES / version / "parquet" / "stations.parquet")
    df = duckdb.sql(f"SELECT * FROM read_parquet('{path}') LIMIT 100").df()
    assert isinstance(df, pd.DataFrame), (
        f"{version}/parquet/stations: expected pandas DataFrame from .df(), "
        f"got {type(df)}"
    )
    assert df.shape == (STATION_COUNT, len(STATION_COLUMNS)), (
        f"{version}/parquet/stations: expected shape ({STATION_COUNT}, {len(STATION_COLUMNS)}), "
        f"got {df.shape}"
    )
    assert list(df.columns) == STATION_COLUMNS


# ---------------------------------------------------------------------------
# DuckDB — read_csv
# Reference: "DuckDB" section, "SELECT * FROM read_csv(...)"
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("version", ["v1", "v2"])
def test_duckdb_read_csv_stations(version):
    """read_csv loads 5 station rows with the expected column names."""
    path = str(EXAMPLES / version / "csv" / "stations.csv")
    con = duckdb.connect()
    df = con.execute(f"SELECT * FROM read_csv('{path}')").df()
    assert df.shape == (STATION_COUNT, len(STATION_COLUMNS)), (
        f"{version}/csv/stations: expected shape ({STATION_COUNT}, {len(STATION_COLUMNS)}), "
        f"got {df.shape}"
    )
    assert list(df.columns) == STATION_COLUMNS


@pytest.mark.parametrize("version", ["v1", "v2"])
def test_duckdb_read_csv_readings(version):
    """read_csv loads 150 reading rows."""
    path = str(EXAMPLES / version / "csv" / "daily-readings.csv")
    con = duckdb.connect()
    count = con.execute(f"SELECT count(*) FROM read_csv('{path}')").fetchall()[0][0]
    assert count == READING_COUNT, (
        f"{version}/csv/daily-readings: expected {READING_COUNT} rows, got {count}"
    )


# ---------------------------------------------------------------------------
# DuckDB ATTACH — SQLite backend
# Reference: "SQLite" section — "Via DuckDB (preferred)"
#
# The resource's sqlite_table extension field identifies which table inside the
# .sqlite file corresponds to this resource.  Using it is the correct approach
# per storage-backends.md.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "version,resource_name,expected_count",
    [
        ("v1", "stations", STATION_COUNT),
        ("v1", "daily-readings", READING_COUNT),
        ("v2", "stations", STATION_COUNT),
        ("v2", "daily-readings", READING_COUNT),
    ],
)
def test_duckdb_attach_sqlite(version, resource_name, expected_count):
    """ATTACH sqlite reads the table named by the sqlite_table extension field."""
    descriptor = load_descriptor(version, "sqlite")
    resource = resource_by_name(descriptor, resource_name)

    # Use the sqlite_table extension field as documented in storage-backends.md
    table_name = resource["sqlite_table"]
    db_path = str(EXAMPLES / version / "sqlite" / resource["path"])

    con = duckdb.connect()
    con.execute(f"ATTACH '{db_path}' AS db (TYPE sqlite, READ_ONLY)")
    count = con.execute(f'SELECT count(*) FROM db."{table_name}"').fetchall()[0][0]
    assert count == expected_count, (
        f"{version}/sqlite/{resource_name}: expected {expected_count} rows "
        f"in table '{table_name}', got {count}"
    )


# ---------------------------------------------------------------------------
# DuckDB ATTACH — DuckDB file backend
# Reference: "DuckDB" section — ATTACH for .duckdb files
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "version,resource_name,expected_count",
    [
        ("v1", "stations", STATION_COUNT),
        ("v1", "daily-readings", READING_COUNT),
        ("v2", "stations", STATION_COUNT),
        ("v2", "daily-readings", READING_COUNT),
    ],
)
def test_duckdb_attach_duckdb_file(version, resource_name, expected_count):
    """ATTACH duckdb reads the table named by the duckdb_table extension field."""
    descriptor = load_descriptor(version, "duckdb")
    resource = resource_by_name(descriptor, resource_name)

    # Use the duckdb_table extension field as documented in storage-backends.md
    table_name = resource["duckdb_table"]
    db_path = str(EXAMPLES / version / "duckdb" / resource["path"])

    con = duckdb.connect()
    con.execute(f"ATTACH '{db_path}' AS db (READ_ONLY)")
    count = con.execute(f'SELECT count(*) FROM db."{table_name}"').fetchall()[0][0]
    assert count == expected_count, (
        f"{version}/duckdb/{resource_name}: expected {expected_count} rows "
        f"in table '{table_name}', got {count}"
    )


# ---------------------------------------------------------------------------
# polars — preferred for large Python workflows
# Reference: "Polars" section
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("version", ["v1", "v2"])
def test_polars_read_parquet_stations(version):
    """polars read_parquet loads stations with the correct shape and date type."""
    path = str(EXAMPLES / version / "parquet" / "stations.parquet")
    df = pl.read_parquet(path)
    assert df.shape == (STATION_COUNT, len(STATION_COLUMNS)), (
        f"{version}/parquet/stations: expected shape ({STATION_COUNT}, {len(STATION_COLUMNS)}), "
        f"got {df.shape}"
    )
    assert df.schema["commissioned_date"] == pl.Date, (
        f"{version}/parquet/stations: 'commissioned_date' has polars type "
        f"'{df.schema['commissioned_date']}', expected pl.Date. "
        "The Parquet file should store this column as date32."
    )


@pytest.mark.parametrize("version", ["v1", "v2"])
def test_polars_read_parquet_readings(version):
    """polars read_parquet loads daily-readings with the correct shape and date type."""
    path = str(EXAMPLES / version / "parquet" / "daily-readings.parquet")
    df = pl.read_parquet(path)
    assert df.shape == (READING_COUNT, len(READING_COLUMNS)), (
        f"{version}/parquet/daily-readings: expected shape "
        f"({READING_COUNT}, {len(READING_COLUMNS)}), got {df.shape}"
    )
    assert df.schema["date"] == pl.Date, (
        f"{version}/parquet/daily-readings: 'date' column has polars type "
        f"'{df.schema['date']}', expected pl.Date."
    )


@pytest.mark.parametrize("version", ["v1", "v2"])
def test_polars_to_pandas_stations(version):
    """polars.to_pandas() produces a pandas DataFrame with the correct shape and columns.

    Documents the recommended conversion pattern from the "Polars" section:
    read with polars (which handles date32 natively), then convert to pandas
    only when a pandas-idiomatic workflow is required downstream.
    """
    path = str(EXAMPLES / version / "parquet" / "stations.parquet")
    df_pandas = pl.read_parquet(path).to_pandas()
    assert isinstance(df_pandas, pd.DataFrame), (
        f"{version}/parquet/stations: expected pandas DataFrame after .to_pandas(), "
        f"got {type(df_pandas)}"
    )
    assert df_pandas.shape == (STATION_COUNT, len(STATION_COLUMNS)), (
        f"{version}/parquet/stations: expected shape ({STATION_COUNT}, {len(STATION_COLUMNS)}), "
        f"got {df_pandas.shape}"
    )
    assert list(df_pandas.columns) == STATION_COLUMNS


@pytest.mark.parametrize("version", ["v1", "v2"])
def test_polars_precipitation_has_nulls(version):
    """precipitation_mm contains null values (stations that didn't report)."""
    path = str(EXAMPLES / version / "parquet" / "daily-readings.parquet")
    df = pl.read_parquet(path, columns=["precipitation_mm"])
    null_count = df["precipitation_mm"].null_count()
    assert null_count > 0, (
        f"{version}/parquet: expected some null precipitation_mm values "
        f"(stations that didn't report), but got 0 nulls. "
        "Check generate_examples.py — null values indicate no precipitation report."
    )


# ---------------------------------------------------------------------------
# pandas
# Reference: "pandas" section
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("version", ["v1", "v2"])
def test_pandas_read_parquet_stations(version):
    """pandas read_parquet loads stations with the expected shape."""
    path = str(EXAMPLES / version / "parquet" / "stations.parquet")
    df = pd.read_parquet(path)
    assert df.shape == (STATION_COUNT, len(STATION_COLUMNS)), (
        f"{version}/parquet/stations: expected shape ({STATION_COUNT}, {len(STATION_COLUMNS)}), "
        f"got {df.shape}"
    )
    assert list(df.columns) == STATION_COLUMNS


@pytest.mark.parametrize("version", ["v1", "v2"])
def test_pandas_read_parquet_readings(version):
    """pandas read_parquet loads daily-readings with the expected shape."""
    path = str(EXAMPLES / version / "parquet" / "daily-readings.parquet")
    df = pd.read_parquet(path)
    assert df.shape == (READING_COUNT, len(READING_COLUMNS)), (
        f"{version}/parquet/daily-readings: expected shape "
        f"({READING_COUNT}, {len(READING_COLUMNS)}), got {df.shape}"
    )


# ---------------------------------------------------------------------------
# Python sqlite3 stdlib
# Reference: "SQLite" section — "Via Python stdlib (when DuckDB is unavailable)"
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("version", ["v1", "v2"])
def test_sqlite3_stations(version):
    """Python sqlite3 reads stations using the sqlite_table extension field."""
    descriptor = load_descriptor(version, "sqlite")
    resource = resource_by_name(descriptor, "stations")
    table_name = resource["sqlite_table"]
    db_path = str(EXAMPLES / version / "sqlite" / resource["path"])

    con = sqlite3.connect(db_path)
    count = con.execute(f'SELECT count(*) FROM "{table_name}"').fetchone()[0]
    con.close()
    assert count == STATION_COUNT, (
        f"{version}/sqlite: expected {STATION_COUNT} rows in '{table_name}', got {count}"
    )


# ---------------------------------------------------------------------------
# Pyarrow schema — confirms date32 is written correctly
# (Lower-level check; polars and DuckDB tests above are the main behavioral test.)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "version,resource_name,expected_date_cols",
    [
        ("v1", "stations", DATE_COLUMNS["stations"]),
        ("v2", "stations", DATE_COLUMNS["stations"]),
        ("v1", "daily-readings", DATE_COLUMNS["daily-readings"]),
        ("v2", "daily-readings", DATE_COLUMNS["daily-readings"]),
    ],
)
def test_parquet_date32_schema(version, resource_name, expected_date_cols):
    """Parquet date columns are stored as date32[day], not string or timestamp."""
    filename = f"{resource_name}.parquet"
    path = EXAMPLES / version / "parquet" / filename
    schema = pq.read_schema(path)
    pa_types = {field.name: str(field.type) for field in schema}
    for col in expected_date_cols:
        assert pa_types[col] == "date32[day]", (
            f"{version}/parquet/{filename}: column '{col}' has pyarrow type "
            f"'{pa_types[col]}', expected 'date32[day]'. "
            "Check that generate_examples.py uses datetime.date objects, "
            "not strings, for date fields."
        )
