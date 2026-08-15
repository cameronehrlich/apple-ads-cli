"""Campaign planning and audit workflows built on Platform API v1."""

from __future__ import annotations

import json
from typing import Any

import typer

from ..config import (
    CAMPAIGN_STRUCTURE,
    CAMPAIGN_TYPE_NAMES,
    CampaignType,
    detect_campaign_type,
    load_app_config,
)
from ..platform.runtime import PlatformAPIError, hydrate_model, invoke

app = typer.Typer(help="Campaign structure planning and audit workflows.")


def query_all_campaigns(
    *,
    ad_account_id: str | None = None,
    page_size: int = 100,
) -> list[dict[str, Any]]:
    """Return a complete campaign result set using explicit SDK pagination."""
    if page_size < 1:
        raise ValueError("page_size must be at least 1")

    campaigns: list[dict[str, Any]] = []
    seen_pages: set[str] = set()
    offset = 0
    while True:
        if len(seen_pages) >= 10_000:
            raise PlatformAPIError("Campaign pagination exceeded the 10,000-page safety limit")
        request = hydrate_model(
            "QueryRequest",
            {
                "pagination": {
                    "offset": offset,
                    "pageSize": page_size,
                    "fetchTotalCount": True,
                }
            },
        )
        response = invoke(
            "campaigns_query_post",
            arguments={"query_request": request},
            ad_account_id=ad_account_id,
        )
        page = response.get("result") or []
        if not isinstance(page, list):
            raise PlatformAPIError("Campaign query returned a non-list result")
        page_fingerprint = json.dumps(page, sort_keys=True, separators=(",", ":"))
        if page and page_fingerprint in seen_pages:
            raise PlatformAPIError(
                "Campaign pagination repeated a page without making progress"
            )
        seen_pages.add(page_fingerprint)
        campaigns.extend(item for item in page if isinstance(item, dict))

        pagination = response.get("pagination") or {}
        total_count = pagination.get("totalCount")
        if not page:
            break
        if isinstance(total_count, int):
            if len(campaigns) >= total_count:
                break
        elif len(page) < page_size:
            break
        offset += len(page)

    return campaigns


def campaign_audit(campaigns: list[dict[str, Any]]) -> dict[str, Any]:
    """Classify campaigns against the retained four-campaign convention."""
    app_config = load_app_config()
    app_name = app_config.app_name if app_config else None
    app_id = str(app_config.app_id) if app_config else None
    scoped = [
        campaign
        for campaign in campaigns
        if app_id is None or str(campaign.get("promotedObjectId")) == app_id
    ]

    by_type: dict[CampaignType, list[dict[str, Any]]] = {
        campaign_type: [] for campaign_type in CampaignType
    }
    unclassified = []
    for campaign in scoped:
        campaign_type = detect_campaign_type(str(campaign.get("name", "")), app_name=app_name)
        if campaign_type is None:
            unclassified.append(campaign)
        else:
            by_type[campaign_type].append(campaign)

    missing = [campaign_type.value for campaign_type, items in by_type.items() if not items]
    duplicates = {
        campaign_type.value: [item.get("id") for item in items]
        for campaign_type, items in by_type.items()
        if len(items) > 1
    }
    return {
        "workflow": "campaign-structure-audit",
        "transport": "apple-ads-platform-sdk",
        "app": (
            {"name": app_config.app_name, "adamId": app_config.app_id}
            if app_config
            else None
        ),
        "campaignCount": len(scoped),
        "types": {
            campaign_type.value: [
                {
                    "id": item.get("id"),
                    "name": item.get("name"),
                    "status": item.get("status"),
                    "displayStatus": item.get("displayStatus"),
                }
                for item in items
            ]
            for campaign_type, items in by_type.items()
        },
        "missing": missing,
        "duplicates": duplicates,
        "unclassified": [
            {"id": item.get("id"), "name": item.get("name")} for item in unclassified
        ],
        "healthy": not missing and not duplicates,
    }


@app.command("audit")
def audit(
    ad_account_id: str | None = typer.Option(
        None,
        "--ad-account",
        envvar="ASA_AD_ACCOUNT_ID",
        help="Apple Ads Platform ad account ID",
    ),
    page_size: int = typer.Option(100, "--page-size", min=1, help="Campaigns per SDK query"),
) -> None:
    """Read and audit the complete campaign set without changing live state."""
    try:
        campaigns = query_all_campaigns(
            ad_account_id=ad_account_id,
            page_size=page_size,
        )
        result = campaign_audit(campaigns)
    except (PlatformAPIError, ValueError) as exc:
        typer.echo(json.dumps({"error": {"message": str(exc)}}, indent=2), err=True)
        raise typer.Exit(1) from exc

    typer.echo(json.dumps(result, indent=2, sort_keys=True))


@app.command("plan-four-structure")
def plan_four_structure(
    countries: str | None = typer.Option(
        None,
        "--countries",
        help="Comma-separated country or region codes; defaults to configured app countries",
    ),
    daily_budget: float | None = typer.Option(
        None,
        "--daily-budget",
        min=0.01,
        help="Planning value per campaign; no API mutation is sent",
    ),
) -> None:
    """Print a no-write four-campaign plan for owner review."""
    app_config = load_app_config()
    resolved_countries = (
        [country.strip().upper() for country in countries.split(",") if country.strip()]
        if countries
        else app_config.default_countries
        if app_config
        else ["US"]
    )
    app_name = app_config.app_name if app_config else "App"
    plans = []
    for campaign_type, configuration in CAMPAIGN_STRUCTURE.items():
        plans.append(
            {
                "type": campaign_type.value,
                "name": f"{app_name} - {CAMPAIGN_TYPE_NAMES[campaign_type]}",
                "description": configuration.description,
                "countriesOrRegions": resolved_countries,
                "dailyBudget": daily_budget or configuration.recommended_budget,
                "adGroups": [
                    {
                        "name": ad_group.name,
                        "matchType": ad_group.match_type.value if ad_group.match_type else None,
                        "searchMatch": ad_group.search_match_enabled,
                    }
                    for ad_group in configuration.ad_groups
                ],
            }
        )

    typer.echo(
        json.dumps(
            {
                "workflow": "four-campaign-plan",
                "dryRun": True,
                "mutationAvailable": False,
                "campaigns": plans,
            },
            indent=2,
            sort_keys=True,
        )
    )
