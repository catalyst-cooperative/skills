# [Catalyst Cooperative](http://github.com/catalyst-cooperative) Agent Skills

This repository contains experimental [agent skills](https://agentskills.io) related to PUDL (the Public Utility Data Liberation Project).

- `datapackage` is for exploring metadata annotations stored in [Frictionless Data Packages](https://specs.frictionlessdata.io/data-package/) generally.
- `pudl` is for exploring and working with [PUDL open energy data and metadata](https://data.catalyst.coop)
- `pudl-dev` is for maintaining and contributing to the [PUDL open source project](https://github.com/catalyst-cooperative/pudl)

## Agent Skills Resources

### For Users

- [Using Agent Skills in VS Code](https://code.visualstudio.com/docs/copilot/customization/agent-skills)
- [Extend Claude with Agent Skills](https://code.claude.com/docs/en/skills)
- [npx skills](https://github.com/vercel-labs/skills) (CLI for installing skills)
- [Agent Skill Installation CLI](https://www.npmjs.com/package/skills)
- ⚠️ [The Agent Skills Directory](https://skills.sh/) ⚠️

### For Skills Authors

- [The Agent Skills Standard](https://agentskills.io)
- [Skill Authoring Best Practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices) (Anthropic)
- [Equipping Agents for the Real World With Agent Skills](https://claude.com/blog/equipping-agents-for-the-real-world-with-agent-skills) (Anthropic)
- [Claude Developer Guide Agent Skills Overview](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview) (Anthropic)
- [Create a Claude Plugin Marketplace](https://code.claude.com/docs/en/plugin-marketplaces) (Anthropic)

## Agentic (Data) Engineering

- [Agentic Engineering Patterns](https://simonwillison.net/guides/agentic-engineering-patterns/) (Simon Willison)
- [Zero Degree-of-Freedom LLM Coding using Executable Oracles](https://john.regehr.org/writing/zero_dof_programming.html) (John Regehr)
- [Dagster University AI Driven Data Engineering](https://courses.dagster.io/courses/take/ai-driven-data-engineering) (Dagster)
- [Best practices for LLM Dagster Development](https://www.youtube.com/watch?v=nmuQPU9bzQ4) (Dagster)
- [What Is Code Review For](https://blog.glyph.im/2026/03/what-is-code-review-for.html) (Glyph)
- [Your job is to deliver code you have proven to work](https://simonwillison.net/2025/Dec/18/code-proven-to-work/) (Simon Willison)

## Agentic (Meta)Data Exploration

- [Coding agents for data analysis](https://simonw.github.io/nicar-2026-coding-agents/) (Simon Willison)

## Other related skills

Agent skills defined outside of this repo that we either used in creating the Catalyst
Cooperative agent skills, or that we delegate to within the skill.

- [duckdb-skills](https://github.com/duckdb/duckdb-skills)
- [marimo-pair](https://github.com/marimo-team/marimo-pair)
- [skill-creator](https://github.com/anthropics/claude-plugins-official/tree/main/plugins/skill-creator)
- [dignified-python](https://github.com/dagster-io/skills/tree/main/plugins/dignified-python)

## Skill Development Tasks

### `agent-skills` Repository Setup

- [x] Make markdown linting work for everything!
- [x] Merge repo setup into `main` to reduce diffs
- [x] Set up typos exceptions & excluded files to work with actual repo contents.
- [ ] Add an `AGENTS.md` to make the :robot: less annoying

### Datapackage Skill

- [x] Add datapackage v1 JSON schema / spec links
- [x] Add informal v1 "patterns" summary / reference & link
- [x] Add informal v2 "recipes" summary / reference & link
- [ ] **Also** generate example data packages using v1 schema for reference

### PUDL Skill

#### Metadata Retrieval

- [x] Given a topical query, return a list of related tables with summaries
- [x] Explain limitations, caveats, or warnings associated with a table
- [ ] Provide correct background information about a specific data source (ferceqr, eia923, phmsagas, etc)
- [ ] Provide table-links to data viewer and data dictionary in responses
- [ ] Correctly identify the data sources that went into a table
- [ ] Construct a Mermaid diagram based on ancestor/child nodes in Dagster graph
- [ ] Construct a Mermaid diagram based on foreign key relationships in the datapackage metadata

#### Data Provenance

- [x] Link to appropriate Methodology pages
- [ ] Construct URLs that link to data source documentation pages
- [ ] Provide Zenodo DOIs of raw source data inputs for a given table
- [ ] Tell when the data associated with this datapackage was published by Catalyst
- [ ] Tell when a given dataset was last updated by its source
- [ ] Correctly describe licensing of the data
- [ ] Provide correct PUDL data citation
- [ ] Provide link to Zenodo archive of PUDL data release + DOI
- [ ] Provide link to original data source site (EIA, FERC, etc.)

#### Data Retrieval

- [ ] Given a table, quickly return a readable Parquet data sample from S3
- [ ] Given a table, quickly return a readable FERC XBRL DuckDB data sample from S3
- [ ] Given a table, quickly return a readable FERC DBF SQLite data sample from S3
- [ ] Figure out why it's so slow when returning sample data
- [ ] Tell it to return rendered markdown, not CSV in chat
- [ ] Test sample data retrieval in JupyterLab
- [ ] Test sample data retrieval in Marimo
- [ ] Test sample data retrieval in Claude Code
- [ ] Test sample data retrieval in VS Code / Co-pilot Chat
- [ ] Test sample data retrieval in Codex
- [ ] Provide correct size (MB), length (rows) and width (columns) for data
- [ ] Caution the user against trying to do analysis directly within the LLM

#### Comms Handoff

Providing users with next steps to get help, ask questions, or contribute.

- [ ] Connect user to PUDL Data Viewer to explore data interactively
- [ ] Construct URLs that link to PUDL Data Viewer for a specific table
- [ ] Guide user through creating a new GitHub discussion to ask for help
- [ ] Guide user through opening a new data bug for a specific table on GitHub
- [ ] Guide user through signing up for PUDL office hours
- [ ] Guide user through signing up for email newsletter
- [ ] Provide Catalyst business contact information so user can hire us
- [ ] Connect user to OpenCollective PUDL project to contribute financially
- [ ] Connect user to PUDL GitHub repo to contribute code or documentation (good first issues)

### Metadata Compilation

With [a good prompt](prompts/compile-ferc-schedule-metadata.md) the clankers can pull
together FERC metadata from several different sources into a structured JSON file that
links together the form schedules, DBF/XBRL database tables, relevant FERC Accounts, and
human-readable descriptions. This is helpful for data discovery since people could be
approaching the data from any of those directions, and being able to connect to the CFR,
the blank forms, the XBRL derived metadata, and of course the data itself makes the FERC
mess a lot more accessible. We're one of the only semi-usable sources for this data so
even though it's not fully integrated into PUDL it feels important to expose it well.

#### General Improvements

- [ ] **Review and Regenerate** The long prompt resulted in much better human-readable
    descriptions (for Form 6). I've spot checked to make sure they aren't hallucinations,
    and so far so good, but we should probably do a more comprehensive review. If they're
    good then we should try regenerating the FERC 1 and FERC 2 outputs and compare them to
    the current versions.
- [ ] **Extract more FERC Accounts** Spot checks also revealed that the clankers didn't
    extract all of the mentioned FERC Accounts, so we might want to explicitly ask them to
    be more aggressive about that, and then to validate the account numbers extracted and
    their local context vs. the account descriptions extracted from the CFR.
- [ ] **Compile FERC Account Summaries** One thing that I discovered looking through the
    extracted metadata is that there are **separate** systems of accounts for electricity,
    natural gas, oil pipelines, and service companies, which are all documented in different
    parts of the CFR. We should extract the titles and short descriptions for all of them.

#### FERC Form 1

- [x] Rename `ferc_accounts.json` -> `ferc_electricity_accounts.json` since now we
    have multiple systems of accounts for different domains.
- [x] Rename `ferc-uniform-system-of-accounts.md` -> `ferc-electricity-accounts.md`
    to `ferc-electricity-accounts.md`
- [x] Update outdated links / references to `ferc-uniform-system-of-accounts.md` and
    `ferc_electricity_accounts.json`.
- [ ] Try regenerating ferc1_schedules.json using [this prompt](prompts/compile-ferc-schedule-metadata.md)
    and compare the results to our existing file.
- [ ] Add reference and link back to the PDF & HTML forms in the PUDL docs

#### FERC Form 2

- [x] extract schedule titles, descriptions, and FERC Accounts from HTML docs
- [x] generate schedule to XBRL table mappings
- [x] generate schedule to DBF table mappings
- [ ] Add reference and link back to the HTML form in PUDL docs
- [ ] Try regenerating ferc2_schedules.json using [this prompt](prompts/compile-ferc-schedule-metadata.md)
- [ ] Compile `ferc_natural_gas_accounts.json`/`ferc-natural-gas-accounts.md` based on
    [18 C.F.R. Part 201](https://www.ecfr.gov/current/title-18/chapter-I/subchapter-B/part-201)

#### FERC Form 6

- [x] extract schedule titles, descriptions, and FERC Accounts from HTML docs
- [x] generate schedule to XBRL table mappings
- [x] generate schedule to DBF table mappings
- [ ] Add reference and link back to the HTML form in PUDL docs
- [ ] Compile `ferc_oil_pipeline_accounts.json`/`ferc-oil-pipeline-accounts.md` based on
    [18 C.F.R. Part 352](https://www.ecfr.gov/current/title-18/chapter-I/subchapter-Q/part-352)

#### FERC Form 60

- [ ] extract schedule titles, descriptions, and FERC Accounts from HTML docs
- [ ] generate schedule to XBRL table mappings
- [ ] generate schedule to DBF table mappings
- [ ] Add reference and link back to the HTML form in PUDL docs
- [ ] Compile `ferc_service_company_accounts.json`/`ferc-service-company-accounts.md` based on
    [18 C.F.R. Part 367](https://www.ecfr.gov/current/title-18/chapter-I/subchapter-F/part-367)

#### FERC Form 714

- [ ] extract schedule titles, descriptions, and FERC Accounts from HTML docs
- [ ] generate schedule to XBRL table mappings
- [ ] Add reference and link back to the HTML form in PUDL docs

## Evaluate Skill Performance / Ergonomics

### Eval Mechanics

- Understand the eval JSON format so we can write our own.
- Figure out how to run one eval at a time and look at the results, without having to
    run the whole suite. Otherwise the token burn is too high.

### Review existing evals

- Created by the clankers. Mostly focused on mechanics of using the skill, whether
    instructions are followed, etc.

### Create domain-specific evals

- Q: "Does PUDL have any data related to electric utility political spending?"
    - A: Should surface FERC Form 1, Schedule 114, and FERC Account 426.4.
- Q: "I'm working on a report about the rising cost of electricity. What data does PUDL
    have that could be relevant?"
- Q: "I want to understand how the heat rate of coal and natural gas generators
    varies seasonally. What data does PUDL have that could help me with that?"
- Q: "I want to understand how the heat rate of coal and natural gas fired generators
    varies with the level of power output. What data does PUDL have that could help me with
    that?"
- Q: "I'm working on a project about how utilities overestimate future electricity
    demand in order to justify building new power plants, which increases costs for
    customers and leads to overbuilding. What data does PUDL have that could be relevant
    to that?"
- Q: "I want to understand where battery storage is being deployed on the grid, and how
    it's being used. What data does PUDL have that could help me with that?"
- Q: "I want to understand how increasing electricity demand from datacenters is driving
    new fossil fuel power plant construction, or resulting in keeping fossil power plants
    open that would otherwise be retired. What data does PUDL have that could help me with
    that?"
- Q: "I want to understand how weather impacts renewable energy generation and what that
    means in terms of the need for fossil fuel backup generation. What data does PUDL have
    that could help me with that?"
- Q: "I'm looking for dta on how the wind and solar power purchase agreement (PPA)
    prices have evolved over time, how they vary by location, and how including battery
    storage impacts those prices. What data does PUDL have that could be relevant to that?"
- Q: "/pudl tell me what kinds of electricity products are being bought and sold in the
    transactions reported in the FERC EQR dataset."
    - Good answer, but it repeatedly used `curl` to download the EQR datapackage descriptor
        via https and pipe the output into jq, instead of querying the remote JSON using
        `duckdb-skills:query` or downloading the descriptor once and querying it locally.
        This suggests that the skill instructions may not be clear enough about how to use
        `duckdb` for metadata queries, or that the agent is having trouble following them.

### Skills Environment Ergonomics

- How hard is it to get `duckdb` installed on the user's machine if they don't have it
    already?
- How hard is it for agents to run python code if we encourage `uv` for dependency
    management? Use `pip` as a fallback only?
- How much does behavior / performance vary across agents and environments?
- How can we prevent the clankers from cheating and looking at the PUDL repo if I have
    it checked out locally?

### Metadata Queries

- Test performance of `jq` vs `duckdb-skills:query` for metadata queries on large
    `datapackage.json` files. If `duckdb-skills:query` is much better, make `jq` the fallback.
- Experiment with DuckDB natural language queries through the query skill. How does it work?
    Does it work well? Should we explicitly direct agents / users to use it?
- Should we check the hash and size of files before querying them? Or at some point in
    the process to avoid accidentally using metadata associated with the wrong data?

### Data Querying

- While experimenting locally, queries seemed **very** slow, which is surprising. Need to
    investigate.
- Figure out what the best output format is for chat-based results. DuckDB and pandas can both
    produce markedown tables. What about polars? Should experiment and see what instructions
    result in best outputs, assuming user is not in Jupyter/Marimo.
- Needs to be able to sample data, not just download the whole thing, or the first 10 rows.
- Create some heuristics for when to use `duckdb` vs. `pandas` vs. `polars`. `duckdb`
    seems more likely to be installable, works for both JSON and tabular data. Known to be
    very robust.

## PUDL Improvements

- **High Priority:** Convert RST to Markdown at export time — the biggest single
    improvement. Descriptions are authored in RST for Sphinx, but the descriptor's
    primary consumers are now agents, data scientists, and tools that all expect
    Markdown or plain text. Converting at export (using docutils + a Markdown writer, or
    rst2md) eliminates the parsing burden we just documented, and makes descriptions
    immediately readable in any JSON viewer, notebook, or agent context.
- **High Priority:** Structured warnings field — currently warnings are embedded as ..
    `warning::` blocks inside RST description text, which means agents must parse prose
    to find them. A dedicated "warnings": ["..."] array on each resource (using a
    Frictionless custom property) would let agents trivially surface them before
    providing loading code, without any text parsing.
- **High Priority:** Explicit tier field — the `out_*` / `core_*` / `_core_*` / `raw_*`
    naming convention encodes a lot of semantics that agents and humans currently infer
    from the name. An explicit "tier": "output" (or "core", "raw") field makes it
    queryable directly and removes dependence on parsing the table name.
- **Medium Priority:** Per-field example values — the Frictionless spec supports an
    example property on fields. Adding representative values (e.g., "2023-01-01" for a
    date column, "DUKE ENERGY CAROLINAS" for a utility name) would give agents and users
    immediate intuition about what each column contains without loading data.
- **Enhancement:** Source linkage per table — the Frictionless sources property can be
    attached at the resource level, not just the package level. Populating it with the
    originating EIA/FERC/EPA form name, URL, and Zenodo DOI per table would let agents
    answer provenance questions directly from the descriptor.
- **Enhancement:** Many warnings actually pertain to a single column rather than a
    whole table. Providing column-level structured warnings would give users and agents
    more precise information about potential issues in the data and how to handle them.
- We should explicitly describe any non-standard metadata fields we add to our
    datapackages. They could be documented with an extended PUDL datapackage JSON schema.
- Add foreign key constraints to our datapackage metadata. We already generate them
    programmatically and the standard supports them. Including them in the metadata would
    allow agents to understand the relationships between tables and generate more
    accurate queries/join code.
- Add field content constraints that we have already defined, like regexes or min/max
    values, to help users and agents understand the expected format and range of values in
    each column. (goes well with "example values" above)
- Calculate the hash and file size fields for our Parquet datapackage outputs so that
    agents can check that the user has the right file before trying to load it.
- Embed unique IDs (UUID, DOI) and versions (e.g. tags `nightly-2026-04-03` or
    `v2026.4.0`) in our datapackages so they don't get used alongside the wrong data.
- The paths we use in the XBRL datapackages are incorrect. They're absolute paths on
    the build machine, which need to be fixed.
- We need separate SQLite and DuckDB data packages to use separate paths, or (better)
    we need to migrate fully to DuckDB alone for the published DBs.
- The table/resource descriptions in the FERC XBRL datapackages are not informative.
    They're just an ID string. We need to figure out how to programmatically extract real
    descriptions and use them.
- We don't currently distribute any structured source-level metadata (e.g. about EIA-860)
    despite the fact that we have compiled a lot of it. Having that in a structured, queryable
    format would be helpful.
- Figure out how we are **really** supposed to be using `path` in the datapackages that
    annotate SQLite and DuckDB files, and how we are supposed to reference the tables within
    them. Update the datapackages to follow the spec and update the skill instructions accordingly.
