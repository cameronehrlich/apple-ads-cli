"""One-to-one Platform API commands for creatives."""

import typer

from ..command_factory import register_commands
from ..manifest_specs import specs_from_manifest

SDK_METHODS = (
    "creatives_id_get",
    "creatives_query_post",
    "creatives_post",
    "creatives_id_put",
    "creatives_id_delete",
)
COMMAND_NAMES = {
    "creatives_id_get": "get",
    "creatives_query_post": "query",
    "creatives_post": "create",
    "creatives_id_put": "update",
    "creatives_id_delete": "delete",
}
COMMAND_SPECS = specs_from_manifest(
    resource_family="creatives",
    sdk_methods=SDK_METHODS,
    command_names=COMMAND_NAMES,
)

app = typer.Typer(help="Creative commands backed by Apple's official SDK.")
register_commands(app, COMMAND_SPECS)
