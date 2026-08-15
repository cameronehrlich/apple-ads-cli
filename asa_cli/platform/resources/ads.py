"""One-to-one Platform API commands for ads."""

import typer

from ..command_factory import register_commands
from ..manifest_specs import specs_from_manifest

SDK_METHODS = (
    "ads_id_get",
    "ads_query_post",
    "ads_post",
    "ads_id_put",
    "ads_id_delete",
)
COMMAND_NAMES = {
    "ads_id_get": "get",
    "ads_query_post": "query",
    "ads_post": "create",
    "ads_id_put": "update",
    "ads_id_delete": "delete",
}
COMMAND_SPECS = specs_from_manifest(
    resource_family="ads",
    sdk_methods=SDK_METHODS,
    command_names=COMMAND_NAMES,
)

app = typer.Typer(help="Ad resource commands backed by Apple's official SDK.")
register_commands(app, COMMAND_SPECS)
