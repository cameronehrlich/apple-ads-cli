"""One-to-one Platform API commands for Apple Maps business brands."""

import typer

from ..command_factory import register_commands
from ..manifest_specs import specs_from_manifest

SDK_METHODS = (
    "get_brand",
    "query_brands",
)
COMMAND_NAMES = {
    "get_brand": "get",
    "query_brands": "query",
}
COMMAND_SPECS = specs_from_manifest(
    resource_family="business-brands",
    sdk_methods=SDK_METHODS,
    command_names=COMMAND_NAMES,
)

app = typer.Typer(help="Apple Maps business brand commands backed by Apple's official SDK.")
register_commands(app, COMMAND_SPECS)
