"""Tests for API client module."""

from unittest.mock import patch

import pytest

from asa_cli.api import SearchAdsClient
from asa_cli.config import AppConfig, Credentials, MatchType


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
        response = {
            "data": [{"dailyBudgetAmount": {"amount": "10", "currency": "EUR"}}],
        }

        with patch.object(mock_client, "_request", return_value=response) as mock_request:
            assert mock_client.get_org_currency() == "EUR"
            assert mock_client.get_org_currency() == "EUR"

        assert mock_client._currency == "EUR"
        assert mock_request.call_count == 1

    def test_get_org_currency_does_not_cache_usd_fallback(self, mock_client):
        """Test the USD fallback is returned without populating the cache."""
        with patch.object(mock_client, "_request", return_value={"data": []}) as mock_request:
            assert mock_client.get_org_currency() == "USD"
            assert mock_client.get_org_currency() == "USD"

        assert mock_client._currency is None
        assert mock_request.call_count == 2

    def test_get_org_currency_propagates_request_errors(self, mock_client):
        """Test request errors surface to the caller."""
        with patch.object(mock_client, "_request", side_effect=RuntimeError("boom")):
            with pytest.raises(RuntimeError, match="boom"):
                mock_client.get_org_currency()

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
