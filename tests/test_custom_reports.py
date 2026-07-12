"""Tests for custom/impression share reports and additional report types."""

from datetime import datetime
from unittest.mock import patch

import pytest

from asa_cli.api import SearchAdsAPIError, SearchAdsClient
from asa_cli.config import AppConfig, Credentials


@pytest.fixture
def mock_credentials():
    """Create mock credentials for testing."""
    return Credentials(
        org_id=123456,
        client_id="test_client",
        team_id="test_team",
        key_id="test_key",
        private_key_path="/path/to/key.pem",
    )


@pytest.fixture
def mock_app_config():
    """Create mock app config for testing."""
    return AppConfig(
        app_id=999999,
        app_name="TestApp",
        default_countries=["US"],
        default_bid=1.50,
    )


@pytest.fixture
def mock_client(mock_credentials, mock_app_config):
    """Create a mock SearchAdsClient."""
    with patch.object(SearchAdsClient, "_get_access_token", return_value="mock_token"):
        client = SearchAdsClient(mock_credentials, app_config=mock_app_config)
        return client


class TestCreateCustomReport:
    """Tests for create_custom_report."""

    def test_create_custom_report_payload(self, mock_client):
        """Test that create_custom_report sends correct payload."""
        mock_response = {
            "data": {
                "id": "report-123",
                "state": "QUEUED",
                "name": "Test Report",
                "startTime": "2024-01-01",
                "endTime": "2024-01-30",
                "granularity": "DAILY",
            }
        }

        with patch.object(mock_client, "_request", return_value=mock_response) as mock_req:
            result = mock_client.create_custom_report(
                name="Test Report",
                start_time="2024-01-01",
                end_time="2024-01-30",
                granularity="DAILY",
            )

            # Verify the payload
            call_args = mock_req.call_args
            assert call_args[0][0] == "POST"
            assert call_args[0][1] == "/custom-reports"
            data = call_args.kwargs.get("data") or call_args[1].get("data")
            assert data["name"] == "Test Report"
            assert data["startTime"] == "2024-01-01"
            assert data["endTime"] == "2024-01-30"
            assert data["granularity"] == "DAILY"

        assert result is not None
        assert result["id"] == "report-123"
        assert result["state"] == "QUEUED"

    def test_create_custom_report_with_conditions(self, mock_client):
        """Test creating a custom report with selector conditions."""
        mock_response = {
            "data": {"id": "report-456", "state": "QUEUED"}
        }

        conditions = [
            {"field": "campaignId", "operator": "EQUALS", "values": ["123"]}
        ]

        with patch.object(mock_client, "_request", return_value=mock_response) as mock_req:
            result = mock_client.create_custom_report(
                name="Filtered Report",
                start_time="2024-01-01",
                end_time="2024-01-30",
                conditions=conditions,
            )

            data = mock_req.call_args.kwargs.get("data") or mock_req.call_args[1].get("data")
            assert "selector" in data
            assert data["selector"]["conditions"] == conditions

        assert result is not None

    def test_create_custom_report_without_conditions(self, mock_client):
        """Test creating a custom report without conditions has no selector."""
        mock_response = {
            "data": {"id": "report-789", "state": "QUEUED"}
        }

        with patch.object(mock_client, "_request", return_value=mock_response) as mock_req:
            mock_client.create_custom_report(
                name="Simple Report",
                start_time="2024-01-01",
                end_time="2024-01-30",
            )

            data = mock_req.call_args.kwargs.get("data") or mock_req.call_args[1].get("data")
            assert "selector" not in data

    def test_create_custom_report_api_error(self, mock_client):
        """Test handling of API error during report creation."""
        with patch.object(mock_client, "_request", side_effect=Exception("Rate limited")):
            result = mock_client.create_custom_report(
                name="Test", start_time="2024-01-01", end_time="2024-01-30"
            )

        assert result is None


