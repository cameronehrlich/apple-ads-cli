"""Tests for selected opinionated workflows built on Platform API v1."""

import json

from typer.testing import CliRunner

from asa_cli.config import AppConfig
from asa_cli.main import app as root_app
from asa_cli.workflows import campaigns

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
        ]
    )

    assert result["campaignCount"] == 1
    assert [item["id"] for item in result["types"]["brand"]] == [1]
    assert result["missing"] == ["category", "competitor", "discovery"]
    assert result["healthy"] is False


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
    assert all(plan["dailyBudget"] == 25 for plan in payload["campaigns"])


def test_root_exposes_workflows_and_keeps_v5_explicit():
    result = runner.invoke(root_app, ["--help"])

    assert result.exit_code == 0
    assert "workflows" in result.stdout
    assert "v5" in result.stdout
