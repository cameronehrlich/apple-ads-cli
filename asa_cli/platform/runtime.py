"""Shared JSON-first execution helpers for one-to-one SDK command wrappers."""

from __future__ import annotations

import json
import sys
from collections.abc import Mapping
from datetime import date, datetime
from enum import Enum
from pathlib import Path
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel

from ..config import Credentials
from .client import (
    PlatformConfigurationError,
    build_platform_api,
    context_header,
    resolve_optional_ad_account_id,
)

ContextMode = Literal["required", "optional", "none"]


class PlatformAPIError(RuntimeError):
    """Normalized failure raised by a Platform API SDK invocation."""

    def __init__(
        self,
        message: str,
        *,
        status: int | None = None,
        body: Any = None,
    ) -> None:
        super().__init__(message)
        self.status = status
        self.body = body


def _mapping_values(value: Any, key: str) -> list[str] | None:
    """Return a targeting string list when its shape is valid enough to inspect."""
    if not isinstance(value, Mapping):
        return None
    items = value.get(key)
    if not isinstance(items, list) or not all(isinstance(item, str) for item in items):
        return None
    return items


def _validate_live_request_contract(model_name: str, payload: Mapping[str, Any]) -> None:
    """Apply narrow server-confirmed requirements missing from SDK 1.109.0."""
    if model_name == "AdGroupCreate" and not payload.get("startTime"):
        raise PlatformAPIError(
            "Invalid AdGroupCreate request: startTime is required by Apple"
        )

    if model_name != "CampaignCreate":
        return

    targeting = payload.get("targeting")
    if not isinstance(targeting, Mapping):
        return
    placement = targeting.get("supplyPlacement")
    placement_values = _mapping_values(placement, "include")
    if not placement_values:
        return

    if set(placement_values) & {"SEARCH_RESULTS", "APP_STORE_SEARCH_RESULTS"}:
        raise PlatformAPIError(
            "Invalid CampaignCreate request: use APPSTORE_SEARCH_RESULTS for "
            "targeting.supplyPlacement.include, not SEARCH_RESULTS"
        )

    source_values = _mapping_values(targeting.get("supplySource"), "include")
    if not source_values:
        raise PlatformAPIError(
            "Invalid CampaignCreate request: targeting.supplySource.include is required "
            "when supplyPlacement is set"
        )
    if "APPSTORE_SEARCH_RESULTS" in placement_values and "APPSTORE" not in source_values:
        raise PlatformAPIError(
            "Invalid CampaignCreate request: APPSTORE_SEARCH_RESULTS requires "
            "targeting.supplySource.include to contain APPSTORE"
        )


def _restore_supplied_fields(model: Any, payload: Any) -> None:
    """Undo generated ``from_dict`` marking omitted fields as explicitly supplied.

    Apple SDK 1.109.0 constructs request models by passing every optional field
    to Pydantic, including absent fields as ``None``. Its wire serializer then
    emits several of those values as explicit JSON nulls. Restore the field-set
    information recursively from the caller's original JSON so ``to_dict``
    omits absent values while preserving the caller's supplied-field intent
    and SDK additional properties.
    """
    if isinstance(model, BaseModel) and isinstance(payload, Mapping):
        supplied: set[str] = set()
        for field_name, field_info in type(model).model_fields.items():
            if field_name == "additional_properties":
                continue
            alias = field_info.alias or field_name
            if alias in payload:
                raw_value = payload[alias]
            elif field_name in payload:
                raw_value = payload[field_name]
            else:
                continue
            supplied.add(field_name)
            _restore_supplied_fields(getattr(model, field_name, None), raw_value)
        object.__setattr__(model, "__pydantic_fields_set__", supplied)
        return
    if isinstance(model, (list, tuple)) and isinstance(payload, list):
        for child, raw_value in zip(model, payload, strict=False):
            _restore_supplied_fields(child, raw_value)


def read_json_payload(path: str | Path) -> Any:
    """Read a JSON request from a file, or stdin when path is ``-``."""
    if str(path) == "-":
        raw = sys.stdin.read()
        source = "stdin"
    else:
        source_path = Path(path)
        try:
            raw = source_path.read_text(encoding="utf-8")
        except OSError as exc:
            raise PlatformAPIError(f"Unable to read request file {source_path}: {exc}") from exc
        source = str(source_path)

    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        raise PlatformAPIError(f"Invalid JSON in {source}: {exc}") from exc


