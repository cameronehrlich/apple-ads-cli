"""One-to-one Platform API commands for Apple Maps business categories."""

import typer

from ..command_factory import register_commands
from ..manifest_specs import specs_from_manifest

SDK_METHODS = (
    "get_category",
    "query_categories",
)
COMMAND_NAMES = {
    "get_category": "get",
    "query_categories": "query",
}
COMMAND_SPECS = specs_from_manifest(
    resource_family="business-categories",
    sdk_methods=SDK_METHODS,
    command_names=COMMAND_NAMES,
)

app = typer.Typer(help="Apple Maps business category commands backed by Apple's official SDK.")
register_commands(app, COMMAND_SPECS)
