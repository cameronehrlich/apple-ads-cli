"""Tests for API client module."""

from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest
import requests

from asa_cli.config import AppConfig, Credentials, MatchType
from asa_cli.v5.api import (
    REPORTING_TIME_ZONE,
    REQUEST_TIMEOUT,
    ReportRows,
    SearchAdsAPIError,
    SearchAdsClient,
    _complete_report_range,
)


def test_default_v5_report_range_is_30_inclusive_completed_dates():
    start, end = _complete_report_range(
        None,
        None,
        now=datetime(2026, 8, 17, 15, 30),
    )

    assert start.isoformat() == "2026-07-18T00:00:00"
    assert end.isoformat() == "2026-08-16T00:00:00"


def test_v5_org_context_requires_explicit_legacy_org_id():
    credentials = Credentials(
        ad_account_id="account-123",
        client_id="client",
        team_id="team",
        key_id="key",
        private_key_path="/tmp/private-key.pem",
    )
    client = SearchAdsClient(credentials=credentials)

    with pytest.raises(ValueError, match="Legacy API v5 requires an organization ID"):
        _ = client.org_id


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
        client._currency = "USD"
        return client


class TestPagination:
    """Tests for pagination support."""

    def test_get_all_paginated_single_page(self, mock_client):
        """Test pagination with single page of results."""
        mock_response = {
            "data": [{"id": 1}, {"id": 2}, {"id": 3}],
            "pagination": {"totalResults": 3, "startIndex": 0, "itemsPerPage": 20},
        }

        with patch.object(mock_client, "_request", return_value=mock_response):
            results = mock_client._get_all_paginated("/test/endpoint")

        assert len(results) == 3
        assert results[0]["id"] == 1

    def test_get_all_paginated_multiple_pages(self, mock_client):
        """Test pagination fetches all pages."""
        # First page
        page1 = {
            "data": [{"id": i} for i in range(20)],
            "pagination": {"totalResults": 35, "startIndex": 0, "itemsPerPage": 20},
        }
        # Second page
        page2 = {
            "data": [{"id": i} for i in range(20, 35)],
            "pagination": {"totalResults": 35, "startIndex": 20, "itemsPerPage": 20},
        }

        with patch.object(mock_client, "_request", side_effect=[page1, page2]):
            results = mock_client._get_all_paginated("/test/endpoint")

        assert len(results) == 35

    def test_get_all_paginated_empty_results(self, mock_client):
        """Test pagination with no results."""
        mock_response = {
            "data": [],
            "pagination": {"totalResults": 0, "startIndex": 0, "itemsPerPage": 20},
        }

        with patch.object(mock_client, "_request", return_value=mock_response):
            results = mock_client._get_all_paginated("/test/endpoint")

        assert len(results) == 0

    def test_get_keywords_uses_pagination(self, mock_client):
        """Test get_keywords uses pagination helper."""
        mock_response = {
            "data": [
                {"id": 1, "text": "keyword1", "deleted": False},
                {"id": 2, "text": "keyword2", "deleted": False},
            ],
            "pagination": {"totalResults": 2, "startIndex": 0, "itemsPerPage": 1000},
        }

        with patch.object(mock_client, "_request", return_value=mock_response):
            results = mock_client.get_keywords(123, 456)

        assert len(results) == 2

    def test_get_keywords_filters_deleted(self, mock_client):
        """Test get_keywords filters deleted keywords by default."""
        mock_response = {
            "data": [
                {"id": 1, "text": "active", "deleted": False},
                {"id": 2, "text": "deleted", "deleted": True},
            ],
            "pagination": {"totalResults": 2, "startIndex": 0, "itemsPerPage": 1000},
        }

        with patch.object(mock_client, "_request", return_value=mock_response):
            results = mock_client.get_keywords(123, 456, include_deleted=False)

        assert len(results) == 1
        assert results[0]["text"] == "active"

    def test_get_keywords_includes_deleted_when_requested(self, mock_client):
        """Test get_keywords can include deleted keywords."""
        mock_response = {
            "data": [
                {"id": 1, "text": "active", "deleted": False},
                {"id": 2, "text": "deleted", "deleted": True},
            ],
            "pagination": {"totalResults": 2, "startIndex": 0, "itemsPerPage": 1000},
        }

        with patch.object(mock_client, "_request", return_value=mock_response):
            results = mock_client.get_keywords(123, 456, include_deleted=True)

        assert len(results) == 2

    def test_report_pagination_fetches_every_page_and_retains_grand_totals(
        self, mock_client
    ):
        page1 = {
            "data": {
                "reportingDataResponse": {
                    "row": [{"metadata": {"keywordId": 1}}],
                    "grandTotals": {
                        "total": {
                            "impressions": 3,
                            "localSpend": {"amount": "1.25"},
                        }
                    },
                }
            },
            "pagination": {"totalResults": 2, "startIndex": 0, "itemsPerPage": 1},
        }
        page2 = {
            "data": {
                "reportingDataResponse": {
                    "row": [{"metadata": {"keywordId": 2}}],
                    "grandTotals": {
                        "total": {
                            "impressions": 3,
                            "localSpend": {"amount": "1.25"},
                        }
                    },
                }
            },
            "pagination": {"totalResults": 2, "startIndex": 1, "itemsPerPage": 1},
        }

        with patch.object(mock_client, "_request", side_effect=[page1, page2]) as request:
            results = mock_client.get_keyword_report(123)

        assert isinstance(results, ReportRows)
        assert [row["metadata"]["keywordId"] for row in results] == [1, 2]
        assert results.api_pages_complete is True
        assert results.page_count == 2
        assert results.total_results == 2
        assert results.grand_totals["localSpend"]["amount"] == "1.25"
        assert results.time_zone == REPORTING_TIME_ZONE
        assert results.start_date is not None
        assert results.end_date is not None
        assert request.call_args_list[0].kwargs["data"]["selector"]["pagination"][
            "offset"
        ] == 0
        assert request.call_args_list[1].kwargs["data"]["selector"]["pagination"][
            "offset"
        ] == 1

    @pytest.mark.parametrize(
        ("method_name", "arguments"),
        [
            ("get_campaign_report", (123,)),
            ("get_keyword_report", (123,)),
            ("get_ad_group_report", (123,)),
            ("get_search_terms_report", (123,)),
            ("get_ad_report", (123,)),
            ("get_keyword_adgroup_report", (123, 456)),
            ("get_search_terms_adgroup_report", (123, 456)),
        ],
    )
    def test_all_v5_performance_reports_use_comparable_ortz_by_default(
        self, mock_client, method_name, arguments
    ):
        response = {
            "data": {"reportingDataResponse": {"row": []}},
            "pagination": {"totalResults": 0, "startIndex": 0, "itemsPerPage": 0},
        }

        with patch.object(mock_client, "_request", return_value=response) as request:
            getattr(mock_client, method_name)(*arguments)

        assert request.call_args.kwargs["data"]["timeZone"] == REPORTING_TIME_ZONE

    def test_non_daily_reports_disable_incompatible_row_and_grand_totals(self, mock_client):
        response = {
            "data": {"reportingDataResponse": {"row": []}},
            "pagination": {"totalResults": 0, "startIndex": 0, "itemsPerPage": 0},
        }

        with patch.object(mock_client, "_request", return_value=response) as request:
            mock_client.get_campaign_report(123, granularity="WEEKLY")

        body = request.call_args.kwargs["data"]
        assert body["granularity"] == "WEEKLY"
        assert body["returnRowTotals"] is False
        assert body["returnGrandTotals"] is False

    def test_report_pagination_fails_closed_when_metadata_is_incomplete(self, mock_client):
        response = {
            "data": {"reportingDataResponse": {"row": [{"metadata": {}}]}},
            "pagination": {"totalResults": 2},
        }

        with patch.object(mock_client, "_request", return_value=response):
            with pytest.raises(SearchAdsAPIError, match="incomplete report pagination"):
                mock_client.get_campaign_report(123)

    def test_report_pagination_fails_closed_when_page_offset_is_inconsistent(
        self, mock_client
    ):
        response = {
            "data": {"reportingDataResponse": {"row": [{"metadata": {}}]}},
            "pagination": {"totalResults": 1, "startIndex": 1, "itemsPerPage": 1},
        }

        with patch.object(mock_client, "_request", return_value=response):
            with pytest.raises(SearchAdsAPIError, match="inconsistent report pagination"):
                mock_client.get_campaign_report(123)


