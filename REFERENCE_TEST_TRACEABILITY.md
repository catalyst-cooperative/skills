# Reference/Test Traceability

This document defines a repository-wide pattern for preventing drift between
agent-facing workflow snippets in markdown references and the tests that verify
those workflows.

## Why this exists

Reference markdown files under `skills/<skill>/references/` are executable
specifications for coding agents. To keep instructions reliable over time, each
tested snippet must be explicitly linked to one or more tests.

## Scope

This pattern applies to any skill that has both:

- workflow snippets in markdown references
- automated tests that verify those snippets

## Development-only artifact location

Development-only traceability artifacts are stored outside distributed skill
content under `dev/`.

- Per-skill manifest: `dev/skills/<skill>/reference-snippet-manifest.json`
- Shared validator: `dev/tools/check_reference_traceability.py`

## Snippet ID format

Add an HTML comment directly above each fenced code block that is intended to
be tested.

```md
<!-- snippet: <reference-stem>.<workflow-name> -->
```

Rules:

- `<reference-stem>` is the markdown filename without `.md`
- `<workflow-name>` is kebab-case and names the workflow pattern
- IDs must be stable over time unless the workflow meaning changes materially

Example:

````md
<!-- snippet: storage-backends.duckdb-read-csv -->
```sql
SELECT * FROM read_csv('/path/to/my_table.csv') LIMIT 100;
````

## Manifest schema

Each skill manifest is JSON with this shape:

```json
{
    "skill": "datapackage",
    "mappings": [
        {
            "snippet_id": "storage-backends.duckdb-read-csv",
            "reference": "skills/datapackage/references/storage-backends.md",
            "tests": [
                "skills/datapackage/tests/test_backends.py::test_duckdb_read_csv_stations"
            ]
        }
    ]
}
```

Field rules:

- `skill`: skill identifier
- `snippet_id`: exact snippet ID from markdown comment
- `reference`: path to markdown reference file
- `tests`: pytest node IDs (`path/to/test_file.py::test_name`)

## Validator behavior

The shared validator enforces:

1. Every manifest is valid JSON with required keys.
1. Every mapped `reference` file exists.
1. Every mapped `snippet_id` exists exactly once in the mapped reference file.
1. Every mapped test node resolves to an existing test function.
1. Every snippet ID present in a mapped reference file is mapped by the
    manifest (no unmapped tagged snippets).

## Update workflow for agents

When editing a tested reference snippet:

1. Update the markdown snippet.
1. Update mapped tests.
1. Update the per-skill manifest.
1. Run:

```bash
pixi run check-reference-traceability
```

1. Run the relevant skill test suite.

## ID lifecycle guidance

- Keep the same snippet ID if the workflow meaning is unchanged.
- Create a new snippet ID if workflow semantics change materially.
- When deleting a snippet, remove its manifest mapping.

## Assertion scope guidance

Mapped tests should verify the workflow shape taught to agents:

- API/command pattern
- expected result form (for example DataFrame/table/query result)
- essential behavior

Avoid asserting incidental fixture details unless those details are explicitly
part of the instructions.
