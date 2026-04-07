#!/usr/bin/env python3
"""Regenerate the human-readable table in references/data-sources.md from assets/data_sources.json.

Run from the skill root:

    python scripts/generate_data_sources_table.py

The JSON asset is the single source of truth. Edit data_sources.json, then run this
script to keep the markdown table in sync.
"""

import json
from pathlib import Path

SKILL_ROOT = Path(__file__).parent.parent
JSON_ASSET = SKILL_ROOT / "assets" / "data_sources.json"
MD_FILE = SKILL_ROOT / "references" / "data-sources.md"

SENTINEL_START = (
    "<!-- Generated from assets/data_sources.json — do not edit by hand -->"
)
SENTINEL_END = "<!-- end generated table -->"

TABLE_HEADER = """| Short code          | Full name                                                                         | Docs                                                                                    |
| ------------------- | --------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------- |"""


def make_row(entry: dict) -> str:
    short_code = f"`{entry['short_code']}`"
    full_name = entry["full_name"]
    url = entry["docs_url"]
    docs = f"[docs]({url})" if url else "—"
    return f"| {short_code:<19} | {full_name:<81} | {docs:<87} |"


def main() -> None:
    sources = json.loads(JSON_ASSET.read_text())
    rows = [make_row(s) for s in sources]
    new_table = TABLE_HEADER + "\n" + "\n".join(rows)

    content = MD_FILE.read_text()

    # Replace everything from the sentinel to end-of-file (or end sentinel if present)
    start_idx = content.find(SENTINEL_START)
    if start_idx == -1:
        raise ValueError(f"Could not find sentinel '{SENTINEL_START}' in {MD_FILE}")

    end_idx = content.find(SENTINEL_END, start_idx)
    if end_idx != -1:
        tail = content[end_idx + len(SENTINEL_END) :]
    else:
        # No end sentinel — replace to end of file
        tail = ""

    new_content = (
        content[:start_idx]
        + SENTINEL_START
        + "\n\n"
        + new_table
        + "\n"
        + (SENTINEL_END + tail if end_idx != -1 else "")
    )

    MD_FILE.write_text(new_content)
    print(
        f"Written {len(sources)} rows to {MD_FILE.relative_to(SKILL_ROOT.parent.parent)}"
    )


if __name__ == "__main__":
    main()
