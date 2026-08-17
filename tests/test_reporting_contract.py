"""Tests for complete windows and stable report JSON."""

import json
from datetime import date
from types import SimpleNamespace
from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from asa_cli.commands.reports import app
from asa_cli.reporting import (
    complete_date_window,
    normalize_performance_row,
    parse_impression_share_csv,
)
from asa_cli.v5.api import ReportRows

runner = CliRunner()


def test_complete_window_is_exact_and_excludes_today():
    window = complete_date_window(7, today=date(2026, 8, 9))

    assert window.start.isoformat() == "2026-08-02"
    assert window.end.isoformat() == "2026-08-08"
    assert window.days == 7
    assert window.as_dict()["complete"] is True


def test_complete_window_rejects_partial_today():
    with pytest.raises(ValueError, match="complete date"):
        complete_date_window(7, end_date="2026-08-09", today=date(2026, 8, 9))


def test_impression_share_csv_parser_uses_true_apple_fields():
    content = (
        "Date,App Name,Adam ID,Country or Region,Search Term,"
        "Low Impression Share,High Impression Share,Rank,Search Popularity\n"
        "2026-08-01,Stitch It,123,US,long screenshot,0.11,0.2,TWO,4\n"
    )

    rows = parse_impression_share_csv(content)

    assert rows == [
        {
            "date": "2026-08-01",
            "app_name": "Stitch It",
            "adam_id": 123,
            "country_or_region": "US",
            "search_term": "long screenshot",
            "low_impression_share": 0.11,
            "high_impression_share": 0.2,
            "rank": "TWO",
            "search_popularity": 4,
        }
    ]


def test_normalized_performance_rates_are_numeric_fractions():
    row = normalize_performance_row(
        {
            "metadata": {"keywordId": 7, "keyword": "screenshot", "matchType": "EXACT"},
            "total": {
                "impressions": 100,
                "taps": 10,
                "totalInstalls": 5,
                "localSpend": {"amount": "2.50"},
            },
        },
        kind="keyword",
        campaign={"id": 1, "name": "Category"},
    )

    assert row["spend"] == 2.5
    assert row["avg_cpt"] == 0.25
    assert row["cpa"] == 0.5
    assert row["ttr"] == 0.1
    assert row["conversion_rate"] == 0.5


class KeywordClient:
    def get_campaigns(self):
        return [{"id": 1, "name": "Category", "displayStatus": "RUNNING"}]

    def get_keyword_report(self, campaign_id, start, end):
        assert campaign_id == 1
        assert start.strftime("%Y-%m-%d") == "2024-01-01"
        assert end.strftime("%Y-%m-%d") == "2024-01-07"
        return [
            {
                "metadata": {
                    "campaignId": 1,
                    "adGroupId": 2,
                    "keywordId": 10,
                    "keyword": "long screenshot",
                    "matchType": "EXACT",
                },
                "total": {
                    "impressions": 10,
                    "taps": 2,
                    "tapInstalls": 1,
                    "localSpend": {"amount": "0.55"},
                },
            }
        ]

    def get_ad_groups(self, campaign_id):
        return [{"id": 2, "name": "Exact"}]

    def get_keywords(self, campaign_id, ad_group_id):
        return [
            {
                "id": 10,
                "text": "long screenshot",
                "matchType": "EXACT",
                "status": "ACTIVE",
                "bidAmount": {"amount": "1.00"},
            },
            {
                "id": 11,
                "text": "scrolling screenshot",
                "matchType": "EXACT",
                "status": "ACTIVE",
                "bidAmount": {"amount": "0.75"},
            },
        ]


