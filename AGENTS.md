# AGENTS.md

## Project Overview

This repository contains shareable agent skills: reusable prompts, references, cached
assets, and small support scripts that give agents specialized knowledge and workflows.
Most of the repository is Markdown and YAML/TOML configuration, not application code.

The main goals when working here are:

- keep skill instructions and references accurate, concise, and easy for agents to consume
- preserve existing formatting, frontmatter, and repository conventions
- prefer updating source data or generator scripts over hand-editing generated outputs

## Canonical Guidance

`AGENTS.md` is the canonical source of repository guidance.

`CLAUDE.md` is only a compatibility symlink that points to `AGENTS.md`. Do not treat it
as a separate file or try to keep two copies in sync.

## Repository Structure

Important top-level paths:

- `skills/` - first-party skills authored in this repository. These are the skill files you may edit.
- `.agents/skills/` - installed dependency/support skills used while developing the first-party skills in this repository. Treat these as read-only inputs. Never edit files under this directory as part of work on this repo.
- `docs/` - Zensical-backed site content for human-facing documentation
- `prompts/` - prompt assets
- `.github/` - CI and repository automation
- `pyproject.toml` - Pixi environment, tool dependencies, and `mdformat` config
- `.pre-commit-config.yaml` - canonical lint, format, and check definitions
- `.markdownlint.yaml` - Markdown lint rules tuned to the repo's formatting style
- `skills-lock.json` - pinned external skill dependencies and metadata
- `zensical.toml` - documentation site configuration

Current first-party skills live under `skills/`:

- `datapackage/` - generic Frictionless Data Package exploration skill
- `pudl/` - PUDL data-user skill
- `pudl-dev/` - PUDL contributor and developer skill

Representative Python utilities live under paths like `skills/*/scripts/`. These are
small maintenance scripts, not a large application framework.

## Environment And Commands

Use `pixi` for all repository-local commands. Do not use `uv`, `pip`, or ad hoc global
tools when a repo-configured tool exists.

Useful repo tasks:

- `pixi run install-skills` - install the external skills pinned in `skills-lock.json`
- `pixi run test-datapackage` - run the datapackage reference-example test suite

For iterative work, call the underlying tools directly rather than routing everything
through `prek`. Direct invocation is faster, targets only the files you changed, and
works on new files without staging them first.

Determine which files to validate from `git status --short`, not from memory. Any file
may be modified by a formatter, a merge, or another tool after your last check.

Prefer these patterns:

- `pixi run ruff check --fix path/to/file.py`
- `pixi run ruff format path/to/file.py`
- `pixi run ty check`
- `pixi run markdownlint-cli2 path/to/file.md`
- `pixi run mdformat path/to/file.md`
- `pixi run prettier --write path/to/file.yaml`
- `pixi run taplo format path/to/file.toml`
- `pixi run typos path/to/file.md`
- `pixi run actionlint path/to/workflow.yml`

For broad validation, prefer the repo's pre-commit configuration instead of inventing
one-off command combinations:

- `pixi run prek run --files ...`
- `pixi run prek run --all-files`

JSON formatting is the main exception to the direct-tools rule. The
`pretty-format-json` hook uses repo-specific arguments (`--autofix --indent=2 --no-sort-keys`), so it is simpler and safer to run it through `prek`.

When Python code writes JSON for this repository, use `indent=2` and the default
`ensure_ascii=True`. Do not pass `ensure_ascii=False`.

If `prek` fails in the VS Code sandbox because of pseudo-terminal restrictions, run the
underlying repo-configured tools directly and report that limitation rather than
silently skipping validation.

## Markdown Conventions

This repository is intentionally Markdown-heavy. Follow the existing conventions rather
than generic Markdown defaults.

- Treat `pyproject.toml` and `.markdownlint.yaml` as authoritative for Markdown formatting behavior.
- `mdformat` is configured with `wrap = "no"`. Do not manually hard-wrap paragraphs.
- `.markdownlint.yaml` disables or relaxes several rules to match the repo's authoring style. Do not "fix" those patterns unless the config changes.
- Four-space indentation for nested list content is the expected style.
- Raw HTML may be valid and intentional in Zensical content.
- Some files contain fenced code blocks, tabs, frontmatter, Mermaid blocks, or generated tables. Preserve those structures.

When editing Markdown:

- preserve existing frontmatter exactly unless the task requires changing it
- keep explanations concrete and directive rather than promotional
- prefer small edits over broad rewrites
- re-run `mdformat` and `markdownlint-cli2` on the changed files

## Generated Content

Several files in this repository are wholly or partly generated. Do not hand-edit
generated table bodies or generated data files if a generator owns them.

Common patterns in this repo:

- sentinel comments that mark generated regions
- JSON sidecars or cached metadata used to render tables
- files marked `linguist-generated=true` in `.gitattributes`
- utility scripts under `skills/*/scripts/` that regenerate sections or datasets

When a file has a generated block or generated path:

- edit the source data, cached metadata, or generator script
- regenerate the output
- avoid manual cleanup edits inside the generated region unless the generator itself now emits that formatting

Examples of script-owned outputs include the generated datapackage examples under
`skills/datapackage/assets/examples/` and generated markdown tables produced from
cached metadata.

