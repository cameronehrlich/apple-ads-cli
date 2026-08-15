"""Construction and account-context handling for Apple's Platform API SDK."""

from __future__ import annotations

import json
import os
from collections.abc import Callable, Mapping
from copy import copy, deepcopy
from types import MethodType
from typing import Any

from pydantic import ValidationError

from ..config import Credentials, load_credentials


class PlatformConfigurationError(RuntimeError):
    """Raised when Platform API credentials or account context are incomplete."""


_IMPRESSION_SHARE_RESPONSE_TYPE = "ImpressionShareQueryResponse"


def _matches_row_validation_error(
    item: Mapping[str, Any],
    *,
    error_type: str,
    field_name: str,
    input_matches: Callable[[Any], bool],
) -> bool:
    """Match one SDK validation failure after nested from_dict location loss."""
    location = tuple(item.get("loc", ()))
    return (
        item.get("type") == error_type
        and location[-1:] == (field_name,)
        and input_matches(item.get("input"))
    )


def _has_live_reporting_keyword_status(
    error: ValidationError,
) -> bool:
    """Match Apple's live ENABLED keyword status rejected by SDK 1.109.0."""
    errors = error.errors()
    return bool(errors) and all(
        _matches_row_validation_error(
            item,
            error_type="value_error",
            field_name="status",
            input_matches=lambda value: value == "ENABLED",
        )
        for item in errors
    )


def _has_live_impression_share_id(error: ValidationError) -> bool:
    """Match Apple's live integer Adam ID that SDK 1.109.0 declares as a string."""
    errors = error.errors()
    return bool(errors) and all(
        _matches_row_validation_error(
            item,
            error_type="string_type",
            field_name="promotedObjectId",
            input_matches=lambda value: type(value) is int,
        )
        for item in errors
    )


def _is_confirmed_live_response_mismatch(
    response_type: Any,
    error: ValidationError,
) -> bool:
    if response_type == "AppsKeywordReportResponse":
        return _has_live_reporting_keyword_status(error)
    if response_type == "AppsSearchTermReportResponse":
        return _has_live_reporting_keyword_status(error)
    if response_type == _IMPRESSION_SHARE_RESPONSE_TYPE:
        return _has_live_impression_share_id(error)
    return False


def _patched_validation_payload(response_type: Any, payload: Any) -> Any | None:
    """Patch only confirmed wire mismatches in a copy used for SDK validation."""
    if not isinstance(payload, Mapping):
        return None
    result = payload.get("result")
    if not isinstance(result, Mapping) or not isinstance(result.get("rows"), list):
        return None

    patched = deepcopy(payload)
    rows = patched["result"]["rows"]
    replacements = 0
    for row in rows:
        if not isinstance(row, dict):
            continue
        if response_type == "AppsKeywordReportResponse":
            metadata = row.get("metadata")
            if isinstance(metadata, dict) and metadata.get("status") == "ENABLED":
                metadata["status"] = "ACTIVE"
                replacements += 1
        elif response_type == "AppsSearchTermReportResponse":
            metadata = row.get("metadata")
            keyword = metadata.get("keyword") if isinstance(metadata, dict) else None
            if isinstance(keyword, dict) and keyword.get("status") == "ENABLED":
                keyword["status"] = "ACTIVE"
                replacements += 1
        elif response_type == _IMPRESSION_SHARE_RESPONSE_TYPE:
            promoted_object_id = row.get("promotedObjectId")
            if type(promoted_object_id) is int:
                row["promotedObjectId"] = str(promoted_object_id)
                replacements += 1
    return patched if replacements else None


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
        validation_payload = _patched_validation_payload(response_type, payload)
        if validation_payload is None:
            raise
        validation_response = copy(response_data)
        validation_response.data = json.dumps(validation_payload).encode("utf-8")
        # A known mismatch may be the first error raised by generated nested
        # from_dict calls. Validate a patched copy fully so later unrelated
        # errors cannot be hidden by the raw-response fallback.
        original(
            response_data=validation_response,
            response_types_map=response_types_map,
        )
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
