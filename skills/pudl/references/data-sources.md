# PUDL Data Sources

## Use this when

- Looking up the short code for a data source (needed for Zenodo S3 paths).
- Finding the documentation page for a specific data source.
- Understanding what raw datasets PUDL ingests and processes.

---

## Source catalog

Each row is one raw input dataset. The **short code** is the identifier used in:

- Zenodo S3 paths: `s3://pudl.catalyst.coop/zenodo/<short_code>/<doi>/`
- Table name prefixes (second component): e.g. `out_eia923__generation`
- FERC XBRL descriptor filenames: e.g. `ferc1_xbrl_datapackage.json`

| Short code          | Full name                                                                         | Docs page                                                                              |
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

Sources with `—` in the docs column have no dedicated documentation page yet. Brief
descriptions above are best-effort — check the raw Zenodo descriptor for authoritative
metadata.

---

## Refreshing this list

The authoritative source is the S3 listing. Run this to see current dataset codes:

```bash
aws s3 ls --no-sign-request s3://pudl.catalyst.coop/zenodo/ | awk '{print $2}' | tr -d '/'
```

---

## Reading per-source documentation

Each source with a docs link above has a page describing:

- What the form collects and who files it
- Years and frequency of coverage
- Known data quality issues and gaps
- How PUDL processes and integrates it

The docs index is at:
<https://docs.catalyst.coop/pudl/en/nightly/data_sources/index.html>

Individual pages follow the pattern:
`https://docs.catalyst.coop/pudl/en/nightly/data_sources/<short_code>.html`

Fetch a source page when the user asks about a specific data source and the table
descriptions in the descriptor don't provide enough context:

```bash
curl -s https://docs.catalyst.coop/pudl/en/nightly/data_sources/eia923.html |
	python3 -c "import sys, html.parser; ..."
```

Or use the `WebFetch` tool if available in your environment.