def hydrate_model(model_name: str, payload: Any, *, many: bool = False) -> Any:
    """Construct an official SDK request model from JSON-compatible data."""
    try:
        import apple_ads_platform.models as sdk_models
    except ImportError as exc:  # pragma: no cover - covered by packaging verification
        raise PlatformAPIError("Apple Ads Platform SDK is not installed") from exc

    model_type = getattr(sdk_models, model_name, None)
    if model_type is None:
        raise PlatformAPIError(f"Unknown Apple Ads SDK request model: {model_name}")

    def build(item: Any) -> Any:
        if not isinstance(item, Mapping):
            raise PlatformAPIError(f"{model_name} input must be a JSON object")
        _validate_live_request_contract(model_name, item)
        try:
            from_dict = getattr(model_type, "from_dict", None)
            if callable(from_dict):
                model = from_dict(dict(item))
            else:
                model = model_type.model_validate(item)
            _restore_supplied_fields(model, item)
            return model
        except Exception as exc:
            raise PlatformAPIError(f"Invalid {model_name} request: {exc}") from exc

    if many:
        if not isinstance(payload, list):
            raise PlatformAPIError(f"{model_name} input must be a JSON array")
        return [build(item) for item in payload]
    return build(payload)


def serialize_response(value: Any) -> Any:
    """Recursively preserve SDK response fields as JSON-compatible values."""
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, (datetime, date, UUID)):
        return str(value)
    if isinstance(value, Enum):
        return serialize_response(value.value)
    if isinstance(value, Mapping):
        return {str(key): serialize_response(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [serialize_response(item) for item in value]
    if hasattr(value, "to_dict"):
        return serialize_response(value.to_dict())
    if isinstance(value, BaseModel):
        return serialize_response(
            value.model_dump(mode="json", by_alias=True, exclude_none=True)
        )
    return str(value)


def _normalize_sdk_exception(method_name: str, exc: Exception) -> PlatformAPIError:
    status = getattr(exc, "status", None)
    raw_body = getattr(exc, "body", None)
    body: Any = raw_body
    if isinstance(raw_body, (bytes, bytearray)):
        raw_body = raw_body.decode("utf-8", errors="replace")
    if isinstance(raw_body, str):
        try:
            body = json.loads(raw_body)
        except json.JSONDecodeError:
            body = raw_body
    reason = getattr(exc, "reason", None)
    message = f"Apple Ads Platform API call {method_name} failed"
    if status is not None:
        message += f" with status {status}"
    if reason:
        message += f": {reason}"
    elif str(exc):
        message += f": {exc}"
    return PlatformAPIError(message, status=status, body=body)


def invoke(
    method_name: str,
    *,
    arguments: Mapping[str, Any] | None = None,
    context: ContextMode = "required",
    credentials: Credentials | None = None,
    ad_account_id: str | None = None,
    api: Any = None,
) -> Any:
    """Invoke exactly one canonical SDK method and return serialized output."""
    call_arguments = dict(arguments or {})
    if context not in {"required", "optional", "none"}:
        raise ValueError(f"Unsupported context mode: {context}")

    try:
        if context == "required":
            call_arguments["x_ap_context"] = context_header(credentials, ad_account_id)
        elif context == "optional":
            optional_account_id = resolve_optional_ad_account_id(
                credentials,
                ad_account_id,
            )
            if optional_account_id is not None:
                call_arguments["x_ap_context"] = context_header(
                    credentials,
                    optional_account_id,
                )
        client = api or build_platform_api(credentials)
    except PlatformConfigurationError as exc:
        raise PlatformAPIError(str(exc)) from exc

    method = getattr(client, method_name, None)
    if method is None or not callable(method):
        raise PlatformAPIError(f"Apple Ads SDK method is unavailable: {method_name}")

    try:
        return serialize_response(method(**call_arguments))
    except PlatformAPIError:
        raise
    except Exception as exc:
        raise _normalize_sdk_exception(method_name, exc) from exc
