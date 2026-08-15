#!/usr/bin/env python3
"""Validate release version and pinned SDK metadata without importing the package."""

from __future__ import annotations

import argparse
import ast
import json
import re
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SEMVER = re.compile(r"(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)")


def package_version() -> str:
    tree = ast.parse((ROOT / "asa_cli" / "__init__.py").read_text())
    for node in tree.body:
        if (
            isinstance(node, ast.Assign)
            and any(isinstance(target, ast.Name) and target.id == "__version__" for target in node.targets)
            and isinstance(node.value, ast.Constant)
            and isinstance(node.value.value, str)
        ):
            return node.value.value
    raise ValueError("asa_cli.__version__ is missing or is not a string literal")


def validate(expected_version: str | None = None) -> tuple[str, str]:
    project = tomllib.loads((ROOT / "pyproject.toml").read_text())["project"]
    project_version = project["version"]
    source_version = package_version()

    if not SEMVER.fullmatch(project_version):
        raise ValueError(f"project version must be X.Y.Z, got {project_version!r}")
    if source_version != project_version:
        raise ValueError(
            f"version mismatch: pyproject.toml={project_version}, asa_cli={source_version}"
        )
    if expected_version is not None:
        if not SEMVER.fullmatch(expected_version):
            raise ValueError(f"release tag must be X.Y.Z, got {expected_version!r}")
        if expected_version != project_version:
            raise ValueError(
                f"release tag {expected_version} does not match project version {project_version}"
            )

    manifest_paths = sorted(
        (ROOT / "asa_cli" / "platform" / "manifest").glob("apple_ads_platform_v*.json")
    )
    if len(manifest_paths) != 1:
        raise ValueError(
            f"expected exactly one versioned SDK manifest, found {len(manifest_paths)}"
        )
    manifest = json.loads(manifest_paths[0].read_text())
    sdk = manifest["sdk"]
    sdk_version = sdk["version"]
    expected_dependency = f"{sdk['distribution']}=={sdk_version}"
    if expected_dependency not in project["dependencies"]:
        raise ValueError(
            f"pyproject dependency must contain the manifest pin {expected_dependency!r}"
        )

    readme = (ROOT / "README.md").read_text()
    if f"Apple Ads Platform SDK {sdk_version}" not in readme:
        raise ValueError("README SDK badge or version statement is stale")

    return project_version, sdk_version


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", help="Expected bare X.Y.Z release tag")
    args = parser.parse_args()

    try:
        cli_version, sdk_version = validate(args.version)
    except (KeyError, OSError, ValueError, json.JSONDecodeError, tomllib.TOMLDecodeError) as exc:
        print(f"release metadata error: {exc}", file=sys.stderr)
        return 1

    print(f"release metadata ok: asa {cli_version}, apple-ads-platform {sdk_version}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