class TestGetCustomReport:
    """Tests for get_custom_report."""

    def test_get_custom_report_queued(self, mock_client):
        """Test getting a report in QUEUED state."""
        mock_response = {
            "data": {
                "id": "report-123",
                "state": "QUEUED",
                "name": "Test Report",
            }
        }

        with patch.object(mock_client, "_request", return_value=mock_response):
            result = mock_client.get_custom_report("report-123")

        assert result is not None
        assert result["state"] == "QUEUED"
        assert "downloadUri" not in result

    def test_get_custom_report_completed(self, mock_client):
        """Test getting a report in COMPLETED state with downloadUri."""
        mock_response = {
            "data": {
                "id": "report-123",
                "state": "COMPLETED",
                "name": "Test Report",
                "downloadUri": "https://example.com/download/report-123.csv",
            }
        }

        with patch.object(mock_client, "_request", return_value=mock_response):
            result = mock_client.get_custom_report("report-123")

        assert result is not None
        assert result["state"] == "COMPLETED"
        assert result["downloadUri"] == "https://example.com/download/report-123.csv"

    def test_get_custom_report_failed(self, mock_client):
        """Test getting a report in FAILED state."""
        mock_response = {
            "data": {
                "id": "report-123",
                "state": "FAILED",
            }
        }

        with patch.object(mock_client, "_request", return_value=mock_response):
            result = mock_client.get_custom_report("report-123")

        assert result is not None
        assert result["state"] == "FAILED"

    def test_get_custom_report_api_error(self, mock_client):
        """Test handling of API error when fetching report."""
        with patch.object(mock_client, "_request", side_effect=Exception("Not found")):
            result = mock_client.get_custom_report("nonexistent-id")

        assert result is None

    def test_get_custom_report_calls_correct_endpoint(self, mock_client):
        """Test that get_custom_report uses the correct endpoint."""
        mock_response = {"data": {"id": "rpt-42", "state": "QUEUED"}}

        with patch.object(mock_client, "_request", return_value=mock_response) as mock_req:
            mock_client.get_custom_report("rpt-42")

            mock_req.assert_called_once_with("GET", "/custom-reports/rpt-42")


class TestGetAllCustomReports:
    """Tests for get_all_custom_reports."""

    def test_get_all_custom_reports(self, mock_client):
        """Test listing all custom reports."""
        mock_response = {
            "data": [
                {"id": "report-1", "state": "COMPLETED", "name": "Report 1"},
                {"id": "report-2", "state": "QUEUED", "name": "Report 2"},
            ]
        }

        with patch.object(mock_client, "_request", return_value=mock_response):
            results = mock_client.get_all_custom_reports()

        assert len(results) == 2
        assert results[0]["id"] == "report-1"

    def test_get_all_custom_reports_empty(self, mock_client):
        """Test listing custom reports when none exist."""
        mock_response = {"data": []}

        with patch.object(mock_client, "_request", return_value=mock_response):
            results = mock_client.get_all_custom_reports()

        assert results == []

    def test_get_all_custom_reports_limit_capped(self, mock_client):
        """Test that limit is capped at 50."""
        mock_response = {"data": []}

        with patch.object(mock_client, "_request", return_value=mock_response) as mock_req:
            mock_client.get_all_custom_reports(limit=100)

            call_args = mock_req.call_args
            params = call_args.kwargs.get("params") or call_args[1].get("params")
            assert params["limit"] == 50

    def test_get_all_custom_reports_api_error(self, mock_client):
        """Test handling of API error when listing reports."""
        with patch.object(mock_client, "_request", side_effect=Exception("Server error")):
            results = mock_client.get_all_custom_reports()

        assert results == []


