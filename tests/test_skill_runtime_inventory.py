"""Coverage checks for generated v1, v5, and workflow command inventories."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from _command_catalog import catalog_entries, load_manifest  # noqa: E402
from _runtime_catalog import (  # noqa: E402
    platform_registrations,
    v5_commands,
    workflow_commands,
)


def test_platform_runtime_reconciles_all_99_manifest_methods_once():
    manifest = load_manifest()
    manifest_methods = {operation["sdk_method"] for operation in manifest["operations"]}
    registrations = platform_registrations()

    assert len(manifest_methods) == 99
    assert set(registrations) == manifest_methods
    assert len({registration.path for registration in registrations.values()}) == 99

    entries = catalog_entries(manifest)
    assert len(entries) == 99
    assert all(entry.status == "implemented" for entry in entries)
    assert all(entry.runtime_registered for entry in entries)


def test_platform_runtime_captures_exact_usage_and_options():
    registration = platform_registrations()["search_term_popularity_query"]

    assert registration.path == "asa insights search-term-popularity"
    assert registration.usage == "Usage: asa insights search-term-popularity [OPTIONS]"
    parameters = {parameter.name: parameter for parameter in registration.parameters}
    assert parameters["request_file"].declarations == ("--file",)
    assert parameters["request_file"].required is True
    assert parameters["ad_account_id"].declarations == ("--ad-account",)
    assert parameters["ad_account_id"].envvar == "ASA_AD_ACCOUNT_ID"


def test_v5_runtime_inventory_has_65_unique_public_commands():
    commands = v5_commands()
    paths = [command.path for command in commands]

    assert len(paths) == len(set(paths)) == 65
    assert all(path.startswith("asa v5 ") for path in paths)
    assert "asa v5 optimize" in paths
    assert "asa v5 campaigns clone" in paths
    assert "asa v5 reports impression-share" in paths


def test_generated_v5_reference_contains_each_public_command_once():
    commands = v5_commands()
    reference = (ROOT / "references" / "v5-fallback.md").read_text()
    headings = re.findall(r"^## `(asa v5 [^`]+)`$", reference, flags=re.MULTILINE)

    assert len(headings) == len(set(headings)) == 65
    assert set(headings) == {command.path for command in commands}


def test_workflow_inventory_contains_the_three_registered_read_only_commands_once():
    commands = workflow_commands()
    paths = [command.path for command in commands]
    assert paths == [
        "asa workflows campaigns audit",
        "asa workflows campaigns plan-four-structure",
        "asa workflows campaigns plan-maximize-conversions",
    ]

    reference = (ROOT / "references" / "workflow-command-index.md").read_text()
    headings = re.findall(r"^## `(asa workflows [^`]+)`$", reference, flags=re.MULTILINE)
    assert headings == paths


def test_lookup_returns_exact_v5_and_workflow_runtime_contracts():
    cases = (
        ("v5", "asa v5 reports custom", "v5-command", "v5-fallback.md"),
        (
            "workflows",
            "asa workflows campaigns audit",
            "workflow",
            "workflow-command-index.md",
        ),
    )
    for version, command, kind, reference in cases:
        result = subprocess.run(
            [
                sys.executable,
                "scripts/lookup_command.py",
                "--version",
                version,
                "--command",
                command,
                "--json",
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode == 0, result.stderr
        payload = json.loads(result.stdout)
        assert len(payload) == 1
        assert payload[0]["kind"] == kind
        assert payload[0]["command"] == command
        assert payload[0]["reference"] == reference
        assert payload[0]["usage"].startswith(f"Usage: {command}")


def test_natural_language_strategy_queries_resolve_to_one_workflow_each():
    cases = {
        "audit campaign strategy": "asa workflows campaigns audit",
        "manual search results plan": "asa workflows campaigns plan-four-structure",
        "maximize conversions plan": "asa workflows campaigns plan-maximize-conversions",
    }
    for query, command in cases.items():
        result = subprocess.run(
            [sys.executable, "scripts/lookup_command.py", query, "--json"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode == 0, result.stderr
        payload = json.loads(result.stdout)
        assert [item["command"] for item in payload] == [command]
        assert payload[0]["kind"] == "workflow"
