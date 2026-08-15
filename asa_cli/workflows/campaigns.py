"""Campaign planning and audit workflows built on Platform API v1."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
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
from .strategy import (
    RequestedStrategy,
    StrategyMode,
    detect_account_strategy,
    load_strategy_contract,
    resolve_requested_strategy,
)

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


def _check(
    check_id: str,
    state: str,
    message: str,
    evidence: Any = None,
) -> dict[str, Any]:
    return {"id": check_id, "state": state, "message": message, "evidence": evidence}


def _money_amount(value: Any) -> float | None:
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, dict):
        amount = value.get("amount")
        if isinstance(amount, (int, float, str)):
            try:
                return float(amount)
            except ValueError:
                return None
    return None


def _campaign_age_days(campaign: dict[str, Any], *, now: datetime | None = None) -> int | None:
    value = campaign.get("creationTime") or campaign.get("createdAt")
    if not isinstance(value, str):
        return None
    try:
        created_at = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if created_at.tzinfo is None:
        created_at = created_at.replace(tzinfo=UTC)
    return max(0, ((now or datetime.now(UTC)) - created_at).days)


def _manual_checks(
    campaigns: list[dict[str, Any]],
    *,
    app_name: str | None,
    evidence: dict[str, Any],
) -> tuple[list[dict[str, Any]], dict[str, list[dict[str, Any]]], list[dict[str, Any]]]:
    by_type: dict[CampaignType, list[dict[str, Any]]] = {
        campaign_type: [] for campaign_type in CampaignType
    }
    unclassified = []
    for campaign in campaigns:
        campaign_type = detect_campaign_type(str(campaign.get("name", "")), app_name=app_name)
        if campaign_type is None:
            unclassified.append(campaign)
        else:
            by_type[campaign_type].append(campaign)

    ad_groups = evidence.get("adGroups")
    if isinstance(ad_groups, list):
        for ad_group in ad_groups:
            if not isinstance(ad_group, dict):
                continue
            campaign_type = detect_campaign_type(str(ad_group.get("name", "")))
            if campaign_type is not None and not by_type[campaign_type]:
                by_type[campaign_type].append(
                    {
                        "id": ad_group.get("id"),
                        "name": ad_group.get("name"),
                        "status": ad_group.get("status"),
                        "source": "ad-group-evidence",
                    }
                )

    missing = [campaign_type.value for campaign_type, items in by_type.items() if not items]
    duplicates = {
        campaign_type.value: [item.get("id") for item in items]
        for campaign_type, items in by_type.items()
        if len(items) > 1
    }
    checks = [
        _check(
            "manual.theme-coverage",
            "fail" if missing else "pass",
            (
                f"Missing manual search-results themes: {', '.join(missing)}"
                if missing
                else "Brand, category, competitor, and discovery themes are represented."
            ),
            {"missing": missing, "duplicates": duplicates},
        )
    ]

    if isinstance(ad_groups, list):
        non_discovery = [
            item
            for item in ad_groups
            if isinstance(item, dict)
            and "discovery" not in str(item.get("name", "")).lower()
        ]
        not_exact = [
            item.get("id") or item.get("name")
            for item in non_discovery
            if str(item.get("matchType", "")).upper() != "EXACT"
        ]
        checks.append(
            _check(
                "manual.exact-match-isolation",
                "fail" if not_exact else "pass",
                (
                    "Non-discovery theme evidence includes non-exact matching."
                    if not_exact
                    else "Non-discovery theme evidence is isolated to exact matching."
                ),
                {"nonExact": not_exact},
            )
        )
        search_match_groups = [
            item.get("id") or item.get("name")
            for item in ad_groups
            if isinstance(item, dict)
            and detect_campaign_type(str(item.get("name", ""))) == CampaignType.DISCOVERY
            and item.get("searchMatch") is True
        ]
        checks.append(
            _check(
                "manual.search-match-discovery",
                "pass" if search_match_groups else "fail",
                (
                    "Search Match discovery evidence is present."
                    if search_match_groups
                    else "No Search Match discovery evidence was supplied."
                ),
                {"groups": search_match_groups},
            )
        )
    else:
        checks.extend(
            [
                _check(
                    "manual.exact-match-isolation",
                    "unverifiable",
                    "Ad-group match-type evidence was not supplied.",
                ),
                _check(
                    "manual.search-match-discovery",
                    "unverifiable",
                    "Ad-group Search Match evidence was not supplied.",
                ),
            ]
        )

    overlap = evidence.get("negativeKeywordOverlaps")
    overlap_count = evidence.get("negativeKeywordOverlapCount")
    if isinstance(overlap, list):
        overlap_count = len(overlap)
    if isinstance(overlap_count, int):
        checks.append(
            _check(
                "manual.negative-overlap-control",
                "pass" if overlap_count == 0 else "fail",
                (
                    "No negative-keyword overlap was reported."
                    if overlap_count == 0
                    else f"{overlap_count} negative-keyword overlaps were reported."
                ),
                {"overlapCount": overlap_count, "overlaps": overlap},
            )
        )
    else:
        checks.append(
            _check(
                "manual.negative-overlap-control",
                "unverifiable",
                "Negative-keyword overlap evidence was not supplied.",
            )
        )

    serialized_types = {
        campaign_type.value: [
            {
                "id": item.get("id"),
                "name": item.get("name"),
                "status": item.get("status"),
                "displayStatus": item.get("displayStatus"),
                "source": item.get("source", "campaign"),
            }
            for item in items
        ]
        for campaign_type, items in by_type.items()
    }
    return checks, serialized_types, unclassified


def _maximize_checks(
    campaigns: list[dict[str, Any]],
    *,
    evidence: dict[str, Any],
) -> list[dict[str, Any]]:
    checks = []
    eligibility = evidence.get("eligible")
    if isinstance(eligibility, bool):
        checks.append(
            _check(
                "maximize.eligibility",
                "pass" if eligibility else "fail",
                "Eligibility evidence is affirmative." if eligibility else "App is not eligible.",
                {"eligible": eligibility, "source": evidence.get("eligibilitySource")},
            )
        )
    else:
        checks.append(
            _check(
                "maximize.eligibility",
                "unverifiable",
                "Maximize Conversions eligibility evidence was not supplied.",
            )
        )

    target_cpa = _money_amount(evidence.get("targetCpa"))
    checks.append(
        _check(
            "maximize.target-cpa",
            "pass" if target_cpa is not None else "unverifiable",
            (
                "Target CPA evidence is present."
                if target_cpa is not None
                else "Target CPA evidence was not supplied."
            ),
            {"amount": target_cpa, "source": evidence.get("targetCpaSource")},
        )
    )
    budgets = [
        amount
        for campaign in campaigns
        if (amount := _money_amount(campaign.get("dailyBudget"))) is not None
    ]
    if target_cpa is not None and budgets:
        minimum = target_cpa * 5
        checks.append(
            _check(
                "maximize.daily-budget-capacity",
                "pass" if all(budget >= minimum for budget in budgets) else "fail",
                f"Daily budget is compared with the five-conversions target ({minimum:g}).",
                {"dailyBudgets": budgets, "recommendedMinimum": minimum},
            )
        )
    else:
        checks.append(
            _check(
                "maximize.daily-budget-capacity",
                "unverifiable",
                "Target CPA and campaign daily-budget evidence are both required.",
            )
        )

    ages = [age for campaign in campaigns if (age := _campaign_age_days(campaign)) is not None]
    if ages:
        checks.append(
            _check(
                "maximize.learning-period",
                "pass" if all(age >= 14 for age in ages) else "fail",
                "Campaign age is checked against Apple's two-week learning guidance.",
                {"campaignAgeDays": ages, "minimumDays": 14},
            )
        )
    else:
        checks.append(
            _check(
                "maximize.learning-period",
                "unverifiable",
                "Campaign creation-time evidence was not supplied by the API.",
            )
        )
    checks.append(
        _check(
            "maximize.search-match-automation",
            "pass",
            "Maximize Conversions uses automated bidding with Search Match; separate discovery groups are not required.",
            {"source": "strategy-contract-v1"},
        )
    )
    recommendations = evidence.get("targetCpaRecommendations") or evidence.get("recommendations")
    if recommendations is not None:
        result = recommendations.get("result") if isinstance(recommendations, dict) else None
        checks.append(
            _check(
                "maximize.recommendations",
                "pass",
                "Target-CPA recommendation evidence was supplied.",
                {"count": len(result) if isinstance(result, list) else None},
            )
        )
    else:
        checks.append(
            _check(
                "maximize.recommendations",
                "unverifiable",
                "Target-CPA recommendation evidence was not supplied.",
            )
        )
    return checks


def campaign_audit(
    campaigns: list[dict[str, Any]],
    *,
    requested_strategy: RequestedStrategy | str = RequestedStrategy.AUTO,
    evidence: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Audit only the checks applicable to the detected or selected strategy."""
    app_config = load_app_config()
    app_name = app_config.app_name if app_config else None
    app_id = str(app_config.app_id) if app_config else None
    scoped = [
        campaign
        for campaign in campaigns
        if app_id is None or str(campaign.get("promotedObjectId")) == app_id
    ]

    supplied_evidence = evidence or {}
    detection = detect_account_strategy(scoped)
    requested_value = RequestedStrategy(requested_strategy)
    evaluated_strategy = resolve_requested_strategy(requested_value, detection["strategy"])
    explicit_conflict = (
        requested_value != RequestedStrategy.AUTO
        and detection["confidence"] in {"high", "medium"}
        and detection["strategy"] != evaluated_strategy
    )
    warnings = []
    if explicit_conflict:
        warnings.append(
            "The requested strategy conflicts with API evidence; cross-strategy checks were skipped."
        )
    elif requested_value != RequestedStrategy.AUTO and detection["strategy"] != evaluated_strategy:
        warnings.append("Low-confidence auto-detection was replaced by the requested strategy.")

    checks: list[dict[str, Any]] = []
    serialized_types = {campaign_type.value: [] for campaign_type in CampaignType}
    unclassified: list[dict[str, Any]] = []
    applicable = not explicit_conflict
    applicability_reason = "Strategy-specific checks are applicable to the scoped campaigns."
    if explicit_conflict:
        applicability_reason = "Requested strategy conflicts with reliable API strategy evidence."
    elif evaluated_strategy == StrategyMode.MANUAL_SEARCH_RESULTS.value:
        checks, serialized_types, unclassified = _manual_checks(
            scoped,
            app_name=app_name,
            evidence=supplied_evidence,
        )
    elif evaluated_strategy == StrategyMode.MAXIMIZE_CONVERSIONS.value:
        checks = _maximize_checks(scoped, evidence=supplied_evidence)
    else:
        applicable = False
        applicability_reason = (
            "Search-results structure checks are not applicable to this placement or evidence set."
        )
        checks.append(
            _check(
                "placement.applicability",
                "unverifiable" if not scoped else "pass",
                applicability_reason,
                detection,
            )
        )

    manual_applies = (
        applicable and evaluated_strategy == StrategyMode.MANUAL_SEARCH_RESULTS.value
    )
    missing = (
        [
            campaign_type.value
            for campaign_type in CampaignType
            if not serialized_types[campaign_type.value]
        ]
        if manual_applies
        else []
    )
    duplicates = (
        {
            campaign_type: [item.get("id") for item in items]
            for campaign_type, items in serialized_types.items()
            if len(items) > 1
        }
        if manual_applies
        else {}
    )
    unverifiable = [check["id"] for check in checks if check["state"] == "unverifiable"]
    failures = [check["id"] for check in checks if check["state"] == "fail"]
    return {
        "workflow": "campaign-structure-audit",
        "transport": "apple-ads-platform-sdk",
        "contractVersion": load_strategy_contract()["contractVersion"],
        "app": (
            {"name": app_config.app_name, "adamId": app_config.app_id}
            if app_config
            else None
        ),
        "campaignCount": len(scoped),
        "detectedStrategy": detection["strategy"],
        "requestedStrategy": requested_value.value,
        "evaluatedStrategy": evaluated_strategy,
        "detectionEvidence": detection,
        "applicability": {"applicable": applicable, "reason": applicability_reason},
        "checks": checks,
        "warnings": warnings,
        "unverifiable": unverifiable,
        "types": serialized_types,
        "missing": missing,
        "duplicates": duplicates,
        "unclassified": [
            {"id": item.get("id"), "name": item.get("name")} for item in unclassified
        ],
        "healthy": applicable and not failures,
        "fullyVerified": applicable and not failures and not unverifiable,
    }


