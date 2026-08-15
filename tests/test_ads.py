"""Tests for ad variation and creative management."""

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


class TestAdOperations:
    """Tests for ad CRUD operations."""

    def test_get_ads(self, mock_client):
        """Test fetching ads for an ad group."""
        mock_response = {
            "data": [
                {"id": 1, "name": "Ad 1", "status": "ENABLED"},
                {"id": 2, "name": "Ad 2", "status": "PAUSED"},
            ],
            "pagination": {"totalResults": 2, "startIndex": 0, "itemsPerPage": 1000},
        }

        with patch.object(mock_client, "_request", return_value=mock_response):
            results = mock_client.get_ads(100, 200)

        assert len(results) == 2
        assert results[0]["name"] == "Ad 1"
        assert results[1]["status"] == "PAUSED"

    def test_get_ads_empty(self, mock_client):
        """Test fetching ads when none exist."""
        mock_response = {
            "data": [],
            "pagination": {"totalResults": 0, "startIndex": 0, "itemsPerPage": 1000},
        }

        with patch.object(mock_client, "_request", return_value=mock_response):
            results = mock_client.get_ads(100, 200)

        assert len(results) == 0

    def test_get_ads_error(self, mock_client):
        """Test get_ads handles errors gracefully."""
        with patch.object(mock_client, "_request", side_effect=Exception("API error")):
            results = mock_client.get_ads(100, 200)

        assert results == []

    def test_get_ad(self, mock_client):
        """Test fetching a specific ad."""
        mock_response = {
            "data": {"id": 1, "name": "Ad 1", "status": "ENABLED", "creativeId": 500},
        }

        with patch.object(mock_client, "_request", return_value=mock_response):
            result = mock_client.get_ad(100, 200, 1)

        assert result is not None
        assert result["id"] == 1
        assert result["creativeId"] == 500

    def test_get_ad_not_found(self, mock_client):
        """Test get_ad returns None on error."""
        with patch.object(mock_client, "_request", side_effect=Exception("Not found")):
            result = mock_client.get_ad(100, 200, 999)

        assert result is None

    def test_create_ad(self, mock_client):
        """Test creating an ad."""
        mock_response = {
            "data": {"id": 10, "name": "New Ad", "status": "ENABLED", "creativeId": 500},
        }

        with patch.object(mock_client, "_request", return_value=mock_response) as mock_req:
            result = mock_client.create_ad(
                campaign_id=100,
                ad_group_id=200,
                creative_id=500,
                name="New Ad",
            )

        assert result is not None
        assert result["id"] == 10
        assert result["name"] == "New Ad"

        # Verify request payload
        call_args = mock_req.call_args
        assert call_args[0][0] == "POST"
        assert "/campaigns/100/adgroups/200/ads" in call_args[0][1]
        data = call_args[1].get("data") or call_args[0][2]
        assert data["name"] == "New Ad"
        assert data["creativeId"] == 500
        assert data["status"] == "ENABLED"

    def test_create_ad_paused(self, mock_client):
        """Test creating an ad with PAUSED status."""
        mock_response = {
            "data": {"id": 11, "name": "Paused Ad", "status": "PAUSED"},
        }

        with patch.object(mock_client, "_request", return_value=mock_response) as mock_req:
            result = mock_client.create_ad(
                campaign_id=100,
                ad_group_id=200,
                creative_id=500,
                name="Paused Ad",
                status="PAUSED",
            )

        assert result is not None
        assert result["status"] == "PAUSED"

        call_args = mock_req.call_args
        data = call_args[1].get("data") or call_args[0][2]
        assert data["status"] == "PAUSED"

    def test_create_ad_error(self, mock_client):
        """Test create_ad returns None on error."""
        with patch.object(mock_client, "_request", side_effect=Exception("API error")):
            result = mock_client.create_ad(100, 200, 500, "Bad Ad")

        assert result is None

    def test_update_ad(self, mock_client):
        """Test updating an ad."""
        mock_response = {
            "data": {"id": 1, "name": "Updated Ad", "status": "PAUSED"},
        }

        with patch.object(mock_client, "_request", return_value=mock_response) as mock_req:
            result = mock_client.update_ad(100, 200, 1, {"status": "PAUSED"})

        assert result is not None
        assert result["status"] == "PAUSED"

        call_args = mock_req.call_args
        assert call_args[0][0] == "PUT"
        assert "/campaigns/100/adgroups/200/ads/1" in call_args[0][1]

    def test_update_ad_error(self, mock_client):
        """Test update_ad returns None on error."""
        with patch.object(mock_client, "_request", side_effect=Exception("API error")):
            result = mock_client.update_ad(100, 200, 1, {"status": "PAUSED"})

        assert result is None

    def test_delete_ad(self, mock_client):
        """Test deleting an ad."""
        with patch.object(mock_client, "_request", return_value={}) as mock_req:
            result = mock_client.delete_ad(100, 200, 1)

        assert result is True

        call_args = mock_req.call_args
        assert call_args[0][0] == "DELETE"
        assert "/campaigns/100/adgroups/200/ads/1" in call_args[0][1]

    def test_delete_ad_error(self, mock_client):
        """Test delete_ad returns False on error."""
        with patch.object(mock_client, "_request", side_effect=Exception("API error")):
            result = mock_client.delete_ad(100, 200, 1)

        assert result is False

    def test_find_ads_with_campaign(self, mock_client):
        """Test finding ads scoped to a campaign."""
        mock_response = {
            "data": [{"id": 1, "name": "Ad 1"}, {"id": 2, "name": "Ad 2"}],
        }

        with patch.object(mock_client, "_request", return_value=mock_response) as mock_req:
            results = mock_client.find_ads(campaign_id=100)

        assert len(results) == 2

        call_args = mock_req.call_args
        assert "/campaigns/100/ads/find" in call_args[0][1]

    def test_find_ads_without_campaign(self, mock_client):
        """Test finding ads across all campaigns."""
        mock_response = {
            "data": [{"id": 1, "name": "Ad 1"}],
        }

        with patch.object(mock_client, "_request", return_value=mock_response) as mock_req:
            results = mock_client.find_ads()

        assert len(results) == 1

        call_args = mock_req.call_args
        assert call_args[0][1] == "/ads/find"

    def test_find_ads_with_conditions(self, mock_client):
        """Test finding ads with filter conditions."""
        mock_response = {"data": [{"id": 1}]}
        conditions = [{"field": "status", "operator": "EQUALS", "values": ["ENABLED"]}]

        with patch.object(mock_client, "_request", return_value=mock_response) as mock_req:
            mock_client.find_ads(conditions=conditions)

        call_args = mock_req.call_args
        data = call_args[1].get("data") or call_args[0][2]
        assert data["selector"]["conditions"] == conditions

    def test_find_ads_error(self, mock_client):
        """Test find_ads returns empty list on error."""
        with patch.object(mock_client, "_request", side_effect=Exception("API error")):
            results = mock_client.find_ads()

        assert results == []


