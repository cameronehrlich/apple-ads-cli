"""One-to-one Platform API change-history commands."""

import typer

from ..command_factory import register_commands
from ..manifest_specs import specs_from_manifest

SDK_METHODS = (
    "get_change_details",
    "query_audit_summary",
)
COMMAND_NAMES = {
    "get_change_details": "get",
    "query_audit_summary": "query",
}
COMMAND_SPECS = specs_from_manifest(
    resource_family="change-history",
    sdk_methods=SDK_METHODS,
    command_names=COMMAND_NAMES,
)

app = typer.Typer(help="Audit-summary and field-level change-history commands.")
register_commands(app, COMMAND_SPECS)
