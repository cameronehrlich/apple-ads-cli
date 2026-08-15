"""Tests for negative keyword CRUD and bulk keyword operations."""

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


class TestFindCampaignNegativeKeywords:
    """Tests for find_campaign_negative_keywords."""

    def test_find_with_no_conditions(self, mock_client):
        """Test find with no conditions returns all negative keywords."""
        mock_response = {
            "data": [
                {"id": 1, "text": "free", "matchType": "EXACT", "status": "ACTIVE"},
                {"id": 2, "text": "cheap", "matchType": "BROAD", "status": "ACTIVE"},
            ],
        }

        with patch.object(mock_client, "_request", return_value=mock_response) as mock_req:
            results = mock_client.find_campaign_negative_keywords(100)

        assert len(results) == 2
        assert results[0]["text"] == "free"
        # Verify correct endpoint
        call_args = mock_req.call_args
        assert call_args[0][1] == "/campaigns/100/negativekeywords/find"

    def test_find_with_conditions(self, mock_client):
        """Test find with selector conditions."""
        mock_response = {
            "data": [{"id": 1, "text": "free", "matchType": "EXACT"}],
        }

        conditions = [{"field": "text", "operator": "CONTAINS", "values": ["free"]}]

        with patch.object(mock_client, "_request", return_value=mock_response) as mock_req:
            results = mock_client.find_campaign_negative_keywords(100, conditions=conditions)

        assert len(results) == 1
        # Verify conditions were passed in selector
        call_data = mock_req.call_args.kwargs.get("data") or mock_req.call_args[1].get("data")
        assert "selector" in call_data
        assert call_data["selector"]["conditions"] == conditions

    def test_find_empty_results(self, mock_client):
        """Test find with no matches."""
        mock_response = {"data": []}

        with patch.object(mock_client, "_request", return_value=mock_response):
            results = mock_client.find_campaign_negative_keywords(100)

        assert len(results) == 0

    def test_find_handles_error(self, mock_client):
        """Test find handles API errors gracefully."""
        with patch.object(mock_client, "_request", side_effect=Exception("API error")):
            results = mock_client.find_campaign_negative_keywords(100)

        assert results == []


class TestUpdateCampaignNegativeKeywords:
    """Tests for update_campaign_negative_keywords."""

    def test_update_status(self, mock_client):
        """Test updating negative keyword status."""
        mock_response = {
            "data": [{"id": 1, "text": "free", "status": "PAUSED"}],
        }

        updates = [{"id": 1, "status": "PAUSED"}]

        with patch.object(mock_client, "_request", return_value=mock_response) as mock_req:
            result = mock_client.update_campaign_negative_keywords(100, updates)

        assert result is not None
        assert result[0]["status"] == "PAUSED"
        # Verify correct endpoint and method
        call_args = mock_req.call_args
        assert call_args[0][0] == "PUT"
        assert call_args[0][1] == "/campaigns/100/negativekeywords/bulk"

    def test_update_empty_list(self, mock_client):
        """Test update with empty list returns empty list."""
        result = mock_client.update_campaign_negative_keywords(100, [])
        assert result == []

    def test_update_multiple(self, mock_client):
        """Test updating multiple negative keywords at once."""
        mock_response = {
            "data": [
                {"id": 1, "status": "PAUSED"},
                {"id": 2, "status": "PAUSED"},
            ],
        }

        updates = [{"id": 1, "status": "PAUSED"}, {"id": 2, "status": "PAUSED"}]

        with patch.object(mock_client, "_request", return_value=mock_response) as mock_req:
            result = mock_client.update_campaign_negative_keywords(100, updates)

        assert len(result) == 2
        # Verify the payload is the list of updates
        call_data = mock_req.call_args.kwargs.get("data") or mock_req.call_args[1].get("data")
        assert len(call_data) == 2

    def test_update_handles_error(self, mock_client):
        """Test update handles API errors gracefully."""
        with patch.object(mock_client, "_request", side_effect=Exception("API error")):
            result = mock_client.update_campaign_negative_keywords(100, [{"id": 1}])

        assert result is None