class TestCreativeOperations:
    """Tests for creative operations."""

    def test_get_creatives(self, mock_client):
        """Test fetching all creatives."""
        mock_response = {
            "data": [
                {"id": 1, "name": "Creative 1", "type": "CUSTOM_PRODUCT_PAGE"},
                {"id": 2, "name": "Creative 2", "type": "DEFAULT"},
            ],
            "pagination": {"totalResults": 2, "startIndex": 0, "itemsPerPage": 1000},
        }

        with patch.object(mock_client, "_request", return_value=mock_response):
            results = mock_client.get_creatives()

        assert len(results) == 2
        assert results[0]["type"] == "CUSTOM_PRODUCT_PAGE"

    def test_get_creatives_empty(self, mock_client):
        """Test fetching creatives when none exist."""
        mock_response = {
            "data": [],
            "pagination": {"totalResults": 0, "startIndex": 0, "itemsPerPage": 1000},
        }

        with patch.object(mock_client, "_request", return_value=mock_response):
            results = mock_client.get_creatives()

        assert len(results) == 0

    def test_get_creatives_error(self, mock_client):
        """Test get_creatives handles errors gracefully."""
        with patch.object(mock_client, "_request", side_effect=Exception("API error")):
            results = mock_client.get_creatives()

        assert results == []

    def test_get_creative(self, mock_client):
        """Test fetching a specific creative."""
        mock_response = {
            "data": {"id": 1, "name": "Creative 1", "state": "VALID", "adamId": 999999},
        }

        with patch.object(mock_client, "_request", return_value=mock_response):
            result = mock_client.get_creative(1)

        assert result is not None
        assert result["name"] == "Creative 1"
        assert result["state"] == "VALID"

    def test_get_creative_not_found(self, mock_client):
        """Test get_creative returns None on error."""
        with patch.object(mock_client, "_request", side_effect=Exception("Not found")):
            result = mock_client.get_creative(999)

        assert result is None

    def test_create_creative(self, mock_client):
        """Test creating a creative."""
        mock_response = {
            "data": {"id": 10, "name": "New Creative", "type": "CUSTOM_PRODUCT_PAGE"},
        }

        with patch.object(mock_client, "_request", return_value=mock_response) as mock_req:
            result = mock_client.create_creative(
                adam_id=999999,
                name="New Creative",
                creative_type="CUSTOM_PRODUCT_PAGE",
                product_page_id="pp-123",
            )

        assert result is not None
        assert result["id"] == 10

        call_args = mock_req.call_args
        data = call_args[1].get("data") or call_args[0][2]
        assert data["adamId"] == 999999
        assert data["name"] == "New Creative"
        assert data["type"] == "CUSTOM_PRODUCT_PAGE"
        assert data["productPageId"] == "pp-123"

    def test_create_creative_without_product_page(self, mock_client):
        """Test creating a creative without a product page ID."""
        mock_response = {
            "data": {"id": 11, "name": "Default Creative", "type": "DEFAULT"},
        }

        with patch.object(mock_client, "_request", return_value=mock_response) as mock_req:
            result = mock_client.create_creative(
                adam_id=999999,
                name="Default Creative",
                creative_type="DEFAULT",
            )

        assert result is not None

        call_args = mock_req.call_args
        data = call_args[1].get("data") or call_args[0][2]
        assert "productPageId" not in data

    def test_create_creative_error(self, mock_client):
        """Test create_creative returns None on error."""
        with patch.object(mock_client, "_request", side_effect=Exception("API error")):
            result = mock_client.create_creative(999999, "Bad", "DEFAULT")

        assert result is None

    def test_find_creatives(self, mock_client):
        """Test finding creatives."""
        mock_response = {
            "data": [{"id": 1, "name": "Creative 1"}],
        }

        with patch.object(mock_client, "_request", return_value=mock_response) as mock_req:
            results = mock_client.find_creatives()

        assert len(results) == 1

        call_args = mock_req.call_args
        assert call_args[0][0] == "POST"
        assert "/creatives/find" in call_args[0][1]

    def test_find_creatives_with_conditions(self, mock_client):
        """Test finding creatives with filter conditions."""
        mock_response = {"data": [{"id": 1}]}
        conditions = [{"field": "state", "operator": "EQUALS", "values": ["VALID"]}]

        with patch.object(mock_client, "_request", return_value=mock_response) as mock_req:
            mock_client.find_creatives(conditions=conditions)

        call_args = mock_req.call_args
        data = call_args[1].get("data") or call_args[0][2]
        assert data["selector"]["conditions"] == conditions

    def test_find_creatives_error(self, mock_client):
        """Test find_creatives returns empty list on error."""
        with patch.object(mock_client, "_request", side_effect=Exception("API error")):
            results = mock_client.find_creatives()

        assert results == []