def _read_evidence(path: Path | None) -> dict[str, Any]:
    if path is None:
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"Could not read evidence JSON: {exc}") from exc
    if not isinstance(payload, dict):
        raise ValueError("Evidence JSON must be an object")
    return payload


@app.command("audit")
def audit(
    ad_account_id: str | None = typer.Option(
        None,
        "--ad-account",
        envvar="ASA_AD_ACCOUNT_ID",
        help="Apple Ads Platform ad account ID",
    ),
    page_size: int = typer.Option(100, "--page-size", min=1, help="Campaigns per SDK query"),
    strategy: RequestedStrategy = typer.Option(
        RequestedStrategy.AUTO,
        "--strategy",
        help="Audit auto-detected, manual search-results, or Maximize Conversions rules",
    ),
    evidence_file: Path | None = typer.Option(
        None,
        "--evidence-file",
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        resolve_path=True,
        help="Optional JSON evidence for ad groups, negatives, eligibility, or target CPA",
    ),
) -> None:
    """Read and audit campaign strategy without changing live state."""
    try:
        campaigns = query_all_campaigns(
            ad_account_id=ad_account_id,
            page_size=page_size,
        )
        result = campaign_audit(
            campaigns,
            requested_strategy=strategy,
            evidence=_read_evidence(evidence_file),
        )
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
    grouping: str = typer.Option(
        "separate-campaigns",
        "--grouping",
        help="Use separate-campaigns or themed-ad-groups for manual search-results themes",
    ),
    objective: str = typer.Option(
        "Manual search-results keyword control and learning",
        "--objective",
        help="Owner-supplied planning objective",
    ),
) -> None:
    """Plan manual search-results themes with no live writes."""
    if grouping not in {"separate-campaigns", "themed-ad-groups"}:
        typer.echo(
            json.dumps(
                {"error": {"message": "--grouping must be separate-campaigns or themed-ad-groups"}},
                indent=2,
            ),
            err=True,
        )
        raise typer.Exit(1)
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
                "dailyBudget": {
                    "amount": daily_budget or configuration.recommended_budget,
                    "approved": False,
                },
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

    if grouping == "themed-ad-groups":
        grouped_ad_groups = [
            {**ad_group, "theme": plan["type"]}
            for plan in plans
            for ad_group in plan["adGroups"]
        ]
        plans = [
            {
                "type": "manual-search-results",
                "name": f"{app_name} - Search Results",
                "description": "Manual search-results campaign with themed ad groups",
                "countriesOrRegions": resolved_countries,
                "dailyBudget": {
                    "amount": daily_budget or sum(
                        configuration.recommended_budget
                        for configuration in CAMPAIGN_STRUCTURE.values()
                    ),
                    "approved": False,
                },
                "adGroups": grouped_ad_groups,
            }
        ]

    typer.echo(
        json.dumps(
            {
                "workflow": "four-campaign-plan",
                "dryRun": True,
                "mutationAvailable": False,
                "contractVersion": load_strategy_contract()["contractVersion"],
                "strategy": StrategyMode.MANUAL_SEARCH_RESULTS.value,
                "placement": "APPSTORE_SEARCH_RESULTS",
                "grouping": grouping,
                "groupingRationale": (
                    "Separate campaigns preserve independent budgets and reporting."
                    if grouping == "separate-campaigns"
                    else "Themed ad groups consolidate country and budget control in one campaign."
                ),
                "objective": objective,
                "countriesOrRegions": resolved_countries,
                "intent": {
                    "exactMatch": "Isolate known brand, category, and competitor demand.",
                    "searchMatch": "Use discovery inventory to find new search terms.",
                    "negativeKeywords": "Prevent discovered exact terms and theme overlap from competing.",
                },
                "campaigns": plans,
            },
            indent=2,
            sort_keys=True,
        )
    )


