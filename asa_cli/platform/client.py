"""Construction and account-context handling for Apple's Platform API SDK."""

from __future__ import annotations

import json
import os
from collections.abc import Callable, Mapping
from types import MethodType
from typing import Any

from pydantic import ValidationError

from ..config import Credentials, load_credentials


class PlatformConfigurationError(RuntimeError):
    """Raised when Platform API credentials or account context are incomplete."""


_REPORTING_KEYWORD_RESPONSE_TYPES = frozenset(
    {"AppsKeywordReportResponse", "AppsSearchTermReportResponse"}
)
_IMPRESSION_SHARE_RESPONSE_TYPE = "ImpressionShareQueryResponse"


def _has_live_reporting_keyword_status(error: ValidationError) -> bool:
    """Match Apple's live ENABLED value that SDK 1.109.0 rejects in report metadata."""
    errors = error.errors()
    return bool(errors) and all(
        item.get("input") == "ENABLED" and tuple(item.get("loc", ()))[-1:] == ("status",)
        for item in errors
    )


def _has_live_impression_share_id(error: ValidationError) -> bool:
    """Match Apple's live integer Adam ID that SDK 1.109.0 declares as a string."""
    errors = error.errors()
    return bool(errors) and all(
        isinstance(item.get("input"), int)
        and tuple(item.get("loc", ()))[-1:] == ("promotedObjectId",)
        for item in errors
    )


def _is_confirmed_live_response_mismatch(
    response_type: Any,
    error: ValidationError,
) -> bool:
    if response_type in _REPORTING_KEYWORD_RESPONSE_TYPES:
        return _has_live_reporting_keyword_status(error)
    if response_type == _IMPRESSION_SHARE_RESPONSE_TYPE:
        return _has_live_impression_share_id(error)
    return False


def _deserialize_with_live_response_compatibility(
    original: Callable[..., Any],
    *,
    response_data: Any,
    response_types_map: Mapping[str, Any],
) -> Any:
    """Preserve raw JSON only for confirmed live response/SDK mismatches."""
    try:
        return original(
            response_data=response_data,
            response_types_map=response_types_map,
        )
    except ValidationError as exc:
        response_type = response_types_map.get(str(response_data.status))
        if not _is_confirmed_live_response_mismatch(response_type, exc):
            raise

        from apple_ads_platform.api_response import ApiResponse

        payload = json.loads(response_data.data.decode("utf-8"))
        return ApiResponse(
            status_code=response_data.status,
            data=payload,
            headers=response_data.headers,
            raw_data=response_data.data,
        )


def _install_sdk_response_compatibility(api: Any) -> Any:
    """Install narrowly scoped response handling without modifying generated SDK code."""
    api_client = api.api_client
    original = api_client.response_deserialize

    def response_deserialize(
        _client: Any,
        response_data: Any,
        response_types_map: Mapping[str, Any] | None = None,
    ) -> Any:
        return _deserialize_with_live_response_compatibility(
            original,
            response_data=response_data,
            response_types_map=response_types_map or {},
        )

    api_client.response_deserialize = MethodType(response_deserialize, api_client)
    return api


def _validate_ad_account_id(value: str) -> str:
    """Reject values that could alter the semicolon-delimited context header."""
    account_id = value.strip()
    if not account_id or any(character in account_id for character in (";", "=", "\r", "\n")):
        raise PlatformConfigurationError("Apple Ads ad account ID contains invalid characters")
    return account_id


def require_credentials(credentials: Credentials | None = None) -> Credentials:
    """Return configured credentials or raise a stable, actionable error."""
    resolved = credentials or load_credentials()
    if resolved is None:
        raise PlatformConfigurationError(
            "No Apple Ads credentials configured. Run 'asa config setup' first."
        )
    return resolved


def resolve_ad_account_id(
    credentials: Credentials | None = None,
    explicit: str | None = None,
) -> str:
    """Resolve a v1 ad account without falling back to the legacy v5 org ID."""
    account_id = explicit or os.environ.get("ASA_AD_ACCOUNT_ID")
    if account_id is None:
        account_id = require_credentials(credentials).ad_account_id
    if account_id is None or not str(account_id).strip():
        raise PlatformConfigurationError(
            "Apple Ads Platform API requires an ad account ID. Pass --ad-account, "
            "set ASA_AD_ACCOUNT_ID, or save ad_account_id in the credentials config."
        )
    return _validate_ad_account_id(str(account_id))


def resolve_optional_ad_account_id(
    credentials: Credentials | None = None,
    explicit: str | None = None,
) -> str | None:
    """Resolve optional context consistently without requiring an account value."""
    resolved = credentials or load_credentials()
    account_id = explicit or os.environ.get("ASA_AD_ACCOUNT_ID")
    if account_id is None and resolved is not None:
        account_id = resolved.ad_account_id
    return _validate_ad_account_id(str(account_id)) if account_id is not None else None


def context_header(
    credentials: Credentials | None = None,
    explicit_ad_account_id: str | None = None,
) -> str:
    """Return the SDK's required X-AP-Context value."""
    return f"adAccountId={resolve_ad_account_id(credentials, explicit_ad_account_id)};"


def build_platform_api(credentials: Credentials | None = None) -> Any:
    """Build the official SDK client using the existing Apple Ads key material."""
    resolved = require_credentials(credentials)

    try:
        from apple_ads_platform.builder import AppleAdsClientBuilder
    except ImportError as exc:  # pragma: no cover - package installation is a packaging gate
        raise PlatformConfigurationError(
            "Apple Ads Platform SDK is not installed. Install this project with "
            "Python 3.12 or newer."
        ) from exc

    try:
        api = AppleAdsClientBuilder.from_private_key_path(
            resolved.client_id,
            resolved.team_id,
            resolved.key_id,
            resolved.private_key_path,
        ).build()
        return _install_sdk_response_compatibility(api)
    except Exception as exc:
        raise PlatformConfigurationError(
            f"Unable to build the Apple Ads Platform SDK client: {exc}"
        ) from exc
