"""One-to-one Platform API commands for creative rejection reasons."""

import typer

from ..command_factory import register_commands
from ..manifest_specs import specs_from_manifest

SDK_METHODS = (
    "rejection_reasons_apps_rejection_reason_id_get",
    "rejection_reasons_apps_query_post",
    "query_rejection_reasons_by_business_brand",
)
COMMAND_NAMES = {
    "rejection_reasons_apps_rejection_reason_id_get": "get-app",
    "rejection_reasons_apps_query_post": "query-apps",
    "query_rejection_reasons_by_business_brand": "query-business-brands",
}
COMMAND_SPECS = specs_from_manifest(
    resource_family="rejection-reasons",
    sdk_methods=SDK_METHODS,
    command_names=COMMAND_NAMES,
)

app = typer.Typer(help="Rejection reason commands backed by Apple's official SDK.")
register_commands(app, COMMAND_SPECS)
