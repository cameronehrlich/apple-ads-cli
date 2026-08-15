"""One-to-one Platform API commands for Apple Maps locations."""

import typer

from ..command_factory import register_commands
from ..manifest_specs import specs_from_manifest

SDK_METHODS = (
    "get_location",
    "query_locations",
)
COMMAND_NAMES = {
    "get_location": "get",
    "query_locations": "query",
}
COMMAND_SPECS = specs_from_manifest(
    resource_family="locations",
    sdk_methods=SDK_METHODS,
    command_names=COMMAND_NAMES,
)

app = typer.Typer(help="Apple Maps location commands backed by Apple's official SDK.")
register_commands(app, COMMAND_SPECS)
