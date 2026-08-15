"""One-to-one Platform API commands for ad accounts."""

import typer

from ..command_factory import register_commands
from ..manifest_specs import specs_from_manifest

SDK_METHODS = (
    "ad_accounts_id_get",
    "ad_accounts_post",
    "ad_accounts_id_put",
)
COMMAND_NAMES = {
    "ad_accounts_id_get": "get",
    "ad_accounts_post": "create",
    "ad_accounts_id_put": "update",
}
COMMAND_SPECS = specs_from_manifest(
    resource_family="ad-accounts",
    sdk_methods=SDK_METHODS,
    command_names=COMMAND_NAMES,
)

app = typer.Typer(help="Ad account commands backed by Apple's official SDK.")
register_commands(app, COMMAND_SPECS)