class TestRequestFailures:
    """Tests for bounded requests and fail-closed API errors."""

    def test_api_request_uses_bounded_timeout(self, mock_client):
        response = MagicMock(status_code=200)
        response.json.return_value = {"data": []}

        with patch.object(mock_client, "_get_access_token", return_value="mock_token"):
            with patch("asa_cli.v5.api.requests.request", return_value=response) as request:
                mock_client._request("GET", "/campaigns")

        assert request.call_args.kwargs["timeout"] == REQUEST_TIMEOUT

    def test_api_network_error_raises_typed_error(self, mock_client):
        with patch.object(mock_client, "_get_access_token", return_value="mock_token"):
            with patch(
                "asa_cli.v5.api.requests.request",
                side_effect=requests.Timeout("timed out"),
            ):
                with pytest.raises(SearchAdsAPIError, match="GET /campaigns"):
                    mock_client._request("GET", "/campaigns")

    def test_oauth_network_error_raises_typed_error(self, mock_client):
        with patch.object(mock_client, "_create_client_secret", return_value="secret"):
            with patch(
                "asa_cli.v5.api.requests.post",
                side_effect=requests.Timeout("timed out"),
            ):
                with pytest.raises(SearchAdsAPIError, match="Apple OAuth"):
                    mock_client._get_access_token()

    def test_campaign_list_error_is_not_converted_to_empty_data(self, mock_client):
        with patch.object(
            mock_client,
            "_get_all_paginated",
            side_effect=SearchAdsAPIError("unavailable"),
        ):
            with pytest.raises(SearchAdsAPIError, match="unavailable"):
                mock_client.get_campaigns()

    @pytest.mark.parametrize(
        ("method_name", "args"),
        [
            ("get_campaign_report", (123,)),
            ("get_keyword_report", (123,)),
            ("get_ad_group_report", (123,)),
            ("get_search_terms_report", (123,)),
            ("get_keyword_adgroup_report", (123, 456)),
        ],
    )
    def test_weekly_report_errors_fail_closed(self, mock_client, method_name, args):
        with patch.object(
            mock_client,
            "_request",
            side_effect=SearchAdsAPIError("unavailable"),
        ):
            with pytest.raises(SearchAdsAPIError, match="unavailable"):
                getattr(mock_client, method_name)(*args)