def _find_first(payload: Any, keys: set[str]) -> Any:
    if isinstance(payload, dict):
        for key, value in payload.items():
            if key in keys and value is not None:
                return value
        for value in payload.values():
            found = _find_first(value, keys)
            if found is not None:
                return found
    elif isinstance(payload, list):
        for value in payload:
            found = _find_first(value, keys)
            if found is not None:
                return found
    return None


def query_maximize_conversions_evidence(
    *,
    adam_id: str,
    ad_account_id: str,
) -> dict[str, Any]:
    """Collect optional read-only eligibility and recommendation evidence."""
    recommendation_request = hydrate_model(
        "RecommendationQueryRequest",
        {
            "filters": [
                {"field": "promotedObjectId", "operator": "EQUALS", "value": [adam_id]},
                {
                    "field": "promotedObjectType",
                    "operator": "EQUALS",
                    "value": ["APPSTORE_APP"],
                },
            ],
            "pagination": {"offset": 0, "pageSize": 100},
        },
    )
    eligibility_request = hydrate_model(
        "EligibilityQueryRequest",
        {
            "filters": [
                {"field": "promotedObjectId", "operator": "EQUALS", "value": adam_id}
            ],
            "pagination": {"offset": 0, "pageSize": 100, "fetchTotalCount": True},
        },
    )
    eligibility = invoke(
        "eligibilities_apps_query_post",
        arguments={"eligibility_query_request": eligibility_request},
        ad_account_id=ad_account_id,
    )
    suggestion = invoke(
        "query_target_cpa_suggestion",
        arguments={"recommendation_query_request": recommendation_request},
        ad_account_id=ad_account_id,
    )
    recommendations = invoke(
        "query_target_cpa_recommendations",
        arguments={"recommendation_query_request": recommendation_request},
        ad_account_id=ad_account_id,
    )
    return {
        "eligibility": eligibility,
        "targetCpaSuggestion": suggestion,
        "targetCpaRecommendations": recommendations,
    }


