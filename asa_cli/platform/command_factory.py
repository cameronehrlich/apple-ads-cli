"""Build exact Typer commands around canonical official-SDK operations."""

from __future__ import annotations

import inspect
import json
from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal

import typer

from .client import (
    PlatformConfigurationError,
    resolve_ad_account_id,
    resolve_optional_ad_account_id,
)
from .runtime import (
    PlatformAPIError,
    hydrate_model,
    invoke,
    read_json_payload,
    serialize_response,
)

MutationKind = Literal[
    "read",
    "create",
    "update",
    "delete",
    "apply",
    "dismiss",
    "upload",
]


@dataclass(frozen=True)
class ParameterSpec:
    """A scalar SDK parameter exposed as a precise CLI option."""

    name: str
    flag: str
    annotation: Any = str
    required: bool = True
    help: str = ""
    default: Any = None
    path_exists: bool = False
    allowed_file_types: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class BodySpec:
    """A JSON request body hydrated into an official SDK model."""

    parameter: str
    model: str
    required: bool = True
    many: bool = False


@dataclass(frozen=True)
class CommandSpec:
    """One public CLI command mapped to exactly one canonical SDK method."""

    name: str
    sdk_method: str
    help: str
    context: Literal["required", "optional", "none"] = "required"
    parameters: tuple[ParameterSpec, ...] = field(default_factory=tuple)
    body: BodySpec | None = None
    mutation: MutationKind = "read"


def _parameter_signature(spec: CommandSpec) -> inspect.Signature:
    parameters: list[inspect.Parameter] = []
    for item in spec.parameters:
        default = ... if item.required else item.default
        parameters.append(
            inspect.Parameter(
                item.name,
                inspect.Parameter.KEYWORD_ONLY,
                annotation=item.annotation,
                default=typer.Option(
                    default,
                    item.flag,
                    help=item.help,
                    exists=item.path_exists,
                    file_okay=True,
                    dir_okay=not item.path_exists,
                    readable=item.path_exists,
                    resolve_path=item.path_exists,
                ),
            )
        )

    if spec.body is not None:
        file_default = ... if spec.body.required else None
        parameters.append(
            inspect.Parameter(
                "request_file",
                inspect.Parameter.KEYWORD_ONLY,
                annotation=Path if spec.body.required else Path | None,
                default=typer.Option(
                    file_default,
                    "--file",
                    help="JSON request file; use '-' to read from stdin",
                ),
            )
        )

    if spec.context != "none":
        parameters.append(
            inspect.Parameter(
                "ad_account_id",
                inspect.Parameter.KEYWORD_ONLY,
                annotation=str | None,
                default=typer.Option(
                    None,
                    "--ad-account",
                    envvar="ASA_AD_ACCOUNT_ID",
                    help="Apple Ads Platform ad account ID",
                ),
            )
        )

    if spec.mutation != "read":
        parameters.extend(
            [
                inspect.Parameter(
                    "dry_run",
                    inspect.Parameter.KEYWORD_ONLY,
                    annotation=bool,
                    default=typer.Option(
                        False,
                        "--dry-run",
                        help="Validate and print the SDK call without sending it",
                    ),
                ),
                inspect.Parameter(
                    "confirm",
                    inspect.Parameter.KEYWORD_ONLY,
                    annotation=bool,
                    default=typer.Option(
                        False,
                        "--confirm",
                        help="Confirm this Apple Ads mutation",
                    ),
                ),
            ]
        )

    return inspect.Signature(parameters)


def _preview(
    spec: CommandSpec,
    arguments: dict[str, Any],
    *,
    ad_account_id: str | None,
) -> dict[str, Any]:
    return {
        "dry_run": True,
        "sdk_method": spec.sdk_method,
        "mutation": spec.mutation,
        "context": spec.context,
        "ad_account_id": ad_account_id,
        "arguments": arguments,
    }


def _resolve_context_account(spec: CommandSpec, explicit: str | None) -> str | None:
    try:
        if spec.context == "required":
            return resolve_ad_account_id(explicit=explicit)
        if spec.context == "optional":
            return resolve_optional_ad_account_id(explicit=explicit)
        return None
    except PlatformConfigurationError as exc:
        raise PlatformAPIError(str(exc)) from exc


