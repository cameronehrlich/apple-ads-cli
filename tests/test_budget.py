"""Tests for budget management features."""

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
        client._currency = "USD"
        return client


class TestGetBudgetOrders:
    """Tests for get_budget_orders."""

    def test_get_budget_orders_pagination(self, mock_client):
        """Test get_budget_orders uses pagination to fetch all results."""
        page1 = {
            "data": [
                {
                    "id": 1,
                    "name": "Q1 Budget",
                    "budget": {"amount": "5000", "currency": "USD"},
                    "startDate": "2025-01-01",
                    "endDate": "2025-03-31",
                    "status": "ACTIVE",
                    "orderNumber": "BO-001",
                },
            ],
            "pagination": {"totalResults": 2, "startIndex": 0, "itemsPerPage": 1},
        }
        page2 = {
            "data": [
                {
                    "id": 2,
                    "name": "Q2 Budget",
                    "budget": {"amount": "10000", "currency": "USD"},
                    "startDate": "2025-04-01",
                    "endDate": "2025-06-30",
                    "status": "ACTIVE",
                    "orderNumber": "BO-002",
                },
            ],
            "pagination": {"totalResults": 2, "startIndex": 1, "itemsPerPage": 1},
        }

        with patch.object(mock_client, "_request", side_effect=[page1, page2]):
            results = mock_client.get_budget_orders()

        assert len(results) == 2
        assert results[0]["name"] == "Q1 Budget"
        assert results[1]["name"] == "Q2 Budget"

    def test_get_budget_orders_empty(self, mock_client):
        """Test get_budget_orders with no budget orders."""
        mock_response = {
            "data": [],
            "pagination": {"totalResults": 0, "startIndex": 0, "itemsPerPage": 1000},
        }

        with patch.object(mock_client, "_request", return_value=mock_response):
            results = mock_client.get_budget_orders()

        assert len(results) == 0

    def test_get_budget_orders_single_page(self, mock_client):
        """Test get_budget_orders with a single page of results."""
        mock_response = {
            "data": [
                {
                    "id": 1,
                    "name": "Annual Budget",
                    "budget": {"amount": "50000", "currency": "USD"},
                    "status": "ACTIVE",
                },
                {
                    "id": 2,
                    "name": "Test Budget",
                    "budget": {"amount": "1000", "currency": "USD"},
                    "status": "PAUSED",
                },
            ],
            "pagination": {"totalResults": 2, "startIndex": 0, "itemsPerPage": 1000},
        }

        with patch.object(mock_client, "_request", return_value=mock_response):
            results = mock_client.get_budget_orders()

        assert len(results) == 2

    def test_get_budget_orders_api_error(self, mock_client):
        """Test get_budget_orders handles API errors gracefully."""
        with patch.object(mock_client, "_request", side_effect=Exception("API Error")):
            results = mock_client.get_budget_orders()

        assert results == []


class TestGetBudgetOrder:
    """Tests for get_budget_order."""

    def test_get_budget_order_success(self, mock_client):
        """Test fetching a specific budget order by ID."""
        mock_response = {
            "data": {
                "id": 42,
                "name": "Q1 Budget",
                "budget": {"amount": "5000", "currency": "USD"},
                "startDate": "2025-01-01",
                "endDate": "2025-03-31",
                "status": "ACTIVE",
                "orderNumber": "BO-042",
            }
        }

        with patch.object(mock_client, "_request", return_value=mock_response):
            result = mock_client.get_budget_order(42)

        assert result is not None
        assert result["id"] == 42
        assert result["name"] == "Q1 Budget"
        assert result["budget"]["amount"] == "5000"

    def test_get_budget_order_not_found(self, mock_client):
        """Test fetching a non-existent budget order returns None."""
        with patch.object(
            mock_client, "_request", side_effect=Exception("API error 404: Not Found")
        ):
            result = mock_client.get_budget_order(99999)

        assert result is None

    def test_get_budget_order_api_error(self, mock_client):
        """Test get_budget_order handles API errors gracefully."""
        with patch.object(mock_client, "_request", side_effect=Exception("Server Error")):
            result = mock_client.get_budget_order(1)

        assert result is None


