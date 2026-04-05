# [Catalyst Cooperative](http://github.com/catalyst-cooperative) Agent Skills

This repository contains experimental [agent skills](https://agentskills.io) related to
PUDL (the Public Utility Data Liberation Project).

- `datapackage` is for exploring metadata annotations stored in
  [Frictionless Data Packages](https://specs.frictionlessdata.io/data-package/) generally.
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
- [Equipping Agents for the Real World With Agent
  Skills](https://claude.com/blog/equipping-agents-for-the-real-world-with-agent-skills)
  (Anthropic)
- [Claude Developer Guide Agent Skills
  Overview](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)
  (Anthropic)
- [Create a Claude Plugin Marketplace](https://code.claude.com/docs/en/plugin-marketplaces) (Anthropic)

## Agentic (Data) Engineering

- [Agentic Engineering Patterns](https://simonwillison.net/guides/agentic-engineering-patterns/) (Simon Willison)
- [Zero Degree-of-Freedom LLM Coding using Executable
  Oracles](https://john.regehr.org/writing/zero_dof_programming.html) (John Regehr)
- [Dagster University AI Driven Data Engineering](https://courses.dagster.io/courses/take/ai-driven-data-engineering) (Dagster)
- [Best practices for LLM Dagster Development](https://www.youtube.com/watch?v=nmuQPU9bzQ4) (Dagster)
- [What Is Code Review For](https://blog.glyph.im/2026/03/what-is-code-review-for.html) (Glyph)
- [Your job is to deliver code you have proven to
  work](https://simonwillison.net/2025/Dec/18/code-proven-to-work/) (Simon Willison)

## Agentic (Meta)Data Exploration

- [Coding agents for data analysis](https://simonw.github.io/nicar-2026-coding-agents/) (Simon Willison)

## Other related skills

- [duckdb-skills](https://github.com/duckdb/duckdb-skills)
- [marimo-pair](https://github.com/marimo-team/marimo-pair)
- [skill-creator](https://github.com/anthropics/claude-plugins-official/tree/main/plugins/skill-creator)
- [dignified-python](https://github.com/dagster-io/skills/tree/main/plugins/dignified-python)

## Remaining Development Tasks

### `agent-skills` Repository Setup

- [x] Make markdown linting work for everything!
- [ ] Set up typos exceptions & excluded files to work with actual repo contents.

### Datapackage Skill

- [x] Add in the datapackage v1 spec
- [x] Add informal v1 "patterns" summary / reference & link
- [x] Add informal v2 "recipes" summary / reference & link
- [ ] Generate example data packages using v1 schema

### PUDL Skill

- [x] Ask why not use a hierarchical JSON structure for the system of accounts data? Right
  now it's just a big list of elements.
- [x] Add links to PUDL Methodology docs
- [x] Add PUDL Dataset Citation
- Compile FERC schedule, table, and account metadata into the skill assets:
  - [ ] **FERC Form 1**
    - [x] Rename `ferc_accounts.json` -> `ferc_electricity_accounts.json` since now we
      have multiple systems of accounts for different domains.
    - [ ] Update outdated links / references to `ferc_accounts.json`.
    - [ ] Try regenerating ferc1_schedules.json using [this prompt](prompts/compile-ferc-schedule-metadata.md)
      and compare the results to our existing file.
    - [ ] Add reference and link back to the PDF & HTML forms in the PUDL docs
  - [ ] **FERC Form 2**
    - [x] extract schedule titles, descriptions, and FERC Accounts from HTML docs
    - [x] generate schedule to XBRL table mappings
    - [x] generate schedule to DBF table mappings
    - [ ] Add reference and link back to the HTML form in PUDL docs
    - [ ] Add separate `ferc_natural_gas_accounts.json` based on
      [Uniform System of Accounts (18 C.F.R. Part 201)](https://www.ecfr.gov/current/title-18/chapter-I/subchapter-B/part-201)
  - [ ] **FERC Form 6**
    - [x] extract schedule titles, descriptions, and FERC Accounts from HTML docs
    - [x] generate schedule to XBRL table mappings
    - [x] generate schedule to DBF table mappings
    - [ ] Add reference and link back to the HTML form in PUDL docs
    - [ ] Add separate `ferc_oil_pipeline_accounts.json` based on
      [Uniform System of Accounts (18 C.F.R. Part 352)](https://www.ecfr.gov/current/title-18/chapter-I/subchapter-Q/part-352)
  - [ ] **FERC Form 60**
    - [ ] extract schedule titles, descriptions, and FERC Accounts from HTML docs
    - [ ] generate schedule to XBRL table mappings
    - [ ] generate schedule to DBF table mappings
    - [ ] Add reference and link back to the HTML form in PUDL docs
    - [ ] Add separate `ferc_service_company_accounts.json` based on
      [Uniform System of Accounts (18 C.F.R. Part 367)](https://www.ecfr.gov/current/title-18/chapter-I/subchapter-F/part-367)
  - [ ] **FERC Form 714**
    - [ ] extract schedule titles, descriptions, and FERC Accounts from HTML docs
    - [ ] generate schedule to XBRL table mappings
    - [ ] Add reference and link back to the HTML form in PUDL docs

### Metadata Access Tasks

- [ ] Note that our table descriptions have 1-line summaries like python docstrings, and
  that full table descriptions can be quite long (paragraphs). Read the first line
  to help determine whether the table is relevant before reading the entire table
  description.

### Data Access Tasks

- [ ] Figure out why it's so slow when returning sample data
- [ ] Tell it to return rendered markdown, not CSV in chat
- [ ] Test it out in a notebook

## Skill Evaluations

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
- Experiment with DuckDB natural language queryies through the query skill. How does it work?
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
  primary consumers are now agents, data scientists, and tools that all expect Markdown
  or plain text. Converting at export (using docutils + a Markdown writer, or rst2md)
  eliminates the parsing burden we just documented, and makes descriptions immediately
  readable in any JSON viewer, notebook, or agent context.
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
