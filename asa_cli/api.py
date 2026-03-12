"""Direct API client for Apple Search Ads using JWT OAuth authentication."""

import time
from datetime import datetime, timedelta
from typing import Any, Optional

import jwt
import requests
from rich.console import Console

from .config import AppConfig, Credentials, MatchType, get_current_app_config, load_credentials

console = Console()

# Apple OAuth endpoints
TOKEN_URL = "https://appleid.apple.com/auth/oauth2/token"
API_BASE_URL = "https://api.searchads.apple.com/api/v5"


class SearchAdsClient:
    """Direct Apple Search Ads API client with JWT authentication."""

    def __init__(self, credentials: Optional[Credentials] = None, app_config: Optional[AppConfig] = None):
        """Initialize the API client.

        Args:
            credentials: API credentials (loaded from config if not provided)
            app_config: App configuration (resolved from current app if not provided)
        """
        self.credentials = credentials or load_credentials()
        self.app_config = app_config or get_current_app_config()
        self._access_token: Optional[str] = None
        self._token_expiry: Optional[float] = None
        self._currency: Optional[str] = None

    def _create_client_secret(self) -> str:
        """Create a JWT client secret for Apple OAuth.

        The client secret is a JWT signed with ES256 algorithm.
        """
        if self.credentials is None:
            raise ValueError("No credentials configured. Run 'asa config setup' first.")

        # Read private key
        with open(self.credentials.private_key_path) as f:
            private_key = f.read()

        # JWT payload
        now = int(time.time())
        payload = {
            "sub": self.credentials.client_id,
            "aud": "https://appleid.apple.com",
            "iat": now,
            "exp": now + 86400 * 180,  # 180 days max
            "iss": self.credentials.team_id,
        }

        # JWT headers
        headers = {
            "alg": "ES256",
            "kid": self.credentials.key_id,
        }

        # Create and sign the JWT
        return jwt.encode(payload, private_key, algorithm="ES256", headers=headers)

    def _get_access_token(self) -> str:
        """Get or refresh the OAuth access token."""
        # Return cached token if still valid
        if self._access_token and self._token_expiry and time.time() < self._token_expiry:
            return self._access_token

        if self.credentials is None:
            raise ValueError("No credentials configured. Run 'asa config setup' first.")

        client_secret = self._create_client_secret()

        data = {
            "grant_type": "client_credentials",
            "client_id": self.credentials.client_id,
            "client_secret": client_secret,
            "scope": "searchadsorg",
        }

        response = requests.post(TOKEN_URL, data=data)

        if response.status_code != 200:
            raise ConnectionError(
                f"Failed to get access token: {response.status_code} - {response.text}"
            )

        token_data = response.json()
        self._access_token = token_data["access_token"]
        # Token typically valid for 1 hour, refresh 5 min early
        self._token_expiry = time.time() + token_data.get("expires_in", 3600) - 300

        return self._access_token

    def _request(
        self,
        method: str,
        endpoint: str,
        data: Optional[dict] = None,
        params: Optional[dict] = None,
        _retry_count: int = 0,
    ) -> dict[str, Any]:
        """Make an authenticated API request with automatic retry on auth failure.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint path
            data: Request body data
            params: Query parameters
            _retry_count: Internal retry counter (do not set manually)

        Returns:
            API response as dict

        Raises:
            ValueError: If credentials not configured
            Exception: On API errors after retries exhausted
        """
        max_retries = 2

        if self.credentials is None:
            raise ValueError("No credentials configured. Run 'asa config setup' first.")

        url = f"{API_BASE_URL}{endpoint}"
        headers = {
            "Authorization": f"Bearer {self._get_access_token()}",
            "X-AP-Context": f"orgId={self.credentials.org_id}",
            "Content-Type": "application/json",
        }

        response = requests.request(
            method=method,
            url=url,
            headers=headers,
            json=data,
            params=params,
        )

        # Handle auth failures with retry
        if response.status_code == 401 and _retry_count < max_retries:
            console.print(f"[yellow]Auth token expired, refreshing... (attempt {_retry_count + 1}/{max_retries})[/yellow]")
            # Clear cached token to force refresh
            self._access_token = None
            self._token_expiry = None
            # Retry the request
            return self._request(method, endpoint, data, params, _retry_count + 1)

        if response.status_code >= 400:
            error_msg = f"API error {response.status_code}: {response.text}"
            console.print(f"[red]{error_msg}[/red]")
            raise Exception(error_msg)

        if response.status_code == 204:  # No content
            return {}

        return response.json()

    def _get_all_paginated(
        self, endpoint: str, params: Optional[dict] = None, limit: int = 1000
    ) -> list[dict[str, Any]]:
        """Fetch all results from a paginated endpoint.

        Apple Search Ads API defaults to 20 items per page. This method fetches
        all pages and returns the combined results.

        Args:
            endpoint: API endpoint path
            params: Optional query parameters
            limit: Items per page (max 1000)

        Returns:
            Combined list of all results across all pages
        """
        all_results: list[dict[str, Any]] = []
        offset = 0
        request_params = params.copy() if params else {}

        while True:
            request_params["limit"] = limit
            request_params["offset"] = offset

            response = self._request("GET", endpoint, params=request_params)

            data = response.get("data", []) if isinstance(response, dict) else []
            all_results.extend(data)

            pagination = response.get("pagination", {})
            total = pagination.get("totalResults", 0)
            fetched = offset + len(data)

            if fetched >= total or len(data) == 0:
                break

            offset = fetched

        return all_results

    @property
    def org_id(self) -> int:
        """Get organization ID."""
        if self.credentials is None:
            raise ValueError("No credentials configured.")
        return self.credentials.org_id

    def get_org_currency(self) -> str:
        """Detect organization currency from existing campaigns (fallback: USD)."""
        if self._currency:
            return self._currency

        try:
            response = self._request("GET", "/campaigns", params={"limit": 1, "offset": 0})
            campaigns = response.get("data", []) if isinstance(response, dict) else []
            if campaigns:
                campaign = campaigns[0]
                daily_budget = campaign.get("dailyBudgetAmount", {})
                currency = daily_budget.get("currency")
                if currency:
                    self._currency = str(currency)
                    return self._currency
        except Exception:
            # Best-effort only; fall back to USD below
            pass

        self._currency = "USD"
        return self._currency

    # =========================================================================
    # Campaign Operations
    # =========================================================================

    def get_campaigns(self) -> list[dict[str, Any]]:
        """Get all campaigns for the organization (handles pagination)."""
        try:
            return self._get_all_paginated("/campaigns")
        except Exception as e:
            console.print(f"[red]Error fetching campaigns: {e}[/red]")
            return []

    def get_campaign(self, campaign_id: int) -> Optional[dict[str, Any]]:
        """Get a specific campaign by ID."""
        try:
            response = self._request("GET", f"/campaigns/{campaign_id}")
            return response.get("data") if isinstance(response, dict) else None
        except Exception as e:
            console.print(f"[red]Error fetching campaign {campaign_id}: {e}[/red]")
            return None

    def create_campaign(
        self,
        name: str,
        budget: float,
        countries: list[str],
        daily_budget: Optional[float] = None,
        status: str = "ENABLED",
    ) -> Optional[dict[str, Any]]:
        """Create a new campaign."""
        if self.app_config is None:
            raise ValueError("No app config. Run 'asa config setup' first.")

        try:
            currency = self.get_org_currency()
            campaign_data = {
                "name": name,
                "adamId": self.app_config.app_id,
                "budgetAmount": {"amount": str(budget), "currency": currency},
                "dailyBudgetAmount": {"amount": str(daily_budget or budget), "currency": currency},
                "countriesOrRegions": countries,
                "status": status,
                "supplySources": ["APPSTORE_SEARCH_RESULTS"],
                "adChannelType": "SEARCH",
                "billingEvent": "TAPS",
            }

            response = self._request("POST", "/campaigns", data=campaign_data)
            return response.get("data") if isinstance(response, dict) else None
        except Exception as e:
            console.print(f"[red]Error creating campaign: {e}[/red]")
            return None

    def update_campaign(self, campaign_id: int, updates: dict[str, Any]) -> Optional[dict[str, Any]]:
        """Update a campaign."""
        try:
            # Apple API requires updates wrapped in 'campaign' object
            payload = {"campaign": updates}
            response = self._request("PUT", f"/campaigns/{campaign_id}", data=payload)
            return response.get("data") if isinstance(response, dict) else None
        except Exception as e:
            console.print(f"[red]Error updating campaign {campaign_id}: {e}[/red]")
            return None

    def pause_campaign(self, campaign_id: int) -> bool:
        """Pause a campaign."""
        result = self.update_campaign(campaign_id, {"status": "PAUSED"})
        return result is not None

    def enable_campaign(self, campaign_id: int) -> bool:
        """Enable a campaign."""
        result = self.update_campaign(campaign_id, {"status": "ENABLED"})
        return result is not None

    def delete_campaign(self, campaign_id: int) -> bool:
        """Delete a campaign."""
        try:
            # Note: Apple API requires campaign to be paused before deletion
            self.pause_campaign(campaign_id)
            self._request("DELETE", f"/campaigns/{campaign_id}")
            return True
        except Exception as e:
            console.print(f"[red]Error deleting campaign {campaign_id}: {e}[/red]")
            return False

    # =========================================================================
    # Ad Group Operations
    # =========================================================================

    def get_ad_groups(self, campaign_id: int) -> list[dict[str, Any]]:
        """Get all ad groups for a campaign (handles pagination)."""
        try:
            return self._get_all_paginated(f"/campaigns/{campaign_id}/adgroups")
        except Exception as e:
            console.print(f"[red]Error fetching ad groups for campaign {campaign_id}: {e}[/red]")
            return []

    def create_ad_group(
        self,
        campaign_id: int,
        name: str,
        default_bid: float,
        search_match_enabled: bool = False,
        status: str = "ENABLED",
        cpa_goal: Optional[float] = None,
    ) -> Optional[dict[str, Any]]:
        """Create an ad group in a campaign."""
        try:
            # startTime must be ISO 8601 format
            from datetime import datetime, timezone

            start_time = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000")

            currency = self.get_org_currency()
            ad_group_data = {
                "name": name,
                "defaultBidAmount": {"amount": str(default_bid), "currency": currency},
                "automatedKeywordsOptIn": search_match_enabled,
                "pricingModel": "CPC",
                "startTime": start_time,
                "status": status,
            }

            # Exclude users who already have the app
            if self.app_config:
                ad_group_data["targetingDimensions"] = {
                    "appDownloaders": {
                        "excluded": [str(self.app_config.app_id)],
                    },
                    "deviceClass": {
                        "included": ["IPHONE", "IPAD"],
                    },
                }

            if cpa_goal:
                ad_group_data["cpaGoal"] = {"amount": str(cpa_goal), "currency": currency}

            response = self._request(
                "POST", f"/campaigns/{campaign_id}/adgroups", data=ad_group_data
            )
            return response.get("data") if isinstance(response, dict) else None
        except Exception as e:
            console.print(f"[red]Error creating ad group: {e}[/red]")
            return None

    def update_ad_group(
        self, campaign_id: int, ad_group_id: int, updates: dict[str, Any]
    ) -> Optional[dict[str, Any]]:
        """Update an ad group."""
        try:
            response = self._request(
                "PUT", f"/campaigns/{campaign_id}/adgroups/{ad_group_id}", data=updates
            )
            return response.get("data") if isinstance(response, dict) else None
        except Exception as e:
            console.print(f"[red]Error updating ad group {ad_group_id}: {e}[/red]")
            return None

    def delete_ad_group(self, campaign_id: int, ad_group_id: int) -> bool:
        """Delete an ad group."""
        try:
            self._request("DELETE", f"/campaigns/{campaign_id}/adgroups/{ad_group_id}")
            return True
        except Exception as e:
            console.print(f"[red]Error deleting ad group {ad_group_id}: {e}[/red]")
            return False

    # =========================================================================
    # Keyword Operations
    # =========================================================================

    def get_keywords(
        self, campaign_id: int, ad_group_id: int, include_deleted: bool = False
    ) -> list[dict[str, Any]]:
        """Get targeting keywords for an ad group (handles pagination).

        Args:
            campaign_id: Campaign ID
            ad_group_id: Ad group ID
            include_deleted: If False (default), filters out deleted keywords
        """
        try:
            keywords = self._get_all_paginated(
                f"/campaigns/{campaign_id}/adgroups/{ad_group_id}/targetingkeywords"
            )
            if not include_deleted:
                keywords = [kw for kw in keywords if not kw.get("deleted", False)]
            return keywords
        except Exception as e:
            console.print(f"[red]Error fetching keywords: {e}[/red]")
            return []

    def add_keywords(
        self,
        campaign_id: int,
        ad_group_id: int,
        keywords: list[str],
        match_type: MatchType,
        bid_amount: Optional[float] = None,
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        """Add targeting keywords to an ad group.

        Returns:
            Tuple of (added_keywords, errors) where errors contains any API error details.
        """
        if not keywords:
            return [], []

        default_bid = bid_amount or (self.app_config.default_bid if self.app_config else 1.50)

        currency = self.get_org_currency()
        keyword_objects = [
            {
                "text": kw.strip().lower(),
                "matchType": match_type.value,
                "bidAmount": {"amount": str(default_bid), "currency": currency},
            }
            for kw in keywords
            if kw.strip()
        ]

        try:
            response = self._request(
                "POST",
                f"/campaigns/{campaign_id}/adgroups/{ad_group_id}/targetingkeywords/bulk",
                data=keyword_objects,
            )
            added: list[dict[str, Any]] = []
            errors: list[dict[str, Any]] = []

            if isinstance(response, dict):
                data_obj = response.get("data")
                if isinstance(data_obj, list):
                    added = data_obj

                error_obj = response.get("error")
                if isinstance(error_obj, dict):
                    errors_obj = error_obj.get("errors")
                    if isinstance(errors_obj, list):
                        errors = errors_obj
            return added, errors
        except Exception as e:
            console.print(f"[red]Error adding keywords: {e}[/red]")
            return [], []

    def get_negative_keywords(self, campaign_id: int) -> list[dict[str, Any]]:
        """Get campaign-level negative keywords (handles pagination)."""
        try:
            return self._get_all_paginated(f"/campaigns/{campaign_id}/negativekeywords")
        except Exception as e:
            console.print(f"[red]Error fetching negative keywords: {e}[/red]")
            return []

    def add_negative_keywords(
        self, campaign_id: int, keywords: list[str], match_type: MatchType = MatchType.EXACT
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        """Add campaign-level negative keywords.

        Returns:
            Tuple of (added_keywords, errors) where errors contains any API error details.
        """
        if not keywords:
            return [], []

        keyword_objects = [
            {"text": kw.strip().lower(), "matchType": match_type.value}
            for kw in keywords
            if kw.strip()
        ]

        try:
            response = self._request(
                "POST",
                f"/campaigns/{campaign_id}/negativekeywords/bulk",
                data=keyword_objects,
            )
            added: list[dict[str, Any]] = []
            errors: list[dict[str, Any]] = []

            if isinstance(response, dict):
                data_obj = response.get("data")
                if isinstance(data_obj, list):
                    added = data_obj

                error_obj = response.get("error")
                if isinstance(error_obj, dict):
                    errors_obj = error_obj.get("errors")
                    if isinstance(errors_obj, list):
                        errors = errors_obj
            return added, errors
        except Exception as e:
            console.print(f"[red]Error adding negative keywords: {e}[/red]")
            return [], []

    def add_ad_group_negative_keywords(
        self, campaign_id: int, ad_group_id: int, keywords: list[str]
    ) -> list[dict[str, Any]]:
        """Add ad group-level negative keywords."""
        if not keywords:
            return []

        keyword_objects = [
            {"text": kw.strip().lower(), "matchType": "EXACT"} for kw in keywords if kw.strip()
        ]

        try:
            response = self._request(
                "POST",
                f"/campaigns/{campaign_id}/adgroups/{ad_group_id}/negativekeywords/bulk",
                data=keyword_objects,
            )
            return response.get("data", []) if isinstance(response, dict) else []
        except Exception as e:
            console.print(f"[red]Error adding ad group negative keywords: {e}[/red]")
            return []

    def delete_keywords(
        self, campaign_id: int, ad_group_id: int, keyword_ids: list[int]
    ) -> bool:
        """Delete targeting keywords from an ad group."""
        if not keyword_ids:
            return True

        try:
            # Use bulk delete endpoint - expects just a list of keyword IDs
            self._request(
                "POST",
                f"/campaigns/{campaign_id}/adgroups/{ad_group_id}/targetingkeywords/delete/bulk",
                data=keyword_ids,
            )
            return True
        except Exception as e:
            console.print(f"[red]Error deleting keywords: {e}[/red]")
            return False

    def update_keyword_bid(
        self, campaign_id: int, ad_group_id: int, keyword_id: int, bid_amount: float
    ) -> Optional[dict[str, Any]]:
        """Update bid amount for a keyword."""
        try:
            # Use bulk update endpoint with keyword object including ID
            currency = self.get_org_currency()
            update_data = [
                {"id": keyword_id, "bidAmount": {"amount": str(bid_amount), "currency": currency}}
            ]
            response = self._request(
                "PUT",
                f"/campaigns/{campaign_id}/adgroups/{ad_group_id}/targetingkeywords/bulk",
                data=update_data,
            )
            return response.get("data") if isinstance(response, dict) else None
        except Exception as e:
            console.print(f"[red]Error updating keyword bid: {e}[/red]")
            return None

    def pause_keyword(self, campaign_id: int, ad_group_id: int, keyword_id: int) -> bool:
        """Pause a keyword."""
        try:
            # Use bulk update endpoint with keyword object including ID
            update_data = [{"id": keyword_id, "status": "PAUSED"}]
            response = self._request(
                "PUT",
                f"/campaigns/{campaign_id}/adgroups/{ad_group_id}/targetingkeywords/bulk",
                data=update_data,
            )
            return response is not None
        except Exception as e:
            console.print(f"[red]Error pausing keyword: {e}[/red]")
            return False

    def enable_keyword(self, campaign_id: int, ad_group_id: int, keyword_id: int) -> bool:
        """Enable a keyword."""
        try:
            # Use bulk update endpoint with keyword object including ID
            update_data = [{"id": keyword_id, "status": "ACTIVE"}]
            response = self._request(
                "PUT",
                f"/campaigns/{campaign_id}/adgroups/{ad_group_id}/targetingkeywords/bulk",
                data=update_data,
            )
            return response is not None
        except Exception as e:
            console.print(f"[red]Error enabling keyword: {e}[/red]")
            return False

    # =========================================================================
    # Reporting Operations
    # =========================================================================

    def get_campaign_report(
        self,
        campaign_id: Optional[int] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        granularity: str = "DAILY",
    ) -> list[dict[str, Any]]:
        """Get campaign performance report.

        Uses the org-level endpoint /reports/campaigns.
        If campaign_id is provided, filters results to that campaign.
        """
        end = end_date or datetime.now()
        start = start_date or (end - timedelta(days=30))

        try:
            report_request = {
                "startTime": start.strftime("%Y-%m-%d"),
                "endTime": end.strftime("%Y-%m-%d"),
                "selector": {
                    "orderBy": [{"field": "localSpend", "sortOrder": "DESCENDING"}],
                    "pagination": {"offset": 0, "limit": 1000},
                },
                "timeZone": "UTC",
                "returnRecordsWithNoMetrics": True,
                "returnRowTotals": True,
                "returnGrandTotals": True,
            }
            if granularity != "DAILY":
                report_request["granularity"] = granularity

            # Use org-level endpoint
            response = self._request("POST", "/reports/campaigns", data=report_request)
            rows = response.get("data", {}).get("reportingDataResponse", {}).get("row", [])

            # Filter by campaign_id if provided
            if campaign_id and rows:
                rows = [r for r in rows if r.get("metadata", {}).get("campaignId") == campaign_id]

            return rows
        except Exception as e:
            console.print(f"[red]Error fetching campaign report: {e}[/red]")
            return []

    def get_keyword_report(
        self,
        campaign_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> list[dict[str, Any]]:
        """Get keyword performance report."""
        end = end_date or datetime.now()
        start = start_date or (end - timedelta(days=30))

        try:
            report_request = {
                "startTime": start.strftime("%Y-%m-%d"),
                "endTime": end.strftime("%Y-%m-%d"),
                "selector": {
                    "orderBy": [{"field": "localSpend", "sortOrder": "DESCENDING"}],
                    "pagination": {"offset": 0, "limit": 1000},
                },
                "timeZone": "UTC",
                "returnRecordsWithNoMetrics": False,
                "returnRowTotals": True,
            }

            response = self._request(
                "POST",
                f"/reports/campaigns/{campaign_id}/keywords",
                data=report_request,
            )
            return response.get("data", {}).get("reportingDataResponse", {}).get("row", [])
        except Exception as e:
            console.print(f"[red]Error fetching keyword report: {e}[/red]")
            return []

    def get_ad_group_report(
        self,
        campaign_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> list[dict[str, Any]]:
        """Get ad group performance report."""
        end = end_date or datetime.now()
        start = start_date or (end - timedelta(days=30))

        try:
            report_request = {
                "startTime": start.strftime("%Y-%m-%d"),
                "endTime": end.strftime("%Y-%m-%d"),
                "selector": {
                    "orderBy": [{"field": "localSpend", "sortOrder": "DESCENDING"}],
                    "pagination": {"offset": 0, "limit": 1000},
                },
                "timeZone": "UTC",
                "returnRecordsWithNoMetrics": True,
                "returnRowTotals": True,
            }

            response = self._request(
                "POST",
                f"/reports/campaigns/{campaign_id}/adgroups",
                data=report_request,
            )
            return response.get("data", {}).get("reportingDataResponse", {}).get("row", [])
        except Exception as e:
            console.print(f"[red]Error fetching ad group report: {e}[/red]")
            return []

    def get_search_terms_report(
        self,
        campaign_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> list[dict[str, Any]]:
        """Get search terms report.

        Note: Search terms reports require:
        - returnRecordsWithNoMetrics=false
        - timeZone="ORTZ" (Organization Relative Time Zone)
        """
        end = end_date or datetime.now()
        start = start_date or (end - timedelta(days=30))

        try:
            report_request = {
                "startTime": start.strftime("%Y-%m-%d"),
                "endTime": end.strftime("%Y-%m-%d"),
                "selector": {
                    "orderBy": [{"field": "localSpend", "sortOrder": "DESCENDING"}],
                    "pagination": {"offset": 0, "limit": 1000},
                },
                "timeZone": "ORTZ",  # Required for search terms
                "returnRecordsWithNoMetrics": False,  # Required for search terms
                "returnRowTotals": True,
            }

            response = self._request(
                "POST",
                f"/reports/campaigns/{campaign_id}/searchterms",
                data=report_request,
            )
            return response.get("data", {}).get("reportingDataResponse", {}).get("row", [])
        except Exception as e:
            console.print(f"[red]Error fetching search terms report: {e}[/red]")
            return []

    def get_impression_share_report(
        self,
        campaign_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> list[dict[str, Any]]:
        """Get impression share (Share of Voice) report for keywords.

        Includes metrics like searchTermImpressionShare which shows how often
        your ads appeared compared to total available impressions.
        """
        end = end_date or datetime.now()
        start = start_date or (end - timedelta(days=30))

        try:
            report_request = {
                "startTime": start.strftime("%Y-%m-%d"),
                "endTime": end.strftime("%Y-%m-%d"),
                "selector": {
                    "orderBy": [{"field": "impressions", "sortOrder": "DESCENDING"}],
                    "pagination": {"offset": 0, "limit": 1000},
                },
                "timeZone": "UTC",
                "returnRecordsWithNoMetrics": False,
                "returnRowTotals": True,
            }

            response = self._request(
                "POST",
                f"/reports/campaigns/{campaign_id}/keywords",
                data=report_request,
            )
            return response.get("data", {}).get("reportingDataResponse", {}).get("row", [])
        except Exception as e:
            console.print(f"[red]Error fetching impression share report: {e}[/red]")
            return []