class TestNegativeKeywordsErrorHandling:
    """Tests for add_negative_keywords error handling."""

    def test_add_negative_keywords_success(self, mock_client):
        """Test successful negative keyword addition."""
        mock_response = {
            "data": [{"id": 1, "text": "blocked"}],
            "pagination": None,
        }

        with patch.object(mock_client, "_request", return_value=mock_response):
            added, errors = mock_client.add_negative_keywords(123, ["blocked"])

        assert len(added) == 1
        assert len(errors) == 0

    def test_add_negative_keywords_duplicate_error(self, mock_client):
        """Test duplicate keyword returns error info."""
        mock_response = {
            "data": [],
            "pagination": None,
            "error": {
                "errors": [
                    {
                        "messageCode": "DUPLICATE_KEYWORD",
                        "message": "duplicate keyword found in the system",
                        "field": "NegativeKeywordImport[0].text:matchType",
                    }
                ]
            },
        }

        with patch.object(mock_client, "_request", return_value=mock_response):
            added, errors = mock_client.add_negative_keywords(123, ["existing"])

        assert len(added) == 0
        assert len(errors) == 1
        assert errors[0]["messageCode"] == "DUPLICATE_KEYWORD"

    def test_add_negative_keywords_empty_list(self, mock_client):
        """Test adding empty keyword list."""
        added, errors = mock_client.add_negative_keywords(123, [])

        assert len(added) == 0
        assert len(errors) == 0

    def test_add_negative_keywords_lowercases_input(self, mock_client):
        """Test keywords are lowercased before sending."""
        mock_response = {"data": [{"id": 1, "text": "test"}], "pagination": None}

        with patch.object(mock_client, "_request", return_value=mock_response) as mock_req:
            mock_client.add_negative_keywords(123, ["TEST", "MiXeD"])

            # Check the data sent to API was lowercased
            call_args = mock_req.call_args
            data = call_args.kwargs.get("data") or call_args[1].get("data")
            texts = [kw["text"] for kw in data]
            assert texts == ["test", "mixed"]


class TestAddKeywordsErrorHandling:
    """Tests for add_keywords error handling (tuple return)."""

    def test_add_keywords_success(self, mock_client):
        """Test successful keyword addition returns tuple."""
        mock_response = {
            "data": [{"id": 1, "text": "test keyword"}],
        }

        with patch.object(mock_client, "_request", return_value=mock_response):
            added, errors = mock_client.add_keywords(123, 456, ["test keyword"], MatchType.EXACT)

        assert len(added) == 1
        assert len(errors) == 0

    def test_add_keywords_duplicate_error(self, mock_client):
        """Test duplicate keyword returns error info."""
        mock_response = {
            "data": [],
            "error": {
                "errors": [
                    {
                        "messageCode": "DUPLICATE_KEYWORD",
                        "message": "duplicate keyword found",
                    }
                ]
            },
        }

        with patch.object(mock_client, "_request", return_value=mock_response):
            added, errors = mock_client.add_keywords(123, 456, ["existing"], MatchType.EXACT)

        assert len(added) == 0
        assert len(errors) == 1
        assert errors[0]["messageCode"] == "DUPLICATE_KEYWORD"

    def test_add_keywords_empty_list(self, mock_client):
        """Test adding empty keyword list."""
        added, errors = mock_client.add_keywords(123, 456, [], MatchType.EXACT)

        assert len(added) == 0
        assert len(errors) == 0


