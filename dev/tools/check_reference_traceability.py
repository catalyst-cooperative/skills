#!/usr/bin/env python3
"""Validate snippet-to-test traceability manifests for all skills."""

import ast
import json
import re
from pathlib import Path
from typing import Annotated

from pydantic import BaseModel, Field, StringConstraints, ValidationError

SNIPPET_PATTERN = re.compile(r"<!--\s*snippet:\s*([a-z0-9][a-z0-9.-]*)\s*-->")
NODE_ID_PATTERN = re.compile(r"^[^:]+\.py::[A-Za-z_][A-Za-z0-9_]*$")

SnippetId = Annotated[str, StringConstraints(pattern=r"^[a-z0-9][a-z0-9.-]*$")]
NodeId = Annotated[
    str, StringConstraints(pattern=r"^[^:]+\.py::[A-Za-z_][A-Za-z0-9_]*$")
]


class SnippetMapping(BaseModel):
    snippet_id: SnippetId
    reference: str
    tests: list[NodeId] = Field(min_length=1)


class SkillManifest(BaseModel):
    skill: str = Field(min_length=1)
    mappings: list[SnippetMapping] = Field(min_length=1)


def load_manifest(path: Path) -> SkillManifest:
    data = json.loads(path.read_text(encoding="utf-8"))
    return SkillManifest.model_validate(data)


def extract_snippet_ids(reference_path: Path) -> list[str]:
    text = reference_path.read_text(encoding="utf-8")
    return SNIPPET_PATTERN.findall(text)


def extract_python_function_names(test_file_path: Path) -> set[str]:
    tree = ast.parse(test_file_path.read_text(encoding="utf-8"))
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            names.add(node.name)
    return names


def parse_node_id(node_id: str) -> tuple[Path, str]:
    file_part, test_part = node_id.split("::", 1)
    test_name = test_part.split("::")[-1]
    return Path(file_part), test_name


def validate_manifest(manifest_path: Path, repo_root: Path) -> list[str]:
    errors: list[str] = []

    try:
        manifest = load_manifest(manifest_path)
    except json.JSONDecodeError as exc:
        return [f"{manifest_path}: invalid JSON ({exc})"]
    except ValidationError as exc:
        return [f"{manifest_path}: manifest schema validation failed\n{exc}"]

    reference_to_mapped_ids: dict[Path, set[str]] = {}
    reference_to_all_ids: dict[Path, list[str]] = {}
    test_function_cache: dict[Path, set[str]] = {}

    for idx, mapping in enumerate(manifest.mappings):
        label = f"{manifest_path}: mappings[{idx}]"
        reference_path = (repo_root / mapping.reference).resolve()

        if not reference_path.exists():
            errors.append(
                f"{label}: reference file does not exist: {mapping.reference}"
            )
            continue

        if reference_path not in reference_to_all_ids:
            reference_to_all_ids[reference_path] = extract_snippet_ids(reference_path)

        all_ids = reference_to_all_ids[reference_path]
        occurrences = all_ids.count(mapping.snippet_id)
        if occurrences == 0:
            errors.append(
                f"{label}: snippet_id '{mapping.snippet_id}' not found in {mapping.reference}"
            )
        elif occurrences > 1:
            errors.append(
                f"{label}: snippet_id '{mapping.snippet_id}' appears {occurrences} times in {mapping.reference}; expected exactly once"
            )

        mapped_ids = reference_to_mapped_ids.setdefault(reference_path, set())
        if mapping.snippet_id in mapped_ids:
            errors.append(
                f"{label}: duplicate mapping entry for snippet_id '{mapping.snippet_id}' in {mapping.reference}"
            )
        mapped_ids.add(mapping.snippet_id)

        for test_idx, node_id in enumerate(mapping.tests):
            test_label = f"{label}.tests[{test_idx}]"
            if not NODE_ID_PATTERN.fullmatch(node_id):
                errors.append(
                    f"{test_label}: invalid node id '{node_id}', expected path.py::test_name"
                )
                continue

            test_file_rel, test_name = parse_node_id(node_id)
            test_file_path = (repo_root / test_file_rel).resolve()
            if not test_file_path.exists():
                errors.append(
                    f"{test_label}: test file does not exist: {test_file_rel.as_posix()}"
                )
                continue

            if test_file_path not in test_function_cache:
                test_function_cache[test_file_path] = extract_python_function_names(
                    test_file_path
                )

            if test_name not in test_function_cache[test_file_path]:
                errors.append(
                    f"{test_label}: test function '{test_name}' not found in {test_file_rel.as_posix()}"
                )

    for reference_path, all_ids in reference_to_all_ids.items():
        mapped_ids = reference_to_mapped_ids.get(reference_path, set())
        unmapped_ids = sorted(set(all_ids) - mapped_ids)
        if unmapped_ids:
            rel = reference_path.relative_to(repo_root)
            errors.append(
                f"{manifest_path}: unmapped snippet IDs in {rel.as_posix()}: {', '.join(unmapped_ids)}"
            )

    return errors


def main() -> int:
    repo_root = Path(__file__).resolve().parents[2]
    manifests = sorted(repo_root.glob("dev/skills/*/reference-snippet-manifest.json"))

    if not manifests:
        print("No manifests found under dev/skills/*/reference-snippet-manifest.json")
        return 1

    all_errors: list[str] = []
    for manifest_path in manifests:
        all_errors.extend(validate_manifest(manifest_path, repo_root))

    if all_errors:
        print("Reference traceability check failed:")
        for error in all_errors:
            print(f"- {error}")
        return 1

    print(f"Reference traceability check passed for {len(manifests)} manifest(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
