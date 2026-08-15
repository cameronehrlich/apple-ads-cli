"""Shared manifest-to-command catalog helpers for the Apple Ads CLI skill."""

from __future__ import annotations

import json
import re
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from _runtime_catalog import (
    RuntimeCommand,
    RuntimeParameter,
    platform_registrations,
    v5_commands,
    workflow_commands,
)

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = (
    REPOSITORY_ROOT
    / "asa_cli"
    / "platform"
    / "manifest"
    / "apple_ads_platform_v1_109_0.json"
)
REFERENCES_DIR = REPOSITORY_ROOT / "references"

GENERATED_NOTICE = (
    "<!-- Generated from the canonical SDK manifest and registered Typer trees. "
    "Do not edit by hand. -->"
)

REFERENCE_GROUPS: tuple[tuple[str, str, tuple[str, ...]], ...] = (
    (
        "v1-recommendations-and-suggestions.md",
        "Recommendations and suggestions",
        ("recommendation", "suggestion"),
    ),
    (
        "v1-change-history.md",
        "Change history",
        ("audit", "change-detail", "change_details", "change-history"),
    ),
    (
        "v1-insights.md",
        "Insights",
        ("impression-share", "impression_share", "search-term-popularity", "search_term_popularity"),
    ),
    (
        "v1-reports.md",
        "Reports",
        ("report", "reporting"),
    ),
    (
        "v1-negative-keywords.md",
        "Negative keywords",
        ("negative-keyword", "negative_keyword"),
    ),
    (
        "v1-keywords.md",
        "Targeting keywords",
        ("keyword",),
    ),
    (
        "v1-shared-budgets.md",
        "Shared budgets",
        ("shared-budget", "shared_budget"),
    ),
    (
        "v1-ad-groups.md",
        "Ad groups",
        ("adgroup", "ad-group", "ad_group"),
    ),
    (
        "v1-campaigns.md",
        "Campaigns",
        ("campaign",),
    ),
    (
        "v1-ads-and-creatives.md",
        "Ads and creatives",
        ("creative", "rejection-reason", "rejection_reason", "ads"),
    ),
    (
        "v1-assets.md",
        "Assets",
        ("asset",),
    ),
    (
        "v1-maps-locations-and-geo.md",
        "Maps locations and geo",
        ("location", "geo"),
    ),
    (
        "v1-maps-brands-and-categories.md",
        "Maps brands and categories",
        ("brand", "business-category", "business_category", "categor"),
    ),
    (
        "v1-apps-and-product-pages.md",
        "Apps and product pages",
        (
            "app-",
            "apps",
            "app_",
            "product-page",
            "product_page",
            "eligibilit",
            "supported-language",
            "supported_language",
        ),
    ),
    (
        "v1-accounts-and-access.md",
        "Accounts and access",
        (
            "account",
            "advertiser-resource",
            "advertiser_resource",
            "org",
            "acl",
            "delegation",
            "policy-assignment",
            "policy_assignment",
            "get-me",
            "get_me",
            "access",
        ),
    ),
)

REFERENCE_BY_RESOURCE = {
    "access": "v1-accounts-and-access.md",
    "ad-accounts": "v1-accounts-and-access.md",
    "ad-groups": "v1-ad-groups.md",
    "ads": "v1-ads-and-creatives.md",
    "apps": "v1-apps-and-product-pages.md",
    "assets": "v1-assets.md",
    "business-brands": "v1-maps-brands-and-categories.md",
    "business-categories": "v1-maps-brands-and-categories.md",
    "campaigns": "v1-campaigns.md",
    "change-history": "v1-change-history.md",
    "creatives": "v1-ads-and-creatives.md",
    "geos": "v1-maps-locations-and-geo.md",
    "insights": "v1-insights.md",
    "keywords": "v1-keywords.md",
    "location-groups": "v1-maps-locations-and-geo.md",
    "locations": "v1-maps-locations-and-geo.md",
    "negative-keywords": "v1-negative-keywords.md",
    "product-pages": "v1-apps-and-product-pages.md",
    "recommendations": "v1-recommendations-and-suggestions.md",
    "rejection-reasons": "v1-ads-and-creatives.md",
    "reports-apps": "v1-reports.md",
    "reports-business-brands": "v1-reports.md",
    "shared-budgets": "v1-shared-budgets.md",
    "suggestions": "v1-recommendations-and-suggestions.md",
}

