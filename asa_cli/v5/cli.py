"""Typer command tree for the Apple Search Ads v5 implementation."""

from typing import Final

import typer

from ..commands import (
    acl,
    adgroups,
    ads,
    budget,
    campaigns,
    config,
    geo,
    keywords,
    optimize,
    reports,
)

V5_COMMAND_GROUPS: Final = (
    ("config", config.app, "Configuration management"),
    ("campaigns", campaigns.app, "Campaign management"),
    ("adgroups", adgroups.app, "Ad group management"),
    ("keywords", keywords.app, "Keyword management"),
    ("reports", reports.app, "Reporting and analytics"),
    ("optimize", optimize.app, "Automated campaign optimization"),
    ("budget", budget.app, "Budget order management"),
    ("geo", geo.app, "Geo targeting and location search"),
    ("ads", ads.app, "Ad variations, creatives, and product pages"),
    ("acl", acl.app, "Access control, user management, and app search"),
)


def register_v5_commands(parent: typer.Typer, *, deprecated: bool = False) -> None:
    """Register the complete v5 command surface on ``parent``."""
    for name, command_app, help_text in V5_COMMAND_GROUPS:
        parent.add_typer(
            command_app,
            name=name,
            help=help_text,
            deprecated=deprecated,
        )


app = typer.Typer(
    name="v5",
    help="Apple Search Ads Campaign Management API v5 commands.",
    no_args_is_help=True,
    rich_markup_mode="rich",
)
register_v5_commands(app)