class TestGetAdReport:
    """Tests for get_ad_report."""

    def test_get_ad_report_has_orderby(self, mock_client):
        """Test that ad report includes required orderBy in selector."""
        mock_response = {
            "data": {
                "reportingDataResponse": {
                    "row": [
                        {
                            "metadata": {"adId": 1, "adName": "Ad 1"},
                            "total": {"impressions": 100, "taps": 10},
                        }
                    ]
                }
            }
        }

        with patch.object(mock_client, "_request", return_value=mock_response) as mock_req:
            result = mock_client.get_ad_report(123)

            call_args = mock_req.call_args
            data = call_args.kwargs.get("data") or call_args[1].get("data")
            # Verify orderBy is present (REQUIRED for ad reports)
            assert "orderBy" in data["selector"]
            assert len(data["selector"]["orderBy"]) > 0
            assert data["selector"]["orderBy"][0]["field"] == "impressions"

        assert len(result) == 1

    def test_get_ad_report_correct_endpoint(self, mock_client):
        """Test that ad report uses the correct endpoint."""
        mock_response = {"data": {"reportingDataResponse": {"row": []}}}

        with patch.object(mock_client, "_request", return_value=mock_response) as mock_req:
            mock_client.get_ad_report(456)

            call_args = mock_req.call_args
            assert call_args[0][1] == "/reports/campaigns/456/ads"

    def test_get_ad_report_empty_results(self, mock_client):
        """Test ad report with no data."""
        mock_response = {"data": {"reportingDataResponse": {"row": []}}}

        with patch.object(mock_client, "_request", return_value=mock_response):
            result = mock_client.get_ad_report(123)

        assert result == []

    def test_get_ad_report_with_granularity(self, mock_client):
        """Test ad report with non-DAILY granularity includes it in payload."""
        mock_response = {"data": {"reportingDataResponse": {"row": []}}}

        with patch.object(mock_client, "_request", return_value=mock_response) as mock_req:
            mock_client.get_ad_report(123, granularity="WEEKLY")

            data = mock_req.call_args.kwargs.get("data") or mock_req.call_args[1].get("data")
            assert data["granularity"] == "WEEKLY"

    def test_get_ad_report_daily_granularity_omitted(self, mock_client):
        """Test ad report with DAILY granularity does not include granularity key."""
        mock_response = {"data": {"reportingDataResponse": {"row": []}}}

        with patch.object(mock_client, "_request", return_value=mock_response) as mock_req:
            mock_client.get_ad_report(123, granularity="DAILY")

            data = mock_req.call_args.kwargs.get("data") or mock_req.call_args[1].get("data")
            assert "granularity" not in data

    def test_get_ad_report_api_error(self, mock_client):
        """Test handling of API error in ad report."""
        with patch.object(mock_client, "_request", side_effect=Exception("Error")):
            result = mock_client.get_ad_report(123)

        assert result == []


class TestKeywordAdGroupReport:
    """Tests for get_keyword_adgroup_report with bid recommendations."""

    def test_keyword_adgroup_report_with_bid_recommendation(self, mock_client):
        """Test keyword report includes bid recommendation in response."""
        mock_response = {
            "data": {
                "reportingDataResponse": {
                    "row": [
                        {
                            "metadata": {
                                "keyword": "test keyword",
                                "keywordId": 111,
                                "bidAmount": {"amount": "1.50", "currency": "USD"},
                            },
                            "total": {
                                "impressions": 500,
                                "taps": 50,
                                "totalInstalls": 5,
                                "localSpend": {"amount": "7.50", "currency": "USD"},
                            },
                            "insights": {
                                "bidRecommendation": {
                                    "suggestedBidAmount": {
                                        "amount": "2.00",
                                        "currency": "USD",
                                    }
                                }
                            },
                        }
                    ]
                }
            }
        }

        with patch.object(mock_client, "_request", return_value=mock_response):
            result = mock_client.get_keyword_adgroup_report(123, 456)

        assert len(result) == 1
        row = result[0]
        assert row["metadata"]["keyword"] == "test keyword"
        assert row["insights"]["bidRecommendation"]["suggestedBidAmount"]["amount"] == "2.00"

    def test_keyword_adgroup_report_correct_endpoint(self, mock_client):
        """Test that keyword adgroup report uses the correct endpoint."""
        mock_response = {"data": {"reportingDataResponse": {"row": []}}}

        with patch.object(mock_client, "_request", return_value=mock_response) as mock_req:
            mock_client.get_keyword_adgroup_report(123, 456)

            call_args = mock_req.call_args
            assert call_args[0][1] == "/reports/campaigns/123/adgroups/456/keywords"

    def test_keyword_adgroup_report_empty_results(self, mock_client):
        """Test keyword adgroup report with no data."""
        mock_response = {"data": {"reportingDataResponse": {"row": []}}}

        with patch.object(mock_client, "_request", return_value=mock_response):
            result = mock_client.get_keyword_adgroup_report(123, 456)

        assert result == []

    def test_keyword_adgroup_report_api_error(self, mock_client):
        """API errors must not be misreported as an empty keyword report."""
        with patch.object(mock_client, "_request", side_effect=Exception("Error")):
            with pytest.raises(SearchAdsAPIError, match="Failed to fetch keyword report"):
                mock_client.get_keyword_adgroup_report(123, 456)

    def test_keyword_adgroup_report_multiple_keywords(self, mock_client):
        """Test keyword report with multiple keywords and varying recommendations."""
        mock_response = {
            "data": {
                "reportingDataResponse": {
                    "row": [
                        {
                            "metadata": {
                                "keyword": "keyword one",
                                "keywordId": 111,
                                "bidAmount": {"amount": "1.00", "currency": "USD"},
                            },
                            "total": {"impressions": 1000, "taps": 100},
                            "insights": {
                                "bidRecommendation": {
                                    "suggestedBidAmount": {"amount": "3.00", "currency": "USD"}
                                }
                            },
                        },
                        {
                            "metadata": {
                                "keyword": "keyword two",
                                "keywordId": 222,
                                "bidAmount": {"amount": "5.00", "currency": "USD"},
                            },
                            "total": {"impressions": 500, "taps": 25},
                            "insights": {
                                "bidRecommendation": {
                                    "suggestedBidAmount": {"amount": "2.50", "currency": "USD"}
                                }
                            },
                        },
                    ]
                }
            }
        }

        with patch.object(mock_client, "_request", return_value=mock_response):
            result = mock_client.get_keyword_adgroup_report(123, 456)

        assert len(result) == 2
        # First keyword: bid below suggestion
        assert float(result[0]["metadata"]["bidAmount"]["amount"]) < float(
            result[0]["insights"]["bidRecommendation"]["suggestedBidAmount"]["amount"]
        )
        # Second keyword: bid above suggestion
        assert float(result[1]["metadata"]["bidAmount"]["amount"]) > float(
            result[1]["insights"]["bidRecommendation"]["suggestedBidAmount"]["amount"]
        )