ALL_GENERATED_REFERENCES = (
    "command-index.md",
    *(group[0] for group in REFERENCE_GROUPS),
    "v1-other.md",
    "v5-fallback.md",
    "workflow-command-index.md",
    "migration-map.md",
)


def _slug(value: str) -> str:
    value = re.sub(r"([a-z0-9])([A-Z])", r"\1-\2", value)
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def load_manifest(path: Path = DEFAULT_MANIFEST) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text())
    except FileNotFoundError as exc:
        raise ValueError(f"Canonical manifest not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON manifest {path}: {exc}") from exc

    required = {
        "schema_version",
        "sdk",
        "operations",
        "request_models",
        "response_models",
    }
    missing = sorted(required.difference(payload))
    if missing:
        raise ValueError(f"Manifest is missing top-level fields: {', '.join(missing)}")
    if not isinstance(payload["operations"], list):
        raise ValueError("Manifest operations must be a list")

    seen: set[str] = set()
    for operation in payload["operations"]:
        for field in (
            "sdk_method",
            "resource_family",
            "http_method",
            "resource_path",
            "signature",
            "context",
            "body_parameters",
            "return_annotation",
            "response_model",
            "mutation",
            "pagination",
            "special_handling",
            "aliases",
        ):
            if field not in operation:
                raise ValueError(
                    f"Operation {operation.get('sdk_method', '<unknown>')} is missing {field}"
                )
        method = operation["sdk_method"]
        if method in seen:
            raise ValueError(f"Duplicate SDK method in manifest: {method}")
        seen.add(method)
    return payload


def _cli_metadata(operation: dict[str, Any]) -> dict[str, Any]:
    cli = operation.get("cli")
    return cli if isinstance(cli, dict) else {}


def _command_from_aliases(operation: dict[str, Any]) -> str | None:
    for alias in operation.get("aliases", []):
        candidate = alias if isinstance(alias, str) else alias.get("command")
        if isinstance(candidate, str) and candidate.startswith("asa "):
            return candidate
    return None


def _derive_action(operation: dict[str, Any]) -> str:
    method = operation["sdk_method"]
    family = _slug(operation["resource_family"])
    normalized = method.lower()
    prefixes = {
        family.replace("-", "_"),
        family.rstrip("s").replace("-", "_"),
        family.replace("-", ""),
        family.rstrip("s").replace("-", ""),
    }
    for prefix in sorted(prefixes, key=len, reverse=True):
        if normalized.startswith(prefix + "_"):
            normalized = normalized[len(prefix) + 1 :]
            break

    replacements = (
        ("bulk_create_post", "bulk-create"),
        ("bulk_update_post", "bulk-update"),
        ("query_post", "query"),
        ("id_get", "get"),
        ("id_put", "update"),
        ("id_delete", "delete"),
    )
    for suffix, action in replacements:
        if normalized == suffix or normalized.endswith("_" + suffix):
            prefix = normalized[: -len(suffix)].strip("_")
            return "-".join(part for part in (_slug(prefix), action) if part)

    if normalized == "post":
        return "create"

    semantic_families = {
        "assets": ("asset", "assets"),
        "business-brands": ("brand", "brands"),
        "business-categories": ("category", "categories"),
        "geos": ("geo", "geos"),
        "location-groups": ("location_group", "location_groups"),
        "locations": ("location", "locations"),
        "product-pages": ("product_page", "product_pages"),
    }
    for noun in semantic_families.get(family, ()):
        for verb in ("get", "query", "create", "update", "delete", "upload", "search"):
            if normalized == f"{verb}_{noun}":
                return verb

    if family == "insights" and normalized.endswith("_query"):
        return _slug(normalized[: -len("_query")])

    if family == "recommendations":
        for verb in ("apply", "dismiss", "query"):
            prefix = verb + "_"
            suffix = "_recommendations"
            if normalized.startswith(prefix) and normalized.endswith(suffix):
                subject = normalized[len(prefix) : -len(suffix)]
                return f"{_slug(subject)}-{verb}"

    if family == "suggestions" and normalized.startswith("query_"):
        return _slug(normalized[len("query_") :])

    report_prefix = {
        "reports-apps": "apps_",
        "reports-business-brands": "brands_",
    }.get(family)
    if report_prefix and normalized.startswith(report_prefix) and normalized.endswith("_reports"):
        return _slug(normalized[len(report_prefix) : -len("_reports")])

    if normalized.startswith("get_"):
        return "get-" + _slug(normalized[4:])
    if normalized.startswith("query_"):
        return "query-" + _slug(normalized[6:])
    if normalized.startswith("create_"):
        return "create-" + _slug(normalized[7:])
    if normalized.startswith("update_"):
        return "update-" + _slug(normalized[7:])
    if normalized.startswith("delete_"):
        return "delete-" + _slug(normalized[7:])
    return _slug(normalized)


