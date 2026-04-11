# AGENTS.md

## Project Overview

This repository contains shareable agent skills — reusable, installable prompts
that give agents specialized knowledge and workflows. Skills live under `skills/`, each
providing reference documentation, example assets, a test suite, and evaluation cases.

## Repository Layout

```
agent-skills/
├── skills/
│   ├── datapackage/     # Generic Frictionless Data Package exploration skill
│   │   ├── SKILL.md           # Skill descriptor (YAML front matter) + usage guide
│   │   ├── scripts/           # generate_examples.py — builds all example datasets
│   │   ├── assets/            # JSON schemas + generated example datapackages
│   │   │   └── examples/      # 8 packages (v1+v2 × csv/parquet/duckdb/sqlite)
│   │   ├── references/        # frictionless-validate.md, metadata-querying.md,
│   │   │                      #   storage-backends.md
│   │   ├── tests/             # pytest suite covering all reference code examples
│   │   └── evals/             # Skill evaluation cases
│   ├── pudl/            # PUDL data-user skill (read tables, explore metadata)
│   └── pudl-dev/        # PUDL developer skill (ETL, schema, CI, dbt, pytest)
├── docs/                # Zensical documentation site source (markdown)
├── .github/workflows/   # CI: test-datapackage.yml, docs.yml
├── pyproject.toml       # Pixi workspace: dependencies, tasks, tool config
├── skills-lock.json     # Pinned external skill versions and hashes
└── .pre-commit-config.yaml
```

External skills (from `skills-lock.json`) are installed into `.agents/skills/`, which
is git-ignored. Install them with `pixi run install-skills`.

## Environment

This repository uses **pixi** for dependency and environment management. All commands
must be run through pixi.

```bash
pixi run <command>          # run any command in the pixi environment
pixi run test-datapackage   # run the datapackage test suite
pixi run install-skills     # install vendored external skills into .agents/
```

Never use `pip install` or `conda install` directly. Add new dependencies with
`pixi add <package>` and commit the updated `pyproject.toml` and `pixi.lock`.

## Pre-commit Checks

Use `prek` to run pre-commit hooks after editing files. Always run the relevant hooks
before staging changes.

**Determine which checks to run from `git status`, not from memory.** Linters,
formatters, and other tools can modify files after you last ran a check, and a file
may arrive via merge or tool output rather than a direct edit. Before deciding which
hooks to run, check what is actually modified — including new untracked files, which
`git diff` does not show:

```bash
git status --short          # all changes: modified, staged, and untracked new files
```

Run the appropriate hooks for every file type that appears in the output.

### Python

```bash
pixi run prek run ruff-check --all-files   # lint (auto-fixes in place)
pixi run prek run ruff-format --all-files  # format (rewrites in place)
pixi run prek run ty-check --all-files     # type checking
```

### JSON

```bash
pixi run prek run pretty-format-json --all-files  # 4-space indent, preserve key order
```

The hook reformats files in place. Python code that writes JSON must use `indent=4`
and the default `ensure_ascii=True` — do **not** pass `ensure_ascii=False`.

### YAML

```bash
pixi run prek run check-yaml --all-files   # syntax validation
pixi run prek run prettier --all-files     # formatting (rewrites in place)
```

For GitHub Actions workflow files, also run:

```bash
pixi run prek run actionlint --all-files   # Actions-specific lint
```

### Markdown

```bash
pixi run prek run markdownlint-cli2 --all-files  # lint
pixi run prek run mdformat --all-files           # format (rewrites in place)
```

`mdformat` is configured with `wrap = "no"` — it does not add hard line breaks. Do not
add hard line breaks manually in markdown files.

### TOML

```bash
pixi run prek run taplo-format --all-files  # format (rewrites in place)
```

## Datapackage Skill Rules

### Editing code examples in reference files

Every code block in `skills/datapackage/references/` is covered by a test in
`skills/datapackage/tests/`. After editing any code example in a reference file, run
the full test suite to confirm the example still works:

```bash
pixi run test-datapackage
```

The mapping from reference file to test file is:

| Reference file                           | Test file                 |
| ---------------------------------------- | ------------------------- |
| `frictionless-validate.md`               | `test_frictionless.py`    |
| `metadata-querying.md` (jq patterns)     | `test_metadata_jq.py`     |
| `metadata-querying.md` (DuckDB patterns) | `test_metadata_duckdb.py` |
| `storage-backends.md`                    | `test_backends.py`        |

### Adding new examples to reference files

When you add a new code example to any reference file, add a corresponding test to the
appropriate test file that runs the pattern against the example data. Check
`tests/conftest.py` for shared constants (row counts, column names, path roots) before
adding new helpers.

### Editing `generate_examples.py`

After modifying `skills/datapackage/scripts/generate_examples.py`, regenerate all
example datasets and verify nothing regressed:

```bash
python skills/datapackage/scripts/generate_examples.py
pixi run test-datapackage
pixi run prek run pretty-format-json --all-files  # reformat generated descriptors
```

## Skill Authoring Guidelines

Each skill directory follows this layout:

```
skills/<name>/
├── SKILL.md       # Required: YAML front matter descriptor + usage guide
├── assets/        # Schemas, cached data, generated example datasets
├── references/    # Long-form reference docs (markdown)
├── scripts/       # Utility scripts (Python or shell)
├── tests/         # pytest suite verifying reference code examples
└── evals/         # Evaluation cases for measuring skill quality
```

- Reference documents in `references/` are the authoritative source for patterns. Test
    files exist solely to validate those patterns; keep them in sync.
- Files marked `linguist-generated=true` in `.gitattributes` are generated outputs —
    never hand-edit them. Regenerate them using the script that produced them. When it
    is not obvious which script to run, check `.gitattributes` first to confirm a file
    is generated, then trace the `linguist-generated` path back to its generator script.
- When adding a test suite to a skill, add a corresponding GitHub Actions workflow under
    `.github/workflows/` with a `paths` filter scoped to that skill's directory.
- External skills are managed through `skills-lock.json`, not added to the repo
    directly. They land in `.agents/skills/` (git-ignored) after `pixi run install-skills`.

## Additional Guidelines

- **Explicit dependencies**: Every tool or runtime invoked directly must be listed as
    an explicit dependency in `pyproject.toml`. Do not rely on transitive dependencies —
    they are an implementation detail of another package and can disappear without warning
    if that package changes. Add missing dependencies with `pixi add <package>`.
- **File size limit**: The `check-added-large-files` hook rejects files over 800 KB. The
    generated DuckDB example files are ~780 KB — avoid making them larger.
- **Typos**: The `typos` checker excludes `skills/*/assets/` because upstream data may
    contain canonical misspellings. Do not add spurious typo suppressions elsewhere.
- **Line endings**: LF only. The `mixed-line-ending` hook enforces this; do not commit
    CRLF line endings.
- **Shell scripts**: Write POSIX-compatible shell. The `shellcheck` hook validates all
    shell scripts.
- **Python type checking**: `ty` runs as a pre-commit hook locally but is skipped in
    CI (`ci: skip: [ty-check]` in `.pre-commit-config.yaml`). Always run it locally
    before committing Python changes.
- **Documentation**: The `docs/` site is built with Zensical and deployed by CI on push
    to `main`. Edit source files in `docs/` (markdown); never commit the `site/` build
    output.