class TestSearchTermsAdGroupReport:
    """Tests for get_search_terms_adgroup_report."""

    def test_search_terms_adgroup_report_uses_ortz(self, mock_client):
        """Test that search terms report uses ORTZ timezone (required)."""
        mock_response = {"data": {"reportingDataResponse": {"row": []}}}

        with patch.object(mock_client, "_request", return_value=mock_response) as mock_req:
            mock_client.get_search_terms_adgroup_report(123, 456)

            data = mock_req.call_args.kwargs.get("data") or mock_req.call_args[1].get("data")
            assert data["timeZone"] == "ORTZ"

    def test_search_terms_adgroup_report_correct_endpoint(self, mock_client):
        """Test that search terms adgroup report uses the correct endpoint."""
        mock_response = {"data": {"reportingDataResponse": {"row": []}}}

        with patch.object(mock_client, "_request", return_value=mock_response) as mock_req:
            mock_client.get_search_terms_adgroup_report(123, 456)

            call_args = mock_req.call_args
            assert call_args[0][1] == "/reports/campaigns/123/adgroups/456/searchterms"

    def test_search_terms_adgroup_report_with_data(self, mock_client):
        """Test search terms report returns row data."""
        mock_response = {
            "data": {
                "reportingDataResponse": {
                    "row": [
                        {
                            "metadata": {
                                "searchTermText": "fax app",
                                "searchTermSource": "TARGETED",
                            },
                            "total": {
                                "impressions": 200,
                                "taps": 20,
                                "totalInstalls": 2,
                            },
                        }
                    ]
                }
            }
        }

        with patch.object(mock_client, "_request", return_value=mock_response):
            result = mock_client.get_search_terms_adgroup_report(123, 456)

        assert len(result) == 1
        assert result[0]["metadata"]["searchTermText"] == "fax app"

    def test_search_terms_adgroup_report_empty(self, mock_client):
        """Test search terms report with no data."""
        mock_response = {"data": {"reportingDataResponse": {"row": []}}}

        with patch.object(mock_client, "_request", return_value=mock_response):
            result = mock_client.get_search_terms_adgroup_report(123, 456)

        assert result == []

    def test_search_terms_adgroup_report_api_error(self, mock_client):
        """Test handling of API error in search terms report."""
        with patch.object(mock_client, "_request", side_effect=Exception("Error")):
            result = mock_client.get_search_terms_adgroup_report(123, 456)

        assert result == []

    def test_search_terms_adgroup_report_no_metrics_false(self, mock_client):
        """Test that returnRecordsWithNoMetrics is False for search terms."""
        mock_response = {"data": {"reportingDataResponse": {"row": []}}}

        with patch.object(mock_client, "_request", return_value=mock_response) as mock_req:
            mock_client.get_search_terms_adgroup_report(123, 456)

            data = mock_req.call_args.kwargs.get("data") or mock_req.call_args[1].get("data")
            assert data["returnRecordsWithNoMetrics"] is False