def command_for(operation: dict[str, Any]) -> str:
    cli = _cli_metadata(operation)
    command_path = cli.get("command_path")
    if isinstance(command_path, list) and all(isinstance(item, str) for item in command_path):
        return " ".join(command_path)
    if isinstance(command_path, str):
        return command_path
    alias = _command_from_aliases(operation)
    if alias:
        return alias
    return f"asa {_slug(operation['resource_family'])} {_derive_action(operation)}"


def status_for(operation: dict[str, Any]) -> str:
    cli = _cli_metadata(operation)
    return str(cli.get("implementation_status", operation.get("implementation_status", "inventory-only")))


def usage_for(operation: dict[str, Any]) -> str:
    cli = _cli_metadata(operation)
    usage = cli.get("usage")
    if isinstance(usage, str):
        return usage
    return command_for(operation)


def reference_for(operation: dict[str, Any]) -> str:
    cli = _cli_metadata(operation)
    explicit = cli.get("reference")
    if isinstance(explicit, str):
        return explicit
    exact = REFERENCE_BY_RESOURCE.get(_slug(operation["resource_family"]))
    if exact:
        return exact
    corpus = " ".join(
        (
            _slug(operation["resource_family"]),
            _slug(operation["sdk_method"]),
            _slug(operation["resource_path"]),
        )
    )
    for filename, _title, needles in REFERENCE_GROUPS:
        if any(needle in corpus for needle in needles):
            return filename
    return "v1-other.md"


def _format_value(value: Any) -> str:
    if value is None:
        return "none"
    if isinstance(value, bool):
        return "yes" if value else "no"
    if isinstance(value, (dict, list)):
        return json.dumps(value, sort_keys=True, separators=(",", ":"))
    return str(value)


def required_parameters(operation: dict[str, Any]) -> list[str]:
    return [
        parameter["name"]
        for parameter in operation.get("signature", [])
        if parameter.get("required")
    ]


@dataclass(frozen=True)
class CatalogEntry:
    sdk_method: str
    resource: str
    command: str
    usage: str
    status: str
    reference: str
    operation: dict[str, Any]
    request_models: dict[str, Any]
    cli_help: str = ""
    cli_parameters: tuple[RuntimeParameter, ...] = ()
    runtime_registered: bool = False

    @property
    def searchable_text(self) -> str:
        operation = self.operation
        aliases = " ".join(
            alias if isinstance(alias, str) else json.dumps(alias, sort_keys=True)
            for alias in operation.get("aliases", [])
        )
        return " ".join(
            (
                self.sdk_method,
                self.resource,
                self.command,
                operation["resource_path"],
                operation["http_method"],
                aliases,
            )
        ).lower()


def catalog_entries(
    manifest: dict[str, Any], *, include_runtime: bool = True
) -> list[CatalogEntry]:
    runtime = platform_registrations() if include_runtime else {}
    manifest_methods = {operation["sdk_method"] for operation in manifest["operations"]}
    if include_runtime and set(runtime) != manifest_methods:
        missing = sorted(manifest_methods.difference(runtime))
        extra = sorted(set(runtime).difference(manifest_methods))
        raise ValueError(
            f"Platform runtime/manifest mismatch; missing={missing}, extra={extra}"
        )

    entries = [
        CatalogEntry(
            sdk_method=operation["sdk_method"],
            resource=operation["resource_family"],
            command=(runtime[operation["sdk_method"]].path if runtime else command_for(operation)),
            usage=(runtime[operation["sdk_method"]].usage if runtime else usage_for(operation)),
            status="implemented" if runtime else status_for(operation),
            reference=reference_for(operation),
            operation=operation,
            request_models=manifest["request_models"],
            cli_help=(runtime[operation["sdk_method"]].help if runtime else ""),
            cli_parameters=(runtime[operation["sdk_method"]].parameters if runtime else ()),
            runtime_registered=bool(runtime),
        )
        for operation in manifest["operations"]
    ]
    entries.sort(key=lambda entry: (entry.reference, entry.command, entry.sdk_method))
    return entries


def _resolve_schema_ref(root: dict[str, Any], reference: str) -> dict[str, Any]:
    if not reference.startswith("#/"):
        return {}
    value: Any = root
    for part in reference[2:].split("/"):
        if not isinstance(value, dict):
            return {}
        value = value.get(part.replace("~1", "/").replace("~0", "~"))
    return value if isinstance(value, dict) else {}


