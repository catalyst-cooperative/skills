#!/usr/bin/env python3
"""Generate markdown table sections in FERC reference files from their JSON sidecars.

The JSON assets are the single source of truth for FERC account and schedule data.
This script reads them and regenerates the human-readable table sections in:

  references/ferc-electricity-accounts.md
  references/ferc1-schedules.md
  references/ferc2-schedules.md

Edit the JSON, then run this script to update the markdown.

Usage (from skill root or anywhere):
  python skills/pudl/scripts/generate_ferc_tables.py
"""

from pathlib import Path

from _reference_table_utils import (
    load_json_file,
    render_markdown_table,
    replace_generated_block,
)

SKILL_ROOT = Path(__file__).resolve().parent.parent
ASSETS = SKILL_ROOT / "assets"
REFS = SKILL_ROOT / "references"

BEGIN_MARKER = "<!-- BEGIN GENERATED CONTENT -->"
END_MARKER = "<!-- END GENERATED CONTENT -->"

# Display heading for each chart, in output order
CHART_ORDER = [
    "balance_sheet",
    "electric_plant",
    "operating_revenue",
    "sales_of_electricity",
    "om_expenses",
]

CHART_HEADINGS = {
    "balance_sheet": "## Balance Sheet Chart of Accounts",
    "electric_plant": "## Electric Plant Chart of Accounts (Account 101)",
    "operating_revenue": "## Operating Revenue Chart of Accounts (Account 400)",
    "sales_of_electricity": "## Sales of Electricity Chart of Accounts (Account 400, sub-accounts)",
    "om_expenses": "## Operation and Maintenance Expense Chart of Accounts",
}

