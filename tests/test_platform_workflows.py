"""Tests for selected opinionated workflows built on Platform API v1."""

import json

from typer.testing import CliRunner

from asa_cli.config import AppConfig
from asa_cli.main import app as root_app
from asa_cli.workflows import campaigns
from asa_cli.workflows.strategy import (
    StrategyMode,
    detect_campaign_strategy,
    load_strategy_contract,
)

runner = CliRunner()


def test_campaign_query_paginates_to_a_complete_result(monkeypatch):
    requests = []
    responses = iter(
        [
            {
                "result": [{"id": 1}, {"id": 2}],
                "pagination": {"totalCount": 3},
            },
            {
                "result": [{"id": 3}],
                "pagination": {"totalCount": 3},
            },
        ]
    )

    def fake_hydrate(model_name, payload, *, many=False):
        requests.append(payload)
        return payload

    monkeypatch.setattr(campaigns, "hydrate_model", fake_hydrate)
    monkeypatch.setattr(campaigns, "invoke", lambda *args, **kwargs: next(responses))

    result = campaigns.query_all_campaigns(ad_account_id="123", page_size=2)

    assert [item["id"] for item in result] == [1, 2, 3]
    assert [request["pagination"]["offset"] for request in requests] == [0, 2]
    assert all(request["pagination"]["fetchTotalCount"] for request in requests)


def test_campaign_query_honors_total_when_server_caps_page_size(monkeypatch):
    requests = []
    responses = iter(
        [
            {"result": [{"id": index} for index in range(50)], "pagination": {"totalCount": 120}},
            {
                "result": [{"id": index} for index in range(50, 100)],
                "pagination": {"totalCount": 120},
            },
            {
                "result": [{"id": index} for index in range(100, 120)],
                "pagination": {"totalCount": 120},
            },
        ]
    )

    def fake_hydrate(model_name, payload, *, many=False):
        requests.append(payload)
        return payload

    monkeypatch.setattr(campaigns, "hydrate_model", fake_hydrate)
    monkeypatch.setattr(campaigns, "invoke", lambda *args, **kwargs: next(responses))

    result = campaigns.query_all_campaigns(page_size=100)

    assert len(result) == 120
    assert [request["pagination"]["offset"] for request in requests] == [0, 50, 100]


def test_campaign_query_rejects_a_repeated_full_page(monkeypatch):
    page = {"result": [{"id": 1}, {"id": 2}], "pagination": {}}
    monkeypatch.setattr(
        campaigns,
        "hydrate_model",
        lambda model_name, payload, *, many=False: payload,
    )
    monkeypatch.setattr(campaigns, "invoke", lambda *args, **kwargs: page)

    try:
        campaigns.query_all_campaigns(page_size=2)
    except campaigns.PlatformAPIError as exc:
        assert "repeated a page" in str(exc)
    else:  # pragma: no cover - protects against non-terminating pagination
        raise AssertionError("repeated campaign page was accepted")


def test_campaign_audit_scopes_to_configured_app_and_reports_gaps(monkeypatch):
    monkeypatch.setattr(
        campaigns,
        "load_app_config",
        lambda: AppConfig(app_id=42, app_name="Stitch It"),
    )

    result = campaigns.campaign_audit(
        [
            {
                "id": 1,
                "name": "Stitch It - Brand",
                "promotedObjectId": "42",
                "status": "ENABLED",
            },
            {
                "id": 2,
                "name": "Other App - Category",
                "promotedObjectId": "99",
            },
        ],
        requested_strategy="manual",
    )

    assert result["campaignCount"] == 1
    assert [item["id"] for item in result["types"]["brand"]] == [1]
    assert result["missing"] == ["category", "competitor", "discovery"]
    assert result["healthy"] is False


def test_theme_name_alone_does_not_establish_strategy():
    detected = detect_campaign_strategy({"id": 1, "name": "Stitch It - Brand"})

    assert detected["themeNameHint"] == "brand"
    assert detected["strategy"] == "non-search-or-unsupported"
    assert detected["confidence"] == "low"


def test_strategy_contract_has_three_explicit_modes():
    contract = load_strategy_contract()

    assert contract["contractVersion"] == 1
    assert set(contract["modes"]) == {
        "manual-search-results",
        "maximize-conversions",
        "non-search-or-unsupported",
    }
    assert len(contract["sources"]) == 3