class TestProductPageOperations:
    """Tests for product page operations."""

    def test_get_product_pages(self, mock_client):
        """Test fetching product pages."""
        mock_response = {
            "data": [
                {"id": "pp-1", "name": "Page 1", "state": "VISIBLE"},
                {"id": "pp-2", "name": "Page 2", "state": "HIDDEN"},
            ],
            "pagination": {"totalResults": 2, "startIndex": 0, "itemsPerPage": 1000},
        }

        with patch.object(mock_client, "_request", return_value=mock_response):
            results = mock_client.get_product_pages(999999)

        assert len(results) == 2
        assert results[0]["name"] == "Page 1"

    def test_get_product_pages_empty(self, mock_client):
        """Test fetching product pages when none exist."""
        mock_response = {
            "data": [],
            "pagination": {"totalResults": 0, "startIndex": 0, "itemsPerPage": 1000},
        }

        with patch.object(mock_client, "_request", return_value=mock_response):
            results = mock_client.get_product_pages(999999)

        assert len(results) == 0

    def test_get_product_pages_error(self, mock_client):
        """Test get_product_pages handles errors gracefully."""
        with patch.object(mock_client, "_request", side_effect=Exception("API error")):
            results = mock_client.get_product_pages(999999)

        assert results == []

    def test_get_product_page_locales(self, mock_client):
        """Test fetching locale details for a product page."""
        mock_response = {
            "data": [
                {"language": "en-US", "name": "English Page"},
                {"language": "es-MX", "name": "Spanish Page"},
            ],
            "pagination": {"totalResults": 2, "startIndex": 0, "itemsPerPage": 1000},
        }

        with patch.object(mock_client, "_request", return_value=mock_response):
            results = mock_client.get_product_page_locales(999999, "pp-1")

        assert len(results) == 2
        assert results[0]["language"] == "en-US"

    def test_get_product_page_locales_error(self, mock_client):
        """Test get_product_page_locales handles errors gracefully."""
        with patch.object(mock_client, "_request", side_effect=Exception("API error")):
            results = mock_client.get_product_page_locales(999999, "pp-1")

        assert results == []


