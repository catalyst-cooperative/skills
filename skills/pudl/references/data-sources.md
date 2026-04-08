# PUDL Data Sources

Use this reference when looking up the short code for a raw input dataset, finding the
documentation page for a specific source, or resolving which datasets PUDL ingests.

> **For agent use, query [`data_sources.json`](../assets/data_sources.json)**
> **with jq or DuckDB rather than reading this file into context.**
> The full source table below is for human reference only.

---

## Querying the machine-readable index

Use [`data_sources.json`](../assets/data_sources.json) for all programmatic lookups.
Fields: `short_code`, `full_name`, `docs_url`.

The **short code** is the identifier used in:

- Cached raw-archive paths: `s3://pudl.catalyst.coop/zenodo/<short_code>/<concrete-doi>/`
- Table name prefixes (second component): e.g. `out_eia923__generation`
- FERC XBRL descriptor filenames: e.g. `ferc1_xbrl_datapackage.json`

### jq examples

```bash
# Find a source by keyword in the full name
jq '[.[] | select(.full_name | test("balancing authority"; "i"))]' assets/data_sources.json

# Get the short code for a specific source
jq '.[] | select(.full_name | test("CEMS"; "i")) | .short_code' assets/data_sources.json

# Get the docs URL for a known short code
jq '.[] | select(.short_code == "ferc1") | .docs_url' assets/data_sources.json

# List all sources with no docs page yet
jq '[.[] | select(.docs_url == null) | .short_code]' assets/data_sources.json
```

### DuckDB examples

```sql
-- Find a source by topic keyword
SELECT short_code, full_name
FROM read_json('assets/data_sources.json')
WHERE full_name ILIKE '%balancing authority%';

-- List all sources that do not yet have docs pages
SELECT short_code, full_name
FROM read_json('assets/data_sources.json')
WHERE docs_url IS NULL
ORDER BY short_code;
```

---

## Refreshing this list

The authoritative source of available datasets is the S3 listing. Run this to see the
current dataset codes:

```bash
aws s3 ls --no-sign-request s3://pudl.catalyst.coop/zenodo/ | awk '{print $2}' | tr -d '/'
```

When a new short code appears there that isn't in `data_sources.json`, add a record to
the JSON asset and regenerate the table below using `python scripts/generate_data_sources_table.py`.

---

## Reading per-source documentation

Each source with a docs URL has a page describing:

- What the form collects and who files it
- Years and frequency of coverage
- Known data quality issues and gaps
- How PUDL processes and integrates it

The docs index is at:
<https://docs.catalyst.coop/pudl/en/nightly/data_sources/index.html>

Fetch a source page when the user asks about a specific data source and the JSON sidecar
does not provide enough context:

```bash
curl -s "$(jq -r '.[] | select(.short_code == "eia923") | .docs_url' assets/data_sources.json)"
```

Or use the `WebFetch` tool if available in your environment.

### Zenodo and DOI conventions

When working with raw input archives, distinguish between the two DOI types:

- The docs page usually lists a **concept DOI** for the dataset lineage as a whole.
- The S3 cache uses the **concrete DOI** for one specific archived version.

Agents should usually use the docs page to understand the source and give users a
stable public link, then use the cached S3 archive for actual metadata lookup or raw
file access.

Prefer the cached S3 `datapackage.json` over the Zenodo website or API when you need to:

- inspect source metadata
- find file names and checksums
- look up licensing or provenance fields
- access the raw files themselves

The Zenodo website is mainly useful when a user wants to visit the source archive on the
web, cite it by DOI, or access a very old version that is no longer present in the S3
cache.

---

## Full source reference

> *Human reference — agents should use the JSON sidecar above.*

<!-- Generated from assets/data_sources.json — do not edit by hand -->