def _validate_body_account(
    spec: CommandSpec,
    arguments: Mapping[str, Any],
    ad_account_id: str | None,
) -> None:
    """Prevent a scoped body from targeting a different account than the header."""
    if spec.body is None or ad_account_id is None:
        return
    body = arguments.get(spec.body.parameter)
    items = body if isinstance(body, list) else [body]
    for item in items:
        if not isinstance(item, Mapping):
            continue
        body_account_id = item.get("adAccountId")
        if body_account_id is None:
            body_account_id = item.get("ad_account_id")
        if body_account_id is not None and str(body_account_id) != ad_account_id:
            raise PlatformAPIError(
                "Request body adAccountId does not match the resolved --ad-account context"
            )


def _validate_file_content(path: Path, allowed_file_types: tuple[str, ...]) -> None:
    """Recognize the image formats accepted by Apple's asset upload endpoint."""
    if not allowed_file_types:
        return
    try:
        with path.open("rb") as file_handle:
            header = file_handle.read(12)
    except OSError as exc:
        raise PlatformAPIError(f"Unable to read upload file {path}: {exc}") from exc

    detected = None
    if header.startswith(b"\x89PNG\r\n\x1a\n"):
        detected = "png"
    elif header.startswith(b"\xff\xd8\xff"):
        detected = "jpeg"
    elif len(header) >= 12 and header[4:8] == b"ftyp" and header[8:12] in {
        b"heic",
        b"heix",
        b"hevc",
        b"hevx",
        b"mif1",
        b"msf1",
    }:
        detected = "heic"
    if detected not in allowed_file_types:
        choices = ", ".join(name.upper() for name in allowed_file_types)
        raise PlatformAPIError(f"Upload file must contain one of: {choices}")


def build_callback(spec: CommandSpec):
    """Create a Typer callback with an exact generated signature."""

    def callback(**values):
        request_file = values.pop("request_file", None)
        ad_account_id = values.pop("ad_account_id", None)
        dry_run = values.pop("dry_run", False)
        confirm = values.pop("confirm", False)

        try:
            parameter_specs = {parameter.name: parameter for parameter in spec.parameters}
            arguments = {}
            for key, value in values.items():
                if isinstance(value, Path):
                    _validate_file_content(
                        value,
                        parameter_specs[key].allowed_file_types,
                    )
                    arguments[key] = str(value)
                else:
                    arguments[key] = value
            if spec.body is not None and request_file is not None:
                payload = read_json_payload(request_file)
                arguments[spec.body.parameter] = hydrate_model(
                    spec.body.model,
                    payload,
                    many=spec.body.many,
                )

            effective_ad_account_id = _resolve_context_account(spec, ad_account_id)
            serialized_arguments = serialize_response(arguments)
            _validate_body_account(
                spec,
                serialized_arguments,
                effective_ad_account_id,
            )

            if spec.mutation != "read" and (dry_run or not confirm):
                typer.echo(
                    json.dumps(
                        _preview(
                            spec,
                            serialized_arguments,
                            ad_account_id=effective_ad_account_id,
                        ),
                        indent=2,
                        sort_keys=True,
                    )
                )
                if not dry_run and not confirm:
                    typer.echo(
                        "Mutation not sent. Re-run with --confirm after reviewing this request.",
                        err=True,
                    )
                return

            result = invoke(
                spec.sdk_method,
                arguments=arguments,
                context=spec.context,
                ad_account_id=effective_ad_account_id,
            )
        except PlatformAPIError as exc:
            error = {
                "error": {
                    "message": str(exc),
                    "status": exc.status,
                    "body": exc.body,
                }
            }
            typer.echo(json.dumps(error, indent=2, sort_keys=True), err=True)
            raise typer.Exit(1) from exc

        typer.echo(json.dumps(result, indent=2, sort_keys=True))

    callback.__name__ = spec.name.replace("-", "_")
    callback.__doc__ = spec.help
    callback.__signature__ = _parameter_signature(spec)
    return callback


def register_commands(app: typer.Typer, specs: tuple[CommandSpec, ...]) -> None:
    """Register a resource module's canonical SDK commands exactly once."""
    seen: set[str] = set()
    for spec in specs:
        if spec.name in seen:
            raise ValueError(f"Duplicate command name: {spec.name}")
        seen.add(spec.name)
        app.command(spec.name)(build_callback(spec))