def test_keyword_json_can_certify_complete_inventory():
    with (
        patch("asa_cli.commands.reports.load_credentials", return_value=object()),
        patch("asa_cli.commands.reports.SearchAdsClient", return_value=KeywordClient()),
        patch("asa_cli.commands.reports._resolve_app_name", return_value=None),
    ):
        result = runner.invoke(
            app,
            [
                "keywords",
                "--all",
                "--include-zero",
                "--start",
                "2024-01-01",
                "--end",
                "2024-01-07",
                "--json",
            ],
        )

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["schema_version"] == 1
    assert payload["window"]["complete"] is True
    assert payload["window"]["days"] == 7
    assert payload["inventory_complete"] is True
    assert [row["keyword_id"] for row in payload["rows"]] == [10, 11]
    assert payload["rows"][1]["impressions"] == 0


class ImpressionShareClient:
    def get_custom_report(self, report_id):
        return {
            "id": report_id,
            "name": "Test",
            "state": "COMPLETED",
            "downloadUri": "https://example.com/report.csv",
        }

    def download_custom_report(self, download_uri):
        assert download_uri.startswith("https://")
        return (
            "Date,App Name,Adam ID,Country or Region,Search Term,"
            "Low Impression Share,High Impression Share,Rank,Search Popularity\n"
            "2024-01-01,Test,999,US,screenshot,0.21,0.3,ONE,5\n"
        )


def test_impression_share_json_downloads_completed_custom_report():
    with (
        patch("asa_cli.commands.reports.load_credentials", return_value=object()),
        patch(
            "asa_cli.commands.reports.SearchAdsClient", return_value=ImpressionShareClient()
        ),
        patch(
            "asa_cli.commands.reports.get_current_app_config",
            return_value=SimpleNamespace(app_id=999),
        ),
    ):
        result = runner.invoke(
            app,
            [
                "impression-share",
                "--report-id",
                "42",
                "--start",
                "2024-01-01",
                "--end",
                "2024-01-07",
                "--json",
            ],
        )

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["report_type"] == "impression_share"
    assert payload["report"]["id"] == "42"
    assert payload["rows"][0]["low_impression_share"] == 0.21
    assert payload["coverage"]["report_complete"] is True
    assert payload["coverage"]["selection_complete"] is True


class PendingImpressionShareClient:
    def get_custom_report(self, report_id):
        return {"id": report_id, "name": "Test", "state": "RUNNING"}


def test_pending_impression_share_json_marks_coverage_incomplete():
    with (
        patch("asa_cli.commands.reports.load_credentials", return_value=object()),
        patch(
            "asa_cli.commands.reports.SearchAdsClient",
            return_value=PendingImpressionShareClient(),
        ),
        patch(
            "asa_cli.commands.reports.get_current_app_config",
            return_value=SimpleNamespace(app_id=999),
        ),
    ):
        result = runner.invoke(
            app,
            [
                "impression-share",
                "--report-id",
                "42",
                "--start",
                "2024-01-01",
                "--end",
                "2024-01-07",
                "--no-wait",
                "--json",
            ],
        )

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["rows"] == []
    assert payload["coverage"]["api_pages_complete"] is False
    assert payload["coverage"]["report_complete"] is False
    assert payload["coverage"]["selection_complete"] is False
    assert payload["coverage"]["source_kind"] == "unavailable_pending_report"