## Python And Script Conventions

Python in this repository is mostly utility scripting. Follow the style already present
in `skills/*/scripts/`.

- use `pathlib.Path` for filesystem work
- add explicit type hints where they improve readability
- prefer small helper functions over large inline script bodies
- keep top-of-file module docstrings accurate when behavior changes
- use UTF-8 when reading or writing text files
- prefer standard library solutions unless a repo dependency is already the right fit

When changing substantive script behavior, update docstrings and inline usage guidance
to match.

Shell scripts should be POSIX-compatible. The repository validates them with
`shellcheck`.

Every tool or runtime invoked directly should be listed as an explicit dependency in
`pyproject.toml`. Do not rely on transitive dependencies remaining available.

## Skill And Reference File Norms

Skill files and supporting references are part of the product here. Preserve their
structure.

- keep YAML frontmatter valid and minimal
- maintain the established section layout in `SKILL.md` files unless there is a good reason to redesign it
- prefer references and cached artifacts for large factual lookups instead of bloating `SKILL.md`
- write instructions for agents, not marketing copy for humans
- keep examples realistic and copyable

Reference documents in `references/` are the authoritative source for reusable patterns.
Tests exist to validate those patterns and should stay in sync with them.

Each skill directory generally follows this layout:

```text
skills/<name>/
├── SKILL.md
├── assets/
├── references/
├── scripts/
├── tests/
└── evals/
```

When adding a test suite to a skill, add a corresponding GitHub Actions workflow under
`.github/workflows/` with a `paths` filter scoped to that skill's directory.

External skills are managed through `skills-lock.json`, not by editing the installed
copies under `.agents/skills/`.

### Layered Skills

Prefer linking layered skills to shared references instead of duplicating content.

That means:

- generic knowledge belongs in the lower-level skill that owns it
- higher-level skills should reference that shared guidance and add only domain-specific or workflow-specific context
- when a shared reference already exists, link to it instead of maintaining a second copy

In this repository, `datapackage` owns generic datapackage querying and loading
patterns, `pudl` layers PUDL-specific data context on top of that, and `pudl-dev`
should reference shared data-context guidance rather than duplicating it.

If a skill depends on another skill conceptually, make that dependency explicit in the
skill's frontmatter or instructions rather than copying large sections of shared text.

## Datapackage-Specific Rules

The datapackage skill has a few repository-level rules that are specific enough to call
out here.

When editing code examples in `skills/datapackage/references/`, run the full datapackage
test suite afterward:

```bash
pixi run test-datapackage
```

When adding a new example to a datapackage reference file:

- add a corresponding test under `skills/datapackage/tests/`
- check `skills/datapackage/tests/conftest.py` for shared constants before adding new helpers

After modifying `skills/datapackage/scripts/generate_examples.py`, regenerate the
example datasets and reformat the generated descriptors:

```bash
pixi run python skills/datapackage/scripts/generate_examples.py
pixi run test-datapackage
pixi run prek run pretty-format-json --files skills/datapackage/assets/examples/v*/*/datapackage.json
```

Do not hand-edit generated example assets under `skills/datapackage/assets/examples/`
when the generator is the real source of truth.

## Additional Repository Constraints

- The `check-added-large-files` hook is configured at 800 KB to catch accidental large-file additions. Treat that threshold as a prompt to confirm intent, not as a blanket prohibition on larger generated artifacts.
- LF line endings are required. The repository fixes or rejects mixed line endings.
- `typos` excludes `skills/*/assets/` and certain generated reference tables because upstream canonical data may contain intentional misspellings. Do not add unnecessary suppressions elsewhere.
- `ty` is intentionally run over the whole repository. It is fast enough not to be burdensome here, and project-wide checking catches cross-file import, symbol redefinition, and interface drift issues that file-scoped checks can miss.
- The `ty` hook is skipped in CI, so run it locally when Python changes are relevant.

## Docs And Site Content

The docs site is configured through `zensical.toml`. When working on content under
`docs/`, preserve Zensical-compatible Markdown features already in use, such as
admonitions, tabs, and other extended syntax.

If you need to run docs tooling, run Zensical through Pixi rather than assuming a
global install.

Edit source files in `docs/`. Do not commit the built `site/` output.

## Change Scope

Keep changes focused.

- do not reformat unrelated files
- do not rewrite large reference documents unless the task requires it
- do not replace repo-specific commands with generic alternatives
- do not remove generated-content markers or explanatory comments that other scripts rely on

When you are unsure whether a section is generated or hand-maintained, inspect nearby
comments and the corresponding `skills/*/scripts/` directory before editing.

## Validation Checklist

After editing, validate only the files you changed unless the task explicitly calls for
a broader sweep.

Use `git status --short` to decide which files need checking.

- Python: `ruff check --fix`, `ruff format`, and `ty check` when Python changes are relevant
- Markdown: `mdformat` and `markdownlint-cli2`
- JSON: `pixi run prek run pretty-format-json --files ...`
- YAML: `prettier --write`
- GitHub Actions workflows: `actionlint`
- TOML: `taplo format`
- spelling-sensitive docs: `typos` when appropriate

If a task touches multiple file types, prefer `pixi run prek run --files ...` once the
individual file-level checks are in place.