def maximize_conversions_plan(
    *,
    adam_id: str | None,
    countries: list[str],
    daily_budget: float,
    target_cpa: float | None,
    evidence: dict[str, Any] | None = None,
    pre_order: bool = False,
    campaign_created_at: str | None = None,
) -> dict[str, Any]:
    """Build a provenance-rich, no-write Maximize Conversions plan."""
    supplied = evidence or {}
    suggested_value = _find_first(
        supplied.get("targetCpaSuggestion", supplied),
        {"targetCpa", "suggestedTargetCpa", "targetCPA"},
    )
    resolved_target_cpa = target_cpa
    target_source = "user" if target_cpa is not None else None
    if resolved_target_cpa is None:
        resolved_target_cpa = _money_amount(suggested_value)
        if resolved_target_cpa is not None:
            target_source = "Apple suggestion or supplied evidence"

    eligible_value = _find_first(supplied.get("eligibility", supplied), {"eligible", "isEligible"})
    eligible = eligible_value if isinstance(eligible_value, bool) else None
    minimum_budget = resolved_target_cpa * 5 if resolved_target_cpa is not None else None
    created_campaign = {"creationTime": campaign_created_at} if campaign_created_at else {}
    age_days = _campaign_age_days(created_campaign) if campaign_created_at else None
    recommendation_items = supplied.get("targetCpaRecommendations")
    unresolved = []
    if resolved_target_cpa is None:
        unresolved.append("targetCpa")
    if eligible is None:
        unresolved.append("eligibility")
    budget_sufficient = (
        daily_budget >= minimum_budget if minimum_budget is not None else None
    )
    launch_blockers = [
        message
        for condition, message in (
            (pre_order, "app is in pre-order"),
            (eligible is not True, "Apple eligibility is not affirmative"),
            (resolved_target_cpa is None, "target CPA is unresolved"),
            (budget_sufficient is not True, "daily budget capacity is unresolved or insufficient"),
        )
        if condition
    ]

    return {
        "workflow": "maximize-conversions-plan",
        "contractVersion": load_strategy_contract()["contractVersion"],
        "dryRun": True,
        "mutationAvailable": False,
        "strategy": StrategyMode.MAXIMIZE_CONVERSIONS.value,
        "placement": "APPSTORE_SEARCH_RESULTS",
        "app": {"adamId": adam_id},
        "countriesOrRegions": countries,
        "targetCpa": {
            "amount": resolved_target_cpa,
            "source": target_source,
            "confidence": "high" if target_source == "user" else "medium" if target_source else "none",
            "approved": False,
        },
        "dailyBudget": {
            "amount": daily_budget,
            "approved": False,
            "recommendedMinimum": minimum_budget,
            "supportsFiveConversionsPerDay": budget_sufficient,
        },
        "eligibility": {
            "eligible": eligible,
            "source": "Apple live read or supplied evidence" if eligible is not None else None,
        },
        "learningPeriod": {
            "minimumDays": 14,
            "campaignAgeDays": age_days,
            "complete": age_days >= 14 if age_days is not None else None,
            "guidance": "Allow at least two weeks before judging or materially changing the strategy.",
        },
        "automation": {
            "searchMatch": True,
            "automaticBidding": True,
            "separateDiscoveryAdGroupRequired": False,
        },
        "launchGuard": {
            "preOrder": pre_order,
            "ready": not launch_blockers,
            "blockingReasons": launch_blockers,
            "message": (
                "Resolve every blocking reason before launch."
                if launch_blockers
                else "Eligibility, target CPA, and budget-capacity planning gates are satisfied."
            ),
        },
        "recommendationEvidencePresent": recommendation_items is not None,
        "unresolvedInputs": unresolved,
        "warnings": [
            message
            for condition, message in (
                (pre_order, "Do not launch Maximize Conversions while the app is in pre-order."),
                (
                    minimum_budget is not None and daily_budget < minimum_budget,
                    "Daily budget is below the five-conversions-per-day planning threshold.",
                ),
                (eligible is False, "Apple eligibility evidence is negative."),
            )
            if condition
        ],
        "provenance": {
            "strategy": "strategy-contract-v1",
            "liveOrSuppliedEvidenceKeys": sorted(supplied),
        },
    }


