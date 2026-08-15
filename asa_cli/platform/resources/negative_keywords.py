"""One-to-one Platform API commands for negative keywords."""

import typer

from ..command_factory import register_commands
from ..manifest_specs import specs_from_manifest

SDK_METHODS = (
    "negative_keywords_id_get",
    "negative_keywords_query_post",
    "negative_keywords_post",
    "negative_keywords_id_put",
    "negative_keywords_id_delete",
    "negative_keywords_bulk_create_post",
    "negative_keywords_bulk_update_post",
)
COMMAND_NAMES = {
    "negative_keywords_id_get": "get",
    "negative_keywords_query_post": "query",
    "negative_keywords_post": "create",
    "negative_keywords_id_put": "update",
    "negative_keywords_id_delete": "delete",
    "negative_keywords_bulk_create_post": "bulk-create",
    "negative_keywords_bulk_update_post": "bulk-update",
}
COMMAND_SPECS = specs_from_manifest(
    resource_family="negative-keywords",
    sdk_methods=SDK_METHODS,
    command_names=COMMAND_NAMES,
)

app = typer.Typer(help="Negative keyword commands backed by Apple's official SDK.")
register_commands(app, COMMAND_SPECS)