def test_strategy_detection_uses_placement_then_bid_precedence():
    non_search = detect_campaign_strategy(
        {
            "targeting": {
                "supplySource": {"include": ["APPSTORE"]},
                "supplyPlacement": {"include": ["TODAY_TAB"]},
            },
            "bidStrategy": {"bidStrategyType": "MAX_CONVERSIONS"},
        }
    )
    maximize = detect_campaign_strategy(
        {
            "targeting": {"supplyPlacement": {"include": ["SEARCH_RESULTS"]}},
            "bidStrategy": {"bidStrategyType": "MAX_CONVERSIONS"},
        }
    )
    manual = detect_campaign_strategy(
        {
            "targeting": {"supplyPlacement": {"include": ["SEARCH_RESULTS"]}},
            "bidStrategy": {"bidStrategyType": "MANUAL_CPT"},
        }
    )

    assert non_search["strategy"] == StrategyMode.NON_SEARCH_OR_UNSUPPORTED.value
    assert maximize["strategy"] == StrategyMode.MAXIMIZE_CONVERSIONS.value
    assert manual["strategy"] == StrategyMode.MANUAL_SEARCH_RESULTS.value


def test_manual_audit_can_verify_ad_group_structure(monkeypatch):
    monkeypatch.setattr(
        campaigns,
        "load_app_config",
        lambda: AppConfig(app_id=42, app_name="Stitch It"),
    )
    result = campaigns.campaign_audit(
        [
            {
                "id": 1,
                "name": "Stitch It - Search Results",
                "promotedObjectId": "42",
                "targeting": {"supplyPlacement": {"include": ["SEARCH_RESULTS"]}},
                "bidStrategy": {"bidStrategyType": "MANUAL_CPT"},
            }
        ],
        evidence={
            "adGroups": [
                {"id": 11, "name": "Brand", "matchType": "EXACT"},
                {"id": 12, "name": "Category", "matchType": "EXACT"},
                {"id": 13, "name": "Competitor", "matchType": "EXACT"},
                {
                    "id": 14,
                    "name": "Discovery",
                    "matchType": "BROAD",
                    "searchMatch": True,
                },
            ],
            "negativeKeywordOverlapCount": 0,
        },
    )

    assert result["detectedStrategy"] == "manual-search-results"
    assert result["fullyVerified"] is True
    assert {check["state"] for check in result["checks"]} == {"pass"}


def test_maximize_audit_does_not_apply_manual_theme_failures(monkeypatch):
    monkeypatch.setattr(campaigns, "load_app_config", lambda: None)
    result = campaigns.campaign_audit(
        [
            {
                "id": 1,
                "name": "Automated",
                "bidStrategy": {"bidStrategyType": "MAX_CONVERSIONS"},
                "targeting": {"supplyPlacement": {"include": ["SEARCH_RESULTS"]}},
                "dailyBudget": {"amount": 100},
                "creationTime": "2020-01-01T00:00:00Z",
            }
        ],
        evidence={
            "eligible": True,
            "targetCpa": 20,
            "targetCpaSource": "Apple",
            "targetCpaRecommendations": {"result": []},
        },
    )

    assert result["evaluatedStrategy"] == "maximize-conversions"
    assert all(not check["id"].startswith("manual.") for check in result["checks"])
    assert result["missing"] == []
    assert result["healthy"] is True


def test_conflicting_strategy_override_skips_cross_strategy_checks(monkeypatch):
    monkeypatch.setattr(campaigns, "load_app_config", lambda: None)
    result = campaigns.campaign_audit(
        [
            {
                "id": 1,
                "bidStrategy": {"bidStrategyType": "MAX_CONVERSIONS"},
                "targeting": {"supplyPlacement": {"include": ["SEARCH_RESULTS"]}},
            }
        ],
        requested_strategy="manual",
    )

    assert result["applicability"]["applicable"] is False
    assert result["checks"] == []
    assert "cross-strategy checks were skipped" in result["warnings"][0]


