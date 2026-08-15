"""Campaign management commands."""

from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm
from rich.table import Table

from ..config import (
    CAMPAIGN_STRUCTURE,
    CampaignType,
    detect_campaign_type,
    get_campaign_name,
    get_current_app_config,
    is_multi_app,
    load_credentials,
    parse_campaign_name,
)
from ..v5.api import SearchAdsClient

app = typer.Typer(help="Campaign management commands")
console = Console()


def _resolve_app_name() -> Optional[str]:
    """Get the app_name for campaign scoping (None if single-app)."""
    if not is_multi_app():
        return None
    app_config = get_current_app_config()
    return app_config.app_name if app_config else None


@app.command("list")
def list_campaigns(
    all_campaigns: bool = typer.Option(
        False, "--all", "-a", help="Show all campaigns, not just ASA CLI managed"
    ),
    filter_name: Optional[str] = typer.Option(None, "--filter", "-f", help="Filter campaigns by name"),
    status_filter: Optional[str] = typer.Option(None, "--status", "-s", help="Filter by status (RUNNING, PAUSED)"),
    campaign_type: Optional[str] = typer.Option(None, "--type", "-t", help="Filter by type (brand, category, competitor, discovery)"),
    show_bids: bool = typer.Option(False, "--bids", "-b", help="Show ad group default bids (slower)"),
):
    """List all campaigns."""
    credentials = load_credentials()
    if not credentials:
        console.print("[red]No credentials configured. Run 'asa config setup' first.[/red]")
        raise typer.Exit(1)

    client = SearchAdsClient(credentials)
    app_name = _resolve_app_name()

    with console.status("[bold blue]Fetching campaigns..."):
        campaigns = client.get_campaigns()

    if not campaigns:
        console.print("[yellow]No campaigns found.[/yellow]")
        return

    # Apply filters
    filtered_campaigns = []
    for campaign in campaigns:
        name = campaign.get("name", "")
        parsed = parse_campaign_name(name, app_name=app_name)
        ctype = detect_campaign_type(name, app_name=app_name)

        # Skip non-managed campaigns unless --all flag
        if not all_campaigns and not parsed:
            continue

        # Apply name filter
        if filter_name and filter_name.lower() not in name.lower():
            continue

        # Apply status filter
        status = campaign.get("displayStatus", campaign.get("status", "UNKNOWN"))
        if status_filter and status_filter.upper() not in status.upper():
            continue

        # Apply campaign type filter
        if campaign_type:
            if not ctype or ctype.value.lower() != campaign_type.lower():
                continue

        filtered_campaigns.append(campaign)

    if not filtered_campaigns:
        console.print("[yellow]No campaigns found matching filters.[/yellow]")
        return

    # Fetch ad group bids if requested
    campaign_bids: dict[int, str] = {}
    if show_bids:
        with console.status("[bold blue]Fetching ad group bids..."):
            for campaign in filtered_campaigns:
                cid = campaign.get("id")
                ad_groups = client.get_ad_groups(cid)
                if ad_groups:
                    bids = []
                    for ag in ad_groups:
                        bid_data = ag.get("defaultBidAmount", {})
                        bid_amount = bid_data.get("amount", "?")
                        ag_name = ag.get("name", "")[:15]
                        bids.append(f"{ag_name}: ${bid_amount}")
                    campaign_bids[cid] = " | ".join(bids)
                else:
                    campaign_bids[cid] = "-"

    table = Table(title="Campaigns", show_header=True, header_style="bold magenta")
    table.add_column("ID", style="cyan")
    table.add_column("Name")
    table.add_column("Type", style="green")
    table.add_column("Status")
    table.add_column("Daily Budget")
    table.add_column("Lifetime")
    if show_bids:
        table.add_column("Ad Group Bids")
    else:
        table.add_column("Countries")

    for campaign in filtered_campaigns:
        name = campaign.get("name", "")
        ctype = detect_campaign_type(name, app_name=app_name)

        ctype_str = ctype.value if ctype else "-"
        status = campaign.get("displayStatus", campaign.get("status", "UNKNOWN"))
        daily_budget = campaign.get("dailyBudgetAmount", {})
        budget_str = f"${daily_budget.get('amount', '?')} {daily_budget.get('currency', '')}"

        # Lifetime budget — flag campaigns that silently stopped serving
        # because they hit their lifetime cap. Apple is discontinuing
        # lifetime budgets on 2026-06-16, so flag these everywhere.
        lt = campaign.get("budgetAmount") or {}
        lt_amt = lt.get("amount") if isinstance(lt, dict) else None
        serving = campaign.get("servingStatus", "")
        user_status = campaign.get("status", "")
        if lt_amt is None:
            lt_str = "[dim]—[/dim]"
        elif user_status == "ENABLED" and serving != "RUNNING":
            lt_str = f"[red]${lt_amt} CAPPED[/red]"
        else:
            lt_str = f"[yellow]${lt_amt}[/yellow]"

        countries = ", ".join(campaign.get("countriesOrRegions", []))

        status_style = "green" if status == "RUNNING" else "yellow" if status == "PAUSED" else "red"

        if show_bids:
            bid_str = campaign_bids.get(campaign.get("id"), "-")
            table.add_row(
                str(campaign.get("id")),
                name[:40] + "..." if len(name) > 40 else name,
                ctype_str,
                f"[{status_style}]{status}[/{status_style}]",
                budget_str,
                lt_str,
                bid_str[:50] + "..." if len(bid_str) > 50 else bid_str,
            )
        else:
            table.add_row(
                str(campaign.get("id")),
                name[:40] + "..." if len(name) > 40 else name,
                ctype_str,
                f"[{status_style}]{status}[/{status_style}]",
                budget_str,
                lt_str,
                countries[:20] + "..." if len(countries) > 20 else countries,
            )

    console.print(table)
    console.print(f"\n[dim]Total: {len(filtered_campaigns)} campaigns[/dim]")


