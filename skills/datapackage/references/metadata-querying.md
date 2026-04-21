# Metadata Querying

## Use this when

- Discovering which resources (tables) a dataset contains.
- Looking up what a resource or field means before loading data.
- Reading descriptions to understand data provenance, processing notes, and caveats.
- Searching for a column by name or topic across all resources.

---

## Spec reference

The Frictionless Data Package v2.0 specification and its JSON Schema are at
<https://datapackage.org/>. The JSON Schema itself (useful for validation) is at:
<https://datapackage.org/profiles/2.0/datapackage.json>

The spec is intentionally permissive: it defines a set of standard fields but allows
implementors to add non-standard keys anywhere — at the package, resource, or field
level. When you encounter unrecognized keys (like `unit`, `warning`, `bytes`, `hash`,
or source-specific metadata), treat them as informative extensions, not errors.

**Non-tabular resources**: not all resources have a `schema`. A resource may describe
an opaque file (PDF, ZIP, CSV without column metadata) and omit `schema.fields`
entirely. When `schema` is absent, the resource is still valid — just treat it as a
file reference rather than a queryable table.

**Integrity fields**: real-world descriptors often include `bytes` (file size in bytes)
and `hash` (checksum) on each resource. The `hash` value is usually in
`algorithm:hex` format (e.g. `"md5:abc123..."` or `"sha256:def456..."`); if no prefix
is present, assume MD5. For small files, use these to verify a download. For large
files (hundreds of MB or more), hashing is slow — check `bytes` first as a quick
sanity check, and only verify the hash if you suspect corruption.

```bash
# Find which resources have hashes
jq '.resources[] | select(.hash != null) | {name, bytes, hash}' "$PKG"

# Check hash of a downloaded file (macOS — strip any "md5:" prefix before comparing)
md5 stations.csv

# Check hash (Linux)
md5sum stations.csv
```

---

## Golden rule: never load the full datapackage.json into context

A `datapackage.json` can be megabytes with hundreds of resources and thousands of
fields. Always query it selectively — extract only the slice you need.

**Do not use Python for metadata queries.** Use jq or DuckDB instead —
they are purpose-built for selective extraction. jq works on local files; DuckDB can
query both local files and remote URLs directly.

---

## Workflow

1. **Locate the descriptor** — find or download `datapackage.json` and note its base
    URL if remote (needed to resolve relative resource paths).
1. **Identify candidate resources** — search by name or description keyword.
1. **Read the resource description** — it contains source notes, primary key
    conventions, caveats, and processing history. Read it fully before presenting.
