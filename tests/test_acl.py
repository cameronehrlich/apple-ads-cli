"""Tests for ACL, user, and app search API methods."""

from unittest.mock import patch

import pytest

from asa_cli.config import AppConfig, Credentials
from asa_cli.v5.api import SearchAdsClient


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


class TestGetAcls:
    """Tests for get_acls endpoint."""

    def test_get_acls_returns_orgs(self, mock_client):
        """Test get_acls returns a list of organizations."""
        mock_response = {
            "data": [
                {
                    "orgId": 123456,
                    "orgName": "My Org",
                    "roleNames": ["Admin"],
                    "currency": "USD",
                    "paymentModel": "LOC",
                },
                {
                    "orgId": 789012,
                    "orgName": "Other Org",
                    "roleNames": ["Read Only"],
                    "currency": "EUR",
                    "paymentModel": "PAYG",
                },
            ]
        }

        with patch.object(mock_client, "_request", return_value=mock_response) as mock_req:
            results = mock_client.get_acls()

        assert len(results) == 2
        assert results[0]["orgName"] == "My Org"
        assert results[1]["orgId"] == 789012

        # Verify skip_org_context=True was passed
        mock_req.assert_called_once_with("GET", "/acls", skip_org_context=True)

    def test_get_acls_no_orgs(self, mock_client):
        """Test get_acls with no organizations."""
        mock_response = {"data": []}

        with patch.object(mock_client, "_request", return_value=mock_response) as mock_req:
            results = mock_client.get_acls()

        assert len(results) == 0
        mock_req.assert_called_once_with("GET", "/acls", skip_org_context=True)

    def test_get_acls_no_org_header(self, mock_client, mock_credentials):
        """Test that get_acls does not send X-AP-Context header."""
        import requests as req_lib

        mock_response = type("Response", (), {
            "status_code": 200,
            "json": lambda self: {"data": []},
            "text": "",
        })()

        with patch.object(req_lib, "request", return_value=mock_response) as mock_http:
            with patch.object(SearchAdsClient, "_get_access_token", return_value="mock_token"):
                client = SearchAdsClient(mock_credentials)
                client.get_acls()

        # Verify the actual HTTP call did NOT include X-AP-Context
        call_kwargs = mock_http.call_args
        headers = call_kwargs.kwargs.get("headers") or call_kwargs[1].get("headers")
        assert "X-AP-Context" not in headers

    def test_get_acls_handles_error(self, mock_client):
        """Test get_acls handles API errors gracefully."""
        with patch.object(mock_client, "_request", side_effect=Exception("API error")):
            results = mock_client.get_acls()

        assert results == []


class TestGetMe:
    """Tests for get_me endpoint."""

    def test_get_me_returns_user_info(self, mock_client):
        """Test get_me returns current user information."""
        mock_response = {
            "data": {
                "userId": 42,
                "parentId": 123456,
            }
        }

        with patch.object(mock_client, "_request", return_value=mock_response) as mock_req:
            result = mock_client.get_me()

        assert result is not None
        assert result["userId"] == 42

        # Verify skip_org_context=True was passed
        mock_req.assert_called_once_with("GET", "/me", skip_org_context=True)

    def test_get_me_no_org_header(self, mock_client, mock_credentials):
        """Test that get_me does not send X-AP-Context header."""
        import requests as req_lib

        mock_response = type("Response", (), {
            "status_code": 200,
            "json": lambda self: {"data": {"userId": 1}},
            "text": "",
        })()

        with patch.object(req_lib, "request", return_value=mock_response) as mock_http:
            with patch.object(SearchAdsClient, "_get_access_token", return_value="mock_token"):
                client = SearchAdsClient(mock_credentials)
                client.get_me()

        call_kwargs = mock_http.call_args
        headers = call_kwargs.kwargs.get("headers") or call_kwargs[1].get("headers")
        assert "X-AP-Context" not in headers

    def test_get_me_handles_error(self, mock_client):
        """Test get_me handles API errors gracefully."""
        with patch.object(mock_client, "_request", side_effect=Exception("API error")):
            result = mock_client.get_me()

        assert result is None