@app.command("plan-maximize-conversions")
def plan_maximize_conversions(
    daily_budget: float = typer.Option(
        ...,
        "--daily-budget",
        min=0.01,
        help="Proposed daily budget; retained as unapproved planning data",
    ),
    target_cpa: float | None = typer.Option(
        None,
        "--target-cpa",
        min=0.01,
        help="Owner-proposed target CPA; otherwise use Apple or evidence suggestion",
    ),
    adam_id: str | None = typer.Option(None, "--adam-id", help="App Store adam ID"),
    countries: str | None = typer.Option(
        None,
        "--countries",
        help="Comma-separated country or region codes; defaults to configured app countries",
    ),
    ad_account_id: str | None = typer.Option(
        None,
        "--ad-account",
        envvar="ASA_AD_ACCOUNT_ID",
        help="When supplied, collect read-only Apple eligibility and target-CPA evidence",
    ),
    evidence_file: Path | None = typer.Option(
        None,
        "--evidence-file",
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        resolve_path=True,
        help="Optional saved Apple eligibility, suggestion, or recommendation JSON",
    ),
    pre_order: bool = typer.Option(False, "--pre-order", help="Mark the app as pre-order"),
    campaign_created_at: str | None = typer.Option(
        None,
        "--campaign-created-at",
        help="ISO-8601 creation timestamp for the two-week learning guard",
    ),
) -> None:
    """Plan Maximize Conversions using optional safe live reads and no writes."""
    app_config = load_app_config()
    resolved_adam_id = adam_id or (str(app_config.app_id) if app_config else None)
    resolved_countries = (
        [country.strip().upper() for country in countries.split(",") if country.strip()]
        if countries
        else app_config.default_countries
        if app_config
        else ["US"]
    )
    try:
        evidence = _read_evidence(evidence_file)
        if ad_account_id:
            if resolved_adam_id is None:
                raise ValueError("--adam-id or a configured app is required for live reads")
            live_evidence = query_maximize_conversions_evidence(
                adam_id=resolved_adam_id,
                ad_account_id=ad_account_id,
            )
            evidence = {**evidence, **live_evidence}
        result = maximize_conversions_plan(
            adam_id=resolved_adam_id,
            countries=resolved_countries,
            daily_budget=daily_budget,
            target_cpa=target_cpa,
            evidence=evidence,
            pre_order=pre_order,
            campaign_created_at=campaign_created_at,
        )
    except (PlatformAPIError, ValueError) as exc:
        typer.echo(json.dumps({"error": {"message": str(exc)}}, indent=2), err=True)
        raise typer.Exit(1) from exc
    typer.echo(json.dumps(result, indent=2, sort_keys=True))
