"""One-to-one Platform API commands for Apple Maps location groups."""

import typer

from ..command_factory import register_commands
from ..manifest_specs import specs_from_manifest

SDK_METHODS = (
    "get_location_group",
    "query_location_groups",
    "create_location_group",
    "update_location_group",
    "delete_location_group",
)
COMMAND_NAMES = {
    "get_location_group": "get",
    "query_location_groups": "query",
    "create_location_group": "create",
    "update_location_group": "update",
    "delete_location_group": "delete",
}
COMMAND_SPECS = specs_from_manifest(
    resource_family="location-groups",
    sdk_methods=SDK_METHODS,
    command_names=COMMAND_NAMES,
)

app = typer.Typer(help="Apple Maps location group commands backed by Apple's official SDK.")
register_commands(app, COMMAND_SPECS)