@app.command("setup")
def setup_campaigns(
    countries: str = typer.Option("US", "--countries", "-c", help="Comma-separated country codes"),
    budget: float = typer.Option(50.0, "--budget", "-b", help="Daily budget per campaign (USD)"),
    bid: float = typer.Option(1.50, "--bid", help="Default keyword bid (USD)"),
    dry_run: bool = typer.Option(False, "--dry-run", "-n", help="Preview without creating"),
):
    """Set up the 4-campaign structure (Brand, Category, Competitor, Discovery)."""
    credentials = load_credentials()
    app_config = get_current_app_config()

    if not credentials:
        console.print("[red]No credentials configured. Run 'asa config setup' first.[/red]")
        raise typer.Exit(1)

    if not app_config:
        console.print("[red]No app config. Run 'asa config setup' first.[/red]")
        raise typer.Exit(1)

    country_list = [c.strip().upper() for c in countries.split(",")]
    multi_app = is_multi_app()
    app_name = app_config.app_name if multi_app else None

    # Show what will be created
    console.print(Panel("[bold]Campaign Structure Setup[/bold]", expand=False))
    console.print(f"\nApp: [cyan]{app_config.app_name}[/cyan] (ID: {app_config.app_id})")
    console.print(f"Countries: [cyan]{', '.join(country_list)}[/cyan]")
    console.print(f"Daily Budget: [cyan]${budget}[/cyan] per campaign")
    console.print(f"Default Bid: [cyan]${bid}[/cyan]\n")

    table = Table(title="Campaigns to Create", show_header=True)
    table.add_column("Type")
    table.add_column("Campaign Name")
    table.add_column("Ad Groups")
    table.add_column("Budget")

    for ctype, config in CAMPAIGN_STRUCTURE.items():
        campaign_name = get_campaign_name(ctype, app_name=app_name)
        ad_groups = ", ".join([ag.name for ag in config.ad_groups])
        table.add_row(ctype.value.upper(), campaign_name, ad_groups, f"${budget}/day")

    console.print(table)

    if dry_run:
        console.print("\n[yellow]Dry run - no changes made.[/yellow]")
        return

    if not Confirm.ask("\nProceed with campaign creation?"):
        console.print("[yellow]Cancelled.[/yellow]")
        return

    client = SearchAdsClient(credentials)

    # Check for existing campaigns with same type
    with console.status("[bold blue]Checking for existing campaigns..."):
        existing = client.get_campaigns()

    existing_types = {parse_campaign_name(c.get("name", ""), app_name=app_name)[1] for c in existing if parse_campaign_name(c.get("name", ""), app_name=app_name)}

    for ctype, config in CAMPAIGN_STRUCTURE.items():
        campaign_name = get_campaign_name(ctype, app_name=app_name)

        if ctype in existing_types:
            console.print(f"[yellow]Skipping {ctype.value} - campaign type already exists[/yellow]")
            continue

        with console.status(f"[bold blue]Creating {ctype.value} campaign..."):
            campaign = client.create_campaign(
                name=campaign_name,
                budget=budget * 30,  # Monthly budget
                daily_budget=budget,
                countries=country_list,
            )

        if not campaign:
            console.print(f"[red]Failed to create {ctype.value} campaign[/red]")
            continue

        campaign_id = campaign.get("id")
        console.print(f"[green]Created campaign: {campaign_name} (ID: {campaign_id})[/green]")

        # Create ad groups
        for ag_config in config.ad_groups:
            with console.status(f"  Creating ad group: {ag_config.name}..."):
                ad_group = client.create_ad_group(
                    campaign_id=campaign_id,
                    name=ag_config.name,
                    default_bid=bid,
                    search_match_enabled=ag_config.search_match_enabled,
                )

            if ad_group:
                console.print(f"  [green]Created ad group: {ag_config.name}[/green]")
            else:
                console.print(f"  [red]Failed to create ad group: {ag_config.name}[/red]")

    console.print("\n[bold green]Campaign setup complete![/bold green]")
    console.print(
        Panel(
            "[yellow]Tip:[/yellow] The CLI identifies campaign types by name.\n"
            "Keep 'Brand', 'Category', 'Competitor', or 'Discovery' in the campaign name\n"
            "for automatic keyword routing to work correctly.",
            title="Info",
            border_style="cyan",
        )
    )


