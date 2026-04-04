#!/usr/bin/env python3
"""Generate markdown table sections in FERC reference files from their JSON sidecars.

The JSON assets are the single source of truth for FERC account and schedule data.
This script reads them and regenerates the human-readable table sections in:

  references/ferc-uniform-system-of-accounts.md
  references/ferc1-schedules.md

Edit the JSON, then run this script to update the markdown.

Usage (from skill root or anywhere):
  python skills/pudl/scripts/generate_ferc_tables.py
"""

import json
from collections import OrderedDict
from pathlib import Path

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
    ("balance_sheet", "Assets and Other Debits", "Other Property and Investments"): "2.",
    ("balance_sheet", "Assets and Other Debits", "Current and Accrued Assets"): "3.",
    ("balance_sheet", "Assets and Other Debits", "Deferred Debits"): "4.",
    ("balance_sheet", "Liabilities and Other Credits", "Proprietary Capital"): "5.",
    ("balance_sheet", "Liabilities and Other Credits", "Long-Term Debt"): "6.",
    ("balance_sheet", "Liabilities and Other Credits", "Other Noncurrent Liabilities"): "7.",
    ("balance_sheet", "Liabilities and Other Credits", "Current and Accrued Liabilities"): "8.",
    ("balance_sheet", "Liabilities and Other Credits", "Deferred Credits"): "9.",
    # Electric plant production groups
    ("electric_plant", "2. Production Plant", "Steam Production"): "A.",
    ("electric_plant", "2. Production Plant", "Nuclear Production"): "B.",
    ("electric_plant", "2. Production Plant", "Hydraulic Production"): "C.",
    ("electric_plant", "2. Production Plant", "Other Production"): "D.",
    # Operating revenue sub-groups
    ("operating_revenue", "2. Other Income and Deductions", "Other Income"): "A.",
    ("operating_revenue", "2. Other Income and Deductions", "Other Income Deductions"): "B.",
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
    ("om_expenses", "1. Power Production Expenses", "Other Power Supply Expenses"): "E.",
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def splice_generated(path: Path, content: str) -> None:
    """Replace the content between BEGIN/END markers in a markdown file."""
    text = path.read_text()
    begin_idx = text.index(BEGIN_MARKER)
    end_idx = text.index(END_MARKER)
    new_text = (
        text[: begin_idx + len(BEGIN_MARKER)]
        + "\n\n"
        + content.strip()
        + "\n\n"
        + text[end_idx:]
    )
    path.write_text(new_text)


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


# ---------------------------------------------------------------------------
# Accounts table generator
# ---------------------------------------------------------------------------

def generate_accounts_tables() -> str:
    """Generate the full account listing from ferc_accounts.json."""
    with open(ASSETS / "ferc_accounts.json") as f:
        raw = json.load(f)

    # Build an ordered dict keyed by (chart, section, group, operation_type)
    # preserving the JSON order for the hierarchy while allowing us to sort
    # accounts numerically within each leaf bucket.
    buckets: OrderedDict[tuple, list[dict]] = OrderedDict()
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

        lines += ["", "| Account | Description |", "|---------|-------------|"]
        for r in records:
            lines.append(f"| {r['account']} | {fmt_account_description(r)} |")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Schedules table generator
# ---------------------------------------------------------------------------

def fmt_tables(names: list[str]) -> str:
    """Format a list of table names as backtick-quoted, comma-separated."""
    return ", ".join(f"`{n}`" for n in names) if names else ""


def generate_schedules_table() -> str:
    """Generate the full schedule table from ferc1_schedules.json."""
    with open(ASSETS / "ferc1_schedules.json") as f:
        schedules = json.load(f)

    header = (
        "| Schedule (Page) | Title | Description | FERC Accounts"
        " | PUDL Integrated Tables (use first)"
        " | XBRL Raw Tables (2021-present, fallback)"
        " | DBF Raw Tables (1994-2020, fallback) |"
    )
    separator = (
        "| --- | --- | --- | --- | --- | --- | --- |"
    )

    lines = [header, separator]
    for s in schedules:
        accounts = ", ".join(s.get("ferc_accounts", []))
        pudl = fmt_tables(s.get("pudl_tables", []))
        if not pudl:
            pudl = "*(not yet integrated)*"
        xbrl = fmt_tables(s.get("xbrl_tables", []))
        dbf = fmt_tables(s.get("dbf_tables", []))
        desc = s.get("description", "").replace("|", "\\|")
        lines.append(
            f"| {s['schedule']} | {s['title']} | {desc}"
            f" | {accounts} | {pudl} | {xbrl} | {dbf} |"
        )

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    print("Generating FERC accounts table...")
    accounts_content = generate_accounts_tables()
    splice_generated(REFS / "ferc-uniform-system-of-accounts.md", accounts_content)
    print("  -> references/ferc-uniform-system-of-accounts.md updated")

    print("Generating FERC Form 1 schedules table...")
    schedules_content = generate_schedules_table()
    splice_generated(REFS / "ferc1-schedules.md", schedules_content)
    print("  -> references/ferc1-schedules.md updated")

    print("Done.")


if __name__ == "__main__":
    main()
