"""Drift checks for the checked-in generated skill references."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from _command_catalog import (  # noqa: E402
    ALL_GENERATED_REFERENCES,
    DEFAULT_MANIFEST,
    catalog_entries,
    load_manifest,
)

pytestmark = pytest.mark.skipif(
    not DEFAULT_MANIFEST.exists(), reason="canonical Platform API manifest is generated separately"
)


def test_checked_in_references_match_manifest():
    result = subprocess.run(
        [sys.executable, "scripts/generate_skill_references.py", "--check"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr


def test_every_operation_has_one_domain_reference():
    manifest = load_manifest()
    entries = catalog_entries(manifest)
    assert len(entries) == len(manifest["operations"])
    assert len({entry.sdk_method for entry in entries}) == len(entries)
    for entry in entries:
        path = ROOT / "references" / entry.reference
        assert path.exists(), entry.reference
        assert path.read_text().count(f"## `{entry.sdk_method}`") == 1


def test_pinned_resource_families_do_not_fall_into_other():
    entries = catalog_entries(load_manifest())
    unexpected = [entry.sdk_method for entry in entries if entry.reference == "v1-other.md"]
    assert not unexpected


def test_every_skill_reference_link_exists():
    skill = (ROOT / "SKILL.md").read_text()
    links = re.findall(r"\]\((references/[^)]+)\)", skill)
    assert links
    for link in links:
        assert (ROOT / link).exists(), link


def test_all_expected_generated_files_are_checked_in():
    missing = [
        filename for filename in ALL_GENERATED_REFERENCES if not (ROOT / "references" / filename).exists()
    ]
    assert not missing


def test_all_99_v1_entries_are_runtime_registered_and_implemented():
    entries = catalog_entries(load_manifest())
    assert len(entries) == 99
    assert len({entry.command for entry in entries}) == 99
    assert all(entry.status == "implemented" for entry in entries)
    assert all(entry.runtime_registered for entry in entries)
    assert all(entry.usage.startswith("Usage: asa ") for entry in entries)


def test_lookup_returns_exact_inventory_status_without_live_discovery():
    result = subprocess.run(
        [
            sys.executable,
            "scripts/lookup_command.py",
            "--sdk-method",
            "search_term_popularity_query",
            "--json",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)[0]
    assert payload["sdk_method"] == "search_term_popularity_query"
    assert payload["status"] == "implemented"
    assert payload["reference"] == "v1-insights.md"
    model = payload["request_models"][
        "apple_ads_platform.models.search_term_popularity_query_request.SearchTermPopularityQueryRequest"
    ]
    assert model["schema"]["required"] == ["timeRange"]


def test_generated_insights_include_required_body_contract():
    insights = (ROOT / "references" / "v1-insights.md").read_text()
    assert "Required-field body skeleton" in insights
    assert '"timeRange": {' in insights
    assert "##### `SearchTermPopularityTimeRange`" in insights


def test_list_body_skeleton_is_wrapped_in_a_json_array():
    recommendations = (
        ROOT / "references" / "v1-recommendations-and-suggestions.md"
    ).read_text()
    apply_section = recommendations.split(
        "## `apply_daily_budget_recommendations`", 1
    )[1].split("## `", 1)[0]

    assert "Required-field body skeleton" in apply_section
    assert "```json\n[\n  {" in apply_section


def test_generated_v1_references_mark_all_runtime_entries_implemented():
    statuses = 0
    for path in (ROOT / "references").glob("v1-*.md"):
        statuses += path.read_text().count("- Status: `implemented`")
    assert statuses == 99
