"""Construction and account-context handling for Apple's Platform API SDK."""

from __future__ import annotations

import os
from typing import Any

from ..config import Credentials, load_credentials


class PlatformConfigurationError(RuntimeError):
    """Raised when Platform API credentials or account context are incomplete."""


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
        return AppleAdsClientBuilder.from_private_key_path(
            resolved.client_id,
            resolved.team_id,
            resolved.key_id,
            resolved.private_key_path,
        ).build()
    except Exception as exc:
        raise PlatformConfigurationError(
            f"Unable to build the Apple Ads Platform SDK client: {exc}"
        ) from exc
