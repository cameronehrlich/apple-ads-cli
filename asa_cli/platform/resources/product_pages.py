"""One-to-one Platform API commands for App Store product pages."""

import typer

from ..command_factory import register_commands
from ..manifest_specs import specs_from_manifest

SDK_METHODS = (
    "get_product_page_by_id",
    "query_product_pages",
    "query_product_page_locale_details",
)
COMMAND_NAMES = {
    "get_product_page_by_id": "get",
    "query_product_pages": "query",
    "query_product_page_locale_details": "query-locales",
}
COMMAND_SPECS = specs_from_manifest(
    resource_family="product-pages",
    sdk_methods=SDK_METHODS,
    command_names=COMMAND_NAMES,
)

app = typer.Typer(help="Product page commands backed by Apple's official SDK.")
register_commands(app, COMMAND_SPECS)
