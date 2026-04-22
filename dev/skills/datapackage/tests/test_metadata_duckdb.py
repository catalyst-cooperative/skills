"""Tests for DuckDB SQL metadata query patterns from references/metadata-querying.md.

Mirrors the jq tests but uses the DuckDB Python API, running exactly the SQL
queries shown in the reference.  Parametrized over all 8 packages to confirm
every descriptor is queryable via DuckDB.

Run:  pixi run pytest dev/skills/datapackage/tests/test_metadata_duckdb.py -v
"""

import json

import duckdb
import pytest
from conftest import (
    EXAMPLES,
    READING_COLUMNS,
    RESOURCE_NAMES,
)

# Use v2/csv as the canonical subject for single-package tests.
PKG = str(EXAMPLES / "v2" / "csv" / "datapackage.json")

# ---------------------------------------------------------------------------
# Helper — builds the reusable "unnest resources" fragment
# ---------------------------------------------------------------------------


def _resources_from(pkg_path: str) -> str:
    """Return the inner FROM clause that unnests resources from a descriptor."""
    return f"SELECT unnest(resources) AS r FROM read_json('{pkg_path}', format='auto')"


# ---------------------------------------------------------------------------
# Step 2: Count and list resources
# Reference: "Steps 2–5: DuckDB" section
# ---------------------------------------------------------------------------


def test_resource_count():
    """Resource count query from the DuckDB section of metadata-querying.md."""
    count = duckdb.sql(f"SELECT count(*) FROM ({_resources_from(PKG)})").fetchall()[0][
        0
    ]
    assert count == 2, f"Expected 2 resources, got {count}"


def test_resource_names_and_paths():
    """Resource names and paths query — verifies both columns are populated."""
    rows = duckdb.sql(
        f"SELECT r->>'$.name' AS name, r->>'$.path' AS path "
        f"FROM ({_resources_from(PKG)})"
    ).fetchall()
    names = {r[0] for r in rows}
    paths = {r[1] for r in rows}
    assert names == set(RESOURCE_NAMES), f"Unexpected resource names: {names}"
    assert all(isinstance(p, str) and p.endswith(".csv") for p in paths), (
        f"Unexpected paths: {paths}"
    )


# ---------------------------------------------------------------------------
# Step 3: Read descriptions
# Reference: "Steps 2–5: DuckDB" section
# ---------------------------------------------------------------------------


def test_resource_description_query():
    """Description query for a specific resource by name."""
    desc = duckdb.sql(
        f"SELECT r->>'$.description' AS description "
        f"FROM ({_resources_from(PKG)}) "
        f"WHERE r->>'$.name' = 'stations'"
    ).fetchall()[0][0]
    assert isinstance(desc, str) and len(desc) > 20, (
        f"Expected a non-empty description, got: {desc!r}"
    )


def test_field_metadata_query():
    """Full field metadata query returns all columns including non-spec extensions.

    Note: read_json(format='auto') infers resources as typed STRUCTTs, so use
    struct dot-notation (r.schema.fields, f.unit) rather than JSON path operators
    (r->'$.schema.fields').  The JSON path operators return a JSON type that
    UNNEST can't iterate.  See the DuckDB section of metadata-querying.md.
    """
    rows = duckdb.sql(
        f"""
        SELECT
            f.name,
            f.description,
            f.unit,
            f.warning
        FROM (
            SELECT unnest(r.schema.fields) AS f
            FROM ({_resources_from(PKG)})
            WHERE r.name = 'daily-readings'
        )
        """
    ).fetchall()

    by_name = {r[0]: {"description": r[1], "unit": r[2], "warning": r[3]} for r in rows}

    # All expected columns should be present
    for col in READING_COLUMNS:
        assert col in by_name, (
            f"Expected column '{col}' in field metadata, got: {list(by_name)}"
        )

    # Unit annotations
    assert by_name["temp_min_c"]["unit"] == "degrees Celsius"
    assert by_name["precipitation_mm"]["unit"] == "millimeters"
    assert by_name["wind_speed_avg_ms"]["unit"] == "meters per second"

    # Warning annotation — only precipitation_mm has one
    assert by_name["precipitation_mm"]["warning"] is not None, (
        "precipitation_mm should have a warning annotation"
    )
    assert by_name["temp_min_c"]["warning"] is None, (
        "temp_min_c should not have a warning annotation"
    )


# ---------------------------------------------------------------------------
# Top-level package metadata
# Reference: "Steps 2–5: DuckDB" section — "Explore all top-level package fields"
# ---------------------------------------------------------------------------


def test_top_level_metadata_excludes_resources():
    """SELECT * EXCLUDE (resources) returns package fields without the resources array."""
    result = duckdb.sql(
        f"SELECT * EXCLUDE (resources) FROM read_json('{PKG}', format='auto')"
    )
    columns = [desc[0] for desc in result.description]
    assert "resources" not in columns, "resources should be excluded"
    for key in ("name", "title"):
        assert key in columns, f"Missing expected package-level column: {key!r}"

    row = result.fetchall()[0]
    name_idx = columns.index("name")
    assert row[name_idx] == "weather-stations", (
        f"Expected package name 'weather-stations', got: {row[name_idx]!r}"
    )


# ---------------------------------------------------------------------------
# All 8 packages: confirm each descriptor is DuckDB-queryable
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "version,backend",
    [
        ("v1", "csv"),
        ("v1", "parquet"),
        ("v1", "sqlite"),
        ("v1", "duckdb"),
        ("v2", "csv"),
        ("v2", "parquet"),
        ("v2", "sqlite"),
        ("v2", "duckdb"),
    ],
)
def test_all_packages_queryable(version, backend):
    """Every descriptor returns exactly 2 resource names via DuckDB SQL."""
    pkg = str(EXAMPLES / version / backend / "datapackage.json")
    rows = duckdb.sql(
        f"SELECT r->>'$.name' AS name FROM ({_resources_from(pkg)})"
    ).fetchall()
    names = {r[0] for r in rows}
    assert names == set(RESOURCE_NAMES), (
        f"{version}/{backend}: expected resources {RESOURCE_NAMES}, got {names}"
    )


# ---------------------------------------------------------------------------
# Foreign key structure queryable via DuckDB
# ---------------------------------------------------------------------------


def test_foreign_key_via_duckdb():
    """Foreign key structure on daily-readings is accessible via DuckDB JSON extraction."""
    fk_json = duckdb.sql(
        f"""
        SELECT r->'$.schema.foreignKeys' AS fks
        FROM ({_resources_from(PKG)})
        WHERE r->>'$.name' = 'daily-readings'
        """
    ).fetchall()[0][0]
    fks = json.loads(fk_json) if isinstance(fk_json, str) else fk_json
    assert len(fks) == 1
    fk = fks[0]
    assert fk["fields"] == ["station_id"]
    assert fk["reference"]["resource"] == "stations"