class TestCampaignOperations:
    """Tests for campaign operations."""

    def test_get_campaigns_uses_pagination(self, mock_client):
        """Test get_campaigns uses pagination."""
        mock_response = {
            "data": [{"id": 1, "name": "Brand"}, {"id": 2, "name": "Category"}],
            "pagination": {"totalResults": 2, "startIndex": 0, "itemsPerPage": 1000},
        }

        with patch.object(mock_client, "_request", return_value=mock_response):
            results = mock_client.get_campaigns()

        assert len(results) == 2

    def test_get_ad_groups_uses_pagination(self, mock_client):
        """Test get_ad_groups uses pagination."""
        mock_response = {
            "data": [{"id": 1, "name": "Exact"}, {"id": 2, "name": "Broad"}],
            "pagination": {"totalResults": 2, "startIndex": 0, "itemsPerPage": 1000},
        }

        with patch.object(mock_client, "_request", return_value=mock_response):
            results = mock_client.get_ad_groups(123)

        assert len(results) == 2


class TestOrgCurrencyDetection:
    """Tests for org currency detection and caching."""

    def test_get_org_currency_caches_detected_currency(self, mock_client):
        """Test a discovered currency is cached for later calls."""
        mock_client._currency = None
        response = {
            "data": [
                {"orgId": 999999, "currency": "USD"},
                {"orgId": "123456", "currency": "eur"},
            ],
        }

        with patch.object(mock_client, "_request", return_value=response) as mock_request:
            assert mock_client.get_org_currency() == "EUR"
            assert mock_client.get_org_currency() == "EUR"

        assert mock_client._currency == "EUR"
        assert mock_request.call_count == 1
        mock_request.assert_called_once_with("GET", "/acls", skip_org_context=True)

    @pytest.mark.parametrize(
        "response",
        [
            {"data": []},
            {"data": [{"orgId": 123456}]},
            {"data": [{"orgId": 123456, "currency": ""}]},
            {"data": [{"orgId": 123456, "currency": 123}]},
            {"data": "not-a-list"},
            [],
        ],
    )
    def test_get_org_currency_fails_closed_without_matching_currency(self, mock_client, response):
        """Test missing or malformed ACL currency never falls back to USD."""
        mock_client._currency = None
        with patch.object(mock_client, "_request", return_value=response):
            with pytest.raises(SearchAdsAPIError, match="organization 123456"):
                mock_client.get_org_currency()

        assert mock_client._currency is None

    def test_get_org_currency_propagates_request_errors(self, mock_client):
        """Test request errors surface to the caller."""
        mock_client._currency = None
        with patch.object(mock_client, "_request", side_effect=RuntimeError("boom")):
            with pytest.raises(RuntimeError, match="boom"):
                mock_client.get_org_currency()

    def test_money_writes_use_detected_org_currency(self, mock_client):
        """Test every client-owned money payload uses the resolved currency."""
        mock_client._currency = "EUR"
        response = {"data": [{"id": 1}]}

        with patch.object(mock_client, "_request", return_value=response) as request:
            mock_client.create_campaign("Campaign", budget=100, daily_budget=10, countries=["DE"])
            campaign_payload = request.call_args.kwargs["data"]
            assert campaign_payload["budgetAmount"]["currency"] == "EUR"
            assert campaign_payload["dailyBudgetAmount"]["currency"] == "EUR"

            mock_client.create_ad_group(1, "Exact", 1.5, cpa_goal=2.5)
            ad_group_payload = request.call_args.kwargs["data"]
            assert ad_group_payload["defaultBidAmount"]["currency"] == "EUR"
            assert ad_group_payload["cpaGoal"]["currency"] == "EUR"

            mock_client.add_keywords(1, 2, ["fax"], MatchType.EXACT, bid_amount=3)
            keyword_payload = request.call_args.kwargs["data"]
            assert keyword_payload[0]["bidAmount"]["currency"] == "EUR"

            mock_client.update_keyword_bid(1, 2, 3, 4)
            update_payload = request.call_args.kwargs["data"]
            assert update_payload[0]["bidAmount"]["currency"] == "EUR"

    def test_get_negative_keywords_uses_pagination(self, mock_client):
        """Test get_negative_keywords uses pagination."""
        mock_response = {
            "data": [{"id": 1, "text": "blocked1"}, {"id": 2, "text": "blocked2"}],
            "pagination": {"totalResults": 2, "startIndex": 0, "itemsPerPage": 1000},
        }

        with patch.object(mock_client, "_request", return_value=mock_response):
            results = mock_client.get_negative_keywords(123)

        assert len(results) == 2

    def test_client_uses_injected_app_config(self, mock_credentials, mock_app_config):
        """Test client uses the injected app_config instead of loading from file."""
        with patch.object(SearchAdsClient, "_get_access_token", return_value="mock_token"):
            client = SearchAdsClient(mock_credentials, app_config=mock_app_config)
            assert client.app_config.app_id == 999999
            assert client.app_config.app_name == "TestApp"