1. **Read column descriptions** for the specific columns the user needs.
1. **Confirm the data file path** — the `path` field is either a relative path
    (resolve against the descriptor's base directory or base URL) or an absolute URL.
1. **Load the data** *(only if the user asks)* — see
    [`storage-backends.md`](storage-backends.md).

---

## Step 1: Locate the descriptor

Check in this order:

1. **User-provided path** — the user may have a local file or know the URL.
1. **Alongside the data files** — `datapackage.json` is conventionally placed in the
    same directory as the data files it describes.
1. **Published URL** — dataset publishers often host the descriptor at a stable HTTPS
    URL. Check the dataset's README or documentation.

**Multiple descriptor files**: the spec requires the filename `datapackage.json`, but
in practice a directory may contain several descriptors (e.g.
`pudl_parquet_datapackage.json`, `ferc1_xbrl_datapackage.json`) associated with
different datasets. Treat each as a separate package.

**Remote descriptors and path resolution**: if you download a remote `datapackage.json`,
store its original base URL. Resource `path` values may be relative (e.g.
`my_table.parquet`) and must be resolved against that base URL, not the local download
directory. For example, if the descriptor was at
`https://example.com/data/datapackage.json` and a resource has `path: my_table.parquet`, the full data URL is `https://example.com/data/my_table.parquet`.

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

## Steps 2–5: Query the descriptor

Use **jq** for local files (see below) or **DuckDB** for local or remote files (see
the DuckDB section). Both tools work on the same descriptor — pick the one that fits
your setup.

---

## Steps 2–5: jq (local files only)

jq is the best tool for selective querying of a local JSON file. It reads only what
you ask for and requires no additional setup. **jq cannot fetch over HTTPS** — if the
descriptor is remote, download it first with `curl -O <URL>`, then point jq at the
local file. (To query a remote descriptor without downloading, use DuckDB instead.)

### Step 2: Identify candidate resources

```bash
# Count total number of resources
jq '.resources | length' "$PKG"

# List all resource names
jq -r '.resources[].name' "$PKG"

# List resource names and their file formats
jq -r '.resources[] | "\(.name)\t\(.format // "unknown")"' "$PKG"

# Find resources whose name contains a keyword
jq -r '.resources[] | select(.name | test("generation"; "i")) | .name' "$PKG"

# Find resources whose description contains a keyword
jq '.resources[] | select(.description | test("capacity factor"; "i")) | {name, description: .description[:300]}' "$PKG"
```

### Step 3: Read resource and field descriptions

The spec is permissive — resources often carry extra non-spec fields beyond `name`,
`path`, `description`, and `schema`. Explore openly:

```bash
# Full description for one resource (includes processing notes, primary key, caveats)
jq -r '.resources[] | select(.name == "my_table") | .description' "$PKG"

# See all keys present on a resource (not just spec-defined ones)
jq '.resources[] | select(.name == "my_table") | keys' "$PKG"

# See all non-schema fields on a resource
jq '.resources[] | select(.name == "my_table") | del(.schema)' "$PKG"
```

Fields are also permissive — in addition to `name`, `description`, and `type`, a
field may carry extra metadata such as `unit`, `constraints`, `warning`, or
dataset-specific annotations. Always explore the full field object:

```bash
# Column names for a resource
jq -r '.resources[] | select(.name == "my_table") | .schema.fields[].name' "$PKG"

# All metadata for every field (not just name and description)
jq '.resources[] | select(.name == "my_table") | .schema.fields[]' "$PKG"

# Column names, descriptions, and units (unit may be absent on some fields)
jq '.resources[] | select(.name == "my_table") | .schema.fields[] | {name, description, unit}' "$PKG"

# Find fields that have a unit defined
jq '.resources[] | select(.name == "my_table") | .schema.fields[] | select(.unit != null) | {name, unit}' "$PKG"

# Find fields that carry a non-standard warning annotation
jq '.resources[] | select(.name == "my_table") | .schema.fields[] | select(.warning != null) | {name, warning}' "$PKG"

# See all keys used across all fields in a resource (reveals non-spec extensions)
jq '[.resources[] | select(.name == "my_table") | .schema.fields[] | keys[]] | unique' "$PKG"

# Find all resources that contain a specific column name
jq '.resources[] | {table: .name, fields: [.schema.fields[] | select(.name == "plant_id_eia")]} | select(.fields | length > 0)' "$PKG"
```

Package-level metadata follows the same pattern:

```bash
# See all top-level fields (excluding the potentially huge resources array)
jq 'del(.resources)' "$PKG"

# Or just the keys present at the top level
jq 'keys' "$PKG"
```

### Steps 4–5: Confirm the path, then load

```bash
# Data file path for a resource (may be a relative path or a URL)
jq -r '.resources[] | select(.name == "my_table") | .path' "$PKG"

# List resource names and their paths
jq -r '.resources[] | "\(.name)\t\(.path)"' "$PKG"
```

If the path is relative, prepend `$BASE_URL/` (recorded in Step 1). Then load —
see [`storage-backends.md`](storage-backends.md).

---

## Steps 2–5: DuckDB (local and remote)

DuckDB is a standalone CLI tool — no Python environment required. Install it with
`brew install duckdb`, `conda install duckdb`, or download from <https://duckdb.org/>.
Use `/duckdb-skills:query` to run queries through it — that skill handles CLI
invocation, session state, natural language, and large result warnings.

DuckDB can query the descriptor as a JSON file using SQL.

**Typed-struct access**: `read_json(file, format='auto')` infers the full structure of `datapackage.json` and materialises `resources` as a typed `STRUCT[]`. Once unnested, each `r` is a typed STRUCT — use **dot-notation** (`r.name`, `r.schema.fields`) for nested access. The JSON path operators (`r->>'$.name'`) also work for scalar fields but return `JSON` for sub-objects and arrays, which `UNNEST` cannot iterate. Dot-notation is both more readable and more reliable for nested fields.

```sql
-- Count resources (Step 2)
SELECT count(*)
FROM (SELECT unnest(resources) AS r FROM read_json('datapackage.json', format='auto'));

-- List all resource names and paths (Steps 2 and 4)
SELECT r.name, r.path
FROM (SELECT unnest(resources) AS r FROM read_json('datapackage.json', format='auto'));

-- Get description for a specific resource (Step 3)
SELECT r.description
FROM (SELECT unnest(resources) AS r FROM read_json('datapackage.json', format='auto'))
WHERE r.name = 'my_table';

-- List all metadata for every field in a resource (Step 3)
SELECT f AS field_metadata
FROM (
    SELECT unnest(r.schema.fields) AS f
    FROM (SELECT unnest(resources) AS r FROM read_json('datapackage.json', format='auto'))
    WHERE r.name = 'my_table'
);

-- Select specific known fields plus any extras you discover (Step 3)
SELECT
    f.name,
    f.description,
    f.unit,
    f.warning
FROM (
    SELECT unnest(r.schema.fields) AS f
    FROM (SELECT unnest(resources) AS r FROM read_json('datapackage.json', format='auto'))
    WHERE r.name = 'my_table'
);

-- Explore all top-level package fields, excluding resources (Step 3)
SELECT * EXCLUDE (resources) FROM read_json('datapackage.json', format='auto');
```

DuckDB can also read a remote descriptor directly without downloading (Step 1 optional):

```sql
SELECT r->>'$.name' AS name
FROM (
    SELECT unnest(resources) AS r
    FROM read_json('https://example.com/data/datapackage.json', format='auto')
);
```

DuckDB is especially useful when you want to **query descriptor metadata and data
files in the same session** (Steps 3–5). Once you have found a resource's path from
the descriptor, you can query it immediately:

```sql
-- After finding a resource path from the descriptor, query it directly (Step 5)
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
