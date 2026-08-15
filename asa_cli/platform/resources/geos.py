"""One-to-one Platform API commands for geographic targeting search."""

import typer

from ..command_factory import register_commands
from ..manifest_specs import specs_from_manifest

SDK_METHODS = (
    "get_geos_by_ids",
    "search_geos",
)
COMMAND_NAMES = {
    "get_geos_by_ids": "get-by-ids",
    "search_geos": "search",
}
COMMAND_SPECS = specs_from_manifest(
    resource_family="geos",
    sdk_methods=SDK_METHODS,
    command_names=COMMAND_NAMES,
)

app = typer.Typer(help="Geographic targeting commands backed by Apple's official SDK.")
register_commands(app, COMMAND_SPECS)
