___
name: datapackage
description: >
  Explore and query any dataset annotated with a Frictionless Data Package descriptor
  (datapackage.json). Use this skill whenever a user wants to discover what tables or
  resources a dataset contains, look up column names and descriptions, surface usage
  warnings embedded in metadata, or understand how to load data from Parquet files,
  DuckDB or SQLite databases, or CSV files described by a datapackage.json. Also use
  when the user has a datapackage.json and wants to know what's in it, how to query it
  efficiently, or how to connect its metadata to actual data files. Pairs well with
  dataset-specific skills (like `pudl`) that layer domain knowledge on top.
license: CC-BY-4.0
compatibility: |
  Required CLI tools: jq >= 1.7
  Required skills: duckdb-skills (attach-db, query)
  Optional Python packages: marimo, pandas, polars, duckdb (for DataFrame work)
metadata:
- author: Catalyst Cooperative
- email: hello@catalyst.coop
- last-updated: 2026-04-02
___

# Frictionless Data Package Guide

This skill covers any dataset described by a
[Frictionless Data Package](https://datapackage.org/) descriptor file
(`datapackage.json`). It is intentionally generic — it works for any conforming
datapackage, regardless of who published it or what the data contains.

For PUDL-specific knowledge (S3 bucket paths, table tier conventions, data source
context, usage warnings), also use the `pudl` skill on top of this one.

## What is a datapackage.json?

A `datapackage.json` is a JSON file that describes a collection of tabular data
resources. Each resource represents one table (or file) and includes:

- `name`: machine-readable identifier
- `description`: human-readable description, often including processing notes, primary
  keys, and usage warnings
- `path`: filename or URL of the actual data file
- `schema.fields`: list of columns, each with a `name` and `description`

The file can be large (hundreds of resources, megabytes of JSON). Always query it
selectively — never load it whole into context.

## Dependency check

Before querying metadata, verify `jq` is available:

```bash
command -v jq
```

If not found, tell the user how to install it:

- macOS: `brew install jq`
- Linux (apt): `sudo apt install jq`
- Linux (conda): `conda install jq`
- Windows: `winget install jqlang.jq`

For data loading and SQL queries, the `attach-db` and `query` skills from
`duckdb-skills` must be installed. Install them from `duckdb/duckdb-skills`.

## Workflow overview

1. **Locate the descriptor** — find or download `datapackage.json` (see below).
2. **Query metadata selectively** — use jq or DuckDB to extract only what you need. See [Metadata Querying](./references/metadata-querying.md).
3. **Surface warnings** — always check for usage warnings before presenting a resource.
4. **Load the data** *(optional)* — only if the user explicitly wants to query or
   explore the actual data. Data files can be large and remote access can be slow or
   costly. Don't initiate data loading as a follow-on to a metadata lookup without
   confirming the user wants it. See [Storage Backends](./references/storage-backends.md).

## Reference index

- [Metadata Querying](./references/metadata-querying.md) — locate the descriptor,
  query it selectively with jq or DuckDB, surface usage warnings
- [Storage Backends](./references/storage-backends.md) — load data from Parquet,
  DuckDB, SQLite, or CSV files referenced by the descriptor

## Companion skills

This skill delegates actual data querying to:

- **`/duckdb-skills:attach-db`** — attach a `.duckdb` or `.sqlite` database file and
  set up a persistent session for querying
- **`/duckdb-skills:query`** — run SQL or natural language queries against attached
  databases, ad-hoc files (Parquet, CSV, remote HTTPS/S3), and JSON files including
  `datapackage.json` itself (via DuckDB's `read_json`)

These skills must be installed. See `skills-lock.json` in the project root.

## Key constraints

- **Never load the full datapackage.json into context.** It may be megabytes with
  hundreds of resources. Always query selectively.
- **Always surface usage warnings** from the `description` field before presenting a
  resource. Many well-maintained datapackages embed explicit warnings about known
  limitations, unstable identifiers, or data quality issues.
- **Do not use Python to query descriptor metadata.** Python is not the right tool here
  — it loads the full JSON into memory (violating the golden rule above), adds
  unnecessary dependencies, and can't easily handle remote descriptors. Use jq for
  metadata-only tasks; use DuckDB when you need to combine metadata queries with data
  queries. Python is only appropriate for loading data (via pandas or polars) after you
  already know which table and columns you need.

## Schema reference

The Frictionless Data Package JSON Schema (draft-07) describing the standard itself is
at [`assets/datapackage.schema.json`](./assets/datapackage.schema.json). Read it when
you need to understand what fields are valid in a descriptor, or to validate a
descriptor programmatically.