| Short code          | Full name                                                                         | Docs                                                                                   |
| ------------------- | --------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------- |
| `censusdp1tract`    | Census DP1 – Profile of General Demographic Characteristics                       | [docs](https://docs.catalyst.coop/pudl/en/nightly/data_sources/censusdp1tract.html)    |
| `censuspep`         | Census Population Estimates Program (PEP) FIPS Codes                              | [docs](https://docs.catalyst.coop/pudl/en/nightly/data_sources/censuspep.html)         |
| `eia176`            | EIA Form 176 – Annual Natural and Supplemental Gas Supply and Disposition         | [docs](https://docs.catalyst.coop/pudl/en/nightly/data_sources/eia176.html)            |
| `eia191`            | EIA Form 191 – Underground Natural Gas Storage Report                             | —                                                                                      |
| `eia757a`           | EIA Form 757A – Natural Gas Processing Survey                                     | —                                                                                      |
| `eia860`            | EIA Form 860 – Annual Electric Generator Report                                   | [docs](https://docs.catalyst.coop/pudl/en/nightly/data_sources/eia860.html)            |
| `eia860m`           | EIA Form EIA-860M – Monthly Generator Updates                                     | [docs](https://docs.catalyst.coop/pudl/en/nightly/data_sources/eia860.html)            |
| `eia861`            | EIA Form 861 – Annual Electric Power Industry Report                              | [docs](https://docs.catalyst.coop/pudl/en/nightly/data_sources/eia861.html)            |
| `eia923`            | EIA Form 923 – Power Plant Operations Report                                      | [docs](https://docs.catalyst.coop/pudl/en/nightly/data_sources/eia923.html)            |
| `eia930`            | EIA Form 930 – Hourly and Daily Balancing Authority Operations                    | [docs](https://docs.catalyst.coop/pudl/en/nightly/data_sources/eia930.html)            |
| `eiaaeo`            | EIA Annual Energy Outlook (AEO)                                                   | [docs](https://docs.catalyst.coop/pudl/en/nightly/data_sources/eiaaeo.html)            |
| `eiaapi`            | EIA Bulk API Data                                                                 | [docs](https://docs.catalyst.coop/pudl/en/nightly/data_sources/eiaapi.html)            |
| `eiawater`          | EIA Water Thermoelectric Power Report                                             | —                                                                                      |
| `epacamd_eia`       | EPA CAMD to EIA Power Sector Data Crosswalk                                       | [docs](https://docs.catalyst.coop/pudl/en/nightly/data_sources/epacamd_eia.html)       |
| `epacems`           | EPA Hourly Continuous Emissions Monitoring System (CEMS)                          | [docs](https://docs.catalyst.coop/pudl/en/nightly/data_sources/epacems.html)           |
| `ferc1`             | FERC Form 1 – Annual Report of Major Electric Utilities                           | [docs](https://docs.catalyst.coop/pudl/en/nightly/data_sources/ferc1.html)             |
| `ferc2`             | FERC Form 2 – Annual Report of Natural Gas Companies                              | —                                                                                      |
| `ferc6`             | FERC Form 6 – Annual Report of Oil Pipeline Companies                             | —                                                                                      |
| `ferc60`            | FERC Form 60 – Annual Report of Centralized Service Companies                     | —                                                                                      |
| `ferc714`           | FERC Form 714 – Annual Electric Balancing Authority Area and Planning Area Report | [docs](https://docs.catalyst.coop/pudl/en/nightly/data_sources/ferc714.html)           |
| `ferccid`           | FERC Company Identifier (CID) Listing                                             | —                                                                                      |
| `ferceqr`           | FERC Form 920 – Electric Quarterly Report (EQR)                                   | [docs](https://docs.catalyst.coop/pudl/en/nightly/data_sources/ferceqr.html)           |
| `gridpathratoolkit` | GridPath Resource Adequacy Toolkit                                                | [docs](https://docs.catalyst.coop/pudl/en/nightly/data_sources/gridpathratoolkit.html) |
| `nrelatb`           | NREL Annual Technology Baseline (ATB) for Electricity                             | [docs](https://docs.catalyst.coop/pudl/en/nightly/data_sources/nrelatb.html)           |
| `phmsagas`          | PHMSA Annual Natural Gas Report                                                   | [docs](https://docs.catalyst.coop/pudl/en/nightly/data_sources/phmsagas.html)          |
| `rus12`             | USDA RUS Form 12 – Financial and Operating Report: Electric Power Supply          | [docs](https://docs.catalyst.coop/pudl/en/nightly/data_sources/rus12.html)             |
| `rus7`              | USDA RUS Form 7 – Financial and Operating Report: Electric Distribution           | [docs](https://docs.catalyst.coop/pudl/en/nightly/data_sources/rus7.html)              |
| `sec10k`            | U.S. SEC Form 10-K Annual Reports                                                 | [docs](https://docs.catalyst.coop/pudl/en/nightly/data_sources/sec10k.html)            |
| `vcerare`           | Vibrant Clean Energy RARE Power Dataset                                           | [docs](https://docs.catalyst.coop/pudl/en/nightly/data_sources/vcerare.html)           |

<!-- end generated table -->

Sources with `—` in the Docs column have no dedicated documentation page yet.