class TestEdgeCases:
    """Edge case tests."""

    def test_rate_limit_error_on_custom_report(self, mock_client):
        """Test that rate limit errors are handled gracefully."""
        with patch.object(
            mock_client, "_request",
            side_effect=Exception("API error 429: Too Many Requests"),
        ):
            result = mock_client.create_custom_report(
                name="Test", start_time="2024-01-01", end_time="2024-01-30"
            )

        assert result is None

    def test_empty_results_in_all_report_types(self, mock_client):
        """Test that all report types handle empty results gracefully."""
        empty_response = {"data": {"reportingDataResponse": {"row": []}}}

        with patch.object(mock_client, "_request", return_value=empty_response):
            assert mock_client.get_ad_report(1) == []
            assert mock_client.get_keyword_adgroup_report(1, 2) == []
            assert mock_client.get_search_terms_adgroup_report(1, 2) == []

    def test_custom_report_never_completes(self, mock_client):
        """Test that a report stuck in QUEUED state is handled."""
        # This tests the API method -- the polling logic is in the CLI command,
        # but the API method itself should return the intermediate state.
        mock_response = {
            "data": {
                "id": "stuck-report",
                "state": "RUNNING",
            }
        }

        with patch.object(mock_client, "_request", return_value=mock_response):
            result = mock_client.get_custom_report("stuck-report")

        assert result is not None
        assert result["state"] == "RUNNING"

    def test_get_ad_report_with_date_range(self, mock_client):
        """Test ad report with explicit date range."""
        mock_response = {"data": {"reportingDataResponse": {"row": []}}}

        start = datetime(2024, 1, 1)
        end = datetime(2024, 1, 31)

        with patch.object(mock_client, "_request", return_value=mock_response) as mock_req:
            mock_client.get_ad_report(123, start_date=start, end_date=end)

            data = mock_req.call_args.kwargs.get("data") or mock_req.call_args[1].get("data")
            assert data["startTime"] == "2024-01-01"
            assert data["endTime"] == "2024-01-31"

    def test_keyword_adgroup_report_with_date_range(self, mock_client):
        """Test keyword adgroup report with explicit date range."""
        mock_response = {"data": {"reportingDataResponse": {"row": []}}}

        start = datetime(2024, 3, 1)
        end = datetime(2024, 3, 15)

        with patch.object(mock_client, "_request", return_value=mock_response) as mock_req:
            mock_client.get_keyword_adgroup_report(123, 456, start_date=start, end_date=end)

            data = mock_req.call_args.kwargs.get("data") or mock_req.call_args[1].get("data")
            assert data["startTime"] == "2024-03-01"
            assert data["endTime"] == "2024-03-15"

    def test_search_terms_adgroup_report_with_date_range(self, mock_client):
        """Test search terms adgroup report with explicit date range."""
        mock_response = {"data": {"reportingDataResponse": {"row": []}}}

        start = datetime(2024, 6, 1)
        end = datetime(2024, 6, 30)

        with patch.object(mock_client, "_request", return_value=mock_response) as mock_req:
            mock_client.get_search_terms_adgroup_report(123, 456, start_date=start, end_date=end)

            data = mock_req.call_args.kwargs.get("data") or mock_req.call_args[1].get("data")
            assert data["startTime"] == "2024-06-01"
            assert data["endTime"] == "2024-06-30"

    def test_create_custom_report_weekly_granularity(self, mock_client):
        """Test creating custom report with weekly granularity."""
        mock_response = {"data": {"id": "weekly-123", "state": "QUEUED"}}

        with patch.object(mock_client, "_request", return_value=mock_response) as mock_req:
            mock_client.create_custom_report(
                name="Weekly Report",
                start_time="2024-01-01",
                end_time="2024-01-30",
                granularity="WEEKLY",
            )

            data = mock_req.call_args.kwargs.get("data") or mock_req.call_args[1].get("data")
            assert data["granularity"] == "WEEKLY"

    def test_get_all_custom_reports_default_limit(self, mock_client):
        """Test that default limit is 50."""
        mock_response = {"data": []}

        with patch.object(mock_client, "_request", return_value=mock_response) as mock_req:
            mock_client.get_all_custom_reports()

            params = mock_req.call_args.kwargs.get("params") or mock_req.call_args[1].get("params")
            assert params["limit"] == 50
            assert params["offset"] == 0
