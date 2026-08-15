"""One-to-one Platform API commands for shared budgets."""

import typer

from ..command_factory import register_commands
from ..manifest_specs import specs_from_manifest

SDK_METHODS = (
    "shared_budgets_id_get",
    "shared_budgets_query_post",
    "shared_budgets_post",
    "shared_budgets_id_put",
    "shared_budgets_id_delete",
)
COMMAND_NAMES = {
    "shared_budgets_id_get": "get",
    "shared_budgets_query_post": "query",
    "shared_budgets_post": "create",
    "shared_budgets_id_put": "update",
    "shared_budgets_id_delete": "delete",
}
COMMAND_SPECS = specs_from_manifest(
    resource_family="shared-budgets",
    sdk_methods=SDK_METHODS,
    command_names=COMMAND_NAMES,
)

app = typer.Typer(help="Shared budget commands backed by Apple's official SDK.")
register_commands(app, COMMAND_SPECS)