class TestDeleteCampaignNegativeKeywords:
    """Tests for delete_campaign_negative_keywords."""

    def test_delete_single(self, mock_client):
        """Test deleting a single negative keyword."""
        mock_response = {}

        with patch.object(mock_client, "_request", return_value=mock_response) as mock_req:
            result = mock_client.delete_campaign_negative_keywords(100, [1])

        assert result is True
        call_args = mock_req.call_args
        assert call_args[0][0] == "POST"
        assert call_args[0][1] == "/campaigns/100/negativekeywords/delete/bulk"

    def test_delete_multiple(self, mock_client):
        """Test deleting multiple negative keywords."""
        mock_response = {}

        with patch.object(mock_client, "_request", return_value=mock_response) as mock_req:
            result = mock_client.delete_campaign_negative_keywords(100, [1, 2, 3])

        assert result is True
        # Verify the payload is the list of IDs
        call_data = mock_req.call_args.kwargs.get("data") or mock_req.call_args[1].get("data")
        assert call_data == [1, 2, 3]

    def test_delete_empty_list(self, mock_client):
        """Test deleting with empty list returns True without API call."""
        with patch.object(mock_client, "_request") as mock_req:
            result = mock_client.delete_campaign_negative_keywords(100, [])

        assert result is True
        mock_req.assert_not_called()

    def test_delete_handles_error(self, mock_client):
        """Test delete handles API errors gracefully."""
        with patch.object(mock_client, "_request", side_effect=Exception("API error")):
            result = mock_client.delete_campaign_negative_keywords(100, [1])

        assert result is False

    def test_delete_duplicate_ids(self, mock_client):
        """Test deleting with duplicate IDs sends them as-is (API handles dedup)."""
        mock_response = {}

        with patch.object(mock_client, "_request", return_value=mock_response) as mock_req:
            result = mock_client.delete_campaign_negative_keywords(100, [1, 1, 2])

        assert result is True
        call_data = mock_req.call_args.kwargs.get("data") or mock_req.call_args[1].get("data")
        assert call_data == [1, 1, 2]


class TestGetAdGroupNegativeKeywords:
    """Tests for get_ad_group_negative_keywords."""

    def test_get_single_page(self, mock_client):
        """Test getting ad group negative keywords (single page)."""
        mock_response = {
            "data": [
                {"id": 1, "text": "free", "matchType": "EXACT"},
                {"id": 2, "text": "cheap", "matchType": "EXACT"},
            ],
            "pagination": {"totalResults": 2, "startIndex": 0, "itemsPerPage": 1000},
        }

        with patch.object(mock_client, "_request", return_value=mock_response):
            results = mock_client.get_ad_group_negative_keywords(100, 200)

        assert len(results) == 2

    def test_get_paginated(self, mock_client):
        """Test pagination of ad group negative keywords."""
        page1 = {
            "data": [{"id": i, "text": f"kw{i}"} for i in range(20)],
            "pagination": {"totalResults": 25, "startIndex": 0, "itemsPerPage": 20},
        }
        page2 = {
            "data": [{"id": i, "text": f"kw{i}"} for i in range(20, 25)],
            "pagination": {"totalResults": 25, "startIndex": 20, "itemsPerPage": 20},
        }

        with patch.object(mock_client, "_request", side_effect=[page1, page2]):
            results = mock_client.get_ad_group_negative_keywords(100, 200)

        assert len(results) == 25

    def test_get_empty(self, mock_client):
        """Test getting empty ad group negative keywords."""
        mock_response = {
            "data": [],
            "pagination": {"totalResults": 0, "startIndex": 0, "itemsPerPage": 1000},
        }

        with patch.object(mock_client, "_request", return_value=mock_response):
            results = mock_client.get_ad_group_negative_keywords(100, 200)

        assert len(results) == 0

    def test_get_handles_error(self, mock_client):
        """Test get handles API errors gracefully."""
        with patch.object(mock_client, "_request", side_effect=Exception("API error")):
            results = mock_client.get_ad_group_negative_keywords(100, 200)

        assert results == []


