"""One-to-one Platform API recommendation commands."""

import typer

from ..command_factory import register_commands
from ..manifest_specs import specs_from_manifest

SDK_METHODS = (
    "query_daily_budget_recommendations",
    "apply_daily_budget_recommendations",
    "dismiss_daily_budget_recommendations",
    "query_target_cpa_recommendations",
    "apply_target_cpa_recommendations",
    "dismiss_target_cpa_recommendations",
)
COMMAND_NAMES = {
    "query_daily_budget_recommendations": "daily-budget-query",
    "apply_daily_budget_recommendations": "daily-budget-apply",
    "dismiss_daily_budget_recommendations": "daily-budget-dismiss",
    "query_target_cpa_recommendations": "target-cpa-query",
    "apply_target_cpa_recommendations": "target-cpa-apply",
    "dismiss_target_cpa_recommendations": "target-cpa-dismiss",
}
COMMAND_SPECS = specs_from_manifest(
    resource_family="recommendations",
    sdk_methods=SDK_METHODS,
    command_names=COMMAND_NAMES,
)

app = typer.Typer(help="Recommendation query, apply, and dismiss commands.")
register_commands(app, COMMAND_SPECS)