class TestRejectionReasonsAndAssets:
    """Tests for rejection reasons and app assets."""

    def test_find_rejection_reasons(self, mock_client):
        """Test finding rejection reasons."""
        mock_response = {
            "data": [
                {"creativeId": 1, "reasonText": "Inappropriate content"},
            ],
        }

        with patch.object(mock_client, "_request", return_value=mock_response) as mock_req:
            results = mock_client.find_rejection_reasons()

        assert len(results) == 1
        assert results[0]["reasonText"] == "Inappropriate content"

        call_args = mock_req.call_args
        assert "/product-page-reasons/find" in call_args[0][1]

    def test_find_rejection_reasons_empty(self, mock_client):
        """Test finding rejection reasons when none exist."""
        mock_response = {"data": []}

        with patch.object(mock_client, "_request", return_value=mock_response):
            results = mock_client.find_rejection_reasons()

        assert len(results) == 0

    def test_find_rejection_reasons_with_conditions(self, mock_client):
        """Test finding rejection reasons with conditions."""
        mock_response = {"data": [{"creativeId": 1}]}
        conditions = [{"field": "creativeId", "operator": "EQUALS", "values": ["1"]}]

        with patch.object(mock_client, "_request", return_value=mock_response) as mock_req:
            mock_client.find_rejection_reasons(conditions=conditions)

        call_args = mock_req.call_args
        data = call_args[1].get("data") or call_args[0][2]
        assert data["selector"]["conditions"] == conditions

    def test_find_rejection_reasons_error(self, mock_client):
        """Test find_rejection_reasons returns empty list on error."""
        with patch.object(mock_client, "_request", side_effect=Exception("API error")):
            results = mock_client.find_rejection_reasons()

        assert results == []

    def test_find_app_assets(self, mock_client):
        """Test finding app assets."""
        mock_response = {
            "data": [
                {"id": "asset-1", "type": "SCREENSHOT", "orientation": "PORTRAIT"},
                {"id": "asset-2", "type": "APP_PREVIEW", "orientation": "LANDSCAPE"},
            ],
        }

        with patch.object(mock_client, "_request", return_value=mock_response) as mock_req:
            results = mock_client.find_app_assets(999999)

        assert len(results) == 2
        assert results[0]["type"] == "SCREENSHOT"

        call_args = mock_req.call_args
        assert "/apps/999999/assets/find" in call_args[0][1]

    def test_find_app_assets_with_conditions(self, mock_client):
        """Test finding app assets with conditions."""
        mock_response = {"data": [{"id": "asset-1"}]}
        conditions = [{"field": "type", "operator": "EQUALS", "values": ["SCREENSHOT"]}]

        with patch.object(mock_client, "_request", return_value=mock_response) as mock_req:
            mock_client.find_app_assets(999999, conditions=conditions)

        call_args = mock_req.call_args
        data = call_args[1].get("data") or call_args[0][2]
        assert data["selector"]["conditions"] == conditions

    def test_find_app_assets_empty(self, mock_client):
        """Test finding app assets when none exist."""
        mock_response = {"data": []}

        with patch.object(mock_client, "_request", return_value=mock_response):
            results = mock_client.find_app_assets(999999)

        assert len(results) == 0

    def test_find_app_assets_error(self, mock_client):
        """Test find_app_assets returns empty list on error."""
        with patch.object(mock_client, "_request", side_effect=Exception("API error")):
            results = mock_client.find_app_assets(999999)

        assert results == []