# Display prefix for each (chart, section, group) combination.
# Groups within a section are numbered/lettered in the source document; these
# prefixes reproduce that display convention without cluttering the JSON keys.
GROUP_PREFIXES: dict[tuple[str, str, str], str] = {
    # Balance sheet groups — numbered 1–9 globally across both sections
    ("balance_sheet", "Assets and Other Debits", "Utility Plant"): "1.",
    (
        "balance_sheet",
        "Assets and Other Debits",
        "Other Property and Investments",
    ): "2.",
    ("balance_sheet", "Assets and Other Debits", "Current and Accrued Assets"): "3.",
    ("balance_sheet", "Assets and Other Debits", "Deferred Debits"): "4.",
    ("balance_sheet", "Liabilities and Other Credits", "Proprietary Capital"): "5.",
    ("balance_sheet", "Liabilities and Other Credits", "Long-Term Debt"): "6.",
    (
        "balance_sheet",
        "Liabilities and Other Credits",
        "Other Noncurrent Liabilities",
    ): "7.",
    (
        "balance_sheet",
        "Liabilities and Other Credits",
        "Current and Accrued Liabilities",
    ): "8.",
    ("balance_sheet", "Liabilities and Other Credits", "Deferred Credits"): "9.",
    # Electric plant production groups
    ("electric_plant", "2. Production Plant", "Steam Production"): "A.",
    ("electric_plant", "2. Production Plant", "Nuclear Production"): "B.",
    ("electric_plant", "2. Production Plant", "Hydraulic Production"): "C.",
    ("electric_plant", "2. Production Plant", "Other Production"): "D.",
    # Operating revenue sub-groups
    ("operating_revenue", "2. Other Income and Deductions", "Other Income"): "A.",
    (
        "operating_revenue",
        "2. Other Income and Deductions",
        "Other Income Deductions",
    ): "B.",
    (
        "operating_revenue",
        "2. Other Income and Deductions",
        "Taxes Applicable to Other Income and Deductions",
    ): "C.",
    # O&M Power Production sub-groups (lettered A–E)
    ("om_expenses", "1. Power Production Expenses", "Steam Power Generation"): "A.",
    ("om_expenses", "1. Power Production Expenses", "Nuclear Power Generation"): "B.",
    ("om_expenses", "1. Power Production Expenses", "Hydraulic Power Generation"): "C.",
    ("om_expenses", "1. Power Production Expenses", "Other Power Generation"): "D.",
    (
        "om_expenses",
        "1. Power Production Expenses",
        "Other Power Supply Expenses",
    ): "E.",
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def account_sort_key(account: str) -> tuple[int, int]:
    """Sort key for FERC account numbers like '101', '101.1', '561.7'."""
    parts = account.split(".")
    try:
        return (int(parts[0]), int(parts[1]) if len(parts) > 1 else 0)
    except ValueError:
        return (0, 0)


def fmt_account_description(record: dict) -> str:
    """Append applicability qualifier to an account description."""
    desc = record["description"]
    if record.get("major_only"):
        desc += " *(Major only)*"
    elif record.get("nonmajor_only"):
        desc += " *(Nonmajor only)*"
    return desc


def fmt_tables(names: list[str]) -> str:
    """Format a list of table names as backtick-quoted, comma-separated."""
    return ", ".join(f"`{n}`" for n in names) if names else ""


def escape_markdown_cell(value: str) -> str:
    """Escape markdown table cell delimiters in plain-text values."""
    return value.replace("|", "\\|")


# ---------------------------------------------------------------------------
# Accounts table generator
# ---------------------------------------------------------------------------


def generate_accounts_tables() -> str:
    """Generate the full account listing from ferc_electricity_accounts.json."""
    raw = load_json_file(ASSETS / "ferc_electricity_accounts.json")

    # Build an ordered dict keyed by (chart, section, group, operation_type)
    # preserving the JSON order for the hierarchy while allowing us to sort
    # accounts numerically within each leaf bucket.
    buckets: dict[tuple[str, str, str | None, str | None], list[dict]] = {}
    for record in raw:
        key = (
            record["chart"],
            record["section"],
            record.get("group"),
            record.get("operation_type"),
        )
        buckets.setdefault(key, []).append(record)

    # Sort accounts within each bucket by account number
    for records in buckets.values():
        records.sort(key=lambda r: account_sort_key(r["account"]))

    lines: list[str] = []
    current_chart = None
    current_section = None
    current_group = None

    for (chart, section, group, op_type), records in buckets.items():
        if chart != current_chart:
            lines += ["", CHART_HEADINGS[chart]]
            current_chart = chart
            current_section = None
            current_group = None

        if section != current_section:
            lines += ["", f"### {section}"]
            current_section = section
            current_group = None

        if group != current_group:
            if group is not None:
                prefix = GROUP_PREFIXES.get((chart, section, group), "")
                label = f"{prefix} {group}".strip() if prefix else group
                lines += ["", f"#### {label}"]
            current_group = group

        if op_type is not None:
            # Use ##### if nested under a group (Power Production A-E);
            # use #### if directly under a section (Transmission, Distribution, etc.)
            level = "#####" if group is not None else "####"
            lines += ["", f"{level} {op_type}"]

        table_rows = [[r["account"], fmt_account_description(r)] for r in records]
        lines += ["", render_markdown_table(["Account", "Description"], table_rows)]

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Schedules table generator
# ---------------------------------------------------------------------------


def generate_schedules_table(json_path: Path) -> str:
    """Generate a schedule table from a FERC schedules JSON file.

    Works for any form (ferc1_schedules.json, ferc2_schedules.json, etc.).
    The DBF column is included only when at least one schedule has dbf_tables data,
    since some forms (e.g. Form 2) have no DBF-era database yet.
    """
    schedules = load_json_file(json_path)

    include_dbf = any(s.get("dbf_tables") for s in schedules)

    if include_dbf:
        headers = [
            "Schedule (Page)",
            "Title",
            "Description",
            "FERC Accounts",
            "PUDL Integrated Tables (use first)",
            "XBRL Raw Tables (2021-present, fallback)",
            "DBF Raw Tables (1994-2020, fallback)",
        ]
    else:
        headers = [
            "Schedule (Page)",
            "Title",
            "Description",
            "FERC Accounts",
            "PUDL Integrated Tables",
            "XBRL Raw Tables (2021-present)",
        ]

    rows: list[list[str]] = []
    for s in schedules:
        accounts = ", ".join(s.get("ferc_accounts", []))
        pudl = fmt_tables(s.get("pudl_tables", []))
        if not pudl:
            pudl = "*(not yet integrated)*"
        xbrl = fmt_tables(s.get("xbrl_tables", []))
        desc = escape_markdown_cell(s.get("description", ""))
        if include_dbf:
            dbf = fmt_tables(s.get("dbf_tables", []))
            rows.append([s["schedule"], s["title"], desc, accounts, pudl, xbrl, dbf])
        else:
            rows.append([s["schedule"], s["title"], desc, accounts, pudl, xbrl])

    return render_markdown_table(headers, rows)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

# Each entry: (json asset filename, markdown reference filename, label for output)
SCHEDULE_FILES: list[tuple[str, str, str]] = [
    ("ferc1_schedules.json", "ferc1-schedules.md", "FERC Form 1"),
    ("ferc2_schedules.json", "ferc2-schedules.md", "FERC Form 2"),
]


def main() -> None:
    print("Generating FERC accounts table...")
    accounts_content = generate_accounts_tables()
    replace_generated_block(
        REFS / "ferc-electricity-accounts.md",
        BEGIN_MARKER,
        END_MARKER,
        accounts_content,
    )
    print("  -> references/ferc-electricity-accounts.md updated")

    for json_name, md_name, label in SCHEDULE_FILES:
        print(f"Generating {label} schedules table...")
        content = generate_schedules_table(ASSETS / json_name)
        replace_generated_block(REFS / md_name, BEGIN_MARKER, END_MARKER, content)
        print(f"  -> references/{md_name} updated")

    print("Done.")


if __name__ == "__main__":
    main()
