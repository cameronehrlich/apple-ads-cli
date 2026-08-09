"""Apple Search Ads CLI - Main entry point."""

from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel

from . import __version__
from .commands import (
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
from .config import set_current_app

app = typer.Typer(
    name="asa",
    help="Apple Search Ads CLI - manage campaigns, keywords, and reporting.",
    no_args_is_help=True,
    rich_markup_mode="rich",
)

console = Console()

# Register command groups
app.add_typer(config.app, name="config", help="Configuration management")
app.add_typer(campaigns.app, name="campaigns", help="Campaign management")
app.add_typer(adgroups.app, name="adgroups", help="Ad group management")
app.add_typer(keywords.app, name="keywords", help="Keyword management")
app.add_typer(reports.app, name="reports", help="Reporting and analytics")
app.add_typer(optimize.app, name="optimize", help="Automated campaign optimization")
app.add_typer(budget.app, name="budget", help="Budget order management")
app.add_typer(geo.app, name="geo", help="Geo targeting and location search")
app.add_typer(ads.app, name="ads", help="Ad variations, creatives, and product pages")
app.add_typer(acl.app, name="acl", help="Access control, user management, and app search")


@app.command("version")
def version():
    """Show version information."""
    console.print(f"ASA CLI version {__version__}")


@app.command("help")
def help_command():
    """Show help and quick start guide."""
    help_text = """
[bold cyan]Apple Search Ads CLI[/bold cyan]

A command-line tool for managing Apple Search Ads campaigns following
Apple's recommended 4-campaign structure.

[bold]Quick Start:[/bold]

  1. Configure credentials and app settings:
     [cyan]asa config setup[/cyan]

  2. Test your API connection:
     [cyan]asa config test[/cyan]

  3. Audit your current campaign structure:
     [cyan]asa campaigns audit[/cyan]

  4. Set up the 4-campaign structure:
     [cyan]asa campaigns setup --countries US --budget 50[/cyan]

[bold]Common Commands:[/bold]

  [bold cyan]Campaigns:[/bold cyan]
    asa campaigns list          - List all campaigns
    asa campaigns create        - Create a new campaign
    asa campaigns update [ID]   - Update campaign name/budget/status
    asa campaigns audit         - Audit structure vs Apple recommendations
    asa campaigns setup         - Create 4-campaign structure
    asa campaigns pause [ID]    - Pause a campaign
    asa campaigns enable [ID]   - Enable a campaign

  [bold cyan]Ad Groups:[/bold cyan]
    asa adgroups list [CID]     - List ad groups for a campaign
    asa adgroups create         - Create ad group in a campaign
    asa adgroups update [ID]    - Update ad group settings
    asa adgroups pause [ID]     - Pause an ad group
    asa adgroups enable [ID]    - Enable an ad group

  [bold cyan]Keywords:[/bold cyan]
    asa keywords list           - List keywords in a campaign
    asa keywords add            - Add keywords with automatic routing
    asa keywords add-negatives  - Block unwanted search terms
    asa keywords list-negatives - List all negative keywords
    asa keywords delete-negatives - Remove negative keywords
    asa keywords find           - Search keywords across ad groups
    asa keywords update-bids-bulk - Bulk update keyword bids
    asa keywords promote        - Graduate Discovery keywords to exact

  [bold cyan]Reports:[/bold cyan]
    asa reports summary         - Performance summary across campaigns
    asa reports keywords        - Keyword performance report
    asa reports search-terms    - Discover new keywords and negatives
    asa reports impression-share - True async Apple impression-share report
    asa reports ads --json      - Stable complete-window ad performance
    asa reports custom          - Create async custom report
    asa reports custom-list     - List custom reports
    asa reports custom-get      - Get/download custom report
    asa reports ads             - Ad-level performance report
    asa reports bid-recommendations - Keyword bid recommendations

  [bold cyan]Budget:[/bold cyan]
    asa budget list             - List budget orders
    asa budget get [ID]         - Get budget order details
    asa budget status           - Campaign budget health overview
    asa budget create           - Create a budget order

  [bold cyan]Geo:[/bold cyan]
    asa geo search              - Search for geo locations
    asa geo show                - Show campaign geo targeting
    asa geo set                 - Set campaign geo targeting

  [bold cyan]Ads:[/bold cyan]
    asa ads list                - List ad variations
    asa ads create              - Create an ad variation
    asa ads experiment          - Validate/apply an existing CPP manifest
    asa ads delete              - Delete an ad variation
    asa ads creatives           - List creative sets
    asa ads product-pages       - List product page results
    asa ads rejections          - View ad rejection reasons

  [bold cyan]ACL:[/bold cyan]
    asa acl list                - List access control entries
    asa acl me                  - Show current user info
    asa acl search-apps         - Search for apps
    asa acl eligibility         - Check campaign eligibility
    asa acl countries           - List supported countries

  [bold cyan]Optimization:[/bold cyan]
    asa optimize                - Run automated optimization workflow
    asa optimize --dry-run      - Preview changes without applying
    asa optimize --days 7       - Analyze last 7 days

[bold]Campaign Structure:[/bold]

  This tool implements Apple's recommended 4-campaign structure:

  • [green]Brand[/green]      - Your app/company name keywords (exact match)
  • [green]Category[/green]   - Non-branded category keywords (exact match)
  • [green]Competitor[/green] - Competitor app names (exact match)
  • [green]Discovery[/green]  - Keyword mining (broad + search match)

[bold]Examples:[/bold]

  Add brand keywords:
    [cyan]asa keywords add "myapp,my app" --type brand[/cyan]

  Add category keywords:
    [cyan]asa keywords add "photo editor,image filter" --type category[/cyan]

  Block irrelevant terms:
    [cyan]asa keywords add-negatives "auto clicker,testflight" --all[/cyan]

  Promote winning search terms:
    [cyan]asa keywords promote "best photo app" --target category[/cyan]

  Find keywords to promote:
    [cyan]asa reports search-terms --winners[/cyan]

  Find terms to block:
    [cyan]asa reports search-terms --negatives[/cyan]

  Run weekly optimization:
    [cyan]asa optimize --dry-run[/cyan]
    [cyan]asa optimize --auto-approve[/cyan]

[bold]Multi-App Management:[/bold]

  Add a second app:
    [cyan]asa config add-app[/cyan]

  List all configured apps:
    [cyan]asa config list-apps[/cyan]

  Switch active app:
    [cyan]asa config switch colorcub[/cyan]

  Run a command for a specific app:
    [cyan]asa --app stitchit campaigns list[/cyan]
    [cyan]asa --app colorcub campaigns setup --countries US --budget 50[/cyan]

[bold]Documentation:[/bold]

  Apple Search Ads Best Practices:
    https://ads.apple.com/app-store/best-practices/campaign-structure

  API Documentation:
    https://developer.apple.com/documentation/apple_ads

  GitHub:
    https://github.com/cameronehrlich/apple-search-ads-cli
"""
    console.print(Panel(help_text, title="ASA CLI Help", border_style="cyan"))


@app.callback()
def main(
    ctx: typer.Context,
    app_slug: Optional[str] = typer.Option(
        None,
        "--app",
        "-A",
        help="App slug to operate on (e.g., 'stitchit', 'colorcub'). Overrides active app.",
        envvar="ASA_APP",
    ),
):
    """Apple Search Ads CLI - manage campaigns, keywords, and reporting."""
    if app_slug:
        set_current_app(app_slug)


if __name__ == "__main__":
    app()
