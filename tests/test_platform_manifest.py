"""Contract tests for the pinned official Apple Ads Platform Python SDK."""

from __future__ import annotations

import hashlib
import importlib
import importlib.metadata
import inspect
import json
from collections import Counter
from pathlib import Path

from pydantic import BaseModel

from asa_cli.platform.generate_manifest import MANIFEST_PATH, SCHEMA_PATH, generate
from asa_cli.platform.manifest_discovery import (
    EXPECTED_CANONICAL_METHOD_COUNT,
    MANIFEST_SCHEMA,
    SDK_API_CLASS,
    SDK_DISTRIBUTION,
    SDK_GIT_COMMIT,
    SDK_VERSION,
    _container,
    _model_closure,
    _model_types,
    canonical_sdk_methods,
    discover_manifest,
)


def _load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_sha256(value) -> str:
    encoded = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode()
    return hashlib.sha256(encoded).hexdigest()


def _import_qualified(name: str):
    module_name, attribute = name.rsplit(".", 1)
    return getattr(importlib.import_module(module_name), attribute)


class _ExampleBody(BaseModel):
    value: str


def test_body_container_detection_is_stable_for_modern_union_annotations():
    assert _container(_ExampleBody | None) == "model"
    assert _container(list[_ExampleBody] | None) == "list"
    assert _container(str | None) == "primitive"


def test_manifest_covers_the_exact_canonical_sdk_surface():
    manifest = _load(MANIFEST_PATH)
    sdk_methods = set(canonical_sdk_methods())
    manifest_methods = {operation["sdk_method"] for operation in manifest["operations"]}

    assert len(sdk_methods) == EXPECTED_CANONICAL_METHOD_COUNT == 99
    assert manifest["sdk"]["canonical_method_count"] == 99
    assert manifest_methods == sdk_methods


def test_every_sdk_method_is_wrapped_exactly_once_in_the_manifest():
    manifest = _load(MANIFEST_PATH)
    methods = [operation["sdk_method"] for operation in manifest["operations"]]

    assert len(methods) == len(set(methods)) == 99


def test_every_public_parameter_is_classified_exactly_once():
    manifest = _load(MANIFEST_PATH)

    for operation in manifest["operations"]:
        public_parameters = {
            parameter["name"]
            for parameter in operation["signature"]
            if parameter["name"] != "x_ap_context"
        }
        classified = [
            parameter["name"]
            for location in (
                "path_parameters",
                "query_parameters",
                "body_parameters",
                "multipart_parameters",
            )
            for parameter in operation[location]
        ]

        assert Counter(classified) == Counter(
            dict.fromkeys(public_parameters, 1)
        ), operation["sdk_method"]


def test_committed_operation_signatures_and_schemas_have_not_drifted():
    committed = _load(MANIFEST_PATH)
    discovered = discover_manifest()

    assert committed["operations"] == discovered["operations"]
    assert committed["request_models"] == discovered["request_models"]
    assert committed["response_models"] == discovered["response_models"]
    assert len(committed["request_models"]) == 35
    assert len(committed["response_models"]) == 220


def test_all_operations_have_one_audited_response_model():
    manifest = _load(MANIFEST_PATH)
    operations = manifest["operations"]
    response_models = manifest["response_models"]

    assert len({operation["response_model"] for operation in operations}) == 71
    assert all(operation["response_model"] in response_models for operation in operations)

    roots = []
    for method in canonical_sdk_methods().values():
        models = _model_types(inspect.signature(method).return_annotation)
        assert len(models) == 1
        roots.extend(models)
    closure = _model_closure(roots)

    assert len(set(roots)) == 71
    assert len(closure) == 220
    assert {
        f"{model.__module__}.{model.__qualname__}" for model in closure
    } == set(response_models)

    audits = [record["field_audit"] for record in response_models.values()]
    assert sum(audit["field_count"] for audit in audits) == 1391
    assert sum(len(audit["strict_fields"]) for audit in audits) == 516
    assert sum(len(audit["identifier_fields"]) for audit in audits) == 135
    assert sum(len(audit["enum_fields"]) for audit in audits) == 101
    assert sum(len(audit["custom_validator_fields"]) for audit in audits) == 15


def test_sdk_and_model_source_provenance_matches_the_pinned_release():
    manifest = _load(MANIFEST_PATH)
    sdk = manifest["sdk"]

    assert importlib.metadata.version(SDK_DISTRIBUTION) == SDK_VERSION
    assert sdk["distribution"] == SDK_DISTRIBUTION
    assert sdk["version"] == SDK_VERSION
    assert sdk["git_commit"] == SDK_GIT_COMMIT
    assert sdk["api_class"] == SDK_API_CLASS

    api_class = _import_qualified(SDK_API_CLASS)
    api_source = inspect.getsourcefile(api_class)
    assert api_source is not None
    assert sdk["api_source_sha256"] == _sha256(Path(api_source))

    model_manifests = {
        **manifest["request_models"],
        **manifest["response_models"],
    }
    for qualified_name, provenance in model_manifests.items():
        model = _import_qualified(qualified_name)
        model_source = inspect.getsourcefile(model)
        assert model_source is not None
        assert provenance["source_sha256"] == _sha256(Path(model_source))
        assert provenance["schema_sha256"] == _canonical_sha256(
            model.model_json_schema(by_alias=True)
        )


def test_committed_manifest_and_schema_are_generator_outputs():
    assert _load(SCHEMA_PATH) == MANIFEST_SCHEMA
    assert generate(check=True)


def test_manifest_preserves_nonstandard_transport_contracts():
    operations = {
        operation["sdk_method"]: operation for operation in _load(MANIFEST_PATH)["operations"]
    }

    upload = operations["upload_asset"]
    assert upload["special_handling"] == ["multipart-upload"]
    assert [parameter["wire_name"] for parameter in upload["multipart_parameters"]] == [
        "file",
        "promotedObjectId",
        "promotedObjectType",
    ]

    apply_daily_budget = operations["apply_daily_budget_recommendations"]
    assert apply_daily_budget["body_parameters"][0]["container"] == "list"
    assert apply_daily_budget["mutation"] is True

    get_shared_budget = operations["shared_budgets_id_get"]
    assert get_shared_budget["context"] == "optional"

    assert operations["search_apps"]["pagination"] == "offset-limit"
    assert operations["search_geos"]["pagination"] == "offset-page-size"
    assert operations["get_asset"]["special_handling"] == [
        "metadata-only-no-download"
    ]
