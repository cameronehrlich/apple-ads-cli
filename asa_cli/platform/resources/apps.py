"""One-to-one Platform API commands for App Store app resources."""

import typer

from ..command_factory import register_commands
from ..manifest_specs import specs_from_manifest

SDK_METHODS = (
    "get_app_details_by_adam_id",
    "search_apps",
    "eligibilities_apps_query_post",
    "query_app_locale_details",
    "query_supported_app_languages",
)
COMMAND_NAMES = {
    "get_app_details_by_adam_id": "get",
    "search_apps": "search",
    "eligibilities_apps_query_post": "eligibilities",
    "query_app_locale_details": "locale-details",
    "query_supported_app_languages": "supported-languages",
}
COMMAND_SPECS = specs_from_manifest(
    resource_family="apps",
    sdk_methods=SDK_METHODS,
    command_names=COMMAND_NAMES,
)

app = typer.Typer(help="App Store app commands backed by Apple's official SDK.")
register_commands(app, COMMAND_SPECS)