class TestSearchApps:
    """Tests for search_apps endpoint."""

    def test_search_apps_returns_results(self, mock_client):
        """Test search_apps returns matching apps."""
        mock_response = {
            "data": [
                {
                    "adamId": 111111,
                    "appName": "My App",
                    "developerName": "Dev Inc",
                    "countryOrRegionCodes": ["US"],
                },
                {
                    "adamId": 222222,
                    "appName": "Other App",
                    "developerName": "Other Dev",
                    "countryOrRegionCodes": ["US", "GB"],
                },
            ]
        }

        with patch.object(mock_client, "_request", return_value=mock_response) as mock_req:
            results = mock_client.search_apps("My App")

        assert len(results) == 2
        assert results[0]["appName"] == "My App"

        # Verify params were passed correctly
        call_kwargs = mock_req.call_args
        params = call_kwargs.kwargs.get("params") or call_kwargs[1].get("params")
        assert params["query"] == "My App"
        assert params["returnOwnedApps"] == "true"

    def test_search_apps_empty_results(self, mock_client):
        """Test search_apps with no matching apps."""
        mock_response = {"data": []}

        with patch.object(mock_client, "_request", return_value=mock_response):
            results = mock_client.search_apps("nonexistent app xyz")

        assert len(results) == 0

    def test_search_apps_return_all(self, mock_client):
        """Test search_apps with return_owned=False returns all apps."""
        mock_response = {"data": [{"adamId": 111111}]}

        with patch.object(mock_client, "_request", return_value=mock_response) as mock_req:
            mock_client.search_apps("test", return_owned=False)

        call_kwargs = mock_req.call_args
        params = call_kwargs.kwargs.get("params") or call_kwargs[1].get("params")
        assert params["returnOwnedApps"] == "false"

    def test_search_apps_custom_limit(self, mock_client):
        """Test search_apps with custom limit."""
        mock_response = {"data": []}

        with patch.object(mock_client, "_request", return_value=mock_response) as mock_req:
            mock_client.search_apps("test", limit=10)

        call_kwargs = mock_req.call_args
        params = call_kwargs.kwargs.get("params") or call_kwargs[1].get("params")
        assert params["limit"] == 10

    def test_search_apps_handles_error(self, mock_client):
        """Test search_apps handles API errors gracefully."""
        with patch.object(mock_client, "_request", side_effect=Exception("API error")):
            results = mock_client.search_apps("test")

        assert results == []


class TestAppEligibility:
    """Tests for get_app_eligibility endpoint."""

    def test_get_eligibility_returns_data(self, mock_client):
        """Test get_app_eligibility returns eligibility info."""
        mock_response = {
            "data": [
                {"condition": "canRunAds", "status": "ELIGIBLE"},
                {"condition": "appStoreSearchAds", "status": "ELIGIBLE"},
            ]
        }

        with patch.object(mock_client, "_request", return_value=mock_response) as mock_req:
            result = mock_client.get_app_eligibility(999999)

        assert result is not None
        assert len(result) == 2

        # Verify endpoint includes adam_id
        call_kwargs = mock_req.call_args
        assert "/apps/999999/eligibilities/find" in call_kwargs[0][1]

    def test_get_eligibility_with_conditions(self, mock_client):
        """Test get_app_eligibility passes conditions in body."""
        mock_response = {"data": [{"condition": "canRunAds", "status": "ELIGIBLE"}]}

        with patch.object(mock_client, "_request", return_value=mock_response) as mock_req:
            mock_client.get_app_eligibility(999999, conditions=["canRunAds"])

        call_kwargs = mock_req.call_args
        data = call_kwargs.kwargs.get("data") or call_kwargs[1].get("data")
        assert data["conditions"] == ["canRunAds"]

    def test_get_eligibility_no_conditions(self, mock_client):
        """Test get_app_eligibility with no conditions sends empty data."""
        mock_response = {"data": {}}

        with patch.object(mock_client, "_request", return_value=mock_response) as mock_req:
            mock_client.get_app_eligibility(999999)

        call_kwargs = mock_req.call_args
        data = call_kwargs.kwargs.get("data") or call_kwargs[1].get("data")
        assert data == {}

    def test_get_eligibility_handles_error(self, mock_client):
        """Test get_app_eligibility handles API errors gracefully."""
        with patch.object(mock_client, "_request", side_effect=Exception("API error")):
            result = mock_client.get_app_eligibility(999999)

        assert result is None


