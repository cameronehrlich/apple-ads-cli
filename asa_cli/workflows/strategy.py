"""Versioned campaign-strategy contract and evidence-based detection."""

from __future__ import annotations

import json
from enum import Enum
from importlib.resources import files
from typing import Any


class StrategyMode(str, Enum):
    """Campaign strategy modes supported by opinionated workflows."""

    MANUAL_SEARCH_RESULTS = "manual-search-results"
    MAXIMIZE_CONVERSIONS = "maximize-conversions"
    NON_SEARCH_OR_UNSUPPORTED = "non-search-or-unsupported"


class RequestedStrategy(str, Enum):
    """User-facing strategy selection for audits."""

    AUTO = "auto"
    MANUAL = "manual"
    MAXIMIZE_CONVERSIONS = "maximize-conversions"


SEARCH_RESULTS_PLACEMENTS = {
    "APPSTORE_SEARCH_RESULTS",
    "APP_STORE_SEARCH_RESULTS",
    "SEARCH_RESULTS",
}
NON_SEARCH_PLACEMENTS = {"SEARCH_TAB", "TODAY_TAB", "PRODUCT_PAGES", "MAPS"}


def load_strategy_contract() -> dict[str, Any]:
    """Load the packaged, versioned strategy contract."""
    contract_path = files("asa_cli.workflows").joinpath("strategy_contract_v1.json")
    return json.loads(contract_path.read_text(encoding="utf-8"))


def _nested(mapping: dict[str, Any], *paths: tuple[str, ...]) -> Any:
    for path in paths:
        value: Any = mapping
        for key in path:
            if not isinstance(value, dict) or key not in value:
                break
            value = value[key]
        else:
            return value
    return None


def _values(value: Any) -> list[str]:
    if isinstance(value, dict):
        value = value.get("include") or value.get("values")
    if value is None:
        return []
    if not isinstance(value, list):
        value = [value]
    return [str(item).upper() for item in value if item is not None]


def campaign_strategy_evidence(campaign: dict[str, Any]) -> dict[str, Any]:
    """Extract normalized placement, supply-source, and bid-strategy evidence."""
    placements = _values(
        _nested(
            campaign,
            ("targeting", "supplyPlacement"),
            ("targeting", "supply_placement"),
            ("supplyPlacement",),
        )
    )
    supply_sources = _values(
        _nested(
            campaign,
            ("targeting", "supplySource"),
            ("targeting", "supply_source"),
            ("supplySource",),
        )
    )
    bid_strategy_type = _nested(
        campaign,
        ("bidStrategy", "bidStrategyType"),
        ("bid_strategy", "bid_strategy_type"),
        ("bidStrategyType",),
    )
    return {
        "campaignId": campaign.get("id"),
        "placements": placements,
        "supplySources": supply_sources,
        "bidStrategyType": (
            str(getattr(bid_strategy_type, "value", bid_strategy_type)).upper()
            if bid_strategy_type is not None
            else None
        ),
        "themeNameHint": next(
            (
                theme
                for theme in ("brand", "category", "competitor", "discovery")
                if theme in str(campaign.get("name", "")).lower()
            ),
            None,
        ),
    }


def detect_campaign_strategy(campaign: dict[str, Any]) -> dict[str, Any]:
    """Detect one campaign's strategy using the contract's explicit precedence."""
    evidence = campaign_strategy_evidence(campaign)
    placements = set(evidence["placements"])
    supply_sources = set(evidence["supplySources"])
    bid_strategy_type = evidence["bidStrategyType"]

    if "MAPS" in supply_sources or placements.intersection(NON_SEARCH_PLACEMENTS):
        mode = StrategyMode.NON_SEARCH_OR_UNSUPPORTED
        confidence = "high"
        reason = "non-search placement or MAPS supply source"
    elif placements.intersection(SEARCH_RESULTS_PLACEMENTS) and bid_strategy_type == "MAX_CONVERSIONS":
        mode = StrategyMode.MAXIMIZE_CONVERSIONS
        confidence = "high"
        reason = "App Store search-results placement uses MAX_CONVERSIONS"
    elif placements.intersection(SEARCH_RESULTS_PLACEMENTS) and bid_strategy_type == "MANUAL_CPT":
        mode = StrategyMode.MANUAL_SEARCH_RESULTS
        confidence = "high"
        reason = "App Store search-results placement uses MANUAL_CPT"
    else:
        mode = StrategyMode.NON_SEARCH_OR_UNSUPPORTED
        confidence = "low"
        reason = (
            "bid strategy is present but search-results placement evidence is unavailable"
            if bid_strategy_type in {"MANUAL_CPT", "MAX_CONVERSIONS"}
            else "campaign name suggests a manual theme but cannot establish strategy alone"
            if evidence["themeNameHint"]
            else "strategy evidence is missing, mixed, or unsupported"
        )

    return {
        "strategy": mode.value,
        "confidence": confidence,
        "reason": reason,
        **evidence,
    }


def detect_account_strategy(campaigns: list[dict[str, Any]]) -> dict[str, Any]:
    """Detect a homogeneous account strategy and fail closed for mixed evidence."""
    campaign_evidence = [detect_campaign_strategy(campaign) for campaign in campaigns]
    strategies = {item["strategy"] for item in campaign_evidence}
    if len(strategies) == 1:
        strategy = next(iter(strategies))
        confidence = min(
            (item["confidence"] for item in campaign_evidence),
            key=("low", "medium", "high").index,
        )
        reason = "all scoped campaigns resolve to the same strategy"
    elif not strategies:
        strategy = StrategyMode.NON_SEARCH_OR_UNSUPPORTED.value
        confidence = "low"
        reason = "no scoped campaigns are available"
    else:
        strategy = StrategyMode.NON_SEARCH_OR_UNSUPPORTED.value
        confidence = "high"
        reason = "scoped campaigns use mixed strategies or placements"
    return {
        "strategy": strategy,
        "confidence": confidence,
        "reason": reason,
        "campaigns": campaign_evidence,
    }


def resolve_requested_strategy(
    requested: RequestedStrategy | str,
    detected: str,
) -> str:
    """Resolve an explicit audit selection without claiming auto-detection."""
    requested_value = RequestedStrategy(requested)
    if requested_value == RequestedStrategy.MANUAL:
        return StrategyMode.MANUAL_SEARCH_RESULTS.value
    if requested_value == RequestedStrategy.MAXIMIZE_CONVERSIONS:
        return StrategyMode.MAXIMIZE_CONVERSIONS.value
    return detected