class TestCreateBudgetOrder:
    """Tests for create_budget_order."""

    def test_create_budget_order_success(self, mock_client):
        """Test creating a budget order."""
        mock_client._currency = "EUR"
        mock_response = {
            "data": {
                "id": 100,
                "name": "New Budget",
                "budget": {"amount": "10000", "currency": "EUR"},
                "startDate": "2025-06-01",
                "endDate": "2025-12-31",
                "status": "ACTIVE",
            }
        }

        with patch.object(mock_client, "_request", return_value=mock_response) as mock_req:
            result = mock_client.create_budget_order(
                name="New Budget",
                budget=10000.0,
                start_date="2025-06-01",
                end_date="2025-12-31",
            )

        assert result is not None
        assert result["id"] == 100
        assert result["name"] == "New Budget"

        # Verify the request payload
        call_args = mock_req.call_args
        data = call_args.kwargs.get("data") or call_args[1].get("data")
        assert data["name"] == "New Budget"
        assert data["budget"]["amount"] == "10000.0"
        assert data["budget"]["currency"] == "EUR"
        assert data["startDate"] == "2025-06-01"
        assert data["endDate"] == "2025-12-31"

    def test_create_budget_order_with_kwargs(self, mock_client):
        """Test creating a budget order with extra fields."""
        mock_response = {
            "data": {
                "id": 101,
                "name": "Client Budget",
                "clientName": "Acme Corp",
            }
        }

        with patch.object(mock_client, "_request", return_value=mock_response) as mock_req:
            result = mock_client.create_budget_order(
                name="Client Budget",
                budget=5000.0,
                start_date="2025-01-01",
                end_date="2025-12-31",
                clientName="Acme Corp",
            )

        assert result is not None
        call_args = mock_req.call_args
        data = call_args.kwargs.get("data") or call_args[1].get("data")
        assert data["clientName"] == "Acme Corp"

    def test_create_budget_order_api_error(self, mock_client):
        """Test create_budget_order handles API errors gracefully."""
        with patch.object(mock_client, "_request", side_effect=Exception("API Error")):
            result = mock_client.create_budget_order(
                name="Fail",
                budget=1000.0,
                start_date="2025-01-01",
                end_date="2025-12-31",
            )

        assert result is None


class TestUpdateBudgetOrder:
    """Tests for update_budget_order."""

    def test_update_budget_order_success(self, mock_client):
        """Test updating a budget order."""
        mock_response = {
            "data": {
                "id": 42,
                "name": "Updated Budget",
                "budget": {"amount": "20000", "currency": "USD"},
            }
        }

        with patch.object(mock_client, "_request", return_value=mock_response):
            result = mock_client.update_budget_order(42, {"name": "Updated Budget"})

        assert result is not None
        assert result["name"] == "Updated Budget"

    def test_update_budget_order_api_error(self, mock_client):
        """Test update_budget_order handles API errors gracefully."""
        with patch.object(mock_client, "_request", side_effect=Exception("API Error")):
            result = mock_client.update_budget_order(42, {"name": "Fail"})

        assert result is None