@app.command("audit")
def audit_campaigns(
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed information"),
):
    """Audit current campaign structure against Apple's recommendations."""
    credentials = load_credentials()
    if not credentials:
        console.print("[red]No credentials configured. Run 'asa config setup' first.[/red]")
        raise typer.Exit(1)

    client = SearchAdsClient(credentials)
    app_name = _resolve_app_name()

    with console.status("[bold blue]Fetching campaigns and ad groups..."):
        campaigns = client.get_campaigns()

    if not campaigns:
        console.print("[yellow]No campaigns found.[/yellow]")
        return

    # Categorize campaigns
    managed_campaigns: dict[CampaignType, list] = {ctype: [] for ctype in CampaignType}
    unmanaged_campaigns = []

    for campaign in campaigns:
        parsed = parse_campaign_name(campaign.get("name", ""), app_name=app_name)
        if parsed:
            _, ctype, _ = parsed
            managed_campaigns[ctype].append(campaign)
        else:
            unmanaged_campaigns.append(campaign)

    # Structure report
    console.print(Panel("[bold]Campaign Structure Audit[/bold]", expand=False))

    # Check for Apple's 4-campaign structure
    console.print("\n[bold]Apple Recommended Structure:[/bold]")

    structure_issues = []

    for ctype in CampaignType:
        count = len(managed_campaigns[ctype])

        if count == 0:
            status = "[red]MISSING[/red]"
            structure_issues.append(f"Missing {ctype.value} campaign")
        elif count == 1:
            status = "[green]OK[/green]"
        else:
            status = f"[yellow]{count} campaigns[/yellow]"

        console.print(f"  {ctype.value.upper():12} {status}")

        if verbose and count > 0:
            for campaign in managed_campaigns[ctype]:
                campaign_id = campaign.get("id")
                ad_groups = client.get_ad_groups(campaign_id)

                console.print(f"    Campaign: {campaign.get('name')}")
                console.print(f"    Status: {campaign.get('displayStatus')}")
                console.print(f"    Ad Groups: {len(ad_groups)}")

                for ag in ad_groups:
                    search_match = ag.get("automatedKeywordsOptIn", False)
                    sm_str = "[Search Match]" if search_match else ""
                    console.print(f"      - {ag.get('name')} {sm_str}")

    # Other campaigns (without recognized type in name)
    if unmanaged_campaigns:
        console.print(f"\n[bold]Other Campaigns:[/bold] {len(unmanaged_campaigns)}")
        console.print("  [dim](Campaigns without Brand/Category/Competitor/Discovery in name)[/dim]")
        for campaign in unmanaged_campaigns:
            status = campaign.get("displayStatus", "UNKNOWN")
            console.print(f"  - {campaign.get('name')} [{status}]")

    # Summary
    if structure_issues:
        console.print("\n[bold red]Issues Found:[/bold red]")
        for issue in structure_issues:
            console.print(f"  [red]•[/red] {issue}")
        console.print("\nRun [cyan]asa v5 campaigns setup[/cyan] to create missing campaigns.")
    else:
        console.print("\n[bold green]Campaign structure matches Apple's recommendations[/bold green]")