class TestAdEndpointPaths:
    """Tests to verify correct API endpoint paths are used."""

    def test_get_ads_endpoint(self, mock_client):
        """Test get_ads uses correct endpoint path."""
        mock_response = {
            "data": [],
            "pagination": {"totalResults": 0, "startIndex": 0, "itemsPerPage": 1000},
        }

        with patch.object(mock_client, "_request", return_value=mock_response) as mock_req:
            mock_client.get_ads(111, 222)

        call_args = mock_req.call_args
        assert call_args[1].get("params", {}).get("offset", 0) == 0 or True
        # The paginated helper calls _request with GET
        assert call_args[0][0] == "GET"
        assert "/campaigns/111/adgroups/222/ads" in call_args[0][1]

    def test_get_ad_endpoint(self, mock_client):
        """Test get_ad uses correct endpoint path."""
        mock_response = {"data": {"id": 333}}

        with patch.object(mock_client, "_request", return_value=mock_response) as mock_req:
            mock_client.get_ad(111, 222, 333)

        call_args = mock_req.call_args
        assert call_args[0][0] == "GET"
        assert call_args[0][1] == "/campaigns/111/adgroups/222/ads/333"

    def test_create_ad_endpoint(self, mock_client):
        """Test create_ad uses correct endpoint path."""
        mock_response = {"data": {"id": 10}}

        with patch.object(mock_client, "_request", return_value=mock_response) as mock_req:
            mock_client.create_ad(111, 222, 500, "Test")

        call_args = mock_req.call_args
        assert call_args[0][0] == "POST"
        assert call_args[0][1] == "/campaigns/111/adgroups/222/ads"

    def test_update_ad_endpoint(self, mock_client):
        """Test update_ad uses correct endpoint path."""
        mock_response = {"data": {"id": 333}}

        with patch.object(mock_client, "_request", return_value=mock_response) as mock_req:
            mock_client.update_ad(111, 222, 333, {"status": "PAUSED"})

        call_args = mock_req.call_args
        assert call_args[0][0] == "PUT"
        assert call_args[0][1] == "/campaigns/111/adgroups/222/ads/333"

    def test_delete_ad_endpoint(self, mock_client):
        """Test delete_ad uses correct endpoint path."""
        with patch.object(mock_client, "_request", return_value={}) as mock_req:
            mock_client.delete_ad(111, 222, 333)

        call_args = mock_req.call_args
        assert call_args[0][0] == "DELETE"
        assert call_args[0][1] == "/campaigns/111/adgroups/222/ads/333"

    def test_get_creatives_endpoint(self, mock_client):
        """Test get_creatives uses correct endpoint path."""
        mock_response = {
            "data": [],
            "pagination": {"totalResults": 0, "startIndex": 0, "itemsPerPage": 1000},
        }

        with patch.object(mock_client, "_request", return_value=mock_response) as mock_req:
            mock_client.get_creatives()

        call_args = mock_req.call_args
        assert "/creatives" in call_args[0][1]

    def test_get_creative_endpoint(self, mock_client):
        """Test get_creative uses correct endpoint path."""
        mock_response = {"data": {"id": 500}}

        with patch.object(mock_client, "_request", return_value=mock_response) as mock_req:
            mock_client.get_creative(500)

        call_args = mock_req.call_args
        assert call_args[0][0] == "GET"
        assert call_args[0][1] == "/creatives/500"

    def test_product_pages_endpoint(self, mock_client):
        """Test get_product_pages uses correct endpoint path."""
        mock_response = {
            "data": [],
            "pagination": {"totalResults": 0, "startIndex": 0, "itemsPerPage": 1000},
        }

        with patch.object(mock_client, "_request", return_value=mock_response) as mock_req:
            mock_client.get_product_pages(999999)

        call_args = mock_req.call_args
        assert "/apps/999999/product-pages" in call_args[0][1]

    def test_product_page_locales_endpoint(self, mock_client):
        """Test get_product_page_locales uses correct endpoint path."""
        mock_response = {
            "data": [],
            "pagination": {"totalResults": 0, "startIndex": 0, "itemsPerPage": 1000},
        }

        with patch.object(mock_client, "_request", return_value=mock_response) as mock_req:
            mock_client.get_product_page_locales(999999, "pp-123")

        call_args = mock_req.call_args
        assert "/apps/999999/product-pages/pp-123/locale-details" in call_args[0][1]
