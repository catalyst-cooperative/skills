# AGENTS.md

## Project Overview

This repository contains reusable agent skills, prompts, reference documents, and a small set of utility scripts that support them. Most of the repository is Markdown and YAML/TOML configuration, not application code.

The main goals when working here are:

- keep skill instructions and references accurate, concise, and easy for agents to consume
- preserve the repository's existing formatting and frontmatter conventions
- prefer updating source data or generator scripts over hand-editing generated sections

## Repository Structure

Important top-level paths:

- `skills/` - first-party skills and their references, scripts, and cached assets
- `.agents/skills/` - locally installed supporting skills used by this repository
- `docs/` - Zensical-backed site content for human-facing documentation
- `prompts/` - prompt assets
- `.github/` - CI and repo automation
- `pyproject.toml` - Pixi environment, tool dependencies, and `mdformat` config
- `.pre-commit-config.yaml` - canonical lint/format/check definitions
- `.markdownlint.yaml` - Markdown lint rules tuned to the repo's formatting style
- `zensical.toml` - documentation site configuration

Representative Python utilities live under paths like `skills/*/scripts/`. These are small maintenance scripts, not a large application framework.

## Environment And Commands

Use `pixi` for all repository-local commands. Do not use `uv`, `pip`, or ad hoc global tools when a repo-configured tool exists.

Prefer these patterns:

- `pixi run ruff check path/to/file.py`
- `pixi run ruff format path/to/file.py`
- `pixi run ty check path/to/file.py`
- `pixi run markdownlint-cli2 path/to/file.md`
- `pixi run mdformat path/to/file.md`
- `pixi run prettier --write path/to/file.yml`
- `pixi run taplo format path/to/file.toml`
- `pixi run typos path/to/file.md`

For broad validation, prefer the repo's pre-commit configuration instead of inventing one-off command combinations:

- `pixi run prek run --files ...`
- `pixi run prek run --all-files`

`pixi run prek ...` is used in this repo, but `.pre-commit-config.yaml` is the source of truth for what checks should run.

If `prek` fails in the VS Code sandbox because of pseudo-terminal restrictions, run the underlying repo-configured tools directly and report that limitation rather than skipping validation silently.

## Markdown Conventions

This repository is intentionally Markdown-heavy. Follow the existing conventions rather than generic Markdown defaults.

- Treat `pyproject.toml` and `.markdownlint.yaml` as authoritative for Markdown formatting behavior.
- `mdformat` is configured with `wrap = "no"`. Do not manually hard-wrap paragraphs just to satisfy another style preference.
- `.markdownlint.yaml` disables or relaxes several rules to match the repo's actual authoring style. Do not "fix" those patterns unless the config changes.
- Four-space indentation for nested list content is the expected style.
- Raw HTML may be valid and intentional in Zensical content.
- Some files contain fenced code blocks, content tabs, frontmatter, Mermaid blocks, or generated tables. Preserve those structures.

When editing Markdown:

- preserve existing frontmatter exactly unless the task requires changing it
- keep explanations concrete and directive rather than promotional
- prefer small edits over broad rewrites
- re-run `mdformat` and `markdownlint-cli2` on the changed files

## Generated Content

Several Markdown references are partly generated. Do not hand-edit generated table bodies if the file or surrounding instructions indicate a generator owns that section.

Common patterns in this repo:

- sentinel comments that mark generated regions
- JSON sidecars or cached metadata used to render tables
- utility scripts under `skills/*/scripts/` that regenerate sections

When a file has a generated block:

- edit the source data, cached metadata, or generator script
- regenerate the output
- avoid manual follow-up formatting changes inside the generated region unless the generator itself now emits that formatting

## Python Conventions

Python in this repository is mostly utility scripting. Follow the style already present in `skills/*/scripts/`.

- use `pathlib.Path` for filesystem work
- add explicit type hints where they improve readability
- prefer small helper functions over large inline script bodies
- keep top-of-file module docstrings accurate, especially when behavior changes
- use UTF-8 when reading or writing text files
- prefer standard library solutions unless a repo dependency is already the right fit

When changing substantive script behavior, update docstrings and inline usage guidance to match.

## Skill And Reference File Norms

Skill files and supporting references are part of the product here. Preserve their structure.

- keep YAML frontmatter valid and minimal
- maintain the established section layout in `SKILL.md` files unless there is a reason to redesign it
- prefer references and cached artifacts for large factual lookups instead of bloating `SKILL.md`
- write instructions for agents, not marketing copy for humans
- keep examples realistic and copyable

For PUDL-related skills specifically, the repo already encodes conventions like methodology-first explanations and preference for cached metadata over expensive or noisy sources. Extend those patterns rather than replacing them.

## Docs And Site Content

The docs site is configured through `zensical.toml`. When working on content under `docs/`, preserve Zensical-compatible Markdown features already in use, such as admonitions, tabs, and other extended syntax.

If you need to run docs tooling, run Zensical through Pixi rather than assuming a global install.

## Change Scope

Keep changes focused.

- do not reformat unrelated files
- do not rewrite large reference documents unless the task requires it
- do not replace repo-specific commands with generic alternatives
- do not remove generated-content markers or explanatory comments that other scripts rely on

When you are unsure whether a section is generated or hand-maintained, inspect nearby comments and the corresponding `skills/*/scripts/` directory before editing.

## Validation Checklist

After editing, validate only the files you changed unless the task explicitly calls for a broader sweep.

- Python: `ruff check`, `ruff format`, and `ty check` where relevant
- Markdown: `mdformat` and `markdownlint-cli2`
- YAML: `prettier --write` if formatting changed
- TOML: `taplo format` if formatting changed
- spelling-sensitive docs: `typos` when appropriate

If the task touches multiple file types, prefer `pixi run prek run --files ...` once the individual edits are in place.
