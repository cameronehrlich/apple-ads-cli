"""Tests for geo targeting API methods and commands."""

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


class TestGeoSearch:
    """Tests for geo_search API method."""

    def test_geo_search_basic(self, mock_client):
        """Test basic geo search returns results."""
        mock_response = {
            "data": [
                {
                    "id": "US",
                    "displayName": "United States",
                    "entity": "Country",
                    "countryOrRegion": "US",
                },
                {
                    "id": "US|CA",
                    "displayName": "California",
                    "entity": "AdminArea",
                    "countryOrRegion": "US",
                },
            ],
        }

        with patch.object(mock_client, "_request", return_value=mock_response) as mock_req:
            results = mock_client.geo_search("california")

        assert len(results) == 2
        assert results[0]["id"] == "US"
        assert results[1]["entity"] == "AdminArea"
        mock_req.assert_called_once_with(
            "GET",
            "/search/geo",
            params={
                "query": "california",
                "countrycode": "US",
                "limit": 20,
                "offset": 0,
            },
        )

    def test_geo_search_with_entity_filter(self, mock_client):
        """Test geo search with entity type filter."""
        mock_response = {
            "data": [
                {
                    "id": "US|CA|Los Angeles",
                    "displayName": "Los Angeles",
                    "entity": "Locality",
                    "countryOrRegion": "US",
                },
            ],
        }

        with patch.object(mock_client, "_request", return_value=mock_response) as mock_req:
            results = mock_client.geo_search("los angeles", entity="Locality", country_code="US")

        assert len(results) == 1
        assert results[0]["entity"] == "Locality"
        call_params = mock_req.call_args[1]["params"]
        assert call_params["entity"] == "Locality"

    def test_geo_search_empty_results(self, mock_client):
        """Test geo search with no matches returns empty list."""
        mock_response = {"data": []}

        with patch.object(mock_client, "_request", return_value=mock_response):
            results = mock_client.geo_search("xyznonexistent")

        assert results == []

    def test_geo_search_custom_limit_and_offset(self, mock_client):
        """Test geo search respects limit and offset parameters."""
        mock_response = {"data": [{"id": "US", "displayName": "United States"}]}

        with patch.object(mock_client, "_request", return_value=mock_response) as mock_req:
            mock_client.geo_search("us", limit=5, offset=10)

        call_params = mock_req.call_args[1]["params"]
        assert call_params["limit"] == 5
        assert call_params["offset"] == 10

    def test_geo_search_api_error(self, mock_client):
        """Test geo search handles API errors gracefully."""
        with patch.object(mock_client, "_request", side_effect=Exception("API error")):
            results = mock_client.geo_search("test")

        assert results == []

    def test_geo_search_no_entity_param_when_none(self, mock_client):
        """Test that entity param is omitted when not provided."""
        mock_response = {"data": []}

        with patch.object(mock_client, "_request", return_value=mock_response) as mock_req:
            mock_client.geo_search("test")

        call_params = mock_req.call_args[1]["params"]
        assert "entity" not in call_params


class TestGetGeoLocations:
    """Tests for get_geo_locations POST method."""

    def test_get_geo_locations_success(self, mock_client):
        """Test looking up specific geo locations."""
        mock_response = {
            "data": [
                {
                    "id": "US",
                    "displayName": "United States",
                    "entity": "Country",
                },
                {
                    "id": "CA",
                    "displayName": "Canada",
                    "entity": "Country",
                },
            ],
        }

        geo_requests = [
            {"id": "US", "entity": "Country"},
            {"id": "CA", "entity": "Country"},
        ]

        with patch.object(mock_client, "_request", return_value=mock_response) as mock_req:
            results = mock_client.get_geo_locations(geo_requests)

        assert len(results) == 2
        assert results[0]["displayName"] == "United States"
        mock_req.assert_called_once_with("POST", "/search/geo", data=geo_requests)

    def test_get_geo_locations_empty_request(self, mock_client):
        """Test looking up with empty request list."""
        mock_response = {"data": []}

        with patch.object(mock_client, "_request", return_value=mock_response):
            results = mock_client.get_geo_locations([])

        assert results == []

    def test_get_geo_locations_api_error(self, mock_client):
        """Test get_geo_locations handles API errors gracefully."""
        with patch.object(mock_client, "_request", side_effect=Exception("API error")):
            results = mock_client.get_geo_locations([{"id": "US", "entity": "Country"}])

        assert results == []


