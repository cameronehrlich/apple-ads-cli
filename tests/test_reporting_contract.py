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