class TestFindAdGroupNegativeKeywords:
    """Tests for find_ad_group_negative_keywords."""

    def test_find_with_no_conditions(self, mock_client):
        """Test find across all ad groups."""
        mock_response = {
            "data": [
                {"id": 1, "text": "free", "adGroupId": 200},
                {"id": 2, "text": "cheap", "adGroupId": 201},
            ],
        }

        with patch.object(mock_client, "_request", return_value=mock_response) as mock_req:
            results = mock_client.find_ad_group_negative_keywords(100)

        assert len(results) == 2
        call_args = mock_req.call_args
        assert call_args[0][1] == "/campaigns/100/adgroups/negativekeywords/find"

    def test_find_with_conditions(self, mock_client):
        """Test find with selector conditions."""
        mock_response = {
            "data": [{"id": 1, "text": "free"}],
        }

        conditions = [{"field": "text", "operator": "EQUALS", "values": ["free"]}]

        with patch.object(mock_client, "_request", return_value=mock_response) as mock_req:
            results = mock_client.find_ad_group_negative_keywords(100, conditions=conditions)

        assert len(results) == 1
        call_data = mock_req.call_args.kwargs.get("data") or mock_req.call_args[1].get("data")
        assert call_data["selector"]["conditions"] == conditions

    def test_find_empty_results(self, mock_client):
        """Test find with no matches."""
        mock_response = {"data": []}

        with patch.object(mock_client, "_request", return_value=mock_response):
            results = mock_client.find_ad_group_negative_keywords(100)

        assert len(results) == 0


class TestUpdateAdGroupNegativeKeywords:
    """Tests for update_ad_group_negative_keywords."""

    def test_update_status(self, mock_client):
        """Test updating ad group negative keyword status."""
        mock_response = {
            "data": [{"id": 1, "text": "free", "status": "PAUSED"}],
        }

        updates = [{"id": 1, "status": "PAUSED"}]

        with patch.object(mock_client, "_request", return_value=mock_response) as mock_req:
            result = mock_client.update_ad_group_negative_keywords(100, 200, updates)

        assert result is not None
        assert result[0]["status"] == "PAUSED"
        call_args = mock_req.call_args
        assert call_args[0][0] == "PUT"
        assert call_args[0][1] == "/campaigns/100/adgroups/200/negativekeywords/bulk"

    def test_update_empty_list(self, mock_client):
        """Test update with empty list returns empty list."""
        result = mock_client.update_ad_group_negative_keywords(100, 200, [])
        assert result == []

    def test_update_handles_error(self, mock_client):
        """Test update handles API errors gracefully."""
        with patch.object(mock_client, "_request", side_effect=Exception("API error")):
            result = mock_client.update_ad_group_negative_keywords(100, 200, [{"id": 1}])

        assert result is None


class TestDeleteAdGroupNegativeKeywords:
    """Tests for delete_ad_group_negative_keywords."""

    def test_delete_single(self, mock_client):
        """Test deleting a single ad group negative keyword."""
        mock_response = {}

        with patch.object(mock_client, "_request", return_value=mock_response) as mock_req:
            result = mock_client.delete_ad_group_negative_keywords(100, 200, [1])

        assert result is True
        call_args = mock_req.call_args
        assert call_args[0][0] == "POST"
        assert call_args[0][1] == "/campaigns/100/adgroups/200/negativekeywords/delete/bulk"

    def test_delete_multiple(self, mock_client):
        """Test deleting multiple ad group negative keywords."""
        mock_response = {}

        with patch.object(mock_client, "_request", return_value=mock_response) as mock_req:
            result = mock_client.delete_ad_group_negative_keywords(100, 200, [1, 2, 3])

        assert result is True
        call_data = mock_req.call_args.kwargs.get("data") or mock_req.call_args[1].get("data")
        assert call_data == [1, 2, 3]

    def test_delete_empty_list(self, mock_client):
        """Test deleting with empty list returns True without API call."""
        with patch.object(mock_client, "_request") as mock_req:
            result = mock_client.delete_ad_group_negative_keywords(100, 200, [])

        assert result is True
        mock_req.assert_not_called()

    def test_delete_handles_error(self, mock_client):
        """Test delete handles API errors gracefully."""
        with patch.object(mock_client, "_request", side_effect=Exception("API error")):
            result = mock_client.delete_ad_group_negative_keywords(100, 200, [1])

        assert result is False

    def test_delete_duplicate_ids(self, mock_client):
        """Test deleting with duplicate IDs sends them as-is."""
        mock_response = {}

        with patch.object(mock_client, "_request", return_value=mock_response) as mock_req:
            result = mock_client.delete_ad_group_negative_keywords(100, 200, [5, 5, 6])

        assert result is True
        call_data = mock_req.call_args.kwargs.get("data") or mock_req.call_args[1].get("data")
        assert call_data == [5, 5, 6]


