"""One-to-one Platform API commands for access and organization resources."""

import typer

from ..command_factory import register_commands
from ..manifest_specs import specs_from_manifest

SDK_METHODS = (
    "get_advertiser_resources",
    "orgs_id_get",
    "get_me",
    "get_user_acls",
)
COMMAND_NAMES = {
    "get_advertiser_resources": "advertiser-resources",
    "orgs_id_get": "org",
    "get_me": "me",
    "get_user_acls": "acls",
}
COMMAND_SPECS = specs_from_manifest(
    resource_family="access",
    sdk_methods=SDK_METHODS,
    command_names=COMMAND_NAMES,
)

app = typer.Typer(help="Access and organization commands backed by Apple's official SDK.")
register_commands(app, COMMAND_SPECS)
