# Metadata Querying

## Use this when

- Discovering which resources (tables) a dataset contains.
- Looking up what a resource or field means before loading data.
- Surfacing usage warnings to help users avoid known data pitfalls.
- Searching for a column by name or topic across all resources.

---

## Golden rule: never load the full datapackage.json into context

A `datapackage.json` can be megabytes with hundreds of resources and thousands of
fields. Always query it selectively — extract only the slice you need.

**Do not use Python for metadata queries.** A Python one-liner like
`json.load(open('datapackage.json'))` loads the entire file into memory, violates the
golden rule, and can't handle remote descriptors at all. Use jq or DuckDB instead —
they are purpose-built for selective extraction and work on local and remote files
without loading everything into context.

---

## Step 0: Locate the descriptor

Check in this order:

1. **User-provided path** — the user may have a local file or know the URL.
2. **Alongside the data files** — `datapackage.json` is conventionally placed in the
   same directory as the data files it describes.
3. **Published URL** — dataset publishers often host the descriptor at a stable HTTPS
   URL. Check the dataset's README or documentation.

**Multiple descriptor files**: the spec requires the filename `datapackage.json`, but
in practice a directory may contain several descriptors (e.g.
`pudl_parquet_datapackage.json`, `ferc1_xbrl_datapackage.json`) associated with
different datasets. Treat each as a separate package.

**Remote descriptors and path resolution**: if you download a remote `datapackage.json`,
store its original base URL. Resource `path` values may be relative (e.g.
`my_table.parquet`) and must be resolved against that base URL, not the local download
directory. For example, if the descriptor was at
`https://example.com/data/datapackage.json` and a resource has `path:
my_table.parquet`, the full data URL is `https://example.com/data/my_table.parquet`.

```bash
# Download and record the base URL
BASE_URL="https://example.com/data"
curl -O "$BASE_URL/datapackage.json"
PKG=datapackage.json

# Resolve a resource path to its full URL
jq -r '.resources[] | select(.name == "my_table") | .path' "$PKG"
# → "my_table.parquet"  (prepend $BASE_URL/ to get the full URL)
```

**Version checking**: before using a descriptor, verify it matches the data you have.
If the descriptor contains hash or byte-size information for resources, check them:

```bash
# Look for hash or bytes fields on resources (non-standard but common)
jq '.resources[] | {name, hash, bytes}' "$PKG"
```

Store the local path in `PKG` for reuse in queries below.

---

## Primary tool: jq

jq is the best tool for selective querying of a local JSON file. It reads only what
you ask for and requires no additional setup.

### Discovery

```bash
# Count total number of resources
jq '.resources | length' "$PKG"

# List all resource names
jq -r '.resources[].name' "$PKG"

# List resource names and their file formats
jq -r '.resources[] | "\(.name)\t\(.format // "unknown")"' "$PKG"

# List resource names and their paths
jq -r '.resources[] | "\(.name)\t\(.path)"' "$PKG"
```

### Search

```bash
# Find resources whose name contains a keyword
jq -r '.resources[] | select(.name | test("generation"; "i")) | .name' "$PKG"

# Find resources whose description contains a keyword
jq '.resources[] | select(.description | test("capacity factor"; "i")) | {name, description: .description[:300]}' "$PKG"

# Find resources that have usage warnings
jq -r '.resources[] | select(.description | test("Usage Warning"; "i")) | .name' "$PKG"
```

### Resource metadata

The spec is permissive — resources often carry extra non-spec fields beyond `name`,
`path`, `description`, and `schema`. Explore openly:

```bash
# Full description for one resource (includes processing notes, primary key, warnings)
jq -r '.resources[] | select(.name == "my_table") | .description' "$PKG"

# Data file path for a resource (may be a relative path or a URL)
jq -r '.resources[] | select(.name == "my_table") | .path' "$PKG"

# See all keys present on a resource (not just spec-defined ones)
jq '.resources[] | select(.name == "my_table") | keys' "$PKG"

# See all non-schema fields on a resource
jq '.resources[] | select(.name == "my_table") | del(.schema)' "$PKG"
```

### Column (field) queries

Fields are also permissive — in addition to `name`, `description`, and `type`, a
field may carry extra metadata such as `unit` (units of measure), `constraints`,
`warnings`, or dataset-specific annotations. Always explore the full field object
rather than assuming only spec-defined keys are present:

```bash
# Column names for a resource
jq -r '.resources[] | select(.name == "my_table") | .schema.fields[].name' "$PKG"

# All metadata for every field (not just name and description)
jq '.resources[] | select(.name == "my_table") | .schema.fields[]' "$PKG"

# Column names, descriptions, and units (unit may be absent on some fields)
jq '.resources[] | select(.name == "my_table") | .schema.fields[] | {name, description, unit}' "$PKG"

# Find fields that have a unit defined
jq '.resources[] | select(.name == "my_table") | .schema.fields[] | select(.unit != null) | {name, unit}' "$PKG"

# Find fields that have an inline warning
jq '.resources[] | select(.name == "my_table") | .schema.fields[] | select(.warning != null or (.description | test("WARNING"; "i"))) | {name, warning, description}' "$PKG"

# See all keys used across all fields in a resource (reveals non-spec extensions)
jq '[.resources[] | select(.name == "my_table") | .schema.fields[] | keys[]] | unique' "$PKG"

# Find all resources that contain a specific column name
jq '.resources[] | {table: .name, fields: [.schema.fields[] | select(.name == "plant_id_eia")]} | select(.fields | length > 0)' "$PKG"
```