class TestUpdateKeywordsBulk:
    """Tests for update_keywords_bulk."""

    def test_update_bids(self, mock_client):
        """Test bulk bid update."""
        mock_response = {
            "data": [
                {"id": 1, "bidAmount": {"amount": "2.50", "currency": "USD"}},
                {"id": 2, "bidAmount": {"amount": "2.50", "currency": "USD"}},
            ],
        }

        updates = [
            {"id": 1, "bidAmount": {"amount": "2.50", "currency": "USD"}},
            {"id": 2, "bidAmount": {"amount": "2.50", "currency": "USD"}},
        ]

        with patch.object(mock_client, "_request", return_value=mock_response) as mock_req:
            result = mock_client.update_keywords_bulk(100, 200, updates)

        assert result is not None
        assert len(result) == 2
        assert result[0]["bidAmount"]["amount"] == "2.50"
        call_args = mock_req.call_args
        assert call_args[0][0] == "PUT"
        assert call_args[0][1] == "/campaigns/100/adgroups/200/targetingkeywords/bulk"

    def test_update_payload_structure(self, mock_client):
        """Test that the bulk update payload is structured correctly."""
        mock_response = {"data": [{"id": 1}]}

        updates = [
            {"id": 1, "bidAmount": {"amount": "3.00", "currency": "USD"}},
            {"id": 2, "bidAmount": {"amount": "1.50", "currency": "USD"}, "status": "PAUSED"},
        ]

        with patch.object(mock_client, "_request", return_value=mock_response) as mock_req:
            mock_client.update_keywords_bulk(100, 200, updates)

        call_data = mock_req.call_args.kwargs.get("data") or mock_req.call_args[1].get("data")
        assert isinstance(call_data, list)
        assert len(call_data) == 2
        assert call_data[0]["id"] == 1
        assert call_data[0]["bidAmount"]["amount"] == "3.00"
        assert call_data[1]["status"] == "PAUSED"

    def test_update_empty_list(self, mock_client):
        """Test update with empty list returns empty list."""
        result = mock_client.update_keywords_bulk(100, 200, [])
        assert result == []

    def test_update_handles_error(self, mock_client):
        """Test update handles API errors gracefully."""
        with patch.object(mock_client, "_request", side_effect=Exception("API error")):
            result = mock_client.update_keywords_bulk(100, 200, [{"id": 1}])

        assert result is None


class TestFindTargetingKeywords:
    """Tests for find_targeting_keywords."""

    def test_find_with_no_conditions(self, mock_client):
        """Test find across all ad groups with no conditions."""
        mock_response = {
            "data": [
                {"id": 1, "text": "photo editor", "adGroupId": 200},
                {"id": 2, "text": "image editor", "adGroupId": 201},
            ],
        }

        with patch.object(mock_client, "_request", return_value=mock_response) as mock_req:
            results = mock_client.find_targeting_keywords(100)

        assert len(results) == 2
        call_args = mock_req.call_args
        assert call_args[0][1] == "/campaigns/100/adgroups/targetingkeywords/find"

    def test_find_with_conditions(self, mock_client):
        """Test find with selector conditions."""
        mock_response = {
            "data": [{"id": 1, "text": "photo editor"}],
        }

        conditions = [{"field": "text", "operator": "CONTAINS", "values": ["photo"]}]

        with patch.object(mock_client, "_request", return_value=mock_response) as mock_req:
            results = mock_client.find_targeting_keywords(100, conditions=conditions)

        assert len(results) == 1
        call_data = mock_req.call_args.kwargs.get("data") or mock_req.call_args[1].get("data")
        assert "selector" in call_data
        assert call_data["selector"]["conditions"] == conditions
        assert call_data["selector"]["pagination"] == {"offset": 0, "limit": 1000}

    def test_find_empty_results(self, mock_client):
        """Test find with no matches."""
        mock_response = {"data": []}

        with patch.object(mock_client, "_request", return_value=mock_response):
            results = mock_client.find_targeting_keywords(100)

        assert len(results) == 0

    def test_find_handles_error(self, mock_client):
        """Test find handles API errors gracefully."""
        with patch.object(mock_client, "_request", side_effect=Exception("API error")):
            results = mock_client.find_targeting_keywords(100)

        assert results == []