def _schema_type(schema: dict[str, Any]) -> str:
    if "$ref" in schema:
        return schema["$ref"].split("/")[-1]
    if "type" in schema:
        if schema["type"] == "array":
            return f"array[{_schema_type(schema.get('items', {}))}]"
        return str(schema["type"])
    if "anyOf" in schema:
        types = [_schema_type(option) for option in schema["anyOf"]]
        return " | ".join(dict.fromkeys(types))
    return "any"


def _schema_skeleton(schema: dict[str, Any], root: dict[str, Any]) -> Any:
    if "$ref" in schema:
        return _schema_skeleton(_resolve_schema_ref(root, schema["$ref"]), root)
    if "anyOf" in schema:
        candidates = [option for option in schema["anyOf"] if option.get("type") != "null"]
        return _schema_skeleton(candidates[0], root) if candidates else None
    if schema.get("enum"):
        return f"<one of: {' | '.join(map(str, schema['enum']))}>"
    schema_type = schema.get("type")
    if schema_type == "object" or "properties" in schema:
        required = set(schema.get("required", []))
        selected = required or {
            name for name in schema.get("properties", {}) if name != "additional_properties"
        }
        return {
            name: _schema_skeleton(field, root)
            for name, field in schema.get("properties", {}).items()
            if name in selected and name != "additional_properties"
        }
    if schema_type == "array":
        return [_schema_skeleton(schema.get("items", {}), root)]
    if schema_type in {"integer", "number"}:
        return 0
    if schema_type == "boolean":
        return False
    if schema_type == "null":
        return None
    return "<string>"


def request_model_records(entry: CatalogEntry) -> list[tuple[str, dict[str, Any]]]:
    records: list[tuple[str, dict[str, Any]]] = []
    for parameter in entry.operation.get("body_parameters", []):
        model = parameter.get("model")
        if isinstance(model, str) and model in entry.request_models:
            records.append((model, entry.request_models[model]))
    return records


def _markdown_cell(value: Any) -> str:
    return " ".join(str(value).split()).replace("|", "\\|")


def _render_field_table(schema: dict[str, Any]) -> list[str]:
    required = set(schema.get("required", []))
    lines = [
        "| Field | Required | Type | Default | Description |",
        "|---|---|---|---|---|",
    ]
    for name, field in schema.get("properties", {}).items():
        if name == "additional_properties":
            continue
        default = field.get("default", "—")
        lines.append(
            "| "
            + " | ".join(
                (
                    f"`{name}`",
                    "yes" if name in required else "no",
                    f"`{_schema_type(field)}`",
                    f"`{_markdown_cell(default)}`" if default != "—" else "—",
                    _markdown_cell(field.get("description", "")),
                )
            )
            + " |"
        )
    return lines


def render_request_model(
    model: str,
    record: dict[str, Any],
    *,
    container: str = "model",
) -> str:
    schema = record.get("schema", {})
    lines = [
        f"### Request model `{model}`",
        "",
        _markdown_cell(schema.get("description", "No model description provided.")),
        "",
        f"- Schema SHA-256: `{record.get('schema_sha256', 'unknown')}`",
        f"- Source SHA-256: `{record.get('source_sha256', 'unknown')}`",
        "",
        *_render_field_table(schema),
    ]
    skeleton = _schema_skeleton(schema, schema)
    if container == "list":
        skeleton = [skeleton]
    lines.extend(
        (
            "",
            "Required-field body skeleton (replace every placeholder and add optional fields only as needed):",
            "",
            "```json",
            json.dumps(skeleton, indent=2, sort_keys=True),
            "```",
        )
    )
    definitions = schema.get("$defs", {})
    if definitions:
        lines.extend(("", "#### Referenced structures"))
        for name, definition in sorted(definitions.items()):
            lines.extend(
                (
                    "",
                    f"##### `{name}`",
                    "",
                    _markdown_cell(definition.get("description", "")),
                    "",
                    *_render_field_table(definition),
                )
            )
    return "\n".join(lines)