@app.command("pause")
def pause_campaign(
    campaign_id: Optional[int] = typer.Argument(None, help="Campaign ID to pause"),
    all_campaigns: bool = typer.Option(False, "--all", "-a", help="Pause all managed campaigns"),
):
    """Pause a campaign or all managed campaigns."""
    credentials = load_credentials()
    if not credentials:
        console.print("[red]No credentials configured. Run 'asa config setup' first.[/red]")
        raise typer.Exit(1)

    client = SearchAdsClient(credentials)
    app_name = _resolve_app_name()

    if all_campaigns:
        campaigns = client.get_campaigns()
        managed = [c for c in campaigns if parse_campaign_name(c.get("name", ""), app_name=app_name)]

        if not managed:
            console.print("[yellow]No managed campaigns found.[/yellow]")
            return

        if not Confirm.ask(f"Pause {len(managed)} managed campaigns?"):
            return

        for campaign in managed:
            cid = campaign.get("id")
            if client.pause_campaign(cid):
                console.print(f"[green]Paused: {campaign.get('name')}[/green]")
            else:
                console.print(f"[red]Failed to pause: {campaign.get('name')}[/red]")

    elif campaign_id:
        if client.pause_campaign(campaign_id):
            console.print(f"[green]Campaign {campaign_id} paused.[/green]")
        else:
            console.print(f"[red]Failed to pause campaign {campaign_id}.[/red]")
    else:
        console.print("[red]Provide a campaign ID or use --all flag.[/red]")
        raise typer.Exit(1)


@app.command("enable")
def enable_campaign(
    campaign_id: Optional[int] = typer.Argument(None, help="Campaign ID to enable"),
    all_campaigns: bool = typer.Option(False, "--all", "-a", help="Enable all managed campaigns"),
):
    """Enable a campaign or all managed campaigns."""
    credentials = load_credentials()
    if not credentials:
        console.print("[red]No credentials configured. Run 'asa config setup' first.[/red]")
        raise typer.Exit(1)

    client = SearchAdsClient(credentials)
    app_name = _resolve_app_name()

    if all_campaigns:
        campaigns = client.get_campaigns()
        managed = [c for c in campaigns if parse_campaign_name(c.get("name", ""), app_name=app_name)]

        if not managed:
            console.print("[yellow]No managed campaigns found.[/yellow]")
            return

        if not Confirm.ask(f"Enable {len(managed)} managed campaigns?"):
            return

        for campaign in managed:
            cid = campaign.get("id")
            if client.enable_campaign(cid):
                console.print(f"[green]Enabled: {campaign.get('name')}[/green]")
            else:
                console.print(f"[red]Failed to enable: {campaign.get('name')}[/red]")

    elif campaign_id:
        if client.enable_campaign(campaign_id):
            console.print(f"[green]Campaign {campaign_id} enabled.[/green]")
        else:
            console.print(f"[red]Failed to enable campaign {campaign_id}.[/red]")
    else:
        console.print("[red]Provide a campaign ID or use --all flag.[/red]")
        raise typer.Exit(1)


