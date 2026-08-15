"""Build explicit command registries from the committed SDK manifest."""

from __future__ import annotations

import ast
import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Literal, cast

from .command_factory import BodySpec, CommandSpec, MutationKind, ParameterSpec

MANIFEST_PATH = (
    Path(__file__).with_name("manifest") / "apple_ads_platform_v1_109_0.json"
)


@lru_cache(maxsize=1)
def load_manifest() -> dict[str, Any]:
    """Load the authoritative checked-in Apple Ads Platform SDK manifest."""
    try:
        payload = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    except OSError as exc:
        raise RuntimeError(f"Unable to read Platform API manifest: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Platform API manifest is invalid JSON: {exc}") from exc

    operations = payload.get("operations")
    if not isinstance(operations, list):
        raise RuntimeError("Platform API manifest does not contain an operations list")
    return payload


def _parse_default(value: Any) -> Any:
    if value is None:
        return None
    if not isinstance(value, str):
        return value
    try:
        return ast.literal_eval(value)
    except (SyntaxError, ValueError):
        return value


def _scalar_annotation(annotation: str) -> Any:
    if "List[" in annotation or "list[" in annotation:
        if "StrictBool" in annotation or "bool" in annotation:
            return list[bool]
        if "StrictInt" in annotation or "int" in annotation:
            return list[int]
        if any(token in annotation for token in ("StrictFloat", "float", "Decimal")):
            return list[float]
        return list[str]
    if "StrictBool" in annotation or annotation in {"bool", "Optional[bool]"}:
        return bool
    if "StrictInt" in annotation or annotation in {"int", "Optional[int]"}:
        return int
    if any(token in annotation for token in ("StrictFloat", "float", "Decimal")):
        return float
    return str


def _parameter_spec(record: dict[str, Any]) -> ParameterSpec:
    name = str(record["name"])
    required = bool(record["required"])
    wire_name = str(record.get("wire_name", name))
    return ParameterSpec(
        name=name,
        flag=f"--{name.replace('_', '-')}",
        annotation=_scalar_annotation(str(record.get("annotation", "str"))),
        required=required,
        default=None if required else _parse_default(record.get("default")),
        help=f"{wire_name} parameter",
    )


def _body_spec(records: list[dict[str, Any]]) -> BodySpec | None:
    if not records:
        return None
    if len(records) != 1:
        raise ValueError("CommandSpec supports exactly one SDK request body")
    record = records[0]
    model_path = record.get("model")
    if not isinstance(model_path, str) or not model_path:
        raise ValueError(f"Manifest body parameter {record.get('name')} has no request model")
    return BodySpec(
        parameter=str(record["name"]),
        model=model_path.rsplit(".", 1)[-1],
        required=bool(record["required"]),
        many=record.get("container") == "list",
    )


def _mutation_kind(operation: dict[str, Any]) -> MutationKind:
    if not operation["mutation"]:
        return "read"

    method_name = str(operation["sdk_method"])
    http_method = str(operation["http_method"])
    if method_name.startswith("apply_"):
        return "apply"
    if method_name.startswith("dismiss_"):
        return "dismiss"
    if "upload" in method_name:
        return "upload"
    if http_method == "DELETE" or "delete" in method_name:
        return "delete"
    if http_method == "PUT" or "update" in method_name:
        return "update"
    return "create"


def specs_from_manifest(
    *,
    resource_family: str,
    sdk_methods: tuple[str, ...],
    command_names: dict[str, str],
) -> tuple[CommandSpec, ...]:
    """Create exact CommandSpecs for an explicit resource-owned SDK method list."""
    if len(sdk_methods) != len(set(sdk_methods)):
        raise ValueError(f"Duplicate SDK method in {resource_family} registry")
    if set(command_names) != set(sdk_methods):
        raise ValueError(f"Command names must cover every {resource_family} SDK method exactly once")
    if len(command_names.values()) != len(set(command_names.values())):
        raise ValueError(f"Duplicate command name in {resource_family} registry")

    operation_index = {
        str(operation["sdk_method"]): operation
        for operation in load_manifest()["operations"]
    }
    specs = []
    for method_name in sdk_methods:
        operation = operation_index.get(method_name)
        if operation is None:
            raise ValueError(f"SDK method is absent from the manifest: {method_name}")
        if operation["resource_family"] != resource_family:
            raise ValueError(
                f"SDK method {method_name} belongs to {operation['resource_family']}, "
                f"not {resource_family}"
            )
        if operation.get("multipart_parameters"):
            raise ValueError(f"Multipart SDK method requires a specialized wrapper: {method_name}")

        parameters = tuple(
            _parameter_spec(record)
            for record in operation["path_parameters"] + operation["query_parameters"]
        )
        context = cast(
            Literal["required", "optional", "none"],
            operation["context"],
        )
        command_name = command_names[method_name]
        specs.append(
            CommandSpec(
                name=command_name,
                sdk_method=method_name,
                help=f"{command_name.replace('-', ' ').capitalize()} {resource_family.replace('-', ' ')}.",
                context=context,
                parameters=parameters,
                body=_body_spec(operation["body_parameters"]),
                mutation=_mutation_kind(operation),
            )
        )
    return tuple(specs)