def test_four_campaign_plan_is_explicitly_no_write(monkeypatch):
    monkeypatch.setattr(
        campaigns,
        "load_app_config",
        lambda: AppConfig(app_id=42, app_name="Stitch It", default_countries=["US", "CA"]),
    )

    result = runner.invoke(
        campaigns.app,
        ["plan-four-structure", "--daily-budget", "25"],
    )

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["dryRun"] is True
    assert payload["mutationAvailable"] is False
    assert len(payload["campaigns"]) == 4
    assert {plan["type"] for plan in payload["campaigns"]} == {
        "brand",
        "category",
        "competitor",
        "discovery",
    }
    assert payload["strategy"] == "manual-search-results"
    assert payload["placement"] == "APPSTORE_SEARCH_RESULTS"
    assert all(plan["dailyBudget"] == {"amount": 25.0, "approved": False} for plan in payload["campaigns"])


def test_manual_plan_supports_themed_ad_groups(monkeypatch):
    monkeypatch.setattr(
        campaigns,
        "load_app_config",
        lambda: AppConfig(app_id=42, app_name="Stitch It", default_countries=["US", "GB"]),
    )

    result = runner.invoke(
        campaigns.app,
        ["plan-four-structure", "--grouping", "themed-ad-groups", "--daily-budget", "75"],
    )

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["grouping"] == "themed-ad-groups"
    assert len(payload["campaigns"]) == 1
    assert {group["theme"] for group in payload["campaigns"][0]["adGroups"]} == {
        "brand",
        "category",
        "competitor",
        "discovery",
    }


def test_maximize_plan_has_budget_learning_and_preorder_guards():
    result = campaigns.maximize_conversions_plan(
        adam_id="42",
        countries=["US", "GB"],
        daily_budget=75,
        target_cpa=20,
        evidence={"eligibility": {"eligible": True}},
        pre_order=True,
        campaign_created_at="2020-01-01T00:00:00Z",
    )

    assert result["dryRun"] is True
    assert result["mutationAvailable"] is False
    assert result["dailyBudget"]["recommendedMinimum"] == 100
    assert result["dailyBudget"]["supportsFiveConversionsPerDay"] is False
    assert result["learningPeriod"]["complete"] is True
    assert result["automation"]["separateDiscoveryAdGroupRequired"] is False
    assert result["launchGuard"]["ready"] is False


def test_maximize_plan_preserves_ineligible_and_unavailable_evidence():
    result = campaigns.maximize_conversions_plan(
        adam_id="42",
        countries=["US"],
        daily_budget=50,
        target_cpa=None,
        evidence={"eligibility": {"eligible": False}},
    )

    assert result["eligibility"]["eligible"] is False
    assert result["targetCpa"]["amount"] is None
    assert result["targetCpa"]["source"] is None
    assert result["unresolvedInputs"] == ["targetCpa"]
    assert "Apple eligibility evidence is negative." in result["warnings"]


def test_maximize_cli_live_evidence_uses_only_read_methods(monkeypatch):
    calls = []
    monkeypatch.setattr(
        campaigns,
        "load_app_config",
        lambda: AppConfig(app_id=42, app_name="Stitch It", default_countries=["US"]),
    )
    monkeypatch.setattr(
        campaigns,
        "hydrate_model",
        lambda model_name, payload, *, many=False: payload,
    )

    def fake_invoke(method, **kwargs):
        calls.append(method)
        if method == "eligibilities_apps_query_post":
            return {"result": [{"eligible": True}]}
        if method == "query_target_cpa_suggestion":
            return {"result": [{"targetCpa": {"amount": 12}}]}
        return {"result": []}

    monkeypatch.setattr(campaigns, "invoke", fake_invoke)
    result = runner.invoke(
        campaigns.app,
        [
            "plan-maximize-conversions",
            "--daily-budget",
            "60",
            "--ad-account",
            "123",
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["targetCpa"]["amount"] == 12
    assert calls == [
        "eligibilities_apps_query_post",
        "query_target_cpa_suggestion",
        "query_target_cpa_recommendations",
    ]


def test_root_exposes_workflows_and_keeps_v5_explicit():
    result = runner.invoke(root_app, ["--help"])

    assert result.exit_code == 0
    assert "workflows" in result.stdout
    assert "v5" in result.stdout
