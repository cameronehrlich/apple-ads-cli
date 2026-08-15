"""Deterministic reporting helpers shared by human and machine output."""

# ruff: noqa: UP045 -- The package still supports Python 3.9.

from __future__ import annotations

import csv
import io
import re
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Any, Optional

SCHEMA_VERSION = 1


@dataclass(frozen=True)
class CompleteDateWindow:
    """An inclusive range containing completed calendar dates only."""

    start: date
    end: date

    @property
    def days(self) -> int:
        return (self.end - self.start).days + 1

    def as_datetimes(self) -> tuple[datetime, datetime]:
        return (
            datetime.combine(self.start, datetime.min.time()),
            datetime.combine(self.end, datetime.min.time()),
        )

    def as_dict(self, *, time_zone: str = "UTC") -> dict[str, Any]:
        return {
            "start_date": self.start.isoformat(),
            "end_date": self.end.isoformat(),
            "days": self.days,
            "time_zone": time_zone,
            "complete": True,
        }


def complete_date_window(
    days: int,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    *,
    today: Optional[date] = None,
) -> CompleteDateWindow:
    """Resolve an exact inclusive range ending no later than yesterday.

    ``days`` is used when ``start_date`` is omitted. An explicit start and end
    may describe any positive completed-date range.
    """
    if days < 1:
        raise ValueError("--days must be at least 1")

    current_date = today or date.today()
    latest_complete = current_date - timedelta(days=1)

    try:
        end = date.fromisoformat(end_date) if end_date else latest_complete
        start = date.fromisoformat(start_date) if start_date else end - timedelta(days=days - 1)
    except ValueError as exc:
        raise ValueError("Dates must use YYYY-MM-DD format") from exc

    if end > latest_complete:
        raise ValueError(
            f"End date must be a complete date on or before {latest_complete.isoformat()}"
        )
    if start > end:
        raise ValueError("Start date must be on or before end date")

    return CompleteDateWindow(start=start, end=end)


def machine_report(
    report_type: str,
    window: CompleteDateWindow,
    rows: list[dict[str, Any]],
    *,
    totals: Optional[dict[str, Any]] = None,
    inventory_complete: Optional[bool] = None,
    time_zone: str = "UTC",
    extra: Optional[dict[str, Any]] = None,
) -> dict[str, Any]:
    """Build the stable versioned JSON envelope used by integrations."""
    payload: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "report_type": report_type,
        "window": window.as_dict(time_zone=time_zone),
        "rows": rows,
    }
    if totals is not None:
        payload["totals"] = totals
    if inventory_complete is not None:
        payload["inventory_complete"] = inventory_complete
    if extra:
        payload.update(extra)
    return payload


def _money(value: Any) -> Optional[float]:
    if value is None:
        return None
    if isinstance(value, dict):
        value = value.get("amount")
    if value in (None, ""):
        return None
    return float(value)


def _first(mapping: dict[str, Any], *keys: str) -> Any:
    for key in keys:
        if key in mapping and mapping[key] is not None:
            return mapping[key]
    return None