class TestSupportedCountries:
    """Tests for get_supported_countries endpoint."""

    def test_get_countries_returns_list(self, mock_client):
        """Test get_supported_countries returns country records."""
        mock_response = {
            "data": [
                {"countryOrRegion": "US", "displayName": "United States"},
                {"countryOrRegion": "GB", "displayName": "United Kingdom"},
            ]
        }

        with patch.object(mock_client, "_request", return_value=mock_response):
            results = mock_client.get_supported_countries()

        assert len(results) == 2
        assert results[0]["countryOrRegion"] == "US"

    def test_get_countries_with_filter(self, mock_client):
        """Test get_supported_countries with country code filter."""
        mock_response = {
            "data": [{"countryOrRegion": "US", "displayName": "United States"}]
        }

        with patch.object(mock_client, "_request", return_value=mock_response) as mock_req:
            mock_client.get_supported_countries(countries=["US", "GB"])

        call_kwargs = mock_req.call_args
        params = call_kwargs.kwargs.get("params") or call_kwargs[1].get("params")
        assert params["countriesOrRegions"] == "US,GB"

    def test_get_countries_handles_error(self, mock_client):
        """Test get_supported_countries handles API errors gracefully."""
        with patch.object(mock_client, "_request", side_effect=Exception("API error")):
            results = mock_client.get_supported_countries()

        assert results == []


class TestDeviceSizes:
    """Tests for get_app_preview_device_sizes endpoint."""

    def test_get_device_sizes_returns_list(self, mock_client):
        """Test get_app_preview_device_sizes returns device records."""
        mock_response = {
            "data": [
                {"deviceClass": "IPHONE", "displayName": "iPhone 15 Pro"},
                {"deviceClass": "IPAD", "displayName": "iPad Pro 12.9"},
            ]
        }

        with patch.object(mock_client, "_request", return_value=mock_response):
            results = mock_client.get_app_preview_device_sizes()

        assert len(results) == 2

    def test_get_device_sizes_handles_error(self, mock_client):
        """Test get_app_preview_device_sizes handles API errors gracefully."""
        with patch.object(mock_client, "_request", side_effect=Exception("API error")):
            results = mock_client.get_app_preview_device_sizes()

        assert results == []


class TestRequestSkipOrgContext:
    """Tests that _request correctly handles skip_org_context."""

    def test_request_includes_org_header_by_default(self, mock_credentials):
        """Test that _request includes X-AP-Context by default."""
        import requests as req_lib

        mock_response = type("Response", (), {
            "status_code": 200,
            "json": lambda self: {"data": {}},
            "text": "",
        })()

        with patch.object(req_lib, "request", return_value=mock_response) as mock_http:
            with patch.object(SearchAdsClient, "_get_access_token", return_value="mock_token"):
                client = SearchAdsClient(mock_credentials)
                client._request("GET", "/campaigns")

        call_kwargs = mock_http.call_args
        headers = call_kwargs.kwargs.get("headers") or call_kwargs[1].get("headers")
        assert "X-AP-Context" in headers
        assert headers["X-AP-Context"] == "orgId=123456"

    def test_request_omits_org_header_when_skipped(self, mock_credentials):
        """Test that _request omits X-AP-Context when skip_org_context=True."""
        import requests as req_lib

        mock_response = type("Response", (), {
            "status_code": 200,
            "json": lambda self: {"data": {}},
            "text": "",
        })()

        with patch.object(req_lib, "request", return_value=mock_response) as mock_http:
            with patch.object(SearchAdsClient, "_get_access_token", return_value="mock_token"):
                client = SearchAdsClient(mock_credentials)
                client._request("GET", "/acls", skip_org_context=True)

        call_kwargs = mock_http.call_args
        headers = call_kwargs.kwargs.get("headers") or call_kwargs[1].get("headers")
        assert "X-AP-Context" not in headers
