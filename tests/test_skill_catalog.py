"""Tests for the manifest-backed skill catalog helpers."""

from __future__ import annotations

import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from _command_catalog import (  # noqa: E402
    catalog_entries,
    reference_for,
    render_reference_files,
    search_entries,
)


def operation(
    sdk_method: str,
    resource_family: str,
    resource_path: str,
    *,
    cli: dict | None = None,
) -> dict:
    payload = {
        "sdk_method": sdk_method,
        "resource_family": resource_family,
        "http_method": "POST",
        "resource_path": resource_path,
        "signature": [
            {
                "name": "x_ap_context",
                "annotation": "StrictStr",
                "required": True,
                "default": None,
            }
        ],
        "context": "required",
        "body_parameters": [],
        "return_annotation": "Response",
        "mutation": False,
        "pagination": False,
        "special_handling": [],
        "aliases": [],
    }
    if cli is not None:
        payload["cli"] = cli
    return payload


def manifest() -> dict:
    return {
        "schema_version": 1,
        "generated_at": "sdk-release-provenance",
        "sdk": {
            "distribution": "apple-ads-platform",
            "version": "1.109.0",
            "repository": "https://github.com/apple/apple-ads-platform-api-python",
            "git_commit": "abc123",
            "api_class": "apple_ads_platform.api.apple_ads_api.AppleAdsApi",
            "api_source_sha256": "0" * 64,
        },
        "operations": [
            operation(
                "search_term_popularity_query",
                "insights",
                "/v1/insights/apps/search-term-popularity/query",
            ),
            operation("campaigns_query_post", "campaigns", "/v1/campaigns/query"),
            operation(
                "apply_daily_budget_recommendations",
                "recommendations",
                "/v1/recommendations/daily-budget/apply",
                cli={
                    "command_path": ["asa", "recommendations", "daily-budget", "apply"],
                    "implementation_status": "implemented",
                    "input_example": '{"recommendationIds":["example"]}',
                    "verification": "Read the recommendation state back by ID.",
                },
            ),
            operation("get_brand", "business-brands", "/v1/business-brands/{id}"),
        ],
        "request_models": {},
    }


def test_reference_routing_covers_representative_families():
    operations = manifest()["operations"]
    assert reference_for(operations[0]) == "v1-insights.md"
    assert reference_for(operations[1]) == "v1-campaigns.md"
    assert reference_for(operations[2]) == "v1-recommendations-and-suggestions.md"
    assert reference_for(operations[3]) == "v1-maps-brands-and-categories.md"


def test_sdk_only_operations_are_explicitly_inventory_only():
    entries = catalog_entries(manifest(), include_runtime=False)
    search_term = next(entry for entry in entries if entry.sdk_method == "search_term_popularity_query")
    assert search_term.status == "inventory-only"
    assert search_term.command.startswith("asa insights ")


def test_cli_metadata_controls_exact_command_and_status():
    entries = catalog_entries(manifest(), include_runtime=False)
    apply_budget = next(
        entry for entry in entries if entry.sdk_method == "apply_daily_budget_recommendations"
    )
    assert apply_budget.command == "asa recommendations daily-budget apply"
    assert apply_budget.status == "implemented"


def test_natural_language_lookup_finds_search_term_popularity():
    matches = search_entries(
        catalog_entries(manifest(), include_runtime=False), query="search term popularity"
    )
    assert [entry.sdk_method for entry in matches] == ["search_term_popularity_query"]


def test_renderer_emits_index_domain_fallback_and_migration_references():
    rendered = render_reference_files(manifest(), include_runtime=False)
    assert "command-index.md" in rendered
    assert "v1-insights.md" in rendered
    assert "v5-fallback.md" in rendered
    assert "migration-map.md" in rendered
    assert "search_term_popularity_query" in rendered["v1-insights.md"]
    assert "inventory-only" in rendered["command-index.md"]
    assert "asa recommendations daily-budget apply" in rendered[
        "v1-recommendations-and-suggestions.md"
    ]
