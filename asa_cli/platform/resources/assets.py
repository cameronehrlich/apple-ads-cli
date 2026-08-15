"""One-to-one Platform API commands for Apple Maps assets."""

from pathlib import Path

import typer

from ..command_factory import CommandSpec, ParameterSpec, register_commands
from ..manifest_specs import specs_from_manifest

SDK_METHODS = (
    "get_asset",
    "query_assets",
    "upload_asset",
    "delete_asset",
)
COMMAND_NAMES = {
    "get_asset": "get",
    "query_assets": "query",
    "upload_asset": "upload",
    "delete_asset": "delete",
}

STANDARD_METHODS = tuple(method for method in SDK_METHODS if method != "upload_asset")
COMMAND_SPECS = (
    *specs_from_manifest(
        resource_family="assets",
        sdk_methods=STANDARD_METHODS,
        command_names={method: COMMAND_NAMES[method] for method in STANDARD_METHODS},
    ),
    CommandSpec(
        name="upload",
        sdk_method="upload_asset",
        help="Upload an image asset for an Apple Maps business brand.",
        parameters=(
            ParameterSpec(
                "file",
                "--file",
                annotation=Path,
                help="PNG, JPG, or HEIC file path",
                path_exists=True,
                allowed_file_types=("png", "jpeg", "heic"),
            ),
            ParameterSpec(
                "promoted_object_id",
                "--promoted-object-id",
                help="Business brand identifier",
            ),
            ParameterSpec(
                "promoted_object_type",
                "--promoted-object-type",
                help="Promoted object type; currently BUSINESS_BRAND",
            ),
        ),
        mutation="upload",
    ),
)

app = typer.Typer(help="Apple Maps asset commands backed by Apple's official SDK.")
register_commands(app, COMMAND_SPECS)