@app.command("create")
def create_campaign(
    name: str = typer.Argument(..., help="Campaign name"),
    budget: float = typer.Option(50.0, "--budget", "-b", help="Daily budget (USD)"),
    countries: str = typer.Option("US", "--countries", "-c", help="Comma-separated country codes"),
    status: str = typer.Option("ENABLED", "--status", "-s", help="Initial status (ENABLED or PAUSED)"),
):
    """Create a new campaign with custom settings."""
    credentials = load_credentials()
    app_config = get_current_app_config()

    if not credentials:
        console.print("[red]No credentials configured. Run 'asa config setup' first.[/red]")
        raise typer.Exit(1)

    if not app_config:
        console.print("[red]No app config. Run 'asa config setup' first.[/red]")
        raise typer.Exit(1)

    country_list = [c.strip().upper() for c in countries.split(",")]
    status_upper = status.upper()
    if status_upper not in ("ENABLED", "PAUSED"):
        console.print("[red]Status must be ENABLED or PAUSED.[/red]")
        raise typer.Exit(1)

    client = SearchAdsClient(credentials)

    console.print(f"\nCreating campaign: [cyan]{name}[/cyan]")
    console.print(f"  Daily Budget: [cyan]${budget}[/cyan]")
    console.print(f"  Countries: [cyan]{', '.join(country_list)}[/cyan]")
    console.print(f"  Status: [cyan]{status_upper}[/cyan]")

    with console.status("[bold blue]Creating campaign..."):
        campaign = client.create_campaign(
            name=name,
            budget=budget * 30,  # Monthly budget estimate
            daily_budget=budget,
            countries=country_list,
            status=status_upper,
        )

    if campaign:
        console.print("\n[green]Campaign created successfully![/green]")
        console.print(f"  ID: [cyan]{campaign.get('id')}[/cyan]")
        console.print(f"  Name: [cyan]{campaign.get('name')}[/cyan]")
    else:
        console.print("[red]Failed to create campaign.[/red]")
        raise typer.Exit(1)


