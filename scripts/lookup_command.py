#!/usr/bin/env python3
"""Look up exact Apple Ads CLI operations without probing a live API."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from _command_catalog import (
    DEFAULT_MANIFEST,
    catalog_entries,
    load_manifest,
    render_entry,
    render_runtime_command,
    request_model_records,
    search_entries,
)
from _runtime_catalog import search_runtime_commands, v5_commands, workflow_commands


def _contains_all_query_tokens(searchable_text: str, query: str) -> bool:
    tokens = re.findall(r"[a-z0-9]+", query.lower().replace("-", " ").replace("_", " "))
    corpus = searchable_text.lower().replace("-", " ").replace("_", " ")
    return bool(tokens) and all(token in corpus for token in tokens)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("query", nargs="?", help="Natural-language operation description")
    parser.add_argument("--sdk-method", help="Exact Apple SDK method")
    parser.add_argument("--resource", help="Exact manifest resource family")
    parser.add_argument("--command", help="Exact canonical CLI command path")
    parser.add_argument(
        "--version",
        choices=("all", "v1", "v5", "workflows"),
        default="all",
        help="Limit lookup to one public command surface",
    )
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--json", action="store_true", help="Emit machine-readable results")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    selectors = [args.query, args.sdk_method, args.resource, args.command]
    if sum(value is not None for value in selectors) != 1:
        print("Provide exactly one query, --sdk-method, --resource, or --command.", file=sys.stderr)
        return 2
    try:
        manifest = load_manifest(args.manifest)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    v1_matches = []
    if args.version in {"all", "v1"}:
        v1_matches = search_entries(
            catalog_entries(manifest),
            query=args.query,
            sdk_method=args.sdk_method,
            resource=args.resource,
            command=args.command,
        )

    runtime_matches = []
    runtime_reference = ""
    if args.sdk_method is None and args.version in {"all", "v5"}:
        legacy = v5_commands()
        if args.command:
            runtime_matches.extend(item for item in legacy if item.path == args.command)
        elif args.resource:
            prefix = f"asa v5 {args.resource}"
            runtime_matches.extend(item for item in legacy if item.path.startswith(prefix))
        elif args.query:
            runtime_matches.extend(search_runtime_commands(legacy, args.query))
        if runtime_matches:
            runtime_reference = "references/v5-fallback.md"
    if args.sdk_method is None and args.version in {"all", "workflows"}:
        workflows = workflow_commands()
        workflow_matches = []
        if args.command:
            workflow_matches = [item for item in workflows if item.path == args.command]
        elif args.resource:
            prefix = f"asa workflows {args.resource}"
            workflow_matches = [item for item in workflows if item.path.startswith(prefix)]
        elif args.query:
            workflow_matches = search_runtime_commands(workflows, args.query)
        if workflow_matches:
            runtime_matches.extend(workflow_matches)
            if not runtime_reference:
                runtime_reference = "references/workflow-command-index.md"

    if args.query:
        full_v1 = [
            entry
            for entry in v1_matches
            if _contains_all_query_tokens(entry.searchable_text, args.query)
        ]
        full_runtime = [
            command
            for command in runtime_matches
            if _contains_all_query_tokens(command.searchable_text, args.query)
        ]
        if full_v1 or full_runtime:
            v1_matches = full_v1
            runtime_matches = full_runtime

    if not v1_matches and not runtime_matches:
        print("No registered operation matched. Do not guess command syntax.", file=sys.stderr)
        return 1

    if args.json:
        payload = [
            {
                "kind": "v1-sdk-endpoint",
                "sdk_method": entry.sdk_method,
                "resource": entry.resource,
                "command": entry.command,
                "usage": entry.usage,
                "status": entry.status,
                "reference": entry.reference,
                "http_method": entry.operation["http_method"],
                "resource_path": entry.operation["resource_path"],
                "context": entry.operation["context"],
                "mutation": entry.operation["mutation"],
                "pagination": entry.operation["pagination"],
                "body_parameters": entry.operation["body_parameters"],
                "return_annotation": entry.operation["return_annotation"],
                "request_models": dict(request_model_records(entry)),
                "cli_parameters": [parameter.__dict__ for parameter in entry.cli_parameters],
            }
            for entry in v1_matches
        ]
        payload.extend(
            {
                "kind": "v5-command" if command.path.startswith("asa v5 ") else "workflow",
                "command": command.path,
                "usage": command.usage,
                "help": command.help,
                "parameters": [parameter.__dict__ for parameter in command.parameters],
                "reference": (
                    "v5-fallback.md"
                    if command.path.startswith("asa v5 ")
                    else "workflow-command-index.md"
                ),
            }
            for command in runtime_matches
        )
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 0

    match_count = len(v1_matches) + len(runtime_matches)
    if match_count > 1:
        print(f"{match_count} operations matched; choose an exact command or SDK method:")
        for entry in v1_matches:
            print(
                f"- {entry.sdk_method}: {entry.command} "
                f"[{entry.status}; references/{entry.reference}]"
            )
        for command in runtime_matches:
            reference = (
                "v5-fallback.md"
                if command.path.startswith("asa v5 ")
                else "workflow-command-index.md"
            )
            print(f"- {command.path} [implemented; references/{reference}]")
        return 0

    if v1_matches:
        entry = v1_matches[0]
        print(render_entry(entry))
        print(f"\nReference: references/{entry.reference}")
    else:
        print(render_runtime_command(runtime_matches[0]))
        print(f"\nReference: {runtime_reference}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
