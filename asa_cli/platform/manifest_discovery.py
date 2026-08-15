"""Discover a deterministic contract manifest from Apple's official Python SDK.

The upstream SDK is generated from OpenAPI, but it does not ship its source
OpenAPI document. This module therefore combines public signature reflection
with a narrow AST read of each generated serializer to recover the HTTP verb,
resource path, and parameter locations without making network requests.
"""

from __future__ import annotations

import ast
import hashlib
import importlib.metadata
import inspect
import json
from collections.abc import Iterable
from pathlib import Path
from types import UnionType
from typing import Any, get_args, get_origin

from apple_ads_platform.api.apple_ads_api import AppleAdsApi
from pydantic import BaseModel

SDK_DISTRIBUTION = "apple-ads-platform"
SDK_VERSION = "1.109.0"
SDK_REPOSITORY = "https://github.com/apple/apple-ads-platform-api-python"
SDK_RELEASE_URL = f"{SDK_REPOSITORY}/releases/tag/v{SDK_VERSION}"
SDK_GIT_COMMIT = "742ba544433ba9a5bef0ab3603336dcf53ff9338"
SDK_API_CLASS = "apple_ads_platform.api.apple_ads_api.AppleAdsApi"
MANIFEST_SCHEMA_VERSION = 1
MANIFEST_GENERATED_AT = "2026-08-14"
EXPECTED_CANONICAL_METHOD_COUNT = 99

_INTERNAL_PARAMETERS = {
    "_request_timeout",
    "_request_auth",
    "_content_type",
    "_headers",
    "_host_index",
}
_EXCLUDED_METHOD_SUFFIXES = ("_with_http_info", "_without_preload_content")

_RESOURCE_PREFIXES: tuple[tuple[str, str], ...] = (
    ("/reports/business-brands/", "reports-business-brands"),
    ("/reports/apps/", "reports-apps"),
    ("/recommendations/", "recommendations"),
    ("/suggestions/", "suggestions"),
    ("/insights/", "insights"),
    ("/change-history", "change-history"),
    ("/rejection-reasons/", "rejection-reasons"),
    ("/metadata/apps/", "apps"),
    ("/eligibilities/apps/", "apps"),
    ("/search/apps", "apps"),
    ("/apps/", "apps"),
    ("/product-pages", "product-pages"),
    ("/business-brands", "business-brands"),
    ("/business-categories", "business-categories"),
    ("/location-groups", "location-groups"),
    ("/locations", "locations"),
    ("/search/geo", "geos"),
    ("/assets", "assets"),
    ("/ad-accounts", "ad-accounts"),
    ("/advertiser-resources", "access"),
    ("/orgs/", "access"),
    ("/me", "access"),
    ("/acls", "access"),
    ("/shared-budgets", "shared-budgets"),
    ("/negative-keywords", "negative-keywords"),
    ("/keywords", "keywords"),
    ("/creatives", "creatives"),
    ("/campaigns", "campaigns"),
    ("/adgroups", "ad-groups"),
    ("/ads", "ads"),
)