class FaxItMismatchClient:
    """Fixture for the 2026-08-10 through 2026-08-16 live mismatch."""

    campaigns = [
        {"id": 1, "name": "FaxIt - Category", "displayStatus": "RUNNING"},
        {"id": 2, "name": "FaxIt - Competitor", "displayStatus": "RUNNING"},
        {"id": 3, "name": "FaxIt - Discovery", "displayStatus": "RUNNING"},
    ]
    legacy_utc_totals = {"impressions": 131, "spend": 3.8978}
    ortz_grand_totals = {
        "impressions": 140,
        "taps": 3,
        "totalInstalls": 1,
        "localSpend": {"amount": "5.5639"},
    }

    def get_campaigns(self):
        return self.campaigns

    def get_campaign(self, campaign_id):
        return next(campaign for campaign in self.campaigns if campaign["id"] == campaign_id)

    def get_campaign_report(self, campaign_id, start, end, granularity="DAILY"):
        assert start.strftime("%Y-%m-%d") == "2026-08-10"
        assert end.strftime("%Y-%m-%d") == "2026-08-16"
        assert granularity == "DAILY"
        total = self.ortz_grand_totals if campaign_id == 3 else {
            "impressions": 0,
            "taps": 0,
            "totalInstalls": 0,
            "localSpend": {"amount": "0"},
        }
        return ReportRows(
            [{"metadata": {"campaignId": campaign_id}, "total": total}],
            grand_totals=total,
        )

    def get_search_terms_report(self, campaign_id, start, end):
        assert campaign_id == 3
        assert start.strftime("%Y-%m-%d") == "2026-08-10"
        assert end.strftime("%Y-%m-%d") == "2026-08-16"
        rows = []
        for index, (impressions, taps, installs, spend) in enumerate(
            [
                (50, 1, 1, "2.0000"),
                (40, 1, 0, "1.5000"),
                (30, 1, 0, "1.0000"),
                (20, 0, 0, "1.0638"),
            ],
            1,
        ):
            rows.append(
                {
                    "metadata": {
                        "searchTermText": f"fax term {index}",
                        "searchTermSource": "TARGETED",
                    },
                    "total": {
                        "impressions": impressions,
                        "taps": taps,
                        "totalInstalls": installs,
                        "localSpend": {"amount": spend},
                    },
                }
            )
        return ReportRows(rows, grand_totals=self.ortz_grand_totals)


def invoke_fax_it_report(arguments):
    client = FaxItMismatchClient()
    with (
        patch("asa_cli.commands.reports.load_credentials", return_value=object()),
        patch("asa_cli.commands.reports.SearchAdsClient", return_value=client),
        patch("asa_cli.commands.reports._resolve_app_name", return_value=None),
    ):
        return runner.invoke(app, arguments), client


def test_fax_it_mismatch_uses_ortz_grand_totals_for_cross_report_comparison():
    common = ["--start", "2026-08-10", "--end", "2026-08-16", "--json"]
    summary_result, client = invoke_fax_it_report(["summary", *common])
    search_result, _ = invoke_fax_it_report(["search-terms", *common])

    assert summary_result.exit_code == 0, summary_result.output
    assert search_result.exit_code == 0, search_result.output
    summary = json.loads(summary_result.output)
    search_terms = json.loads(search_result.output)

    assert client.legacy_utc_totals == {"impressions": 131, "spend": 3.8978}
    assert summary["window"]["time_zone"] == "ORTZ"
    assert search_terms["window"]["time_zone"] == "ORTZ"
    assert summary["source_totals"]["impressions"] == 140
    assert search_terms["source_totals"]["impressions"] == 140
    assert summary["source_totals"]["spend"] == 5.5639
    assert search_terms["source_totals"]["spend"] == 5.5639

    # Apple row-level money rounds independently by search term. Preserve the
    # compatible returned-row totals while exposing Apple's comparable total.
    assert search_terms["totals"]["spend"] == pytest.approx(5.5638)
    assert search_terms["coverage"]["totals_scope"] == "returned_rows"
    assert search_terms["coverage"]["source_totals_scope"] == "apple_grand_totals"
    assert search_terms["coverage"]["selection_complete"] is True


def test_search_term_coverage_marks_filtering_and_limit_truncation():
    result, _ = invoke_fax_it_report(
        [
            "search-terms",
            "--start",
            "2026-08-10",
            "--end",
            "2026-08-16",
            "--min-impressions",
            "30",
            "--limit",
            "2",
            "--json",
        ]
    )

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["coverage"] == {
        "api_pages": 1,
        "api_pages_complete": True,
        "apple_search_term_minimum_impressions": 10,
        "filtered_rows": 3,
        "filters": {"min_impressions": 30, "mode": "all"},
        "limit": 2,
        "low_volume_terms_may_be_aggregated_as_other": True,
        "returned_rows": 2,
        "selection_complete": False,
        "source_rows": 4,
        "source_totals_scope": "apple_grand_totals",
        "totals_scope": "returned_rows",
        "truncated": True,
    }