class TestCampaignGeoTargeting:
    """Tests for campaign geo targeting extraction."""

    def test_get_campaign_geo_targeting_success(self, mock_client):
        """Test extracting countriesOrRegions from a campaign."""
        mock_campaign = {
            "id": 123,
            "name": "Test Campaign",
            "countriesOrRegions": ["US", "CA", "GB"],
        }

        with patch.object(mock_client, "get_campaign", return_value=mock_campaign):
            countries = mock_client.get_campaign_geo_targeting(123)

        assert countries == ["US", "CA", "GB"]

    def test_get_campaign_geo_targeting_no_countries(self, mock_client):
        """Test campaign with no countriesOrRegions field."""
        mock_campaign = {
            "id": 123,
            "name": "Test Campaign",
        }

        with patch.object(mock_client, "get_campaign", return_value=mock_campaign):
            countries = mock_client.get_campaign_geo_targeting(123)

        assert countries == []

    def test_get_campaign_geo_targeting_campaign_not_found(self, mock_client):
        """Test when campaign does not exist."""
        with patch.object(mock_client, "get_campaign", return_value=None):
            countries = mock_client.get_campaign_geo_targeting(999)

        assert countries == []

    def test_get_campaign_geo_targeting_empty_countries(self, mock_client):
        """Test campaign with empty countriesOrRegions list."""
        mock_campaign = {
            "id": 123,
            "name": "Test Campaign",
            "countriesOrRegions": [],
        }

        with patch.object(mock_client, "get_campaign", return_value=mock_campaign):
            countries = mock_client.get_campaign_geo_targeting(123)

        assert countries == []


class TestUpdateCampaignCountries:
    """Tests for update_campaign_countries."""

    def test_update_campaign_countries_success(self, mock_client):
        """Test successful country update."""
        mock_response = {
            "id": 123,
            "countriesOrRegions": ["US", "CA"],
        }

        with patch.object(mock_client, "update_campaign", return_value=mock_response) as mock_update:
            result = mock_client.update_campaign_countries(123, ["US", "CA"])

        assert result is not None
        assert result["countriesOrRegions"] == ["US", "CA"]
        mock_update.assert_called_once_with(
            123,
            {
                "countriesOrRegions": ["US", "CA"],
                "clearGeoTargetingOnCountryOrRegionChange": True,
            },
        )

    def test_update_campaign_countries_includes_clear_flag(self, mock_client):
        """Test that clearGeoTargetingOnCountryOrRegionChange is always set."""
        with patch.object(mock_client, "update_campaign", return_value={"id": 123}) as mock_update:
            mock_client.update_campaign_countries(123, ["GB"])

        call_args = mock_update.call_args[0]
        updates = call_args[1]
        assert updates["clearGeoTargetingOnCountryOrRegionChange"] is True

    def test_update_campaign_countries_failure(self, mock_client):
        """Test update failure returns None."""
        with patch.object(mock_client, "update_campaign", return_value=None):
            result = mock_client.update_campaign_countries(123, ["US"])

        assert result is None

    def test_update_campaign_countries_single_country(self, mock_client):
        """Test updating to a single country."""
        with patch.object(mock_client, "update_campaign", return_value={"id": 123}) as mock_update:
            mock_client.update_campaign_countries(123, ["JP"])

        call_args = mock_update.call_args[0]
        updates = call_args[1]
        assert updates["countriesOrRegions"] == ["JP"]

    def test_update_campaign_countries_many_countries(self, mock_client):
        """Test updating with many country codes."""
        many_countries = ["US", "CA", "GB", "AU", "DE", "FR", "JP", "KR", "BR", "MX"]

        with patch.object(mock_client, "update_campaign", return_value={"id": 123}) as mock_update:
            mock_client.update_campaign_countries(123, many_countries)

        call_args = mock_update.call_args[0]
        updates = call_args[1]
        assert updates["countriesOrRegions"] == many_countries
        assert len(updates["countriesOrRegions"]) == 10
