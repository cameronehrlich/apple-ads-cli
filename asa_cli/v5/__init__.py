"""Apple Search Ads Campaign Management API v5 compatibility package."""

from .api import (
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
