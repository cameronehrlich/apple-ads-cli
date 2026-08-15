"""One-to-one Platform API report commands for promoted apps."""

import typer

from ..command_factory import register_commands
from ..manifest_specs import specs_from_manifest

SDK_METHODS = (
    "apps_ad_group_reports",
    "apps_ad_reports",
    "apps_campaign_reports",
    "apps_keyword_reports",
    "apps_search_term_reports",
)
COMMAND_NAMES = {
    "apps_ad_group_reports": "ad-group",
    "apps_ad_reports": "ad",
    "apps_campaign_reports": "campaign",
    "apps_keyword_reports": "keyword",
    "apps_search_term_reports": "search-term",
}
COMMAND_SPECS = specs_from_manifest(
    resource_family="reports-apps",
    sdk_methods=SDK_METHODS,
    command_names=COMMAND_NAMES,
)

app = typer.Typer(help="App report commands backed by Apple's official SDK.")
register_commands(app, COMMAND_SPECS)
