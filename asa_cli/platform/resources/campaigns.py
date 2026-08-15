"""One-to-one Platform API commands for campaigns."""

import typer

from ..command_factory import register_commands
from ..manifest_specs import specs_from_manifest

SDK_METHODS = (
    "campaigns_id_get",
    "campaigns_query_post",
    "campaigns_post",
    "campaigns_id_put",
    "campaigns_id_delete",
    "campaigns_id_legacy_app_limited_status_reason_details_get",
)
COMMAND_NAMES = {
    "campaigns_id_get": "get",
    "campaigns_query_post": "query",
    "campaigns_post": "create",
    "campaigns_id_put": "update",
    "campaigns_id_delete": "delete",
    "campaigns_id_legacy_app_limited_status_reason_details_get": (
        "legacy-app-limited-status-reasons"
    ),
}
COMMAND_SPECS = specs_from_manifest(
    resource_family="campaigns",
    sdk_methods=SDK_METHODS,
    command_names=COMMAND_NAMES,
)

app = typer.Typer(help="Campaign commands backed by Apple's official SDK.")
register_commands(app, COMMAND_SPECS)