### Package-level metadata

The spec defines a core set of fields (`name`, `title`, `description`, `version`,
`licenses`, etc.) but descriptors often contain extra non-spec fields with useful
context. Explore openly rather than querying only known fields:

```bash
# See all top-level fields (excluding the potentially huge resources array)
jq 'del(.resources)' "$PKG"

# Or just the keys present at the top level
jq 'keys' "$PKG"
```

---

## Alternative: DuckDB via `/duckdb-skills:query`

DuckDB can query the descriptor as a JSON file using SQL. Use `/duckdb-skills:query`
to run these — it handles session state, natural language, and large result warnings.

```sql
-- Count resources
SELECT count(*)
FROM (SELECT unnest(resources) AS r FROM read_json('datapackage.json', format='auto'));

-- List all resource names and paths
SELECT r->>'$.name' AS name, r->>'$.path' AS path
FROM (SELECT unnest(resources) AS r FROM read_json('datapackage.json', format='auto'));

-- Get description for a specific resource
SELECT r->>'$.description' AS description
FROM (SELECT unnest(resources) AS r FROM read_json('datapackage.json', format='auto'))
WHERE r->>'$.name' = 'my_table';

-- List all metadata for every field in a resource (fields may have non-spec keys)
SELECT f AS field_metadata
FROM (
    SELECT unnest(r->'$.schema.fields') AS f
    FROM (SELECT unnest(resources) AS r FROM read_json('datapackage.json', format='auto'))
    WHERE r->>'$.name' = 'my_table'
);

-- Or select specific known fields plus any extras you discover
SELECT
    f->>'$.name' AS name,
    f->>'$.description' AS description,
    f->>'$.unit' AS unit,
    f->>'$.warning' AS warning
FROM (
    SELECT unnest(r->'$.schema.fields') AS f
    FROM (SELECT unnest(resources) AS r FROM read_json('datapackage.json', format='auto'))
    WHERE r->>'$.name' = 'my_table'
);

-- Explore all top-level package fields (excluding resources)
SELECT * EXCLUDE (resources) FROM read_json('datapackage.json', format='auto');
```

DuckDB can also read a remote descriptor directly without downloading:

```sql
SELECT r->>'$.name' AS name
FROM (
    SELECT unnest(resources) AS r
    FROM read_json('https://example.com/data/datapackage.json', format='auto')
);
```

DuckDB is especially useful when you want to **query descriptor metadata and data
files in the same session**. Once you have found a resource's path from the descriptor,
you can query it immediately using any DuckDB-supported format — not just Parquet:

```sql
-- After finding a resource path from the descriptor, query it directly
SELECT * FROM read_parquet('https://example.com/data/my_table.parquet') LIMIT 10;
SELECT * FROM read_csv('https://example.com/data/my_table.csv') LIMIT 10;
-- For attached DuckDB or SQLite files, use the alias set up by attach-db
SELECT * FROM my_db.my_table LIMIT 10;
```

### Interrupting a long or large query

If a query runs too long or starts returning too much data, interrupt it with `Ctrl+C`
in the terminal. In the `/duckdb-skills:query` skill, the `query` step estimates result
size before running and warns you if it exceeds 1M rows. Always add `LIMIT` when
exploring unfamiliar tables:

```sql
SELECT * FROM read_parquet('large_table.parquet') LIMIT 1000;
```

---

## Mandatory: surface usage warnings

Before presenting any resource to the user, **always check for and display usage
warnings**. Well-maintained datapackages embed explicit warnings about known
limitations directly in the `description` field.

```bash
# Extract the Usage Warnings section from a resource description
jq -r '.resources[] | select(.name == "my_table") | .description' "$PKG" \
  | awk '/Usage Warning/,0'
```

Also scan individual field descriptions for inline warnings:

```bash
jq '.resources[] | select(.name == "my_table") | .schema.fields[] | select(.description | test("WARNING|caution"; "i"))' "$PKG"
```

**Always present warnings prominently and verbatim.** Don't paraphrase — quote the
original text, then explain the practical implication in plain language.

---

## Recommended workflow

1. **Identify candidates** — search by name keyword or description keyword.
2. **Read the resource description** — source, processing notes, primary key, warnings.
3. **Read column descriptions** for the columns the user actually needs.
4. **Surface all warnings** before providing loading code.
5. **Confirm the data file path** — the `path` field is either a relative path
   (resolve against the descriptor's base directory or base URL) or an absolute URL.
6. **Load the data** *(only if the user asks)* — see [`storage-backends.md`](storage-backends.md).
