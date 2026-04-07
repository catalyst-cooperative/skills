#!/usr/bin/env python3
"""Shared helpers for generating markdown reference tables from JSON sidecars."""

import json
from pathlib import Path
from typing import Any, Sequence


def load_json_file(path: Path) -> Any:
    """Load and decode a JSON file."""
    return json.loads(path.read_text(encoding="utf-8"))


def render_markdown_table(headers: Sequence[str], rows: Sequence[Sequence[str]]) -> str:
    """Render a GitHub-flavored markdown table from headers and rows."""
    header_row = "| " + " | ".join(headers) + " |"
    separator_row = "| " + " | ".join("---" for _ in headers) + " |"
    body_rows = ["| " + " | ".join(row) + " |" for row in rows]
    return "\n".join([header_row, separator_row, *body_rows])


def replace_generated_block(
    path: Path, begin_marker: str, end_marker: str, content: str
) -> None:
    """Replace the content between begin and end markers in a markdown file."""
    text = path.read_text(encoding="utf-8")
    begin_idx = text.find(begin_marker)
    if begin_idx == -1:
        raise ValueError(f"Could not find begin marker '{begin_marker}' in {path}")

    content_start = begin_idx + len(begin_marker)
    end_idx = text.find(end_marker, content_start)
    if end_idx == -1:
        raise ValueError(f"Could not find end marker '{end_marker}' in {path}")

    new_text = text[:content_start] + "\n\n" + content.strip() + "\n\n" + text[end_idx:]
    path.write_text(new_text, encoding="utf-8")
