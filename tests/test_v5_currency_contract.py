"""Currency safety contracts for legacy Campaign Management API v5 writes."""

import ast
import json
from pathlib import Path
from unittest.mock import MagicMock, patch

from click import unstyle
from typer.testing import CliRunner

from asa_cli.commands import adgroups, budget, campaigns, keywords, reports
from asa_cli.v5.api import ReportRows, SearchAdsAPIError

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


class ReportsClient:
    """Report fixture whose money is denominated in a non-USD organization currency."""

    campaigns = [{"id": 42, "name": "DE Exact", "displayStatus": "RUNNING"}]

    def get_campaigns(self):
        return self.campaigns

    def get_campaign_report(self, campaign_id, start, end, granularity="DAILY"):
        total = {
            "impressions": 100,
            "taps": 10,
            "totalInstalls": 2,
            "localSpend": {"amount": "25.00", "currency": "EUR"},
        }
        return ReportRows(
            [{"metadata": {"campaignId": campaign_id}, "total": total}],
            grand_totals=total,
        )


def _invoke_reports(arguments):
    client = ReportsClient()
    with (
        patch.object(reports, "load_credentials", return_value=object()),
        patch.object(reports, "SearchAdsClient", return_value=client),
        patch.object(reports, "_resolve_app_name", return_value=None),
    ):
        return runner.invoke(reports.app, arguments), client


def test_report_summary_labels_spend_with_the_reported_currency(monkeypatch):
    # Give the table room so currency labels are not wrapped across lines.
    monkeypatch.setenv("COLUMNS", "200")
    result, _ = _invoke_reports(
        ["summary", "--start", "2024-01-01", "--end", "2024-01-07"]
    )

    assert result.exit_code == 0, result.output
    output = unstyle(result.output)
    assert "$" not in output
    assert "25.00 EUR" in output
    assert "12.50 EUR" in output


def test_report_summary_json_output_carries_the_money_currency():
    result, _ = _invoke_reports(
        ["summary", "--start", "2024-01-01", "--end", "2024-01-07", "--json"]
    )

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["currency"] == "EUR"
    assert payload["totals"]["spend"] == 25.0


class CurrencylessReportsClient(ReportsClient):
    """Report fixture whose money carries no currency of its own."""

    def get_campaign_report(self, campaign_id, start, end, granularity="DAILY"):
        total = {
            "impressions": 100,
            "taps": 10,
            "totalInstalls": 2,
            "localSpend": {"amount": "25.00"},
        }
        return ReportRows(
            [{"metadata": {"campaignId": campaign_id}, "total": total}],
            grand_totals=total,
        )

    def get_org_currency(self):
        raise SearchAdsAPIError(
            "Apple Ads ACL did not return a currency for organization 42"
        )


def _invoke_currencyless_reports(arguments):
    client = CurrencylessReportsClient()
    with (
        patch.object(reports, "load_credentials", return_value=object()),
        patch.object(reports, "SearchAdsClient", return_value=client),
        patch.object(reports, "_resolve_app_name", return_value=None),
    ):
        return runner.invoke(reports.app, arguments), client


def test_report_summary_surfaces_a_failed_currency_lookup(monkeypatch):
    """A failed currency lookup must not be reported as a successful report.

    The legacy v5 client fails closed when the ACL carries no currency, and
    every other command lets that error reach the caller. Reports must not
    paper over it by emitting money without a known currency.
    """
    monkeypatch.setenv("COLUMNS", "200")
    result, _ = _invoke_currencyless_reports(
        ["summary", "--start", "2024-01-01", "--end", "2024-01-07"]
    )

    assert result.exit_code != 0
    assert isinstance(result.exception, SearchAdsAPIError)
    assert "currency" in str(result.exception)


def test_report_summary_json_output_never_reports_success_without_a_currency():
    """Machine output must not claim success when the currency is unknown."""
    result, _ = _invoke_currencyless_reports(
        ["summary", "--start", "2024-01-01", "--end", "2024-01-07", "--json"]
    )

    assert result.exit_code != 0
    assert "25.00" not in result.output


class FailingAclReportsClient(CurrencylessReportsClient):
    """Report fixture whose ACL request fails the way the client really fails.

    SearchAdsClient._request prints the error to stdout before it raises, so
    a report that swallows the failure emits that line in front of the JSON
    envelope and still exits 0.
    """

    def get_org_currency(self):
        print("API error 403: Forbidden")
        raise SearchAdsAPIError("API error 403: Forbidden")


def _invoke_failing_acl_reports(arguments):
    client = FailingAclReportsClient()
    with (
        patch.object(reports, "load_credentials", return_value=object()),
        patch.object(reports, "SearchAdsClient", return_value=client),
        patch.object(reports, "_resolve_app_name", return_value=None),
    ):
        return runner.invoke(reports.app, arguments), client


def test_report_summary_does_not_swallow_a_failed_acl_request():
    """A failed ACL request must not become a successful report.

    The repository's contract requires HTTP failures to exit nonzero, never a
    healthy no-op. The client prints the error to stdout before raising, so
    swallowing the failure would also put a non-JSON line in front of the
    machine envelope.
    """
    result, _ = _invoke_failing_acl_reports(
        ["summary", "--start", "2024-01-01", "--end", "2024-01-07", "--json"]
    )

    assert result.exit_code != 0
    assert isinstance(result.exception, SearchAdsAPIError)
    assert '"schema_version"' not in result.output
    assert "25.00" not in result.output