@app.command("update")
def update_campaign(
    campaign_id: int = typer.Argument(..., help="Campaign ID to update"),
    name: Optional[str] = typer.Option(None, "--name", "-n", help="New campaign name"),
    budget: Optional[float] = typer.Option(None, "--budget", "-b", help="New daily budget (USD)"),
    lifetime_budget: Optional[float] = typer.Option(
        None, "--lifetime-budget", "-L",
        help="New lifetime budget (USD). NOTE: Apple is discontinuing lifetime budgets on 2026-06-16; prefer --clear-lifetime.",
    ),
    clear_lifetime: bool = typer.Option(
        False, "--clear-lifetime",
        help="Remove the lifetime budget cap on the campaign (sets budgetAmount=null). Use this to unblock campaigns that silently stopped serving after hitting their lifetime cap.",
    ),
    status: Optional[str] = typer.Option(None, "--status", "-s", help="New status (ENABLED or PAUSED)"),
):
    """Update a campaign's name, budget, lifetime budget, or status."""
    credentials = load_credentials()
    if not credentials:
        console.print("[red]No credentials configured. Run 'asa config setup' first.[/red]")
        raise typer.Exit(1)

    if not any([name, budget, lifetime_budget, clear_lifetime, status]):
        console.print("[red]No updates provided. Use --name, --budget, --lifetime-budget, --clear-lifetime, or --status.[/red]")
        raise typer.Exit(1)

    if lifetime_budget is not None and clear_lifetime:
        console.print("[red]Use either --lifetime-budget or --clear-lifetime, not both.[/red]")
        raise typer.Exit(1)

    client = SearchAdsClient(credentials)

    # Verify campaign exists
    campaign = client.get_campaign(campaign_id)
    if not campaign:
        console.print(f"[red]Campaign {campaign_id} not found.[/red]")
        raise typer.Exit(1)

    updates = {}
    changes = []

    if name:
        updates["name"] = name
        changes.append(f"Name: {campaign.get('name')} -> {name}")

    if budget:
        updates["dailyBudgetAmount"] = {"amount": str(budget), "currency": "USD"}
        old_budget = campaign.get("dailyBudgetAmount", {}).get("amount", "?")
        changes.append(f"Daily Budget: ${old_budget} -> ${budget}")

    if clear_lifetime:
        updates["budgetAmount"] = None
        old = campaign.get("budgetAmount") or {}
        old_amt = old.get("amount") if isinstance(old, dict) else None
        changes.append(f"Lifetime Budget: ${old_amt or '-'} -> cleared")

    if lifetime_budget is not None:
        updates["budgetAmount"] = {"amount": str(lifetime_budget), "currency": "USD"}
        old = campaign.get("budgetAmount") or {}
        old_amt = old.get("amount") if isinstance(old, dict) else "-"
        changes.append(f"Lifetime Budget: ${old_amt} -> ${lifetime_budget}")

    if status:
        status_upper = status.upper()
        if status_upper not in ("ENABLED", "PAUSED"):
            console.print("[red]Status must be ENABLED or PAUSED.[/red]")
            raise typer.Exit(1)
        updates["status"] = status_upper
        changes.append(f"Status: {campaign.get('status')} -> {status_upper}")

    console.print(f"\nUpdating campaign [cyan]{campaign.get('name')}[/cyan] (ID: {campaign_id}):")
    for change in changes:
        console.print(f"  - {change}")

    with console.status("[bold blue]Updating campaign..."):
        result = client.update_campaign(campaign_id, updates)

    if result:
        console.print("\n[green]Campaign updated successfully![/green]")
    else:
        console.print("[red]Failed to update campaign.[/red]")
        raise typer.Exit(1)


@app.command("clone")
def clone_campaign(
    source_campaign_id: int = typer.Argument(..., help="Campaign ID to duplicate"),
    new_name: Optional[str] = typer.Option(None, "--name", "-n",
        help="Name for the clone (defaults to '<source> v2')"),
    keep_lifetime: bool = typer.Option(False, "--keep-lifetime",
        help="Copy the source's lifetime budget too. Default: drop it, since Apple is discontinuing lifetime budgets on 2026-06-16 and the most common reason to clone is to escape a stuck TOTAL_BUDGET_EXHAUSTED state."),
    pause_source: bool = typer.Option(False, "--pause-source",
        help="Pause the source campaign after a successful clone."),
):
    """Duplicate a campaign (with ad groups, keywords, and negatives).

    Apple Search Ads has no native campaign-duplication endpoint, so
    this reads the source and re-creates it. Useful to escape a stuck
    TOTAL_BUDGET_EXHAUSTED state after clearing a lifetime budget —
    Apple caches that flag even after the cap is gone, and only a fresh
    campaign ID releases it.

    The clone preserves: daily budget, countries, supply/channel,
    billing event, ad-group structure (name, default bid, pricing
    model, targeting dimensions), ACTIVE keywords + bids, and
    campaign-level negatives.

    Keywords that are PAUSED on the source are NOT copied (usually
    intentional). Ad-group-level negatives are NOT copied in this pass
    (campaign-level negatives are).
    """
    credentials = load_credentials()
    if not credentials:
        console.print("[red]No credentials configured. Run 'asa config setup' first.[/red]")
        raise typer.Exit(1)

    client = SearchAdsClient(credentials)
    console.print(f"[cyan]Cloning campaign {source_campaign_id}...[/cyan]")
    with console.status("[bold blue]Reading source + creating clone..."):
        result = client.clone_campaign(
            source_campaign_id,
            new_name=new_name,
            drop_lifetime_budget=not keep_lifetime,
            pause_source=pause_source,
        )

    if not result:
        console.print("[red]Clone failed — no result returned.[/red]")
        raise typer.Exit(1)

    console.print(f"\n[green]✓ Created campaign id={result['new_id']}[/green] name=[cyan]{result['new_name']}[/cyan]")
    total_kw = 0
    total_attempted = 0
    for ag in result["ad_groups"]:
        console.print(
            f"  Ad group [cyan]{ag['name']}[/cyan] (id={ag['new_id']}): "
            f"{ag['keywords_copied']}/{ag['keywords_attempted']} keywords"
        )
        total_kw += ag["keywords_copied"]
        total_attempted += ag["keywords_attempted"]
        for err in ag["keyword_errors"][:3]:
            console.print(f"    [yellow]! keyword error: {err}[/yellow]")
    console.print(
        f"  Negatives: {result['negatives']['copied']}/{result['negatives']['attempted']}"
    )
    if total_attempted and total_kw < total_attempted:
        console.print(
            f"[yellow]Note: {total_attempted - total_kw} keyword(s) failed to copy — review errors above.[/yellow]"
        )
    if result["source_paused"]:
        console.print(f"  [dim]Source campaign {source_campaign_id} paused.[/dim]")
    else:
        console.print(
            f"  [dim]Source campaign {source_campaign_id} unchanged. Pause it with "
            f"'asa v5 campaigns update {source_campaign_id} --status PAUSED' "
            "when you've verified the clone.[/dim]"
        )


