"""Backward-compatible imports for the Apple Ads Campaign Management API v5 client.

New code should import from :mod:`asa_cli.v5.api`.
"""

from .v5.api import (
    API_BASE_URL,
    REQUEST_TIMEOUT,
    TOKEN_URL,
    SearchAdsAPIError,
    SearchAdsClient,
)

__all__ = [
    "API_BASE_URL",
    "REQUEST_TIMEOUT",
    "TOKEN_URL",
    "SearchAdsAPIError",
    "SearchAdsClient",
]
