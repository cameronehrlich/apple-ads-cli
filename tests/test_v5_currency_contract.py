"""Currency safety contracts for legacy Campaign Management API v5 writes."""

import ast
from pathlib import Path
from unittest.mock import MagicMock, patch

from click import unstyle
from typer.testing import CliRunner

from asa_cli.commands import adgroups, budget, campaigns, keywords

ROOT = Path(__file__).resolve().parents[1]
runner = CliRunner()


def _client() -> MagicMock:
    client = MagicMock()
    client.get_org_currency.return_value = "EUR"
    return client


def test_legacy_source_has_no_executable_usd_money_payloads():
    """Prevent a future write path from bypassing organization currency resolution."""
    paths = [ROOT / "asa_cli" / "v5" / "api.py"]
    paths.extend((ROOT / "asa_cli" / "commands").glob("*.py"))
    violations: list[str] = []

    for path in paths:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if not isinstance(node, ast.Dict):
                continue
            for key, value in zip(node.keys, node.values, strict=True):
                if (
                    isinstance(key, ast.Constant)
                    and key.value == "currency"
                    and isinstance(value, ast.Constant)
                    and value.value == "USD"
                ):
                    violations.append(f"{path.relative_to(ROOT)}:{node.lineno}")

    assert violations == []


def test_campaign_budget_updates_preserve_existing_eur_currency():
    client = _client()
    client.get_campaign.return_value = {
        "id": 42,
        "name": "DE Exact",
        "dailyBudgetAmount": {"amount": "10", "currency": "EUR"},
        "budgetAmount": {"amount": "100", "currency": "EUR"},
    }
    client.update_campaign.return_value = {"id": 42}

    with (
        patch.object(campaigns, "load_credentials", return_value=object()),
        patch.object(campaigns, "SearchAdsClient", return_value=client),
    ):
        result = runner.invoke(
            campaigns.app,
            ["update", "42", "--budget", "20", "--lifetime-budget", "200"],
        )

    assert result.exit_code == 0, result.output
    updates = client.update_campaign.call_args.args[1]
    assert updates["dailyBudgetAmount"] == {"amount": "20.0", "currency": "EUR"}
    assert updates["budgetAmount"] == {"amount": "200.0", "currency": "EUR"}
    assert "$" not in unstyle(result.output)


def test_ad_group_bid_update_uses_resolved_eur_currency():
    client = _client()
    client.update_ad_group.return_value = {"id": 7}

    with (
        patch.object(adgroups, "load_credentials", return_value=object()),
        patch.object(adgroups, "SearchAdsClient", return_value=client),
    ):
        result = runner.invoke(
            adgroups.app,
            ["update", "7", "--campaign", "42", "--bid", "1.5"],
        )

    assert result.exit_code == 0, result.output
    updates = client.update_ad_group.call_args.args[2]
    assert updates["defaultBidAmount"] == {"amount": "1.5", "currency": "EUR"}
    assert "$" not in unstyle(result.output)


def test_bulk_keyword_bid_update_uses_resolved_eur_currency():
    client = _client()
    client.get_keywords.return_value = [
        {
            "id": 9,
            "text": "scanner",
            "status": "ACTIVE",
            "bidAmount": {"amount": "1.00", "currency": "EUR"},
        }
    ]
    client.update_keywords_bulk.return_value = [{"id": 9}]

    with (
        patch.object(keywords, "load_credentials", return_value=object()),
        patch.object(keywords, "SearchAdsClient", return_value=client),
    ):
        result = runner.invoke(
            keywords.app,
            [
                "update-bids-bulk",
                "--campaign",
                "42",
                "--ad-group",
                "7",
                "--bid",
                "2.5",
                "--force",
            ],
        )

    assert result.exit_code == 0, result.output
    updates = client.update_keywords_bulk.call_args.args[2]
    assert updates == [{"id": 9, "bidAmount": {"amount": "2.5", "currency": "EUR"}}]
    assert "$" not in unstyle(result.output)


def test_budget_order_preview_uses_resolved_eur_currency():
    client = _client()
    client.create_budget_order.return_value = {"id": 3, "name": "DE Budget"}

    with (
        patch.object(budget, "load_credentials", return_value=object()),
        patch.object(budget, "SearchAdsClient", return_value=client),
    ):
        result = runner.invoke(
            budget.app,
            [
                "create",
                "--name",
                "DE Budget",
                "--budget",
                "1000",
                "--start",
                "2026-09-01",
                "--end",
                "2026-12-31",
            ],
        )

    assert result.exit_code == 0, result.output
    assert "1,000.00 EUR" in unstyle(result.output)
    assert "$" not in unstyle(result.output)