def normalize_performance_row(
    row: dict[str, Any],
    *,
    kind: str,
    campaign: Optional[dict[str, Any]] = None,
    ad_group: Optional[dict[str, Any]] = None,
    inventory: Optional[dict[str, Any]] = None,
) -> dict[str, Any]:
    """Normalize Apple report rows without display strings or inferred data."""
    metadata = row.get("metadata", {})
    metrics = row.get("total", {})
    inventory = inventory or {}
    campaign = campaign or {}
    ad_group = ad_group or {}

    impressions = int(metrics.get("impressions") or 0)
    taps = int(metrics.get("taps") or 0)
    installs = int(metrics.get("totalInstalls") or metrics.get("tapInstalls") or 0)
    spend = _money(metrics.get("localSpend")) or 0.0
    avg_cpt = _money(_first(metrics, "avgCPT", "avgCpt"))
    if avg_cpt is None and taps:
        avg_cpt = spend / taps

    normalized: dict[str, Any] = {
        "campaign_id": _first(metadata, "campaignId") or campaign.get("id"),
        "campaign_name": _first(metadata, "campaignName") or campaign.get("name"),
        "ad_group_id": _first(metadata, "adGroupId") or ad_group.get("id"),
        "ad_group_name": _first(metadata, "adGroupName") or ad_group.get("name"),
        "impressions": impressions,
        "taps": taps,
        "installs": installs,
        "spend": spend,
        "avg_cpt": avg_cpt,
        "cpa": spend / installs if installs else None,
        "ttr": taps / impressions if impressions else None,
        "conversion_rate": installs / taps if taps else None,
    }

    if kind == "keyword":
        normalized.update(
            {
                "keyword_id": _first(metadata, "keywordId") or inventory.get("id"),
                "keyword": _first(metadata, "keyword", "keywordText")
                or inventory.get("text"),
                "match_type": _first(metadata, "matchType") or inventory.get("matchType"),
                "status": _first(metadata, "keywordStatus") or inventory.get("status"),
                "bid": _money(_first(metadata, "bidAmount"))
                or _money(inventory.get("bidAmount")),
            }
        )
    elif kind == "search_term":
        normalized.update(
            {
                "search_term": _first(metadata, "searchTermText", "keyword"),
                "source": _first(metadata, "searchTermSource"),
                "keyword_id": _first(metadata, "keywordId"),
                "keyword": _first(metadata, "keyword", "keywordText"),
                "match_type": _first(metadata, "matchType"),
            }
        )
    elif kind == "ad":
        normalized.update(
            {
                "ad_id": _first(metadata, "adId"),
                "ad_name": _first(metadata, "adName"),
                "status": _first(metadata, "adStatus"),
                "creative_id": _first(metadata, "creativeId"),
            }
        )
    elif kind == "campaign":
        normalized.update(
            {
                "campaign_id": _first(metadata, "campaignId") or campaign.get("id"),
                "campaign_name": _first(metadata, "campaignName") or campaign.get("name"),
                "status": campaign.get("displayStatus") or campaign.get("status"),
            }
        )

    return normalized


def performance_totals(rows: Iterable[dict[str, Any]]) -> dict[str, Any]:
    materialized = list(rows)
    impressions = sum(int(row.get("impressions") or 0) for row in materialized)
    taps = sum(int(row.get("taps") or 0) for row in materialized)
    installs = sum(int(row.get("installs") or 0) for row in materialized)
    spend = sum(float(row.get("spend") or 0) for row in materialized)
    return {
        "impressions": impressions,
        "taps": taps,
        "installs": installs,
        "spend": spend,
        "avg_cpt": spend / taps if taps else None,
        "cpa": spend / installs if installs else None,
        "ttr": taps / impressions if impressions else None,
        "conversion_rate": installs / taps if taps else None,
    }


def _header_key(value: str) -> str:
    return re.sub(r"[^a-z0-9]", "", value.lower())


def parse_impression_share_csv(content: str) -> list[dict[str, Any]]:
    """Parse Apple's downloaded custom-report CSV into stable typed fields."""
    reader = csv.DictReader(io.StringIO(content.lstrip("\ufeff")))
    if not reader.fieldnames:
        raise ValueError("Impression share download did not contain a CSV header")

    aliases = {
        "date": "date",
        "appname": "app_name",
        "adamid": "adam_id",
        "countryorregion": "country_or_region",
        "country": "country_or_region",
        "searchterm": "search_term",
        "lowimpressionshare": "low_impression_share",
        "highimpressionshare": "high_impression_share",
        "rank": "rank",
        "searchpopularity": "search_popularity",
    }
    numeric_float = {"low_impression_share", "high_impression_share"}
    numeric_int = {"adam_id", "search_popularity"}
    rows: list[dict[str, Any]] = []

    for raw in reader:
        normalized: dict[str, Any] = {
            "date": None,
            "app_name": None,
            "adam_id": None,
            "country_or_region": None,
            "search_term": None,
            "low_impression_share": None,
            "high_impression_share": None,
            "rank": None,
            "search_popularity": None,
        }
        for source_key, raw_value in raw.items():
            target = aliases.get(_header_key(source_key or ""))
            if not target:
                continue
            value = raw_value.strip() if isinstance(raw_value, str) else raw_value
            if value in (None, ""):
                normalized[target] = None
            elif target in numeric_float:
                normalized[target] = float(value)
            elif target in numeric_int:
                normalized[target] = int(value)
            else:
                normalized[target] = value
        rows.append(normalized)

    return sorted(
        rows,
        key=lambda row: (
            row.get("date") or "",
            row.get("country_or_region") or "",
            row.get("search_term") or "",
            row.get("adam_id") or 0,
        ),
    )
