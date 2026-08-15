"""One-to-one Platform API report commands for Apple Maps business brands."""

import typer

from ..command_factory import register_commands
from ..manifest_specs import specs_from_manifest

SDK_METHODS = (
    "brands_ad_group_reports",
    "brands_ad_reports",
    "brands_campaign_reports",
    "brands_keyword_reports",
    "brands_search_term_reports",
)
COMMAND_NAMES = {
    "brands_ad_group_reports": "ad-group",
    "brands_ad_reports": "ad",
    "brands_campaign_reports": "campaign",
    "brands_keyword_reports": "keyword",
    "brands_search_term_reports": "search-term",
}
COMMAND_SPECS = specs_from_manifest(
    resource_family="reports-business-brands",
    sdk_methods=SDK_METHODS,
    command_names=COMMAND_NAMES,
)

app = typer.Typer(help="Business-brand report commands backed by Apple's official SDK.")
register_commands(app, COMMAND_SPECS)