@app.command("delete")
def delete_campaign(
    campaign_id: Optional[int] = typer.Argument(None, help="Campaign ID to delete"),
    all_unmanaged: bool = typer.Option(
        False, "--all-unmanaged", help="Delete all unmanaged campaigns"
    ),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation prompt"),
):
    """Delete a campaign. WARNING: This is irreversible."""
    credentials = load_credentials()
    if not credentials:
        console.print("[red]No credentials configured. Run 'asa config setup' first.[/red]")
        raise typer.Exit(1)

    client = SearchAdsClient(credentials)
    app_name = _resolve_app_name()

    if all_unmanaged:
        campaigns = client.get_campaigns()
        unmanaged = [c for c in campaigns if not parse_campaign_name(c.get("name", ""), app_name=app_name)]

        if not unmanaged:
            console.print("[yellow]No unmanaged campaigns found.[/yellow]")
            return

        console.print(f"\n[bold red]WARNING: About to delete {len(unmanaged)} unmanaged campaigns:[/bold red]")
        for campaign in unmanaged:
            console.print(f"  - {campaign.get('name')} (ID: {campaign.get('id')})")

        if not force and not Confirm.ask("\n[red]This is irreversible. Continue?[/red]"):
            console.print("[yellow]Cancelled.[/yellow]")
            return

        for campaign in unmanaged:
            cid = campaign.get("id")
            with console.status(f"Deleting {campaign.get('name')}..."):
                if client.delete_campaign(cid):
                    console.print(f"[green]Deleted: {campaign.get('name')}[/green]")
                else:
                    console.print(f"[red]Failed to delete: {campaign.get('name')}[/red]")

    elif campaign_id:
        # Get campaign info for confirmation
        campaign = client.get_campaign(campaign_id)
        if not campaign:
            console.print(f"[red]Campaign {campaign_id} not found.[/red]")
            raise typer.Exit(1)

        campaign_name = campaign.get("name", "Unknown")
        console.print("\n[bold red]WARNING: About to delete campaign:[/bold red]")
        console.print(f"  Name: {campaign_name}")
        console.print(f"  ID: {campaign_id}")

        if not force and not Confirm.ask("\n[red]This is irreversible. Continue?[/red]"):
            console.print("[yellow]Cancelled.[/yellow]")
            return

        with console.status(f"Deleting campaign {campaign_id}..."):
            if client.delete_campaign(campaign_id):
                console.print(f"[green]Campaign {campaign_id} deleted.[/green]")
            else:
                console.print(f"[red]Failed to delete campaign {campaign_id}.[/red]")
    else:
        console.print("[red]Provide a campaign ID or use --all-unmanaged flag.[/red]")
        raise typer.Exit(1)
