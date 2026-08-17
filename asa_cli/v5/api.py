"""Direct client for Apple Ads Campaign Management API v5 using JWT OAuth."""

import time
from datetime import datetime, timedelta
from typing import Any, Optional

import jwt
import requests
from rich.console import Console

from ..config import AppConfig, Credentials, MatchType, get_current_app_config, load_credentials

console = Console()

# Apple OAuth endpoints
TOKEN_URL = "https://appleid.apple.com/auth/oauth2/token"
API_BASE_URL = "https://api.searchads.apple.com/api/v5"
REQUEST_TIMEOUT = (10, 30)
REPORTING_TIME_ZONE = "ORTZ"
REPORT_PAGE_SIZE = 1000


def _complete_report_range(
    start_date: Optional[datetime],
    end_date: Optional[datetime],
    *,
    days: int = 30,
    now: Optional[datetime] = None,
) -> tuple[datetime, datetime]:
    """Resolve default report dates to an inclusive completed-day window."""
    reference = now or datetime.now()
    default_end = (reference - timedelta(days=1)).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    end = end_date or default_end
    start = start_date or (end - timedelta(days=days - 1))
    return start, end


class SearchAdsAPIError(RuntimeError):
    """Raised when an Apple Ads request fails without returning valid data."""


class ReportRows(list[dict[str, Any]]):
    """Report rows with additive completeness and Apple-total metadata.

    This remains a ``list`` for compatibility with existing v5 callers while
    allowing reporting commands to distinguish complete API results from a
    filtered or truncated display selection.
    """

    def __init__(
        self,
        rows: list[dict[str, Any]],
        *,
        grand_totals: Optional[dict[str, Any]] = None,
        page_count: int = 1,
        total_results: Optional[int] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        time_zone: Optional[str] = None,
    ) -> None:
        super().__init__(rows)
        self.grand_totals = grand_totals
        self.page_count = page_count
        self.total_results = len(rows) if total_results is None else total_results
        self.api_pages_complete = True
        self.start_date = start_date
        self.end_date = end_date
        self.time_zone = time_zone


