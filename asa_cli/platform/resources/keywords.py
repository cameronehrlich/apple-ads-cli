"""One-to-one Platform API commands for targeting keywords."""

import typer

from ..command_factory import register_commands
from ..manifest_specs import specs_from_manifest

SDK_METHODS = (
    "keywords_id_get",
    "keywords_query_post",
    "keywords_post",
    "keywords_id_put",
    "keywords_id_delete",
    "keywords_bulk_create_post",
    "keywords_bulk_update_post",
)
COMMAND_NAMES = {
    "keywords_id_get": "get",
    "keywords_query_post": "query",
    "keywords_post": "create",
    "keywords_id_put": "update",
    "keywords_id_delete": "delete",
    "keywords_bulk_create_post": "bulk-create",
    "keywords_bulk_update_post": "bulk-update",
}
COMMAND_SPECS = specs_from_manifest(
    resource_family="keywords",
    sdk_methods=SDK_METHODS,
    command_names=COMMAND_NAMES,
)

app = typer.Typer(help="Targeting keyword commands backed by Apple's official SDK.")
register_commands(app, COMMAND_SPECS)