def _render_cli_parameter_table(parameters: tuple[RuntimeParameter, ...]) -> list[str]:
    lines = [
        "| Kind | Name or flags | Required | Type | Default | Environment | Help |",
        "|---|---|---|---|---|---|---|",
    ]
    for parameter in parameters:
        declarations = ", ".join(f"`{item}`" for item in parameter.declarations)
        lines.append(
            "| "
            + " | ".join(
                (
                    parameter.kind,
                    declarations,
                    "yes" if parameter.required else "no",
                    f"`{parameter.type_name}`",
                    f"`{_markdown_cell(parameter.default)}`"
                    if parameter.default is not None
                    else "—",
                    f"`{parameter.envvar}`" if parameter.envvar else "—",
                    _markdown_cell(parameter.help),
                )
            )
            + " |"
        )
    return lines


def render_runtime_command(command: RuntimeCommand) -> str:
    lines = [
        f"## `{command.path}`",
        "",
        command.help or "No additional command description.",
        "",
        f"- Usage: `{command.usage}`",
    ]
    if command.parameters:
        lines.extend(("", "### Inputs", "", *_render_cli_parameter_table(command.parameters)))
    else:
        lines.extend(("", "This command has no command-specific inputs."))
    return "\n".join(lines)


def render_entry(entry: CatalogEntry) -> str:
    operation = entry.operation
    required = required_parameters(operation)
    cli = _cli_metadata(operation)
    aliases = operation.get("aliases", [])
    lines = [
        f"## `{entry.sdk_method}`",
        "",
        f"- Status: `{entry.status}`",
        f"- Canonical command: `{entry.command}`",
        f"- Usage: `{entry.usage}`",
        f"- SDK contract: `{operation['http_method']} {operation['resource_path']}`",
        f"- Context: `{operation['context']}`",
        f"- Mutation: `{_format_value(operation['mutation'])}`",
        f"- Pagination: `{_format_value(operation['pagination'])}`",
        f"- Required SDK parameters: `{', '.join(required) if required else 'none'}`",
        f"- Body parameters: `{_format_value(operation['body_parameters'])}`",
        f"- Returns: `{operation['return_annotation']}`",
    ]
    if entry.cli_help:
        lines.append(f"- CLI help: {_markdown_cell(entry.cli_help)}")
    if entry.cli_parameters:
        lines.extend(("", "### Exact CLI inputs", "", *_render_cli_parameter_table(entry.cli_parameters)))
    if aliases:
        lines.append(f"- Aliases: `{_format_value(aliases)}`")
    if operation.get("special_handling"):
        lines.append(f"- Special handling: `{_format_value(operation['special_handling'])}`")
    if cli.get("input_example"):
        lines.extend(("", "Input example:", "", "```json", cli["input_example"], "```"))
    elif request_model_records(entry):
        rendered_models = []
        for model, record in request_model_records(entry):
            body_parameter = next(
                parameter
                for parameter in operation["body_parameters"]
                if parameter.get("model") == model
            )
            rendered_models.append(
                render_request_model(
                    model,
                    record,
                    container=str(body_parameter.get("container", "model")),
                )
            )
        lines.extend(("", "\n\n".join(rendered_models)))
    if cli.get("verification"):
        lines.extend(("", f"Verification: {cli['verification']}"))
    if entry.status == "inventory-only":
        lines.extend(
            (
                "",
                "This entry proves SDK inventory only. Do not execute the planned command until runtime registration is recorded in the manifest.",
            )
        )
    return "\n".join(lines)


def _sdk_heading(manifest: dict[str, Any]) -> list[str]:
    sdk = manifest["sdk"]
    return [
        f"SDK `{sdk.get('distribution', 'unknown')}` version `{sdk.get('version', 'unknown')}`; "
        f"source commit `{sdk.get('git_commit', 'unknown')}`.",
        "",
        "`implemented` means registered and contract-tested locally; it does not mean live Apple acceptance.",
        "",
    ]