class SearchAdsClient:
    """Direct Apple Ads Campaign Management API v5 client with JWT authentication."""

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

        try:
            response = requests.post(TOKEN_URL, data=data, timeout=REQUEST_TIMEOUT)
        except requests.RequestException as exc:
            raise SearchAdsAPIError(f"Failed to reach Apple OAuth: {exc}") from exc

        if response.status_code != 200:
            raise SearchAdsAPIError(
                f"Failed to get access token: {response.status_code} - {response.text}"
            )

        try:
            token_data = response.json()
            self._access_token = token_data["access_token"]
        except (ValueError, KeyError) as exc:
            raise SearchAdsAPIError("Apple OAuth returned an invalid token response") from exc
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
        skip_org_context: bool = False,
    ) -> dict[str, Any]:
        """Make an authenticated API request with automatic retry on auth failure.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint path
            data: Request body data
            params: Query parameters
            _retry_count: Internal retry counter (do not set manually)
            skip_org_context: If True, omit the X-AP-Context header (for /acls, /me)

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
            "Content-Type": "application/json",
        }
        if not skip_org_context:
            headers["X-AP-Context"] = f"orgId={self.org_id}"

        try:
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                json=data,
                params=params,
                timeout=REQUEST_TIMEOUT,
            )
        except requests.RequestException as exc:
            raise SearchAdsAPIError(
                f"Apple Ads API request failed for {method} {endpoint}: {exc}"
            ) from exc

        # Handle auth failures with retry
        if response.status_code == 401 and _retry_count < max_retries:
            console.print(f"[yellow]Auth token expired, refreshing... (attempt {_retry_count + 1}/{max_retries})[/yellow]")
            # Clear cached token to force refresh
            self._access_token = None
            self._token_expiry = None
            # Retry the request
            return self._request(method, endpoint, data, params, _retry_count + 1, skip_org_context)

        if response.status_code >= 400:
            error_msg = f"API error {response.status_code}: {response.text}"
            console.print(f"[red]{error_msg}[/red]")
            raise SearchAdsAPIError(error_msg)

        if response.status_code == 204:  # No content
            return {}

        try:
            return response.json()
        except ValueError as exc:
            raise SearchAdsAPIError(
                f"Apple Ads API returned invalid JSON for {method} {endpoint}"
            ) from exc

    def _get_all_paginated(
        self, endpoint: str, params: Optional[dict] = None, limit: int = 1000
    ) -> list[dict[str, Any]]:
        """Fetch all results from a paginated endpoint.

        Apple Ads Campaign Management API v5 defaults to 20 items per page. This method fetches
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

    def _get_all_report_rows(
        self,
        endpoint: str,
        report_request: dict[str, Any],
    ) -> ReportRows:
        """Fetch every page of a v5 reporting endpoint or fail closed.

        Report pagination lives in the request selector and the response's
        top-level ``pagination`` object. Apple caps report pages at 1,000 rows.
        """
        rows: list[dict[str, Any]] = []
        request_data = {
            **report_request,
            "selector": {
                **report_request.get("selector", {}),
                "pagination": {
                    **report_request.get("selector", {}).get("pagination", {}),
                    "offset": 0,
                    "limit": REPORT_PAGE_SIZE,
                },
            },
        }
        offset = 0
        page_count = 0
        total_results: Optional[int] = None
        grand_totals: Optional[dict[str, Any]] = None

        while True:
            page_request = {
                **request_data,
                "selector": {
                    **request_data["selector"],
                    "pagination": {
                        **request_data["selector"]["pagination"],
                        "offset": offset,
                    },
                },
            }
            response = self._request("POST", endpoint, data=page_request)
            page_count += 1

            reporting = (
                response.get("data", {}).get("reportingDataResponse", {})
                if isinstance(response, dict)
                else {}
            )
            page_rows = reporting.get("row", [])
            if not isinstance(page_rows, list):
                raise SearchAdsAPIError(
                    f"Apple Ads returned invalid reporting rows for {endpoint}"
                )
            rows.extend(page_rows)

            if grand_totals is None:
                raw_grand_totals = reporting.get("grandTotals")
                if isinstance(raw_grand_totals, dict):
                    raw_metrics = raw_grand_totals.get("total")
                    if isinstance(raw_metrics, dict):
                        grand_totals = raw_metrics

            pagination = response.get("pagination") if isinstance(response, dict) else None
            if not isinstance(pagination, dict):
                if len(page_rows) >= REPORT_PAGE_SIZE:
                    raise SearchAdsAPIError(
                        f"Apple Ads omitted pagination for a full report page at {endpoint}; "
                        "coverage cannot be verified"
                    )
                total_results = len(rows)
                break

            required_pagination_fields = {"totalResults", "startIndex", "itemsPerPage"}
            if not required_pagination_fields.issubset(pagination):
                raise SearchAdsAPIError(
                    f"Apple Ads returned incomplete report pagination for {endpoint}; "
                    "coverage cannot be verified"
                )

            try:
                page_total_results = int(pagination["totalResults"])
                start_index = int(pagination["startIndex"])
                items_per_page = int(pagination["itemsPerPage"])
            except (TypeError, ValueError) as exc:
                raise SearchAdsAPIError(
                    f"Apple Ads returned invalid report pagination for {endpoint}"
                ) from exc

            if page_total_results < 0 or start_index != offset:
                raise SearchAdsAPIError(
                    f"Apple Ads returned inconsistent report pagination for {endpoint}"
                )
            if total_results is None:
                total_results = page_total_results
            elif page_total_results != total_results:
                raise SearchAdsAPIError(
                    f"Apple Ads changed report totalResults while paging {endpoint}"
                )

            next_offset = start_index + items_per_page
            if next_offset >= total_results or not page_rows:
                break
            if next_offset <= offset:
                raise SearchAdsAPIError(
                    f"Apple Ads report pagination did not advance for {endpoint}"
                )
            offset = next_offset

        if total_results is not None and len(rows) != total_results:
            raise SearchAdsAPIError(
                f"Apple Ads report returned {len(rows)} of {total_results} rows for {endpoint}"
            )
        return ReportRows(
            rows,
            grand_totals=grand_totals,
            page_count=page_count,
            total_results=total_results,
            start_date=report_request.get("startTime"),
            end_date=report_request.get("endTime"),
            time_zone=report_request.get("timeZone"),
        )

    @staticmethod
    def _report_request(
        start: datetime,
        end: datetime,
        *,
        order_field: str,
        time_zone: str = REPORTING_TIME_ZONE,
        return_records_with_no_metrics: bool,
        granularity: str = "DAILY",
    ) -> dict[str, Any]:
        """Build one consistent, comparable v5 report request."""
        normalized_time_zone = time_zone.upper()
        if normalized_time_zone not in {"ORTZ", "UTC"}:
            raise ValueError("Report time zone must be ORTZ or UTC")

        request: dict[str, Any] = {
            "startTime": start.strftime("%Y-%m-%d"),
            "endTime": end.strftime("%Y-%m-%d"),
            "selector": {
                "orderBy": [{"field": order_field, "sortOrder": "DESCENDING"}],
                "pagination": {"offset": 0, "limit": REPORT_PAGE_SIZE},
            },
            "timeZone": normalized_time_zone,
            "returnRecordsWithNoMetrics": return_records_with_no_metrics,
            "returnRowTotals": True,
            "returnGrandTotals": True,
        }
        if granularity != "DAILY":
            request["granularity"] = granularity
            request["returnRowTotals"] = False
            request["returnGrandTotals"] = False
        return request

    @property
    def org_id(self) -> int:
        """Get organization ID."""
        if self.credentials is None:
            raise ValueError("No credentials configured.")
        if self.credentials.org_id is None:
            raise ValueError(
                "Legacy API v5 requires an organization ID. Run 'asa config setup' "
                "and configure the optional v5 organization ID."
            )
        return self.credentials.org_id

    def get_org_currency(self) -> str:
        """Return the configured v5 organization's ISO currency code.

        Currency is resolved from the authoritative ACL record instead of a
        sample campaign, so new organizations with no campaigns are handled
        correctly. A missing or malformed value fails closed rather than
        allowing a write with an assumed currency.
        """
        if self._currency is not None:
            return self._currency

        target_org_id = self.org_id
        response = self._request("GET", "/acls", skip_org_context=True)
        acls = response.get("data") if isinstance(response, dict) else None
        if isinstance(acls, list):
            for acl in acls:
                if not isinstance(acl, dict) or str(acl.get("orgId")) != str(target_org_id):
                    continue
                currency = acl.get("currency")
                if isinstance(currency, str) and currency.strip():
                    self._currency = currency.strip().upper()
                    return self._currency

        raise SearchAdsAPIError(
            f"Apple Ads ACL did not return a currency for organization {target_org_id}"
        )

    # =========================================================================
    # Campaign Operations
    # =========================================================================

    def get_campaigns(self) -> list[dict[str, Any]]:
        """Get all campaigns for the organization (handles pagination)."""
        return self._get_all_paginated("/campaigns")

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
        budget: Optional[float] = None,
        countries: Optional[list[str]] = None,
        daily_budget: Optional[float] = None,
        status: str = "ENABLED",
        supply_sources: Optional[list[str]] = None,
        ad_channel_type: str = "SEARCH",
        billing_event: str = "TAPS",
    ) -> Optional[dict[str, Any]]:
        """Create a new campaign.

        ``budget`` is the lifetime / total budget. Apple is discontinuing
        lifetime budgets on 2026-06-16, so prefer leaving ``budget`` unset
        and relying on ``daily_budget`` alone. After 2026-06-16 Apple will
        reject campaigns with only a lifetime budget.
        """
        if self.app_config is None:
            raise ValueError("No app config. Run 'asa config setup' first.")
        if daily_budget is None and budget is None:
            raise ValueError("Either daily_budget or budget (lifetime) must be provided.")

        try:
            currency = self.get_org_currency()
            campaign_data: dict[str, Any] = {
                "name": name,
                "adamId": self.app_config.app_id,
                "dailyBudgetAmount": {"amount": str(daily_budget or budget), "currency": currency},
                "countriesOrRegions": countries or ["US"],
                "status": status,
                "supplySources": supply_sources or ["APPSTORE_SEARCH_RESULTS"],
                "adChannelType": ad_channel_type,
                "billingEvent": billing_event,
            }
            if budget is not None:
                campaign_data["budgetAmount"] = {"amount": str(budget), "currency": currency}

            response = self._request("POST", "/campaigns", data=campaign_data)
            return response.get("data") if isinstance(response, dict) else None
        except Exception as e:
            console.print(f"[red]Error creating campaign: {e}[/red]")
            return None

    def clone_campaign(
        self,
        source_campaign_id: int,
        new_name: Optional[str] = None,
        *,
        drop_lifetime_budget: bool = True,
        pause_source: bool = False,
    ) -> Optional[dict[str, Any]]:
        """Duplicate a campaign (with ad groups, keywords, negatives).

        Useful when a campaign is stuck in ``TOTAL_BUDGET_EXHAUSTED``
        because clearing the lifetime budget via PUT doesn't reset
        Apple's serving evaluator. Cloning produces a fresh campaign
        with no exhaustion history.

        Args:
            source_campaign_id: The campaign to duplicate.
            new_name: Defaults to "<source name> v2".
            drop_lifetime_budget: If True (default), the clone is
                created with dailyBudgetAmount only — the recommended
                state ahead of Apple's 2026-06-16 lifetime-budget
                removal.
            pause_source: If True, pauses the source campaign after a
                successful clone.

        Returns:
            A dict summarising the created campaign, ad groups, keyword
            counts, and negative counts.
        """
        from datetime import datetime, timedelta, timezone

        src = self._request("GET", f"/campaigns/{source_campaign_id}").get("data")
        if not src:
            console.print(f"[red]Source campaign {source_campaign_id} not found[/red]")
            return None
        src_ags = self._request("GET", f"/campaigns/{source_campaign_id}/adgroups").get("data", []) or []
        src_negs = self._request("GET", f"/campaigns/{source_campaign_id}/negativekeywords").get("data", []) or []

        new_payload: dict[str, Any] = {
            "name": new_name or f"{src['name']} v2",
            "adamId": src["adamId"],
            "dailyBudgetAmount": src["dailyBudgetAmount"],
            "countriesOrRegions": src["countriesOrRegions"],
            "status": "ENABLED",
            "supplySources": src["supplySources"],
            "adChannelType": src["adChannelType"],
            "billingEvent": src["billingEvent"],
        }
        if not drop_lifetime_budget and src.get("budgetAmount"):
            new_payload["budgetAmount"] = src["budgetAmount"]

        new_camp = self._request("POST", "/campaigns", data=new_payload).get("data")
        if not new_camp:
            return None
        new_id = new_camp["id"]

        # Ad groups + keywords
        start = (datetime.now(timezone.utc) + timedelta(minutes=5)).strftime("%Y-%m-%dT%H:%M:%S.000")
        ag_reports = []
        for src_ag in src_ags:
            ag_payload = {
                "name": src_ag["name"],
                "startTime": start,
                "defaultBidAmount": src_ag["defaultBidAmount"],
                "automatedKeywordsOptIn": src_ag.get("automatedKeywordsOptIn", False),
                "targetingDimensions": src_ag.get("targetingDimensions"),
                "pricingModel": src_ag["pricingModel"],
                "status": "ENABLED",
            }
            ag_payload = {k: v for k, v in ag_payload.items() if v is not None}
            new_ag = self._request("POST", f"/campaigns/{new_id}/adgroups", data=ag_payload).get("data")
            if not new_ag:
                continue

            src_kws = self._request("GET", f"/campaigns/{source_campaign_id}/adgroups/{src_ag['id']}/targetingkeywords").get("data", []) or []
            active_kws = [k for k in src_kws if k.get("status") == "ACTIVE"]
            kw_payload = [
                {"text": k["text"], "matchType": k["matchType"], "bidAmount": k["bidAmount"]}
                for k in active_kws
            ]
            if kw_payload:
                resp = self._request("POST", f"/campaigns/{new_id}/adgroups/{new_ag['id']}/targetingkeywords/bulk", data=kw_payload)
                created = len(resp.get("data") or [])
                errors = (resp.get("error") or {}).get("errors") or []
            else:
                created, errors = 0, []
            ag_reports.append({
                "old_id": src_ag["id"], "new_id": new_ag["id"], "name": src_ag["name"],
                "keywords_copied": created, "keywords_attempted": len(active_kws),
                "keyword_errors": errors,
            })

        # Campaign-level negatives
        neg_report = {"copied": 0, "attempted": 0, "errors": []}
        if src_negs:
            neg_payload = [{"text": n["text"], "matchType": n["matchType"]} for n in src_negs]
            resp = self._request("POST", f"/campaigns/{new_id}/negativekeywords/bulk", data=neg_payload)
            neg_report["copied"] = len(resp.get("data") or [])
            neg_report["attempted"] = len(src_negs)
            neg_report["errors"] = (resp.get("error") or {}).get("errors") or []

        if pause_source:
            self.update_campaign(source_campaign_id, {"status": "PAUSED"})

        return {
            "source_id": source_campaign_id,
            "new_id": new_id,
            "new_name": new_camp["name"],
            "ad_groups": ag_reports,
            "negatives": neg_report,
            "source_paused": pause_source,
        }

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
        return self._get_all_paginated(f"/campaigns/{campaign_id}/adgroups")

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
        keywords = self._get_all_paginated(
            f"/campaigns/{campaign_id}/adgroups/{ad_group_id}/targetingkeywords"
        )
        if not include_deleted:
            keywords = [kw for kw in keywords if not kw.get("deleted", False)]
        return keywords

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
                {
                    "id": keyword_id,
                    "bidAmount": {"amount": str(bid_amount), "currency": currency},
                }
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
    # Campaign Negative Keyword CRUD Operations
    # =========================================================================

    def find_campaign_negative_keywords(
        self, campaign_id: int, conditions: Optional[list[dict[str, Any]]] = None
    ) -> list[dict[str, Any]]:
        """Find campaign-level negative keywords using selector conditions.

        Args:
            campaign_id: Campaign ID
            conditions: Optional selector conditions for filtering

        Returns:
            List of matching negative keywords
        """
        try:
            selector: dict[str, Any] = {
                "pagination": {"offset": 0, "limit": 1000},
            }
            if conditions:
                selector["conditions"] = conditions

            data = {"selector": selector}
            response = self._request(
                "POST",
                f"/campaigns/{campaign_id}/negativekeywords/find",
                data=data,
            )
            return response.get("data", []) if isinstance(response, dict) else []
        except Exception as e:
            console.print(f"[red]Error finding campaign negative keywords: {e}[/red]")
            return []

    def update_campaign_negative_keywords(
        self, campaign_id: int, updates: list[dict[str, Any]]
    ) -> Optional[list[dict[str, Any]]]:
        """Update campaign-level negative keywords in bulk.

        Args:
            campaign_id: Campaign ID
            updates: List of update dicts, e.g. [{"id": 123, "status": "PAUSED"}, ...]

        Returns:
            List of updated keyword data, or None on failure
        """
        if not updates:
            return []

        try:
            response = self._request(
                "PUT",
                f"/campaigns/{campaign_id}/negativekeywords/bulk",
                data=updates,
            )
            return response.get("data") if isinstance(response, dict) else None
        except Exception as e:
            console.print(f"[red]Error updating campaign negative keywords: {e}[/red]")
            return None

    def delete_campaign_negative_keywords(
        self, campaign_id: int, keyword_ids: list[int]
    ) -> bool:
        """Delete campaign-level negative keywords in bulk.

        Args:
            campaign_id: Campaign ID
            keyword_ids: List of negative keyword IDs to delete

        Returns:
            True on success, False on failure
        """
        if not keyword_ids:
            return True

        try:
            self._request(
                "POST",
                f"/campaigns/{campaign_id}/negativekeywords/delete/bulk",
                data=keyword_ids,
            )
            return True
        except Exception as e:
            console.print(f"[red]Error deleting campaign negative keywords: {e}[/red]")
            return False

    # =========================================================================
    # Ad Group Negative Keyword CRUD Operations
    # =========================================================================

    def get_ad_group_negative_keywords(
        self, campaign_id: int, ad_group_id: int
    ) -> list[dict[str, Any]]:
        """Get ad group-level negative keywords (handles pagination).

        Args:
            campaign_id: Campaign ID
            ad_group_id: Ad group ID

        Returns:
            List of negative keywords
        """
        try:
            return self._get_all_paginated(
                f"/campaigns/{campaign_id}/adgroups/{ad_group_id}/negativekeywords"
            )
        except Exception as e:
            console.print(f"[red]Error fetching ad group negative keywords: {e}[/red]")
            return []

    def find_ad_group_negative_keywords(
        self, campaign_id: int, conditions: Optional[list[dict[str, Any]]] = None
    ) -> list[dict[str, Any]]:
        """Find ad group-level negative keywords across all ad groups using selector conditions.

        Args:
            campaign_id: Campaign ID
            conditions: Optional selector conditions for filtering

        Returns:
            List of matching negative keywords
        """
        try:
            selector: dict[str, Any] = {
                "pagination": {"offset": 0, "limit": 1000},
            }
            if conditions:
                selector["conditions"] = conditions

            data = {"selector": selector}
            response = self._request(
                "POST",
                f"/campaigns/{campaign_id}/adgroups/negativekeywords/find",
                data=data,
            )
            return response.get("data", []) if isinstance(response, dict) else []
        except Exception as e:
            console.print(f"[red]Error finding ad group negative keywords: {e}[/red]")
            return []

    def update_ad_group_negative_keywords(
        self, campaign_id: int, ad_group_id: int, updates: list[dict[str, Any]]
    ) -> Optional[list[dict[str, Any]]]:
        """Update ad group-level negative keywords in bulk.

        Args:
            campaign_id: Campaign ID
            ad_group_id: Ad group ID
            updates: List of update dicts, e.g. [{"id": 123, "status": "PAUSED"}, ...]

        Returns:
            List of updated keyword data, or None on failure
        """
        if not updates:
            return []

        try:
            response = self._request(
                "PUT",
                f"/campaigns/{campaign_id}/adgroups/{ad_group_id}/negativekeywords/bulk",
                data=updates,
            )
            return response.get("data") if isinstance(response, dict) else None
        except Exception as e:
            console.print(f"[red]Error updating ad group negative keywords: {e}[/red]")
            return None

    def delete_ad_group_negative_keywords(
        self, campaign_id: int, ad_group_id: int, keyword_ids: list[int]
    ) -> bool:
        """Delete ad group-level negative keywords in bulk.

        Args:
            campaign_id: Campaign ID
            ad_group_id: Ad group ID
            keyword_ids: List of negative keyword IDs to delete

        Returns:
            True on success, False on failure
        """
        if not keyword_ids:
            return True

        try:
            self._request(
                "POST",
                f"/campaigns/{campaign_id}/adgroups/{ad_group_id}/negativekeywords/delete/bulk",
                data=keyword_ids,
            )
            return True
        except Exception as e:
            console.print(f"[red]Error deleting ad group negative keywords: {e}[/red]")
            return False

    # =========================================================================
    # Bulk Targeting Keyword Operations
    # =========================================================================

    def update_keywords_bulk(
        self, campaign_id: int, ad_group_id: int, updates: list[dict[str, Any]]
    ) -> Optional[list[dict[str, Any]]]:
        """Update targeting keywords in bulk.

        Args:
            campaign_id: Campaign ID
            ad_group_id: Ad group ID
            updates: List of update dicts, e.g.
                [{"id": 123, "bidAmount": {"amount": "2.5", "currency": "USD"}}, ...]

        Returns:
            List of updated keyword data, or None on failure
        """
        if not updates:
            return []

        try:
            response = self._request(
                "PUT",
                f"/campaigns/{campaign_id}/adgroups/{ad_group_id}/targetingkeywords/bulk",
                data=updates,
            )
            return response.get("data") if isinstance(response, dict) else None
        except Exception as e:
            console.print(f"[red]Error updating keywords in bulk: {e}[/red]")
            return None

    def find_targeting_keywords(
        self, campaign_id: int, conditions: Optional[list[dict[str, Any]]] = None
    ) -> list[dict[str, Any]]:
        """Find targeting keywords across all ad groups using selector conditions.

        Args:
            campaign_id: Campaign ID
            conditions: Optional selector conditions for filtering

        Returns:
            List of matching targeting keywords
        """
        try:
            selector: dict[str, Any] = {
                "pagination": {"offset": 0, "limit": 1000},
            }
            if conditions:
                selector["conditions"] = conditions

            data = {"selector": selector}
            response = self._request(
                "POST",
                f"/campaigns/{campaign_id}/adgroups/targetingkeywords/find",
                data=data,
            )
            return response.get("data", []) if isinstance(response, dict) else []
        except Exception as e:
            console.print(f"[red]Error finding targeting keywords: {e}[/red]")
            return []

    # =========================================================================
    # Reporting Operations
    # =========================================================================

    def get_campaign_report(
        self,
        campaign_id: Optional[int] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        granularity: str = "DAILY",
        time_zone: str = REPORTING_TIME_ZONE,
    ) -> list[dict[str, Any]]:
        """Get campaign performance report.

        Uses the org-level endpoint /reports/campaigns.
        If campaign_id is provided, filters results to that campaign.
        """
        start, end = _complete_report_range(start_date, end_date)

        try:
            report_request = self._report_request(
                start,
                end,
                order_field="localSpend",
                time_zone=time_zone,
                return_records_with_no_metrics=True,
                granularity=granularity,
            )
            if campaign_id is not None:
                report_request["selector"]["conditions"] = [
                    {
                        "field": "campaignId",
                        "operator": "EQUALS",
                        "values": [str(campaign_id)],
                    }
                ]
            return self._get_all_report_rows("/reports/campaigns", report_request)
        except Exception as e:
            raise SearchAdsAPIError(f"Failed to fetch campaign report: {e}") from e

    def get_keyword_report(
        self,
        campaign_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        time_zone: str = REPORTING_TIME_ZONE,
    ) -> list[dict[str, Any]]:
        """Get keyword performance report."""
        start, end = _complete_report_range(start_date, end_date)

        try:
            report_request = self._report_request(
                start,
                end,
                order_field="localSpend",
                time_zone=time_zone,
                return_records_with_no_metrics=False,
            )
            return self._get_all_report_rows(
                f"/reports/campaigns/{campaign_id}/keywords", report_request
            )
        except Exception as e:
            raise SearchAdsAPIError(
                f"Failed to fetch keyword report for campaign {campaign_id}: {e}"
            ) from e

    def get_ad_group_report(
        self,
        campaign_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        time_zone: str = REPORTING_TIME_ZONE,
    ) -> list[dict[str, Any]]:
        """Get ad group performance report."""
        start, end = _complete_report_range(start_date, end_date)

        try:
            report_request = self._report_request(
                start,
                end,
                order_field="localSpend",
                time_zone=time_zone,
                return_records_with_no_metrics=True,
            )
            return self._get_all_report_rows(
                f"/reports/campaigns/{campaign_id}/adgroups", report_request
            )
        except Exception as exc:
            raise SearchAdsAPIError(
                f"Failed to fetch ad group report for campaign {campaign_id}: {exc}"
            ) from exc

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
        start, end = _complete_report_range(start_date, end_date)

        try:
            report_request = self._report_request(
                start,
                end,
                order_field="localSpend",
                return_records_with_no_metrics=False,
            )
            return self._get_all_report_rows(
                f"/reports/campaigns/{campaign_id}/searchterms", report_request
            )
        except Exception as e:
            raise SearchAdsAPIError(
                f"Failed to fetch search terms report for campaign {campaign_id}: {e}"
            ) from e

    def get_impression_share_report(
        self,
        campaign_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> list[dict[str, Any]]:
        """Reject the legacy keyword-performance proxy for impression share.

        True impression share is app/search-term/country data generated by the
        asynchronous ``/custom-reports`` API. Use ``create_custom_report``,
        ``get_custom_report``, and ``download_custom_report`` instead.
        """
        del campaign_id, start_date, end_date
        raise SearchAdsAPIError(
            "Keyword performance is not impression share; use the asynchronous "
            "custom-report methods or `asa reports impression-share`"
        )

    def get_keyword_recommendations(
        self,
        app_id: str,
        campaign_id: Optional[int] = None,
        ad_group_id: Optional[int] = None,
        keywords: Optional[list[str]] = None,
    ) -> list[dict[str, Any]]:
        """Get keyword recommendations with search popularity scores.

        Note: Apple's keyword recommendation endpoints may not be available
        in all API versions. The ASA web UI (searchads.apple.com) shows
        recommendations and search popularity that aren't exposed via API.
        """
        # TODO: Apple's recommendation endpoints return 404 on API v5.
        # The web dashboard at searchads.apple.com still shows recommendations.
        # This may require a different API version or undocumented endpoint.
        console.print(
            "[yellow]Keyword recommendations are not available via the ASA API v5.[/yellow]\n"
            "[yellow]Use the ASA web dashboard at searchads.apple.com for keyword suggestions[/yellow]\n"
            "[yellow]and search popularity scores, or use a third-party ASO tool.[/yellow]"
        )
        return []

    # =========================================================================
    # Geo Targeting Operations
    # =========================================================================

    def geo_search(
        self,
        query: str,
        entity: Optional[str] = None,
        country_code: str = "US",
        limit: int = 20,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        """Search for geo locations.

        Args:
            query: Search query string
            entity: Entity type filter (Country, AdminArea, Locality)
            country_code: Country code to search within
            limit: Maximum results to return
            offset: Pagination offset

        Returns:
            List of matching geo locations
        """
        params: dict[str, Any] = {
            "query": query,
            "countrycode": country_code,
            "limit": limit,
            "offset": offset,
        }
        if entity:
            params["entity"] = entity

        try:
            response = self._request("GET", "/search/geo", params=params)
            return response.get("data", []) if isinstance(response, dict) else []
        except Exception as e:
            console.print(f"[red]Error searching geo locations: {e}[/red]")
            return []

    def get_geo_locations(self, geo_requests: list[dict[str, str]]) -> list[dict[str, Any]]:
        """Look up specific geo locations by ID and entity.

        Args:
            geo_requests: List of dicts with 'id' and 'entity' keys,
                          e.g. [{"id": "US", "entity": "Country"}, ...]

        Returns:
            List of geo location details
        """
        try:
            response = self._request("POST", "/search/geo", data=geo_requests)
            return response.get("data", []) if isinstance(response, dict) else []
        except Exception as e:
            console.print(f"[red]Error fetching geo locations: {e}[/red]")
            return []

    def get_campaign_geo_targeting(self, campaign_id: int) -> list[str]:
        """Get geo targeting (countriesOrRegions) for a campaign.

        Args:
            campaign_id: Campaign ID

        Returns:
            List of country/region codes
        """
        campaign = self.get_campaign(campaign_id)
        if campaign:
            return campaign.get("countriesOrRegions", [])
        return []

    def update_campaign_countries(
        self, campaign_id: int, countries: list[str]
    ) -> Optional[dict[str, Any]]:
        """Update a campaign's country targeting.

        Sets countriesOrRegions and clearGeoTargetingOnCountryOrRegionChange
        to reset any sub-country geo targeting when countries change.

        Args:
            campaign_id: Campaign ID
            countries: List of country/region codes (e.g. ["US", "CA"])

        Returns:
            Updated campaign data or None on failure
        """
        updates = {
            "countriesOrRegions": countries,
            "clearGeoTargetingOnCountryOrRegionChange": True,
        }
        return self.update_campaign(campaign_id, updates)

    # =========================================================================
    # Budget Order Operations
    # =========================================================================

    def get_budget_orders(self) -> list[dict[str, Any]]:
        """Get all budget orders for the organization (handles pagination)."""
        try:
            return self._get_all_paginated("/budgetorders")
        except Exception as e:
            console.print(f"[red]Error fetching budget orders: {e}[/red]")
            return []

    def get_budget_order(self, bo_id: int) -> Optional[dict[str, Any]]:
        """Get a specific budget order by ID."""
        try:
            response = self._request("GET", f"/budgetorders/{bo_id}")
            return response.get("data") if isinstance(response, dict) else None
        except Exception as e:
            console.print(f"[red]Error fetching budget order {bo_id}: {e}[/red]")
            return None

    def create_budget_order(
        self,
        name: str,
        budget: float,
        start_date: str,
        end_date: str,
        **kwargs: Any,
    ) -> Optional[dict[str, Any]]:
        """Create a new budget order.

        Args:
            name: Budget order name
            budget: Budget amount in the organization's currency
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            **kwargs: Additional fields (e.g. clientName, primaryBuyerEmail)

        Returns:
            Created budget order data or None on failure
        """
        try:
            currency = self.get_org_currency()
            bo_data: dict[str, Any] = {
                "name": name,
                "budget": {"amount": str(budget), "currency": currency},
                "startDate": start_date,
                "endDate": end_date,
            }
            bo_data.update(kwargs)

            response = self._request("POST", "/budgetorders", data=bo_data)
            return response.get("data") if isinstance(response, dict) else None
        except Exception as e:
            console.print(f"[red]Error creating budget order: {e}[/red]")
            return None

    def update_budget_order(self, bo_id: int, updates: dict[str, Any]) -> Optional[dict[str, Any]]:
        """Update a budget order.

        Args:
            bo_id: Budget order ID
            updates: Fields to update

        Returns:
            Updated budget order data or None on failure
        """
        try:
            response = self._request("PUT", f"/budgetorders/{bo_id}", data=updates)
            return response.get("data") if isinstance(response, dict) else None
        except Exception as e:
            console.print(f"[red]Error updating budget order {bo_id}: {e}[/red]")
            return None

    def get_campaign_budget_status(self) -> list[dict[str, Any]]:
        """Get budget status for all campaigns, including spend data.

        Returns a list of dicts with campaign info and budget fields:
            id, name, budgetAmount, dailyBudgetAmount, status, displayStatus,
            totalSpend (from report data).
        """
        campaigns = self.get_campaigns()
        if not campaigns:
            return []

        # Fetch campaign reports for spend data
        report_rows = self.get_campaign_report()
        spend_by_campaign: dict[int, tuple[float, Optional[str]]] = {}
        for row in report_rows:
            cid = row.get("metadata", {}).get("campaignId")
            totals = row.get("total", {})
            spend_data = totals.get("localSpend", {})
            spend = float(spend_data.get("amount", 0))
            spend_currency = spend_data.get("currency")
            if cid:
                spend_by_campaign[cid] = (spend, spend_currency)

        report_window = {
            "startDate": getattr(report_rows, "start_date", None),
            "endDate": getattr(report_rows, "end_date", None),
            "timeZone": getattr(report_rows, "time_zone", REPORTING_TIME_ZONE),
            "complete": True,
            "apiPagesComplete": bool(
                getattr(report_rows, "api_pages_complete", True)
            ),
        }

        results: list[dict[str, Any]] = []
        for campaign in campaigns:
            cid = campaign.get("id")
            campaign_currency = (
                (campaign.get("dailyBudgetAmount") or {}).get("currency")
                or (campaign.get("budgetAmount") or {}).get("currency")
            )
            spend, spend_currency = spend_by_campaign.get(cid, (0.0, None))
            results.append({
                "id": cid,
                "name": campaign.get("name", ""),
                "budgetAmount": campaign.get("budgetAmount"),
                "dailyBudgetAmount": campaign.get("dailyBudgetAmount"),
                "status": campaign.get("status", "UNKNOWN"),
                "displayStatus": campaign.get("displayStatus", "UNKNOWN"),
                "servingStatus": campaign.get("servingStatus", "UNKNOWN"),
                "totalSpend": spend,
                "totalSpendCurrency": spend_currency or campaign_currency,
                "reportWindow": report_window,
            })

        return results

    # =========================================================================
    # ACL / User / App Search Operations
    # =========================================================================

    def get_acls(self) -> list[dict[str, Any]]:
        """Get access control list (organizations and roles).

        This endpoint does NOT require the X-AP-Context header.
        """
        try:
            response = self._request("GET", "/acls", skip_org_context=True)
            return response.get("data", []) if isinstance(response, dict) else []
        except Exception as e:
            console.print(f"[red]Error fetching ACLs: {e}[/red]")
            return []

    def get_me(self) -> Optional[dict[str, Any]]:
        """Get current user info.

        This endpoint does NOT require the X-AP-Context header.
        """
        try:
            response = self._request("GET", "/me", skip_org_context=True)
            return response.get("data") if isinstance(response, dict) else None
        except Exception as e:
            console.print(f"[red]Error fetching user info: {e}[/red]")
            return None

    def search_apps(
        self, query: str, return_owned: bool = True, limit: int = 50
    ) -> list[dict[str, Any]]:
        """Search for iOS apps on the App Store.

        Args:
            query: Search query string
            return_owned: If True, only return apps owned by the org
            limit: Maximum results to return

        Returns:
            List of matching app records
        """
        params = {
            "query": query,
            "returnOwnedApps": str(return_owned).lower(),
            "limit": limit,
        }
        try:
            response = self._request("GET", "/search/apps", params=params)
            return response.get("data", []) if isinstance(response, dict) else []
        except Exception as e:
            console.print(f"[red]Error searching apps: {e}[/red]")
            return []

    def get_app_eligibility(
        self, adam_id: int, conditions: Optional[list[str]] = None
    ) -> Optional[dict[str, Any]]:
        """Get advertising eligibility for an app.

        Args:
            adam_id: Apple App ID
            conditions: Optional list of eligibility conditions to check

        Returns:
            Eligibility data or None on failure
        """
        try:
            data = {}
            if conditions:
                data["conditions"] = conditions
            response = self._request(
                "POST", f"/apps/{adam_id}/eligibilities/find", data=data
            )
            return response.get("data") if isinstance(response, dict) else None
        except Exception as e:
            console.print(f"[red]Error fetching app eligibility for {adam_id}: {e}[/red]")
            return None

    def get_supported_countries(
        self, countries: Optional[list[str]] = None
    ) -> list[dict[str, Any]]:
        """Get supported countries/regions for advertising.

        Args:
            countries: Optional list of country codes to filter

        Returns:
            List of supported country/region records
        """
        params: dict[str, Any] = {}
        if countries:
            params["countriesOrRegions"] = ",".join(countries)
        try:
            response = self._request("GET", "/countries-or-regions", params=params)
            return response.get("data", []) if isinstance(response, dict) else []
        except Exception as e:
            console.print(f"[red]Error fetching supported countries: {e}[/red]")
            return []

    def get_app_preview_device_sizes(self) -> list[dict[str, Any]]:
        """Get creative app mapping device sizes for ad previews.

        Returns:
            List of device size records
        """
        try:
            response = self._request("GET", "/creativeappmappings/devices")
            return response.get("data", []) if isinstance(response, dict) else []
        except Exception as e:
            console.print(f"[red]Error fetching device sizes: {e}[/red]")
            return []

    # =========================================================================
    # Ad Operations
    # =========================================================================

    def get_ads(self, campaign_id: int, ad_group_id: int) -> list[dict[str, Any]]:
        """Get all ads for an ad group (handles pagination).

        Args:
            campaign_id: Campaign ID
            ad_group_id: Ad group ID

        Returns:
            List of ads
        """
        try:
            return self._get_all_paginated(
                f"/campaigns/{campaign_id}/adgroups/{ad_group_id}/ads"
            )
        except Exception as e:
            console.print(f"[red]Error fetching ads: {e}[/red]")
            return []

    def get_ad(
        self, campaign_id: int, ad_group_id: int, ad_id: int
    ) -> Optional[dict[str, Any]]:
        """Get a specific ad by ID.

        Args:
            campaign_id: Campaign ID
            ad_group_id: Ad group ID
            ad_id: Ad ID

        Returns:
            Ad data or None on failure
        """
        try:
            response = self._request(
                "GET",
                f"/campaigns/{campaign_id}/adgroups/{ad_group_id}/ads/{ad_id}",
            )
            return response.get("data") if isinstance(response, dict) else None
        except Exception as e:
            console.print(f"[red]Error fetching ad {ad_id}: {e}[/red]")
            return None

    def create_ad(
        self,
        campaign_id: int,
        ad_group_id: int,
        creative_id: int,
        name: str,
        status: str = "ENABLED",
    ) -> Optional[dict[str, Any]]:
        """Create an ad in an ad group.

        Args:
            campaign_id: Campaign ID
            ad_group_id: Ad group ID
            creative_id: Creative ID to associate with the ad
            name: Ad name
            status: Initial status (ENABLED or PAUSED)

        Returns:
            Created ad data or None on failure
        """
        try:
            ad_data = {
                "name": name,
                "creativeId": creative_id,
                "status": status,
            }
            response = self._request(
                "POST",
                f"/campaigns/{campaign_id}/adgroups/{ad_group_id}/ads",
                data=ad_data,
            )
            return response.get("data") if isinstance(response, dict) else None
        except Exception as e:
            console.print(f"[red]Error creating ad: {e}[/red]")
            return None

    def update_ad(
        self, campaign_id: int, ad_group_id: int, ad_id: int, updates: dict[str, Any]
    ) -> Optional[dict[str, Any]]:
        """Update an ad.

        Args:
            campaign_id: Campaign ID
            ad_group_id: Ad group ID
            ad_id: Ad ID
            updates: Fields to update

        Returns:
            Updated ad data or None on failure
        """
        try:
            response = self._request(
                "PUT",
                f"/campaigns/{campaign_id}/adgroups/{ad_group_id}/ads/{ad_id}",
                data=updates,
            )
            return response.get("data") if isinstance(response, dict) else None
        except Exception as e:
            console.print(f"[red]Error updating ad {ad_id}: {e}[/red]")
            return None

    def delete_ad(self, campaign_id: int, ad_group_id: int, ad_id: int) -> bool:
        """Delete an ad.

        Args:
            campaign_id: Campaign ID
            ad_group_id: Ad group ID
            ad_id: Ad ID

        Returns:
            True on success, False on failure
        """
        try:
            self._request(
                "DELETE",
                f"/campaigns/{campaign_id}/adgroups/{ad_group_id}/ads/{ad_id}",
            )
            return True
        except Exception as e:
            console.print(f"[red]Error deleting ad {ad_id}: {e}[/red]")
            return False

    def find_ads(
        self, campaign_id: Optional[int] = None, conditions: Optional[list[dict[str, Any]]] = None
    ) -> list[dict[str, Any]]:
        """Find ads using selector conditions.

        Args:
            campaign_id: Optional campaign ID to scope the search
            conditions: Optional selector conditions for filtering

        Returns:
            List of matching ads
        """
        try:
            selector: dict[str, Any] = {
                "pagination": {"offset": 0, "limit": 1000},
            }
            if conditions:
                selector["conditions"] = conditions

            data = {"selector": selector}

            if campaign_id:
                endpoint = f"/campaigns/{campaign_id}/ads/find"
            else:
                endpoint = "/ads/find"

            response = self._request("POST", endpoint, data=data)
            return response.get("data", []) if isinstance(response, dict) else []
        except Exception as e:
            console.print(f"[red]Error finding ads: {e}[/red]")
            return []

    # =========================================================================
    # Creative Operations
    # =========================================================================

    def get_creatives(self) -> list[dict[str, Any]]:
        """Get all creatives (handles pagination).

        Returns:
            List of creatives
        """
        try:
            return self._get_all_paginated("/creatives")
        except Exception as e:
            console.print(f"[red]Error fetching creatives: {e}[/red]")
            return []

    def get_creative(self, creative_id: int) -> Optional[dict[str, Any]]:
        """Get a specific creative by ID.

        Args:
            creative_id: Creative ID

        Returns:
            Creative data or None on failure
        """
        try:
            response = self._request("GET", f"/creatives/{creative_id}")
            return response.get("data") if isinstance(response, dict) else None
        except Exception as e:
            console.print(f"[red]Error fetching creative {creative_id}: {e}[/red]")
            return None

    def create_creative(
        self,
        adam_id: int,
        name: str,
        creative_type: str,
        product_page_id: Optional[str] = None,
    ) -> Optional[dict[str, Any]]:
        """Create a creative.

        Args:
            adam_id: App Adam ID
            name: Creative name
            creative_type: Type of creative (e.g., CUSTOM_PRODUCT_PAGE)
            product_page_id: Optional product page ID for custom product page creatives

        Returns:
            Created creative data or None on failure
        """
        try:
            creative_data: dict[str, Any] = {
                "adamId": adam_id,
                "name": name,
                "type": creative_type,
            }
            if product_page_id:
                creative_data["productPageId"] = product_page_id

            response = self._request("POST", "/creatives", data=creative_data)
            return response.get("data") if isinstance(response, dict) else None
        except Exception as e:
            console.print(f"[red]Error creating creative: {e}[/red]")
            return None

    def find_creatives(
        self, conditions: Optional[list[dict[str, Any]]] = None
    ) -> list[dict[str, Any]]:
        """Find creatives using selector conditions.

        Args:
            conditions: Optional selector conditions for filtering

        Returns:
            List of matching creatives
        """
        try:
            selector: dict[str, Any] = {
                "pagination": {"offset": 0, "limit": 1000},
            }
            if conditions:
                selector["conditions"] = conditions

            data = {"selector": selector}
            response = self._request("POST", "/creatives/find", data=data)
            return response.get("data", []) if isinstance(response, dict) else []
        except Exception as e:
            console.print(f"[red]Error finding creatives: {e}[/red]")
            return []

    # =========================================================================
    # Product Page Operations
    # =========================================================================

    def get_product_pages(self, adam_id: int) -> list[dict[str, Any]]:
        """Get custom product pages for an app.

        Args:
            adam_id: App Adam ID

        Returns:
            List of product pages
        """
        try:
            return self._get_all_paginated(f"/apps/{adam_id}/product-pages")
        except Exception as e:
            console.print(f"[red]Error fetching product pages: {e}[/red]")
            return []

    def get_product_page_locales(
        self, adam_id: int, product_page_id: str
    ) -> list[dict[str, Any]]:
        """Get locale details for a product page.

        Args:
            adam_id: App Adam ID
            product_page_id: Product page ID

        Returns:
            List of locale details
        """
        try:
            return self._get_all_paginated(
                f"/apps/{adam_id}/product-pages/{product_page_id}/locale-details"
            )
        except Exception as e:
            console.print(f"[red]Error fetching product page locales: {e}[/red]")
            return []

    # =========================================================================
    # Rejection Reasons & App Assets
    # =========================================================================

    def find_rejection_reasons(
        self, conditions: Optional[list[dict[str, Any]]] = None
    ) -> list[dict[str, Any]]:
        """Find product page rejection reasons.

        Args:
            conditions: Optional selector conditions for filtering

        Returns:
            List of rejection reasons
        """
        try:
            selector: dict[str, Any] = {
                "pagination": {"offset": 0, "limit": 1000},
            }
            if conditions:
                selector["conditions"] = conditions

            data = {"selector": selector}
            response = self._request("POST", "/product-page-reasons/find", data=data)
            return response.get("data", []) if isinstance(response, dict) else []
        except Exception as e:
            console.print(f"[red]Error finding rejection reasons: {e}[/red]")
            return []

    def find_app_assets(
        self, adam_id: int, conditions: Optional[list[dict[str, Any]]] = None
    ) -> list[dict[str, Any]]:
        """Find app assets (screenshots, previews, etc.).

        Args:
            adam_id: App Adam ID
            conditions: Optional selector conditions for filtering

        Returns:
            List of app assets
        """
        try:
            selector: dict[str, Any] = {
                "pagination": {"offset": 0, "limit": 1000},
            }
            if conditions:
                selector["conditions"] = conditions

            data = {"selector": selector}
            response = self._request(
                "POST", f"/apps/{adam_id}/assets/find", data=data
            )
            return response.get("data", []) if isinstance(response, dict) else []
        except Exception as e:
            console.print(f"[red]Error finding app assets: {e}[/red]")
            return []

    # =========================================================================
    # Custom / Impression Share Reports (Async)
    # =========================================================================

    def create_custom_report(
        self,
        name: str,
        start_time: str,
        end_time: str,
        granularity: str = "DAILY",
        conditions: Optional[list[dict[str, Any]]] = None,
    ) -> dict[str, Any]:
        """Create a custom (impression share) report (async).

        Max 10 per 24 hours, max 30-day date range.

        Args:
            name: Report name
            start_time: Start date (YYYY-MM-DD)
            end_time: End date (YYYY-MM-DD)
            granularity: DAILY, WEEKLY, or MONTHLY
            conditions: Optional selector conditions

        Returns:
            Report object with id, state (QUEUED), etc.

        Raises:
            SearchAdsAPIError: If Apple rejects the request or returns no data.
        """
        body: dict[str, Any] = {
            "name": name,
            "startTime": start_time,
            "endTime": end_time,
            "granularity": granularity,
        }
        if conditions:
            body["selector"] = {"conditions": conditions}

        try:
            response = self._request("POST", "/custom-reports", data=body)
            data = response.get("data") if isinstance(response, dict) else None
            if not isinstance(data, dict) or not data.get("id"):
                raise SearchAdsAPIError("Apple Ads returned no custom report ID")
            return data
        except SearchAdsAPIError:
            raise
        except Exception as exc:
            raise SearchAdsAPIError(f"Failed to create custom report: {exc}") from exc

    def get_custom_report(self, report_id: str) -> dict[str, Any]:
        """Get a custom report by ID.

        When state is COMPLETED, the response includes a downloadUri.

        Args:
            report_id: The custom report ID

        Returns:
            Report object.

        Raises:
            SearchAdsAPIError: If the report cannot be retrieved.
        """
        try:
            response = self._request("GET", f"/custom-reports/{report_id}")
            data = response.get("data") if isinstance(response, dict) else None
            if not isinstance(data, dict):
                raise SearchAdsAPIError(f"Apple Ads returned no custom report {report_id}")
            return data
        except SearchAdsAPIError:
            raise
        except Exception as exc:
            raise SearchAdsAPIError(
                f"Failed to fetch custom report {report_id}: {exc}"
            ) from exc

    def get_all_custom_reports(self, limit: Optional[int] = None) -> list[dict[str, Any]]:
        """Get all custom reports.

        Args:
            limit: Optional maximum total reports to return. Apple caps each
                request page at 50.

        Returns:
            List of custom report objects
        """
        try:
            if limit is not None and limit < 1:
                raise ValueError("Custom report limit must be at least 1")
            reports: list[dict[str, Any]] = []
            offset = 0
            total_results: Optional[int] = None

            while True:
                page_size = min(50, limit - len(reports)) if limit is not None else 50
                params = {"limit": page_size, "offset": offset}
                response = self._request("GET", "/custom-reports", params=params)
                data = response.get("data") if isinstance(response, dict) else None
                if not isinstance(data, list):
                    raise SearchAdsAPIError("Apple Ads returned invalid custom report data")
                reports.extend(data)

                if limit is not None and len(reports) >= limit:
                    return reports[:limit]
                pagination = response.get("pagination")
                if not isinstance(pagination, dict):
                    if len(data) >= page_size:
                        raise SearchAdsAPIError(
                            "Apple Ads omitted pagination for a full custom-report page"
                        )
                    return reports

                required_pagination_fields = {"totalResults", "startIndex", "itemsPerPage"}
                if not required_pagination_fields.issubset(pagination):
                    raise SearchAdsAPIError(
                        "Apple Ads returned incomplete custom-report pagination; "
                        "coverage cannot be verified"
                    )

                try:
                    page_total_results = int(pagination["totalResults"])
                    start_index = int(pagination["startIndex"])
                    items_per_page = int(pagination["itemsPerPage"])
                except (TypeError, ValueError) as exc:
                    raise SearchAdsAPIError(
                        "Apple Ads returned invalid custom-report pagination"
                    ) from exc
                if page_total_results < 0 or start_index != offset:
                    raise SearchAdsAPIError(
                        "Apple Ads returned inconsistent custom-report pagination"
                    )
                if total_results is None:
                    total_results = page_total_results
                elif page_total_results != total_results:
                    raise SearchAdsAPIError(
                        "Apple Ads changed custom-report totalResults while paging"
                    )
                next_offset = start_index + items_per_page
                if next_offset >= total_results or not data:
                    if len(reports) != total_results:
                        raise SearchAdsAPIError(
                            f"Apple Ads returned {len(reports)} of {total_results} "
                            "custom reports"
                        )
                    return reports
                if next_offset <= offset:
                    raise SearchAdsAPIError("Custom-report pagination did not advance")
                offset = next_offset
        except SearchAdsAPIError:
            raise
        except Exception as exc:
            raise SearchAdsAPIError(f"Failed to fetch custom reports: {exc}") from exc

    def download_custom_report(self, download_uri: str) -> str:
        """Download a completed custom report before its short-lived URL expires."""
        if not download_uri.startswith("https://"):
            raise SearchAdsAPIError("Custom report download URI must use HTTPS")
        try:
            response = requests.get(download_uri, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
        except requests.RequestException as exc:
            raise SearchAdsAPIError(f"Failed to download custom report: {exc}") from exc
        return response.content.decode("utf-8-sig")

    # =========================================================================
    # Ad-Level Reports
    # =========================================================================

    def get_ad_report(
        self,
        campaign_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        granularity: str = "DAILY",
        time_zone: str = REPORTING_TIME_ZONE,
    ) -> list[dict[str, Any]]:
        """Get ad-level performance report.

        NOTE: orderBy is REQUIRED in the selector for ad reports.

        Args:
            campaign_id: Campaign ID
            start_date: Report start date
            end_date: Report end date
            granularity: DAILY, WEEKLY, or MONTHLY

        Returns:
            List of report rows
        """
        start, end = _complete_report_range(start_date, end_date)

        try:
            report_request = self._report_request(
                start,
                end,
                order_field="impressions",
                time_zone=time_zone,
                return_records_with_no_metrics=False,
                granularity=granularity,
            )
            return self._get_all_report_rows(
                f"/reports/campaigns/{campaign_id}/ads", report_request
            )
        except Exception as exc:
            raise SearchAdsAPIError(
                f"Failed to fetch ad report for campaign {campaign_id}: {exc}"
            ) from exc

    # =========================================================================
    # Keyword within Ad Group Reports
    # =========================================================================

    def get_keyword_adgroup_report(
        self,
        campaign_id: int,
        ad_group_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        time_zone: str = REPORTING_TIME_ZONE,
    ) -> list[dict[str, Any]]:
        """Get keyword performance report within a specific ad group.

        Response includes insights.bidRecommendation.suggestedBidAmount for
        each keyword row.

        Args:
            campaign_id: Campaign ID
            ad_group_id: Ad group ID
            start_date: Report start date
            end_date: Report end date

        Returns:
            List of report rows (with insights containing bid recommendations)
        """
        start, end = _complete_report_range(start_date, end_date)

        try:
            report_request = self._report_request(
                start,
                end,
                order_field="impressions",
                time_zone=time_zone,
                return_records_with_no_metrics=False,
            )
            return self._get_all_report_rows(
                f"/reports/campaigns/{campaign_id}/adgroups/{ad_group_id}/keywords",
                report_request,
            )
        except Exception as e:
            raise SearchAdsAPIError(
                f"Failed to fetch keyword report for campaign {campaign_id} "
                f"ad group {ad_group_id}: {e}"
            ) from e

    # =========================================================================
    # Search Term within Ad Group Reports
    # =========================================================================

    def get_search_terms_adgroup_report(
        self,
        campaign_id: int,
        ad_group_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> list[dict[str, Any]]:
        """Get search terms report within a specific ad group.

        NOTE: timeZone must be "ORTZ" for search term reports.

        Args:
            campaign_id: Campaign ID
            ad_group_id: Ad group ID
            start_date: Report start date
            end_date: Report end date

        Returns:
            List of search term report rows
        """
        start, end = _complete_report_range(start_date, end_date)

        try:
            report_request = self._report_request(
                start,
                end,
                order_field="impressions",
                return_records_with_no_metrics=False,
            )
            return self._get_all_report_rows(
                f"/reports/campaigns/{campaign_id}/adgroups/{ad_group_id}/searchterms",
                report_request,
            )
        except Exception as exc:
            raise SearchAdsAPIError(
                f"Failed to fetch search terms for campaign {campaign_id} "
                f"ad group {ad_group_id}: {exc}"
            ) from exc