class TestCampaignBudgetStatus:
    """Tests for get_campaign_budget_status."""

    def test_campaign_budget_status_with_spend(self, mock_client):
        """Test campaign budget status includes spend data from reports."""
        mock_campaigns = {
            "data": [
                {
                    "id": 1,
                    "name": "Brand Campaign",
                    "budgetAmount": {"amount": "1500", "currency": "USD"},
                    "dailyBudgetAmount": {"amount": "50", "currency": "USD"},
                    "status": "ENABLED",
                    "displayStatus": "RUNNING",
                    "servingStatus": "RUNNING",
                },
                {
                    "id": 2,
                    "name": "Category Campaign",
                    "budgetAmount": {"amount": "3000", "currency": "USD"},
                    "dailyBudgetAmount": {"amount": "100", "currency": "USD"},
                    "status": "ENABLED",
                    "displayStatus": "RUNNING",
                    "servingStatus": "RUNNING",
                },
            ],
            "pagination": {"totalResults": 2, "startIndex": 0, "itemsPerPage": 1000},
        }

        mock_report = {
            "data": {
                "reportingDataResponse": {
                    "row": [
                        {
                            "metadata": {"campaignId": 1},
                            "total": {"localSpend": {"amount": "250.50"}},
                        },
                        {
                            "metadata": {"campaignId": 2},
                            "total": {"localSpend": {"amount": "800.75"}},
                        },
                    ]
                }
            }
        }

        def mock_request(method, endpoint, **kwargs):
            if endpoint == "/reports/campaigns":
                return mock_report
            # Pagination requests for /campaigns
            return mock_campaigns

        with patch.object(mock_client, "_request", side_effect=mock_request):
            results = mock_client.get_campaign_budget_status()

        assert len(results) == 2
        assert results[0]["id"] == 1
        assert results[0]["name"] == "Brand Campaign"
        assert results[0]["totalSpend"] == 250.50
        assert results[0]["dailyBudgetAmount"]["amount"] == "50"
        assert results[1]["totalSpend"] == 800.75

    def test_campaign_budget_status_no_campaigns(self, mock_client):
        """Test campaign budget status with no campaigns."""
        mock_response = {
            "data": [],
            "pagination": {"totalResults": 0, "startIndex": 0, "itemsPerPage": 1000},
        }

        with patch.object(mock_client, "_request", return_value=mock_response):
            results = mock_client.get_campaign_budget_status()

        assert results == []

    def test_campaign_budget_status_no_daily_budget(self, mock_client):
        """Test campaigns with no daily budget set."""
        mock_campaigns = {
            "data": [
                {
                    "id": 1,
                    "name": "No Daily Budget",
                    "budgetAmount": {"amount": "1000", "currency": "USD"},
                    "status": "ENABLED",
                    "displayStatus": "RUNNING",
                    "servingStatus": "RUNNING",
                },
            ],
            "pagination": {"totalResults": 1, "startIndex": 0, "itemsPerPage": 1000},
        }

        mock_report = {"data": {"reportingDataResponse": {"row": []}}}

        def mock_request(method, endpoint, **kwargs):
            if endpoint == "/reports/campaigns":
                return mock_report
            return mock_campaigns

        with patch.object(mock_client, "_request", side_effect=mock_request):
            results = mock_client.get_campaign_budget_status()

        assert len(results) == 1
        assert results[0]["dailyBudgetAmount"] is None
        assert results[0]["totalSpend"] == 0.0

    def test_campaign_budget_status_various_states(self, mock_client):
        """Test campaigns with various budget/status states."""
        mock_campaigns = {
            "data": [
                {
                    "id": 1,
                    "name": "Active Campaign",
                    "budgetAmount": {"amount": "1500", "currency": "USD"},
                    "dailyBudgetAmount": {"amount": "50", "currency": "USD"},
                    "status": "ENABLED",
                    "displayStatus": "RUNNING",
                    "servingStatus": "RUNNING",
                },
                {
                    "id": 2,
                    "name": "Paused Campaign",
                    "budgetAmount": {"amount": "2000", "currency": "USD"},
                    "dailyBudgetAmount": {"amount": "75", "currency": "USD"},
                    "status": "PAUSED",
                    "displayStatus": "PAUSED",
                    "servingStatus": "NOT_RUNNING",
                },
                {
                    "id": 3,
                    "name": "Exhausted Campaign",
                    "budgetAmount": {"amount": "500", "currency": "USD"},
                    "dailyBudgetAmount": {"amount": "25", "currency": "USD"},
                    "status": "ENABLED",
                    "displayStatus": "ON_HOLD",
                    "servingStatus": "NOT_RUNNING",
                },
            ],
            "pagination": {"totalResults": 3, "startIndex": 0, "itemsPerPage": 1000},
        }

        mock_report = {
            "data": {
                "reportingDataResponse": {
                    "row": [
                        {
                            "metadata": {"campaignId": 1},
                            "total": {"localSpend": {"amount": "100.00"}},
                        },
                        {
                            "metadata": {"campaignId": 3},
                            "total": {"localSpend": {"amount": "500.00"}},
                        },
                    ]
                }
            }
        }

        def mock_request(method, endpoint, **kwargs):
            if endpoint == "/reports/campaigns":
                return mock_report
            return mock_campaigns

        with patch.object(mock_client, "_request", side_effect=mock_request):
            results = mock_client.get_campaign_budget_status()

        assert len(results) == 3

        # Active campaign
        assert results[0]["status"] == "ENABLED"
        assert results[0]["displayStatus"] == "RUNNING"
        assert results[0]["totalSpend"] == 100.00

        # Paused campaign (no spend in report)
        assert results[1]["status"] == "PAUSED"
        assert results[1]["displayStatus"] == "PAUSED"
        assert results[1]["totalSpend"] == 0.0

        # Exhausted campaign
        assert results[2]["status"] == "ENABLED"
        assert results[2]["displayStatus"] == "ON_HOLD"
        assert results[2]["totalSpend"] == 500.00

    def test_campaign_budget_status_report_error(self, mock_client):
        """Test campaign budget status when report fails but campaigns succeed."""
        mock_campaigns = {
            "data": [
                {
                    "id": 1,
                    "name": "Campaign",
                    "budgetAmount": {"amount": "1000", "currency": "USD"},
                    "dailyBudgetAmount": {"amount": "50", "currency": "USD"},
                    "status": "ENABLED",
                    "displayStatus": "RUNNING",
                    "servingStatus": "RUNNING",
                },
            ],
            "pagination": {"totalResults": 1, "startIndex": 0, "itemsPerPage": 1000},
        }

        # Reports endpoint returns error rows (empty), campaigns succeed
        call_count = 0

        def mock_request(method, endpoint, **kwargs):
            nonlocal call_count
            if endpoint == "/reports/campaigns":
                # Report returns empty (simulating graceful failure from get_campaign_report)
                return {"data": {"reportingDataResponse": {"row": []}}}
            call_count += 1
            return mock_campaigns

        with patch.object(mock_client, "_request", side_effect=mock_request):
            results = mock_client.get_campaign_budget_status()

        assert len(results) == 1
        assert results[0]["totalSpend"] == 0.0
