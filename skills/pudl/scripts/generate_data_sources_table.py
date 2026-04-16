#!/usr/bin/env python3
"""Regenerate the human-readable table in references/data-sources.md from assets/data_sources.json.

Run from the skill root:

    python scripts/generate_data_sources_table.py

The JSON asset is the single source of truth. Edit data_sources.json, then run this
script to keep the markdown table in sync.
"""

from pathlib import Path
from typing import TypedDict

from _reference_table_utils import (
    load_json_file,
    render_markdown_table,
    replace_generated_block,
)


class DataSourceRecord(TypedDict):
    short_code: str
    full_name: str
    docs_url: str | None


SKILL_ROOT = Path(__file__).parent.parent
JSON_ASSET = SKILL_ROOT / "assets" / "data_sources.json"
MD_FILE = SKILL_ROOT / "references" / "data-sources.md"

SENTINEL_START = (
    "<!-- Generated from assets/data_sources.json — do not edit by hand -->"
)
SENTINEL_END = "<!-- end generated table -->"

TABLE_HEADERS = ["Short code", "Full name", "Docs"]


def render_docs_cell(url: str | None) -> str:
    """Render the docs column for a data source row."""
    return f"[docs]({url})" if url else "—"


def render_table(records: list[DataSourceRecord]) -> str:
    """Render the data sources markdown table."""
    rows = [
        [
            f"`{record['short_code']}`",
            record["full_name"],
            render_docs_cell(record["docs_url"]),
        ]
        for record in records
    ]
    return render_markdown_table(TABLE_HEADERS, rows)


def main() -> None:
    sources: list[DataSourceRecord] = load_json_file(JSON_ASSET)
    replace_generated_block(
        MD_FILE,
        SENTINEL_START,
        SENTINEL_END,
        render_table(sources),
    )
    print(
        f"Written {len(sources)} rows to {MD_FILE.relative_to(SKILL_ROOT.parent.parent)}"
    )


if __name__ == "__main__":
    main()
