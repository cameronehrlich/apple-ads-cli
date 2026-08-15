"""Command tree for the complete Apple Ads Platform API v1 surface."""

from typing import Final

import typer

from .resources import (
    access,
    ad_accounts,
    ad_groups,
    ads,
    apps,
    assets,
    business_brands,
    business_categories,
    campaigns,
    change_history,
    creatives,
    geos,
    insights,
    keywords,
    location_groups,
    locations,
    negative_keywords,
    product_pages,
    recommendations,
    rejection_reasons,
    reports_apps,
    reports_business_brands,
    shared_budgets,
    suggestions,
)

PLATFORM_RESOURCES: Final = (
    ("access", access, "Advertiser resources, users, ACLs, and organizations"),
    ("ad-accounts", ad_accounts, "Ad account management"),
    ("ad-groups", ad_groups, "Ad group management"),
    ("ads", ads, "Ad management"),
    ("apps", apps, "App discovery, metadata, and eligibility"),
    ("assets", assets, "Apple Maps asset management"),
    ("business-brands", business_brands, "Apple Maps business brands"),
    ("business-categories", business_categories, "Apple Maps business categories"),
    ("campaigns", campaigns, "Campaign management"),
    ("change-history", change_history, "Audit summaries and change details"),
    ("creatives", creatives, "Creative management"),
    ("geos", geos, "Geographic targeting search"),
    ("insights", insights, "Impression share and search-term popularity"),
    ("keywords", keywords, "Targeting keyword management"),
    ("location-groups", location_groups, "Apple Maps location groups"),
    ("locations", locations, "Apple Maps locations"),
    ("negative-keywords", negative_keywords, "Negative keyword management"),
    ("product-pages", product_pages, "Custom product page discovery"),
    ("recommendations", recommendations, "Budget and target CPA recommendations"),
    ("rejection-reasons", rejection_reasons, "Creative rejection reasons"),
    ("reports-apps", reports_apps, "App Store ads reporting"),
    ("reports-business-brands", reports_business_brands, "Apple Maps ads reporting"),
    ("shared-budgets", shared_budgets, "Shared budget management"),
    ("suggestions", suggestions, "Keyword, category, phrase, and CPA suggestions"),
)
PLATFORM_COMMAND_GROUPS: Final = tuple(
    (name, module.app, help_text) for name, module, help_text in PLATFORM_RESOURCES
)


def register_platform_commands(parent: typer.Typer) -> None:
    """Register every canonical official-SDK resource group on ``parent``."""
    for name, command_app, help_text in PLATFORM_COMMAND_GROUPS:
        parent.add_typer(command_app, name=name, help=help_text)


app = typer.Typer(
    name="platform",
    help="Apple Ads Platform API v1 commands backed by Apple's official SDK.",
    no_args_is_help=True,
)
register_platform_commands(app)