_PAGINATION_BY_BODY_MODEL = {
    "QueryRequest": "query-pagination",
    "EligibilityQueryRequest": "query-pagination",
    "CreativeRejectionReasonQueryRequest": "query-pagination",
    "PolicyAssignmentQueryRequest": "query-pagination",
    "AppsReportingRequest": "request-pagination",
    "BrandsReportingRequest": "request-pagination",
    "ImpressionShareQueryRequest": "request-pagination",
    "SearchTermPopularityQueryRequest": "request-pagination",
    "AuditQuery": "audit-pagination",
    "RecommendationQueryRequest": "recommendation-pagination",
    "GeoSearchPostRequest": "geo-search-pagination",
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _json_sha256(value: Any) -> str:
    return hashlib.sha256(_canonical_json(value).encode()).hexdigest()


def canonical_sdk_methods() -> dict[str, Any]:
    """Return exactly the canonical convenience methods exposed by the SDK."""

    return {
        name: member
        for name, member in inspect.getmembers(AppleAdsApi, inspect.isfunction)
        if name != "__init__"
        and not name.startswith("_")
        and not name.endswith(_EXCLUDED_METHOD_SUFFIXES)
    }


def _api_source() -> tuple[Path, ast.ClassDef]:
    source_path = inspect.getsourcefile(AppleAdsApi)
    if source_path is None:
        raise RuntimeError("Unable to locate AppleAdsApi source")
    path = Path(source_path).resolve()
    tree = ast.parse(path.read_text(encoding="utf-8"))
    class_node = next(
        node
        for node in tree.body
        if isinstance(node, ast.ClassDef) and node.name == "AppleAdsApi"
    )
    return path, class_node


def _class_methods(class_node: ast.ClassDef) -> dict[str, ast.FunctionDef]:
    return {
        node.name: node
        for node in class_node.body
        if isinstance(node, ast.FunctionDef)
    }


def _function_parameters(node: ast.FunctionDef) -> list[dict[str, Any]]:
    args = node.args.args[1:]
    defaults: list[ast.expr | None] = [None] * (len(args) - len(node.args.defaults)) + list(
        node.args.defaults
    )
    parameters = []
    for argument, default in zip(args, defaults, strict=True):
        if argument.arg in _INTERNAL_PARAMETERS:
            continue
        parameters.append(
            {
                "name": argument.arg,
                "annotation": ast.unparse(argument.annotation) if argument.annotation else "Any",
                "required": default is None,
                "default": None if default is None else ast.unparse(default),
            }
        )
    return parameters


def _serializer_contract(node: ast.FunctionDef) -> dict[str, Any]:
    contract: dict[str, Any] = {
        "http_method": None,
        "resource_path": None,
        "path": {},
        "query": {},
        "body": [],
        "multipart": {},
    }

    for child in ast.walk(node):
        if isinstance(child, ast.Assign) and len(child.targets) == 1:
            target = child.targets[0]
            if (
                isinstance(target, ast.Subscript)
                and isinstance(target.value, ast.Name)
                and isinstance(target.slice, ast.Constant)
                and isinstance(child.value, ast.Name)
            ):
                if target.value.id == "_path_params":
                    contract["path"][child.value.id] = str(target.slice.value)
                elif target.value.id == "_files":
                    contract["multipart"][child.value.id] = str(target.slice.value)
            elif (
                isinstance(target, ast.Name)
                and target.id == "_body_params"
                and isinstance(child.value, ast.Name)
            ):
                contract["body"].append(child.value.id)

        if not isinstance(child, ast.Call) or not isinstance(child.func, ast.Attribute):
            continue

        if child.func.attr == "param_serialize":
            keywords = {keyword.arg: keyword.value for keyword in child.keywords}
            contract["http_method"] = ast.literal_eval(keywords["method"])
            contract["resource_path"] = ast.literal_eval(keywords["resource_path"])
            continue

        if child.func.attr != "append" or not isinstance(child.func.value, ast.Name):
            continue
        if not child.args or not isinstance(child.args[0], ast.Tuple):
            continue
        tuple_values = child.args[0].elts
        if len(tuple_values) != 2 or not isinstance(tuple_values[0], ast.Constant):
            continue
        wire_name = str(tuple_values[0].value)
        parameter_value = tuple_values[1]
        if isinstance(parameter_value, ast.Name):
            parameter_name = parameter_value.id
        elif (
            isinstance(parameter_value, ast.Attribute)
            and parameter_value.attr == "value"
            and isinstance(parameter_value.value, ast.Name)
        ):
            # Generated serializers unwrap enum query values before sending.
            parameter_name = parameter_value.value.id
        else:
            continue
        if child.func.value.id == "_query_params":
            contract["query"][parameter_name] = wire_name
        elif child.func.value.id == "_form_params":
            contract["multipart"][parameter_name] = wire_name

    if contract["http_method"] is None or contract["resource_path"] is None:
        raise RuntimeError(f"Unable to recover serializer contract from {node.name}")
    contract["body"] = sorted(set(contract["body"]))
    return contract


def _resource_family(resource_path: str) -> str:
    for prefix, family in _RESOURCE_PREFIXES:
        if resource_path.startswith(prefix):
            return family
    raise RuntimeError(f"No resource family configured for {resource_path}")


def _model_types(annotation: Any) -> list[type[BaseModel]]:
    if inspect.isclass(annotation) and issubclass(annotation, BaseModel):
        return [annotation]
    models: list[type[BaseModel]] = []
    for argument in get_args(annotation):
        models.extend(_model_types(argument))
    return models


def _container(annotation: Any) -> str:
    origin = get_origin(annotation)
    if origin in (list, tuple, set):
        return "list"
    if origin in (UnionType,):
        return "primitive"
    if _model_types(annotation):
        return "model"
    return "primitive"


def _parameter_record(
    signature_record: dict[str, Any],
    *,
    wire_name: str,
    resolved_parameter: inspect.Parameter,
    body: bool = False,
) -> dict[str, Any]:
    record = {
        **signature_record,
        "wire_name": wire_name,
    }
    if body:
        models = _model_types(resolved_parameter.annotation)
        record.update(
            {
                "model": (
                    f"{models[0].__module__}.{models[0].__qualname__}" if models else None
                ),
                "container": _container(resolved_parameter.annotation),
            }
        )
    return record


def _pagination(method_name: str, body_parameters: Iterable[dict[str, Any]]) -> str | None:
    if method_name in {"search_apps", "get_change_details"}:
        return "offset-limit"
    if method_name == "search_geos":
        return "offset-page-size"
    for parameter in body_parameters:
        model = parameter.get("model")
        if model:
            model_name = model.rsplit(".", 1)[-1]
            pagination = _PAGINATION_BY_BODY_MODEL.get(model_name)
            if pagination:
                return pagination
    return None


def _special_handling(method_name: str) -> list[str]:
    special = []
    if method_name == "upload_asset":
        special.append("multipart-upload")
    if method_name == "get_asset":
        special.append("metadata-only-no-download")
    if method_name.startswith("apply_"):
        special.append("recommendation-apply")
    if method_name.startswith("dismiss_"):
        special.append("recommendation-dismiss")
    return special


def _is_mutation(http_method: str, resource_path: str) -> bool:
    if http_method == "GET":
        return False
    if resource_path.endswith("/query") or resource_path == "/search/geo":
        return False
    return True


def _request_model_manifest(model_types: Iterable[type[BaseModel]]) -> dict[str, Any]:
    manifest = {}
    for model in sorted(set(model_types), key=lambda item: f"{item.__module__}.{item.__qualname__}"):
        name = f"{model.__module__}.{model.__qualname__}"
        source_path_value = inspect.getsourcefile(model)
        if source_path_value is None:
            raise RuntimeError(f"Unable to locate source for {name}")
        schema = model.model_json_schema(by_alias=True)
        manifest[name] = {
            "schema": schema,
            "schema_sha256": _json_sha256(schema),
            "source_sha256": _sha256(Path(source_path_value).resolve()),
        }
    return manifest


def discover_manifest() -> dict[str, Any]:
    """Build the complete deterministic SDK manifest."""

    installed_version = importlib.metadata.version(SDK_DISTRIBUTION)
    if installed_version != SDK_VERSION:
        raise RuntimeError(
            f"Expected {SDK_DISTRIBUTION}=={SDK_VERSION}, found {installed_version}"
        )

    api_path, class_node = _api_source()
    ast_methods = _class_methods(class_node)
    sdk_methods = canonical_sdk_methods()
    operations = []
    request_models: list[type[BaseModel]] = []

    for method_name in sorted(sdk_methods):
        method_node = ast_methods[method_name]
        serializer_node = ast_methods[f"_{method_name}_serialize"]
        serializer = _serializer_contract(serializer_node)
        signature_records = _function_parameters(method_node)
        signature_by_name = {record["name"]: record for record in signature_records}
        resolved_signature = inspect.signature(sdk_methods[method_name])

        def parameters_for(
            location: str,
            *,
            body: bool = False,
            serializer_contract: dict[str, Any] = serializer,
            records_by_name: dict[str, dict[str, Any]] = signature_by_name,
            sdk_signature: inspect.Signature = resolved_signature,
        ) -> list[dict[str, Any]]:
            if location == "body":
                names_and_wires = [
                    (name, "body") for name in serializer_contract[location]
                ]
            else:
                names_and_wires = sorted(serializer_contract[location].items())
            records = []
            for name, wire_name in names_and_wires:
                record = _parameter_record(
                    records_by_name[name],
                    wire_name=wire_name,
                    resolved_parameter=sdk_signature.parameters[name],
                    body=body,
                )
                records.append(record)
                if body:
                    request_models.extend(
                        _model_types(sdk_signature.parameters[name].annotation)
                    )
            return records

        path_parameters = parameters_for("path")
        query_parameters = parameters_for("query")
        body_parameters = parameters_for("body", body=True)
        multipart_parameters = parameters_for("multipart")
        context_record = signature_by_name.get("x_ap_context")
        context = (
            "none"
            if context_record is None
            else "required"
            if context_record["required"]
            else "optional"
        )
        return_annotation = (
            ast.unparse(method_node.returns) if method_node.returns is not None else "Any"
        )
        resource_path = serializer["resource_path"]
        http_method = serializer["http_method"]

        operations.append(
            {
                "sdk_method": method_name,
                "resource_family": _resource_family(resource_path),
                "http_method": http_method,
                "resource_path": resource_path,
                "signature": signature_records,
                "context": context,
                "path_parameters": path_parameters,
                "query_parameters": query_parameters,
                "body_parameters": body_parameters,
                "multipart_parameters": multipart_parameters,
                "return_annotation": return_annotation,
                "mutation": _is_mutation(http_method, resource_path),
                "pagination": _pagination(method_name, body_parameters),
                "special_handling": _special_handling(method_name),
                "aliases": [],
            }
        )

    if len(operations) != EXPECTED_CANONICAL_METHOD_COUNT:
        raise RuntimeError(
            f"Expected {EXPECTED_CANONICAL_METHOD_COUNT} canonical methods, found {len(operations)}"
        )

    return {
        "schema_version": MANIFEST_SCHEMA_VERSION,
        "generated_at": MANIFEST_GENERATED_AT,
        "sdk": {
            "distribution": SDK_DISTRIBUTION,
            "version": SDK_VERSION,
            "repository": SDK_REPOSITORY,
            "release_url": SDK_RELEASE_URL,
            "git_commit": SDK_GIT_COMMIT,
            "api_class": SDK_API_CLASS,
            "api_source_sha256": _sha256(api_path),
            "canonical_method_count": len(operations),
            "excluded_method_suffixes": list(_EXCLUDED_METHOD_SUFFIXES),
        },
        "operations": operations,
        "request_models": _request_model_manifest(request_models),
    }


MANIFEST_SCHEMA: dict[str, Any] = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": "https://github.com/cameronehrlich/apple-search-ads-cli/schemas/apple-ads-platform-manifest-v1.json",
    "title": "Apple Ads Platform SDK manifest",
    "type": "object",
    "additionalProperties": False,
    "required": ["schema_version", "generated_at", "sdk", "operations", "request_models"],
    "properties": {
        "schema_version": {"const": MANIFEST_SCHEMA_VERSION},
        "generated_at": {"type": "string", "format": "date"},
        "sdk": {
            "type": "object",
            "additionalProperties": False,
            "required": [
                "distribution",
                "version",
                "repository",
                "release_url",
                "git_commit",
                "api_class",
                "api_source_sha256",
                "canonical_method_count",
                "excluded_method_suffixes",
            ],
            "properties": {
                "distribution": {"type": "string"},
                "version": {"type": "string"},
                "repository": {"type": "string", "format": "uri"},
                "release_url": {"type": "string", "format": "uri"},
                "git_commit": {"type": "string", "pattern": "^[0-9a-f]{40}$"},
                "api_class": {"type": "string"},
                "api_source_sha256": {"type": "string", "pattern": "^[0-9a-f]{64}$"},
                "canonical_method_count": {"type": "integer", "minimum": 1},
                "excluded_method_suffixes": {
                    "type": "array",
                    "items": {"type": "string"},
                    "uniqueItems": True,
                },
            },
        },
        "operations": {
            "type": "array",
            "items": {"$ref": "#/$defs/operation"},
        },
        "request_models": {
            "type": "object",
            "additionalProperties": {"$ref": "#/$defs/request_model"},
        },
    },
    "$defs": {
        "signature_parameter": {
            "type": "object",
            "additionalProperties": False,
            "required": ["name", "annotation", "required", "default"],
            "properties": {
                "name": {"type": "string"},
                "annotation": {"type": "string"},
                "required": {"type": "boolean"},
                "default": {"type": ["string", "null"]},
            },
        },
        "located_parameter": {
            "type": "object",
            "additionalProperties": False,
            "required": ["name", "annotation", "required", "default", "wire_name"],
            "properties": {
                "name": {"type": "string"},
                "annotation": {"type": "string"},
                "required": {"type": "boolean"},
                "default": {"type": ["string", "null"]},
                "wire_name": {"type": "string"},
            },
        },
        "body_parameter": {
            "type": "object",
            "additionalProperties": False,
            "required": [
                "name",
                "annotation",
                "required",
                "default",
                "wire_name",
                "model",
                "container",
            ],
            "properties": {
                "name": {"type": "string"},
                "annotation": {"type": "string"},
                "required": {"type": "boolean"},
                "default": {"type": ["string", "null"]},
                "wire_name": {"type": "string"},
                "model": {"type": ["string", "null"]},
                "container": {"enum": ["model", "list", "primitive"]},
            },
        },
        "cli": {
            "type": "object",
            "additionalProperties": False,
            "required": ["command_path", "implementation_status"],
            "properties": {
                "command_path": {"type": "array", "items": {"type": "string"}},
                "implementation_status": {"type": "string"},
                "input_example": {"type": "string"},
                "verification": {"type": "string"},
            },
        },
        "operation": {
            "type": "object",
            "additionalProperties": False,
            "required": [
                "sdk_method",
                "resource_family",
                "http_method",
                "resource_path",
                "signature",
                "context",
                "path_parameters",
                "query_parameters",
                "body_parameters",
                "multipart_parameters",
                "return_annotation",
                "mutation",
                "pagination",
                "special_handling",
                "aliases",
            ],
            "properties": {
                "sdk_method": {"type": "string"},
                "resource_family": {"type": "string"},
                "http_method": {"enum": ["GET", "POST", "PUT", "DELETE"]},
                "resource_path": {"type": "string", "pattern": "^/"},
                "signature": {
                    "type": "array",
                    "items": {"$ref": "#/$defs/signature_parameter"},
                },
                "context": {"enum": ["required", "optional", "none"]},
                "path_parameters": {
                    "type": "array",
                    "items": {"$ref": "#/$defs/located_parameter"},
                },
                "query_parameters": {
                    "type": "array",
                    "items": {"$ref": "#/$defs/located_parameter"},
                },
                "body_parameters": {
                    "type": "array",
                    "items": {"$ref": "#/$defs/body_parameter"},
                },
                "multipart_parameters": {
                    "type": "array",
                    "items": {"$ref": "#/$defs/located_parameter"},
                },
                "return_annotation": {"type": "string"},
                "mutation": {"type": "boolean"},
                "pagination": {"type": ["string", "null"]},
                "special_handling": {"type": "array", "items": {"type": "string"}},
                "aliases": {"type": "array", "items": {"type": "string"}},
                "cli": {"$ref": "#/$defs/cli"},
            },
        },
        "request_model": {
            "type": "object",
            "additionalProperties": False,
            "required": ["schema", "schema_sha256", "source_sha256"],
            "properties": {
                "schema": {"type": "object"},
                "schema_sha256": {"type": "string", "pattern": "^[0-9a-f]{64}$"},
                "source_sha256": {"type": "string", "pattern": "^[0-9a-f]{64}$"},
            },
        },
    },
}
