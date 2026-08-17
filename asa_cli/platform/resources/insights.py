"""One-to-one Platform API insight commands."""

import typer

from ..command_factory import register_commands
from ..manifest_specs import specs_from_manifest

SDK_METHODS = (
    "impression_share_query",
    "search_term_popularity_query",
)
COMMAND_NAMES = {
    "impression_share_query": "impression-share",
    "search_term_popularity_query": "search-term-popularity",
}
COMMAND_SPECS = specs_from_manifest(
    resource_family="insights",
    sdk_methods=SDK_METHODS,
    command_names=COMMAND_NAMES,
)

app = typer.Typer(
    help=(
        "UTC-period impression-share and search-popularity commands; do not compare "
        "their boundaries directly with ORTZ performance reports."
    )
)
register_commands(app, COMMAND_SPECS)