def render_reference_files(
    manifest: dict[str, Any], *, include_runtime: bool = True
) -> dict[str, str]:
    entries = catalog_entries(manifest, include_runtime=include_runtime)
    legacy_commands = v5_commands() if include_runtime else ()
    workflow_inventory = workflow_commands() if include_runtime else ()
    rendered: dict[str, str] = {}

    index_lines = [
        GENERATED_NOTICE,
        "",
        "# Apple Ads v1 command index",
        "",
        *_sdk_heading(manifest),
        "Every entry below is reconciled to the default public Typer registration. "
        "`implemented` proves local registration and contract coverage, not live Apple acceptance.",
        "",
        "| Resource | SDK method | Canonical command | Status | Reference |",
        "|---|---|---|---|---|",
    ]
    for entry in sorted(entries, key=lambda item: (item.resource, item.sdk_method)):
        index_lines.append(
            f"| {entry.resource} | `{entry.sdk_method}` | `{entry.command}` | `{entry.status}` | [{entry.reference}]({entry.reference}) |"
        )
    rendered["command-index.md"] = "\n".join(index_lines) + "\n"

    group_titles = {filename: title for filename, title, _needles in REFERENCE_GROUPS}
    group_titles["v1-other.md"] = "Other v1 operations"
    for filename, title in group_titles.items():
        group_entries = [entry for entry in entries if entry.reference == filename]
        lines = [
            GENERATED_NOTICE,
            "",
            f"# {title}",
            "",
            *_sdk_heading(manifest),
        ]
        if not group_entries:
            lines.append("No operations from the pinned manifest route to this reference.")
        else:
            lines.extend(("## Contents", ""))
            lines.extend(f"- [`{entry.sdk_method}`](#{entry.sdk_method.replace('_', '-')})" for entry in group_entries)
            lines.append("")
            lines.append("\n\n".join(render_entry(entry) for entry in group_entries))
        rendered[filename] = "\n".join(lines).rstrip() + "\n"

    fallback_lines = [
        GENERATED_NOTICE,
        "",
        "# Legacy v5 command inventory",
        "",
        f"This frozen namespace contains {len(legacy_commands)} public command leaves. "
        "The inventory proves local registration only; it does not prove live API acceptance.",
        "",
        "## Contents",
        "",
    ]
    fallback_lines.extend(f"- `{command.path}`" for command in legacy_commands)
    if legacy_commands:
        fallback_lines.extend(("", "\n\n".join(render_runtime_command(command) for command in legacy_commands)))
    else:
        fallback_lines.append("- _No public v5 commands registered._")
    rendered["v5-fallback.md"] = "\n".join(fallback_lines).rstrip() + "\n"

    workflow_lines = [
        GENERATED_NOTICE,
        "",
        "# Workflow command inventory",
        "",
        f"This namespace contains {len(workflow_inventory)} public command leaves. "
        "Workflows are higher-level local logic, not one-to-one SDK endpoint coverage.",
        "",
        "## Contents",
        "",
    ]
    workflow_lines.extend(f"- `{command.path}`" for command in workflow_inventory)
    if workflow_inventory:
        workflow_lines.extend(
            ("", "\n\n".join(render_runtime_command(command) for command in workflow_inventory))
        )
    else:
        workflow_lines.append("- _No public workflow commands registered._")
    rendered["workflow-command-index.md"] = "\n".join(workflow_lines).rstrip() + "\n"

    migration_lines = [
        GENERATED_NOTICE,
        "",
        "# v5 to v1 migration map",
        "",
        "Implementation status is local only and does not imply live Apple acceptance.",
        "",
        "| v1 SDK method | Canonical v1 command | Status | v5 fallback |",
        "|---|---|---|---|",
    ]
    for entry in sorted(entries, key=lambda item: item.sdk_method):
        fallback = _cli_metadata(entry.operation).get("v5_fallback", "—")
        migration_lines.append(
            f"| `{entry.sdk_method}` | `{entry.command}` | `{entry.status}` | `{fallback}` |"
        )
    rendered["migration-map.md"] = "\n".join(migration_lines) + "\n"
    return rendered


def search_entries(
    entries: Iterable[CatalogEntry],
    *,
    query: str | None = None,
    sdk_method: str | None = None,
    resource: str | None = None,
    command: str | None = None,
) -> list[CatalogEntry]:
    entries = list(entries)
    if sdk_method:
        return [entry for entry in entries if entry.sdk_method == sdk_method]
    if command:
        normalized = " ".join(command.lower().split())
        return [entry for entry in entries if " ".join(entry.command.lower().split()) == normalized]
    if resource:
        normalized = _slug(resource)
        return [entry for entry in entries if _slug(entry.resource) == normalized]
    if not query:
        return []

    normalized_query = query.lower().replace("-", " ").replace("_", " ")
    tokens = [token for token in re.findall(r"[a-z0-9]+", normalized_query) if token]
    scored: list[tuple[int, CatalogEntry]] = []
    for entry in entries:
        corpus = entry.searchable_text.replace("-", " ").replace("_", " ")
        if normalized_query in corpus:
            score = 100 + len(tokens)
        else:
            matched = sum(token in corpus for token in tokens)
            if not matched:
                continue
            score = matched * 10 - (len(tokens) - matched) * 3
        scored.append((score, entry))
    if not scored:
        return []
    best = max(score for score, _entry in scored)
    return [entry for score, entry in scored if score == best]
