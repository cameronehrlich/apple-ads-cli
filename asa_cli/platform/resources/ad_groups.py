"""One-to-one Platform API commands for ad groups."""

import typer

from ..command_factory import register_commands
from ..manifest_specs import specs_from_manifest

SDK_METHODS = (
    "adgroups_id_get",
    "adgroups_query_post",
    "adgroups_post",
    "adgroups_id_put",
    "adgroups_id_delete",
)
COMMAND_NAMES = {
    "adgroups_id_get": "get",
    "adgroups_query_post": "query",
    "adgroups_post": "create",
    "adgroups_id_put": "update",
    "adgroups_id_delete": "delete",
}
COMMAND_SPECS = specs_from_manifest(
    resource_family="ad-groups",
    sdk_methods=SDK_METHODS,
    command_names=COMMAND_NAMES,
)

app = typer.Typer(help="Ad group commands backed by Apple's official SDK.")
register_commands(app, COMMAND_SPECS)
