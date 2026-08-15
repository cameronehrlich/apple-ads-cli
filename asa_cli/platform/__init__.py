"""Apple Ads Platform API v1 support."""

from .client import build_platform_api
from .runtime import PlatformAPIError, invoke, serialize_response

__all__ = [
    "PlatformAPIError",
    "build_platform_api",
    "invoke",
    "serialize_response",
]
