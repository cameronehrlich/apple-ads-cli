"""Keyword management commands."""

from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.table import Table

from ..config import (
    CampaignType,
    MatchType,
    detect_campaign_type,
    get_current_app_config,
    is_multi_app,
    load_credentials,
)
from ..v5.api import SearchAdsClient

app = typer.Typer(help="Keyword management commands")
console = Console()


def _resolve_app_name() -> Optional[str]:
    """Get the app_name for campaign scoping (None if single-app)."""
    if not is_multi_app():
        return None
    app_config = get_current_app_config()
    return app_config.app_name if app_config else None


def select_campaign(
    client: SearchAdsClient, campaign_type: Optional[CampaignType] = None
) -> Optional[dict]:
    """Interactive campaign selection."""
    campaigns = client.get_campaigns()
    app_name = _resolve_app_name()

    # Filter campaigns by type if specified
    filtered = []
    for c in campaigns:
        ctype = detect_campaign_type(c.get("name", ""), app_name=app_name)
        if campaign_type is None or ctype == campaign_type:
            filtered.append((c, ctype))

    if not filtered:
        if campaign_type:
            console.print(f"[yellow]No {campaign_type.value} campaigns found.[/yellow]")
        else:
            console.print("[yellow]No campaigns found.[/yellow]")
        return None

    if len(filtered) == 1:
        return filtered[0][0]

    table = Table(show_header=True)
    table.add_column("#", style="cyan")
    table.add_column("Type")
    table.add_column("Name")
    table.add_column("Status")

    for idx, (campaign, ctype) in enumerate(filtered, 1):
        type_str = ctype.value.upper() if ctype else "-"
        table.add_row(
            str(idx),
            type_str,
            campaign.get("name", "")[:50],
            campaign.get("displayStatus", ""),
        )

    console.print(table)

    while True:
        choice = Prompt.ask("Select campaign number")
        if choice.isdigit() and 1 <= int(choice) <= len(filtered):
            return filtered[int(choice) - 1][0]
        console.print("[red]Invalid selection.[/red]")


def select_ad_group(client: SearchAdsClient, campaign_id: int) -> Optional[dict]:
    """Interactive ad group selection."""
    ad_groups = client.get_ad_groups(campaign_id)

    if not ad_groups:
        console.print("[yellow]No ad groups found.[/yellow]")
        return None

    if len(ad_groups) == 1:
        return ad_groups[0]

    table = Table(show_header=True)
    table.add_column("#", style="cyan")
    table.add_column("Name")
    table.add_column("Search Match")
    table.add_column("Status")

    for idx, ag in enumerate(ad_groups, 1):
        search_match = "Yes" if ag.get("automatedKeywordsOptIn") else "No"
        table.add_row(str(idx), ag.get("name", ""), search_match, ag.get("status", ""))

    console.print(table)

    while True:
        choice = Prompt.ask("Select ad group number")
        if choice.isdigit() and 1 <= int(choice) <= len(ad_groups):
            return ad_groups[int(choice) - 1]
        console.print("[red]Invalid selection.[/red]")


@app.command("list")
def list_keywords(
    campaign_id: Optional[int] = typer.Option(None, "--campaign", "-c", help="Campaign ID"),
    ad_group_id: Optional[int] = typer.Option(None, "--ad-group", "-g", help="Ad group ID"),
    show_negatives: bool = typer.Option(False, "--negatives", "-n", help="Show negative keywords"),
    filter_text: Optional[str] = typer.Option(None, "--filter", "-f", help="Filter keywords containing text"),
    status: Optional[str] = typer.Option(None, "--status", "-s", help="Filter by status (ACTIVE, PAUSED)"),
    match_type: Optional[str] = typer.Option(None, "--match-type", "-m", help="Filter by match type (EXACT, BROAD)"),
):
    """List keywords in a campaign or ad group."""
    credentials = load_credentials()
    if not credentials:
        console.print("[red]No credentials configured. Run 'asa config setup' first.[/red]")
        raise typer.Exit(1)

    client = SearchAdsClient(credentials)

    # Select campaign if not provided
    if campaign_id is None:
        campaign = select_campaign(client)
        if not campaign:
            return
        campaign_id = campaign.get("id")

    if show_negatives:
        # Show campaign-level negative keywords
        with console.status("[bold blue]Fetching negative keywords..."):
            negatives = client.get_negative_keywords(campaign_id)

        # Apply filters
        if filter_text:
            negatives = [kw for kw in negatives if filter_text.lower() in kw.get("text", "").lower()]
        if status:
            negatives = [kw for kw in negatives if kw.get("status", "").upper() == status.upper()]
        if match_type:
            negatives = [kw for kw in negatives if kw.get("matchType", "").upper() == match_type.upper()]

        if not negatives:
            console.print("[yellow]No negative keywords found matching filters.[/yellow]")
            return

        table = Table(title="Negative Keywords", show_header=True)
        table.add_column("ID", style="cyan")
        table.add_column("Keyword")
        table.add_column("Match Type")
        table.add_column("Status")

        for kw in negatives:
            table.add_row(
                str(kw.get("id")),
                kw.get("text", ""),
                kw.get("matchType", ""),
                kw.get("status", ""),
            )

        console.print(table)
        console.print(f"\n[dim]Total: {len(negatives)} keywords[/dim]")
        return

    # Get ad groups
    ad_groups = client.get_ad_groups(campaign_id)

    if ad_group_id:
        ad_groups = [ag for ag in ad_groups if ag.get("id") == ad_group_id]

    total_count = 0
    for ag in ad_groups:
        ag_id = ag.get("id")
        ag_name = ag.get("name")

        with console.status(f"[bold blue]Fetching keywords for {ag_name}..."):
            keywords = client.get_keywords(campaign_id, ag_id)

        # Apply filters
        if filter_text:
            keywords = [kw for kw in keywords if filter_text.lower() in kw.get("text", "").lower()]
        if status:
            keywords = [kw for kw in keywords if kw.get("status", "").upper() == status.upper()]
        if match_type:
            keywords = [kw for kw in keywords if kw.get("matchType", "").upper() == match_type.upper()]

        if not keywords:
            if not filter_text and not status and not match_type:
                console.print(f"[yellow]{ag_name}: No keywords[/yellow]")
            continue

        total_count += len(keywords)

        table = Table(title=f"Keywords - {ag_name}", show_header=True)
        table.add_column("ID", style="cyan")
        table.add_column("Keyword")
        table.add_column("Match Type")
        table.add_column("Bid")
        table.add_column("Status")

        for kw in keywords:
            bid = kw.get("bidAmount", {})
            bid_str = f"${bid.get('amount', '?')}" if bid else "-"
            table.add_row(
                str(kw.get("id")),
                kw.get("text", ""),
                kw.get("matchType", ""),
                bid_str,
                kw.get("status", ""),
            )

        console.print(table)

    if filter_text or status or match_type:
        console.print(f"\n[dim]Total matching: {total_count} keywords[/dim]")


@app.command("add")
def add_keywords(
    keywords: str = typer.Argument(..., help="Comma-separated keywords to add"),
    campaign_type: CampaignType = typer.Option(
        CampaignType.CATEGORY,
        "--type",
        "-t",
        help="Campaign type: brand, category, competitor",
    ),
    bid: Optional[float] = typer.Option(None, "--bid", "-b", help="Bid amount (organization currency)"),
    dry_run: bool = typer.Option(False, "--dry-run", "-n", help="Preview without adding"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation prompt"),
):
    """Add keywords to a campaign with automatic routing.

    Keywords are added to:
    - The appropriate exact match campaign (brand/category/competitor)
    - Discovery campaign (broad match) for mining
    - Discovery campaign negative keywords (to prevent overlap)
    """
    if campaign_type == CampaignType.DISCOVERY:
        console.print("[red]Cannot add keywords directly to Discovery. Use brand/category/competitor.[/red]")
        raise typer.Exit(1)

    credentials = load_credentials()
    if not credentials:
        console.print("[red]No credentials configured. Run 'asa config setup' first.[/red]")
        raise typer.Exit(1)

    client = SearchAdsClient(credentials)
    app_name = _resolve_app_name()

    # Parse keywords
    keyword_list = [kw.strip().lower() for kw in keywords.split(",") if kw.strip()]

    if not keyword_list:
        console.print("[red]No valid keywords provided.[/red]")
        raise typer.Exit(1)

    # Find campaigns
    with console.status("[bold blue]Finding campaigns..."):
        campaigns = client.get_campaigns()

    # Find target campaign and discovery campaign
    target_campaign = None
    discovery_campaign = None

    for c in campaigns:
        ctype = detect_campaign_type(c.get("name", ""), app_name=app_name)
        if ctype == campaign_type:
            target_campaign = c
        elif ctype == CampaignType.DISCOVERY:
            discovery_campaign = c

    if not target_campaign:
        console.print(f"[red]No {campaign_type.value} campaign found.[/red]")
        console.print(f"[yellow]Tip: Make sure your campaign name contains '{campaign_type.value}'[/yellow]")
        raise typer.Exit(1)

    # Show what will be added
    console.print(Panel(f"[bold]Adding {len(keyword_list)} Keywords[/bold]", expand=False))
    console.print(f"\nKeywords: [cyan]{', '.join(keyword_list)}[/cyan]")
    console.print(f"Target: [cyan]{campaign_type.value.upper()}[/cyan] campaign")
    if bid:
        console.print(f"Bid: [cyan]{bid}[/cyan] (organization currency)")

    console.print("\n[bold]Routing Plan:[/bold]")
    console.print(f"  1. Add as EXACT to {target_campaign.get('name')}")
    if discovery_campaign:
        console.print(f"  2. Add as BROAD to {discovery_campaign.get('name')}")
        console.print(f"  3. Add as NEGATIVE to {discovery_campaign.get('name')}")
    else:
        console.print("  [yellow]Discovery campaign not found - skipping broad match[/yellow]")

    if dry_run:
        console.print("\n[yellow]Dry run - no changes made.[/yellow]")
        return

    if not force and not Confirm.ask("\nProceed?"):
        console.print("[yellow]Cancelled.[/yellow]")
        return

    target_id = target_campaign.get("id")

    # Get the exact match ad group
    ad_groups = client.get_ad_groups(target_id)
    exact_ad_group = next(
        (ag for ag in ad_groups if "Exact" in ag.get("name", "")),
        ad_groups[0] if ad_groups else None,
    )

    if not exact_ad_group:
        console.print(f"[red]No ad group found in {campaign_type.value} campaign.[/red]")
        raise typer.Exit(1)

    # Add to target campaign (exact match)
    with console.status(f"[bold blue]Adding to {campaign_type.value} campaign..."):
        added, errors = client.add_keywords(
            campaign_id=target_id,
            ad_group_id=exact_ad_group.get("id"),
            keywords=keyword_list,
            match_type=MatchType.EXACT,
            bid_amount=bid,
        )

    if added:
        console.print(f"[green]Added {len(added)} keywords to {campaign_type.value} campaign[/green]")
    elif errors:
        all_duplicates = all(e.get("messageCode") == "DUPLICATE_KEYWORD" for e in errors)
        if all_duplicates:
            console.print(f"[dim]Keywords already exist in {campaign_type.value} campaign[/dim]")
        else:
            console.print(f"[red]Failed: {errors[0].get('message', 'Unknown error')}[/red]")
    else:
        console.print(f"[red]Failed to add keywords to {campaign_type.value} campaign[/red]")

    # Add to discovery campaign
    if discovery_campaign:
        discovery_id = discovery_campaign.get("id")
        discovery_ad_groups = client.get_ad_groups(discovery_id)

        # Find broad match ad group
        broad_ad_group = next(
            (ag for ag in discovery_ad_groups if "Broad" in ag.get("name", "")),
            None,
        )

        if broad_ad_group:
            with console.status("[bold blue]Adding to Discovery (broad match)..."):
                broad_added, broad_errors = client.add_keywords(
                    campaign_id=discovery_id,
                    ad_group_id=broad_ad_group.get("id"),
                    keywords=keyword_list,
                    match_type=MatchType.BROAD,
                    bid_amount=bid,
                )

            if broad_added:
                console.print("[green]Added keywords to Discovery (broad match)[/green]")
            elif broad_errors and all(e.get("messageCode") == "DUPLICATE_KEYWORD" for e in broad_errors):
                console.print("[dim]Keywords already exist in Discovery (broad match)[/dim]")

        # Add as negatives to discovery
        with console.status("[bold blue]Adding negatives to Discovery..."):
            added, errors = client.add_negative_keywords(
                campaign_id=discovery_id,
                keywords=keyword_list,
                match_type=MatchType.EXACT,
            )

        if added:
            console.print("[green]Added negative keywords to Discovery[/green]")
        elif errors and all(e.get("messageCode") == "DUPLICATE_KEYWORD" for e in errors):
            console.print("[dim]Negative keywords already exist in Discovery[/dim]")

    console.print("\n[bold green]Keyword addition complete![/bold green]")


@app.command("add-negatives")
def add_negatives(
    keywords: str = typer.Argument(..., help="Comma-separated keywords to block"),
    all_campaigns: bool = typer.Option(
        False, "--all", "-a", help="Add to all managed campaigns"
    ),
    campaign_id: Optional[int] = typer.Option(None, "--campaign", "-c", help="Specific campaign ID"),
    dry_run: bool = typer.Option(False, "--dry-run", "-n", help="Preview without adding"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation prompt"),
):
    """Add negative keywords to block unwanted search terms."""
    credentials = load_credentials()
    if not credentials:
        console.print("[red]No credentials configured. Run 'asa config setup' first.[/red]")
        raise typer.Exit(1)

    client = SearchAdsClient(credentials)
    app_name = _resolve_app_name()

    keyword_list = [kw.strip().lower() for kw in keywords.split(",") if kw.strip()]

    if not keyword_list:
        console.print("[red]No valid keywords provided.[/red]")
        raise typer.Exit(1)

    # Get target campaigns
    target_campaigns = []

    if campaign_id:
        campaign = client.get_campaign(campaign_id)
        if campaign:
            target_campaigns = [campaign]
    elif all_campaigns:
        campaigns = client.get_campaigns()
        # Include campaigns with recognized types
        target_campaigns = [c for c in campaigns if detect_campaign_type(c.get("name", ""), app_name=app_name)]
    else:
        campaign = select_campaign(client)
        if campaign:
            target_campaigns = [campaign]

    if not target_campaigns:
        console.print("[yellow]No campaigns selected.[/yellow]")
        return

    console.print(Panel(f"[bold]Adding {len(keyword_list)} Negative Keywords[/bold]", expand=False))
    console.print(f"\nKeywords: [cyan]{', '.join(keyword_list)}[/cyan]")
    console.print(f"Campaigns: {len(target_campaigns)}")

    for c in target_campaigns:
        console.print(f"  - {c.get('name')}")

    if dry_run:
        console.print("\n[yellow]Dry run - no changes made.[/yellow]")
        return

    if not force and not Confirm.ask("\nProceed?"):
        console.print("[yellow]Cancelled.[/yellow]")
        return

    success_count = 0
    for campaign in target_campaigns:
        cid = campaign.get("id")
        cname = campaign.get("name")

        with console.status(f"[bold blue]Adding negatives to {cname}..."):
            added, errors = client.add_negative_keywords(cid, keyword_list)

        if added:
            console.print(f"[green]Added {len(added)} negatives to {cname}[/green]")
            success_count += 1
        elif errors:
            all_duplicates = all(e.get("messageCode") == "DUPLICATE_KEYWORD" for e in errors)
            if all_duplicates:
                console.print(f"[dim]{len(errors)} negatives already exist in {cname}[/dim]")
                success_count += 1
            else:
                console.print(f"[red]Failed: {errors[0].get('message', 'Unknown error')}[/red]")
        else:
            console.print(f"[red]Failed to add negatives to {cname}[/red]")

    if success_count > 0:
        console.print("\n[bold green]Negative keywords processed![/bold green]")
    else:
        console.print("\n[yellow]No negative keywords were added.[/yellow]")


@app.command("promote")
def promote_keywords(
    keywords: str = typer.Argument(..., help="Comma-separated keywords to promote from Discovery"),
    target_type: CampaignType = typer.Option(
        CampaignType.CATEGORY,
        "--target",
        "-t",
        help="Target campaign type: brand, category, competitor",
    ),
    bid: Optional[float] = typer.Option(None, "--bid", "-b", help="Bid amount (organization currency)"),
    dry_run: bool = typer.Option(False, "--dry-run", "-n", help="Preview without changes"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation prompt"),
):
    """Promote keywords from Discovery to exact match campaigns.

    This command:
    1. Adds keywords as EXACT match to the target campaign
    2. Adds them as negatives in Discovery (to stop paying for broad)
    """
    if target_type == CampaignType.DISCOVERY:
        console.print("[red]Cannot promote to Discovery. Use brand/category/competitor.[/red]")
        raise typer.Exit(1)

    credentials = load_credentials()
    if not credentials:
        console.print("[red]No credentials configured. Run 'asa config setup' first.[/red]")
        raise typer.Exit(1)

    client = SearchAdsClient(credentials)
    app_name = _resolve_app_name()

    keyword_list = [kw.strip().lower() for kw in keywords.split(",") if kw.strip()]

    if not keyword_list:
        console.print("[red]No valid keywords provided.[/red]")
        raise typer.Exit(1)

    # Find campaigns
    with console.status("[bold blue]Finding campaigns..."):
        campaigns = client.get_campaigns()

    target_campaign = None
    discovery_campaign = None

    for c in campaigns:
        ctype = detect_campaign_type(c.get("name", ""), app_name=app_name)
        if ctype == target_type:
            target_campaign = c
        elif ctype == CampaignType.DISCOVERY:
            discovery_campaign = c

    if not target_campaign:
        console.print(f"[red]No {target_type.value} campaign found.[/red]")
        console.print(f"[yellow]Tip: Make sure your campaign name contains '{target_type.value}'[/yellow]")
        raise typer.Exit(1)

    if not discovery_campaign:
        console.print("[yellow]Warning: No Discovery campaign found.[/yellow]")

    console.print(Panel(f"[bold]Promoting {len(keyword_list)} Keywords[/bold]", expand=False))
    console.print(f"\nKeywords: [cyan]{', '.join(keyword_list)}[/cyan]")
    console.print("From: Discovery")
    console.print(f"To: [cyan]{target_type.value.upper()}[/cyan]")

    console.print("\n[bold]Actions:[/bold]")
    console.print(f"  1. Add as EXACT to {target_campaign.get('name')}")
    if discovery_campaign:
        console.print(f"  2. Add as NEGATIVE to {discovery_campaign.get('name')}")

    if dry_run:
        console.print("\n[yellow]Dry run - no changes made.[/yellow]")
        return

    if not force and not Confirm.ask("\nProceed?"):
        console.print("[yellow]Cancelled.[/yellow]")
        return

    # Add to target campaign
    target_id = target_campaign.get("id")
    ad_groups = client.get_ad_groups(target_id)
    exact_ad_group = next(
        (ag for ag in ad_groups if "Exact" in ag.get("name", "")),
        ad_groups[0] if ad_groups else None,
    )

    if exact_ad_group:
        with console.status(f"[bold blue]Adding to {target_type.value}..."):
            added, errors = client.add_keywords(
                campaign_id=target_id,
                ad_group_id=exact_ad_group.get("id"),
                keywords=keyword_list,
                match_type=MatchType.EXACT,
                bid_amount=bid,
            )

        if added:
            console.print(f"[green]Added {len(added)} keywords to {target_type.value} campaign[/green]")
        elif errors:
            all_duplicates = all(e.get("messageCode") == "DUPLICATE_KEYWORD" for e in errors)
            if all_duplicates:
                console.print(f"[dim]Keywords already exist in {target_type.value} campaign[/dim]")
            else:
                console.print(f"[red]Failed: {errors[0].get('message', 'Unknown error')}[/red]")
        else:
            console.print(f"[red]Failed to add to {target_type.value}[/red]")

    # Add as negatives to Discovery
    if discovery_campaign:
        discovery_id = discovery_campaign.get("id")

        with console.status("[bold blue]Adding negatives to Discovery..."):
            added, errors = client.add_negative_keywords(discovery_id, keyword_list)

        if added:
            console.print("[green]Added negatives to Discovery[/green]")
        elif errors and all(e.get("messageCode") == "DUPLICATE_KEYWORD" for e in errors):
            console.print("[dim]Negatives already exist in Discovery[/dim]")

    console.print("\n[bold green]Promotion complete![/bold green]")


@app.command("delete")
def delete_keywords_cmd(
    campaign_id: Optional[int] = typer.Option(None, "--campaign", "-c", help="Campaign ID"),
    ad_group_id: Optional[int] = typer.Option(None, "--ad-group", "-g", help="Ad group ID"),
    keyword_ids: Optional[str] = typer.Option(None, "--ids", help="Comma-separated keyword IDs to delete"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation prompt"),
):
    """Delete keywords from a campaign."""
    credentials = load_credentials()
    if not credentials:
        console.print("[red]No credentials configured. Run 'asa config setup' first.[/red]")
        raise typer.Exit(1)

    client = SearchAdsClient(credentials)

    # Select campaign if not provided
    if campaign_id is None:
        campaign = select_campaign(client)
        if not campaign:
            return
        campaign_id = campaign.get("id")

    # Select ad group if not provided
    if ad_group_id is None:
        ad_group = select_ad_group(client, campaign_id)
        if not ad_group:
            return
        ad_group_id = ad_group.get("id")

    # Get keywords to show for selection
    with console.status("[bold blue]Fetching keywords..."):
        keywords = client.get_keywords(campaign_id, ad_group_id)

    if not keywords:
        console.print("[yellow]No keywords found.[/yellow]")
        return

    # If specific IDs provided, use those
    if keyword_ids:
        ids_to_delete = [int(id.strip()) for id in keyword_ids.split(",") if id.strip().isdigit()]
        keywords_to_delete = [kw for kw in keywords if kw.get("id") in ids_to_delete]
    else:
        # Show keywords for selection
        table = Table(show_header=True)
        table.add_column("#", style="cyan")
        table.add_column("ID")
        table.add_column("Keyword")
        table.add_column("Match Type")
        table.add_column("Status")

        for idx, kw in enumerate(keywords, 1):
            table.add_row(
                str(idx),
                str(kw.get("id")),
                kw.get("text", ""),
                kw.get("matchType", ""),
                kw.get("status", ""),
            )

        console.print(table)

        selection = Prompt.ask("Enter keyword numbers to delete (comma-separated, e.g., 1,3,5)")
        indices = [int(s.strip()) - 1 for s in selection.split(",") if s.strip().isdigit()]
        keywords_to_delete = [keywords[i] for i in indices if 0 <= i < len(keywords)]

    if not keywords_to_delete:
        console.print("[yellow]No keywords selected.[/yellow]")
        return

    console.print(f"\n[bold red]Keywords to delete ({len(keywords_to_delete)}):[/bold red]")
    for kw in keywords_to_delete:
        console.print(f"  - {kw.get('text')} ({kw.get('matchType')})")

    if not force and not Confirm.ask("\n[red]This is irreversible. Continue?[/red]"):
        console.print("[yellow]Cancelled.[/yellow]")
        return

    ids_to_delete = [kw.get("id") for kw in keywords_to_delete]
    with console.status("[bold blue]Deleting keywords..."):
        if client.delete_keywords(campaign_id, ad_group_id, ids_to_delete):
            console.print(f"[green]Deleted {len(ids_to_delete)} keywords.[/green]")
        else:
            console.print("[red]Failed to delete some keywords.[/red]")


@app.command("update-bid")
def update_bid(
    campaign_id: Optional[int] = typer.Option(None, "--campaign", "-c", help="Campaign ID"),
    ad_group_id: Optional[int] = typer.Option(None, "--ad-group", "-g", help="Ad group ID"),
    keyword_id: Optional[int] = typer.Option(None, "--keyword", "-k", help="Keyword ID"),
    bid: float = typer.Option(..., "--bid", "-b", help="New bid amount (organization currency)"),
):
    """Update bid amount for a keyword."""
    credentials = load_credentials()
    if not credentials:
        console.print("[red]No credentials configured. Run 'asa config setup' first.[/red]")
        raise typer.Exit(1)

    client = SearchAdsClient(credentials)

    # Select campaign if not provided
    if campaign_id is None:
        campaign = select_campaign(client)
        if not campaign:
            return
        campaign_id = campaign.get("id")

    # Select ad group if not provided
    if ad_group_id is None:
        ad_group = select_ad_group(client, campaign_id)
        if not ad_group:
            return
        ad_group_id = ad_group.get("id")

    # Select keyword if not provided
    if keyword_id is None:
        with console.status("[bold blue]Fetching keywords..."):
            keywords = client.get_keywords(campaign_id, ad_group_id)

        if not keywords:
            console.print("[yellow]No keywords found.[/yellow]")
            return

        table = Table(show_header=True)
        table.add_column("#", style="cyan")
        table.add_column("Keyword")
        table.add_column("Current Bid")
        table.add_column("Status")

        for idx, kw in enumerate(keywords, 1):
            current_bid = kw.get("bidAmount", {})
            bid_str = (
                f"{current_bid.get('amount', '?')} {current_bid.get('currency', '')}".strip()
                if current_bid
                else "-"
            )
            table.add_row(str(idx), kw.get("text", ""), bid_str, kw.get("status", ""))

        console.print(table)

        while True:
            choice = Prompt.ask("Select keyword number")
            if choice.isdigit() and 1 <= int(choice) <= len(keywords):
                keyword_id = keywords[int(choice) - 1].get("id")
                break
            console.print("[red]Invalid selection.[/red]")

    currency = client.get_org_currency()
    with console.status(f"[bold blue]Updating bid to {bid} {currency}..."):
        result = client.update_keyword_bid(campaign_id, ad_group_id, keyword_id, bid)

    if result:
        console.print(f"[green]Updated keyword {keyword_id} bid to {bid} {currency}.[/green]")
    else:
        console.print(f"[red]Failed to update bid for keyword {keyword_id}.[/red]")


@app.command("pause")
def pause_keyword_cmd(
    campaign_id: Optional[int] = typer.Option(None, "--campaign", "-c", help="Campaign ID"),
    ad_group_id: Optional[int] = typer.Option(None, "--ad-group", "-g", help="Ad group ID"),
    keyword_id: Optional[int] = typer.Option(None, "--keyword", "-k", help="Keyword ID"),
    all_active: bool = typer.Option(False, "--all", "-a", help="Pause all active keywords in the ad group"),
):
    """Pause a keyword or all active keywords."""
    credentials = load_credentials()
    if not credentials:
        console.print("[red]No credentials configured. Run 'asa config setup' first.[/red]")
        raise typer.Exit(1)

    client = SearchAdsClient(credentials)

    # Select campaign if not provided
    if campaign_id is None:
        campaign = select_campaign(client)
        if not campaign:
            return
        campaign_id = campaign.get("id")

    # Select ad group if not provided
    if ad_group_id is None:
        ad_group = select_ad_group(client, campaign_id)
        if not ad_group:
            return
        ad_group_id = ad_group.get("id")

    with console.status("[bold blue]Fetching keywords..."):
        keywords = client.get_keywords(campaign_id, ad_group_id)

    if not keywords:
        console.print("[yellow]No keywords found.[/yellow]")
        return

    # Filter to active keywords
    active_keywords = [kw for kw in keywords if kw.get("status") == "ACTIVE"]
    if not active_keywords:
        console.print("[yellow]No active keywords to pause.[/yellow]")
        return

    # Pause all active keywords if --all flag
    if all_active:
        console.print(f"[bold]Pausing {len(active_keywords)} active keywords...[/bold]")
        success_count = 0
        for kw in active_keywords:
            kw_id = kw.get("id")
            if client.pause_keyword(campaign_id, ad_group_id, kw_id):
                console.print(f"  [green]paused[/green] {kw.get('text')}")
                success_count += 1
            else:
                console.print(f"  [red]failed[/red] {kw.get('text')}")
        console.print(f"\n[bold green]Paused {success_count}/{len(active_keywords)} keywords.[/bold green]")
        return

    # Select keyword if not provided
    if keyword_id is None:
        table = Table(show_header=True)
        table.add_column("#", style="cyan")
        table.add_column("Keyword")
        table.add_column("Bid")

        for idx, kw in enumerate(active_keywords, 1):
            current_bid = kw.get("bidAmount", {})
            bid_str = f"${current_bid.get('amount', '?')}" if current_bid else "-"
            table.add_row(str(idx), kw.get("text", ""), bid_str)

        console.print(table)

        while True:
            choice = Prompt.ask("Select keyword number to pause")
            if choice.isdigit() and 1 <= int(choice) <= len(active_keywords):
                keyword_id = active_keywords[int(choice) - 1].get("id")
                break
            console.print("[red]Invalid selection.[/red]")

    with console.status("[bold blue]Pausing keyword..."):
        if client.pause_keyword(campaign_id, ad_group_id, keyword_id):
            console.print(f"[green]Keyword {keyword_id} paused.[/green]")
        else:
            console.print(f"[red]Failed to pause keyword {keyword_id}.[/red]")


@app.command("enable")
def enable_keyword_cmd(
    campaign_id: Optional[int] = typer.Option(None, "--campaign", "-c", help="Campaign ID"),
    ad_group_id: Optional[int] = typer.Option(None, "--ad-group", "-g", help="Ad group ID"),
    keyword_id: Optional[int] = typer.Option(None, "--keyword", "-k", help="Keyword ID"),
    all_paused: bool = typer.Option(False, "--all", "-a", help="Enable all paused keywords in the ad group"),
):
    """Enable a paused keyword or all paused keywords."""
    credentials = load_credentials()
    if not credentials:
        console.print("[red]No credentials configured. Run 'asa config setup' first.[/red]")
        raise typer.Exit(1)

    client = SearchAdsClient(credentials)

    # Select campaign if not provided
    if campaign_id is None:
        campaign = select_campaign(client)
        if not campaign:
            return
        campaign_id = campaign.get("id")

    # Select ad group if not provided
    if ad_group_id is None:
        ad_group = select_ad_group(client, campaign_id)
        if not ad_group:
            return
        ad_group_id = ad_group.get("id")

    with console.status("[bold blue]Fetching keywords..."):
        keywords = client.get_keywords(campaign_id, ad_group_id)

    if not keywords:
        console.print("[yellow]No keywords found.[/yellow]")
        return

    # Filter to paused keywords
    paused_keywords = [kw for kw in keywords if kw.get("status") == "PAUSED"]
    if not paused_keywords:
        console.print("[yellow]No paused keywords to enable.[/yellow]")
        return

    # Enable all paused keywords if --all flag
    if all_paused:
        console.print(f"[bold]Enabling {len(paused_keywords)} paused keywords...[/bold]")
        success_count = 0
        for kw in paused_keywords:
            kw_id = kw.get("id")
            if client.enable_keyword(campaign_id, ad_group_id, kw_id):
                console.print(f"  [green]enabled[/green] {kw.get('text')}")
                success_count += 1
            else:
                console.print(f"  [red]failed[/red] {kw.get('text')}")
        console.print(f"\n[bold green]Enabled {success_count}/{len(paused_keywords)} keywords.[/bold green]")
        return

    # Select keyword if not provided
    if keyword_id is None:
        table = Table(show_header=True)
        table.add_column("#", style="cyan")
        table.add_column("Keyword")
        table.add_column("Bid")

        for idx, kw in enumerate(paused_keywords, 1):
            current_bid = kw.get("bidAmount", {})
            bid_str = f"${current_bid.get('amount', '?')}" if current_bid else "-"
            table.add_row(str(idx), kw.get("text", ""), bid_str)

        console.print(table)

        while True:
            choice = Prompt.ask("Select keyword number to enable")
            if choice.isdigit() and 1 <= int(choice) <= len(paused_keywords):
                keyword_id = paused_keywords[int(choice) - 1].get("id")
                break
            console.print("[red]Invalid selection.[/red]")

    with console.status("[bold blue]Enabling keyword..."):
        if client.enable_keyword(campaign_id, ad_group_id, keyword_id):
            console.print(f"[green]Keyword {keyword_id} enabled.[/green]")
        else:
            console.print(f"[red]Failed to enable keyword {keyword_id}.[/red]")


@app.command()
def research(
    seed: Optional[str] = typer.Option(
        None, "--seed", "-s",
        help="Comma-separated seed keywords for recommendations"
    ),
    limit: int = typer.Option(
        50, "--limit", "-l",
        help="Max results to show"
    ),
    raw: bool = typer.Option(
        False, "--raw",
        help="Show raw API response for debugging"
    ),
):
    """Research keywords — get Apple's recommendations and search popularity scores.

    Uses ASA API targeting keyword recommendations endpoint to find new keywords
    and get bid recommendations for existing ones.
    """
    config = get_current_app_config()
    creds = load_credentials()
    client = SearchAdsClient(credentials=creds, app_config=config)

    app_name = _resolve_app_name()

    # Find a campaign and ad group to use as context
    with console.status("[bold blue]Finding campaigns..."):
        campaigns = client.get_campaigns()

    # Prefer Category campaign for recommendations
    target_campaign = None
    for c in campaigns:
        ctype = detect_campaign_type(c.get("name", ""), app_name=app_name)
        if ctype == CampaignType.CATEGORY:
            target_campaign = c
            break

    if not target_campaign:
        # Fall back to any campaign for this app
        for c in campaigns:
            ctype = detect_campaign_type(c.get("name", ""), app_name=app_name)
            if ctype is not None:
                target_campaign = c
                break

    if not target_campaign:
        console.print("[red]No campaigns found for this app.[/red]")
        return

    campaign_id = target_campaign["id"]

    # Get ad groups
    with console.status("[bold blue]Finding ad groups..."):
        ad_groups = client.get_ad_groups(campaign_id)

    if not ad_groups:
        console.print("[red]No ad groups found.[/red]")
        return

    ad_group_id = ad_groups[0]["id"]

    with console.status("[bold blue]Fetching keyword recommendations from Apple..."):
        recommendations = client.get_keyword_recommendations(
            app_id=config.app_id,
            campaign_id=campaign_id,
            ad_group_id=ad_group_id,
            keywords=[k.strip() for k in seed.split(",")] if seed else None,
        )

    if raw:
        import json
        console.print(json.dumps(recommendations, indent=2, default=str))
        return

    if not recommendations:
        console.print("[yellow]No recommendations returned.[/yellow]")
        return

    table = Table(title=f"Keyword Recommendations for {config.app_name}")
    table.add_column("Keyword", style="bold")
    table.add_column("Bid Suggestion", justify="right")
    table.add_column("Popularity", justify="center")

    shown = 0
    for item in recommendations[:limit]:
        keyword = item.get("keyword") or item.get("text") or item.get("id", "?")
        bid = item.get("bidAmount", {})
        bid_str = f"${bid.get('amount', '-')}" if isinstance(bid, dict) else str(bid) if bid else "-"
        popularity = item.get("searchPopularity", item.get("popularity", "-"))
        table.add_row(str(keyword), bid_str, str(popularity))
        shown += 1

    console.print(table)
    console.print(f"\n[dim]Showing {shown} of {len(recommendations)} results[/dim]")


@app.command("list-negatives")
def list_negatives(
    campaign_id: Optional[int] = typer.Option(None, "--campaign", "-c", help="Campaign ID"),
):
    """List negative keywords for a campaign (campaign + ad-group level)."""
    credentials = load_credentials()
    if not credentials:
        console.print("[red]No credentials configured. Run 'asa config setup' first.[/red]")
        raise typer.Exit(1)

    client = SearchAdsClient(credentials)

    # Select campaign if not provided
    if campaign_id is None:
        campaign = select_campaign(client)
        if not campaign:
            return
        campaign_id = campaign.get("id")

    # Fetch campaign-level negatives
    with console.status("[bold blue]Fetching campaign-level negative keywords..."):
        campaign_negatives = client.get_negative_keywords(campaign_id)

    # Fetch ad-group-level negatives
    with console.status("[bold blue]Fetching ad groups..."):
        ad_groups = client.get_ad_groups(campaign_id)

    ag_negatives = []
    for ag in ad_groups:
        ag_id = ag.get("id")
        ag_name = ag.get("name", "")
        with console.status(f"[bold blue]Fetching negatives for {ag_name}..."):
            negatives = client.get_ad_group_negative_keywords(campaign_id, ag_id)
        for kw in negatives:
            kw["_level"] = "Ad Group"
            kw["_ad_group_name"] = ag_name
        ag_negatives.extend(negatives)

    # Tag campaign-level keywords
    for kw in campaign_negatives:
        kw["_level"] = "Campaign"
        kw["_ad_group_name"] = "-"

    all_negatives = campaign_negatives + ag_negatives

    if not all_negatives:
        console.print("[yellow]No negative keywords found.[/yellow]")
        return

    table = Table(title="Negative Keywords", show_header=True)
    table.add_column("ID", style="cyan")
    table.add_column("Keyword")
    table.add_column("Match Type")
    table.add_column("Status")
    table.add_column("Level")
    table.add_column("Ad Group")

    for kw in all_negatives:
        table.add_row(
            str(kw.get("id")),
            kw.get("text", ""),
            kw.get("matchType", ""),
            kw.get("status", ""),
            kw.get("_level", ""),
            kw.get("_ad_group_name", ""),
        )

    console.print(table)
    console.print(f"\n[dim]Campaign-level: {len(campaign_negatives)} | Ad-group-level: {len(ag_negatives)} | Total: {len(all_negatives)}[/dim]")


@app.command("delete-negatives")
def delete_negatives(
    ids: str = typer.Argument(..., help="Comma-separated negative keyword IDs to delete"),
    campaign_id: Optional[int] = typer.Option(None, "--campaign", "-c", help="Campaign ID"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation prompt"),
):
    """Delete negative keywords by comma-separated IDs."""
    credentials = load_credentials()
    if not credentials:
        console.print("[red]No credentials configured. Run 'asa config setup' first.[/red]")
        raise typer.Exit(1)

    client = SearchAdsClient(credentials)

    # Select campaign if not provided
    if campaign_id is None:
        campaign = select_campaign(client)
        if not campaign:
            return
        campaign_id = campaign.get("id")

    keyword_ids = [int(id_.strip()) for id_ in ids.split(",") if id_.strip().isdigit()]

    if not keyword_ids:
        console.print("[red]No valid keyword IDs provided.[/red]")
        raise typer.Exit(1)

    console.print(f"[bold red]Deleting {len(keyword_ids)} negative keyword(s):[/bold red]")
    console.print(f"  IDs: {', '.join(str(i) for i in keyword_ids)}")

    if not force and not Confirm.ask("\n[red]This is irreversible. Continue?[/red]"):
        console.print("[yellow]Cancelled.[/yellow]")
        return

    with console.status("[bold blue]Deleting negative keywords..."):
        success = client.delete_campaign_negative_keywords(campaign_id, keyword_ids)

    if success:
        console.print(f"[green]Deleted {len(keyword_ids)} negative keyword(s).[/green]")
    else:
        console.print("[red]Failed to delete some negative keywords.[/red]")


@app.command("find")
def find_keywords(
    query: str = typer.Argument(..., help="Search text to match against keyword names"),
    campaign_id: Optional[int] = typer.Option(None, "--campaign", "-c", help="Campaign ID"),
):
    """Search targeting keywords across a campaign."""
    credentials = load_credentials()
    if not credentials:
        console.print("[red]No credentials configured. Run 'asa config setup' first.[/red]")
        raise typer.Exit(1)

    client = SearchAdsClient(credentials)

    # Select campaign if not provided
    if campaign_id is None:
        campaign = select_campaign(client)
        if not campaign:
            return
        campaign_id = campaign.get("id")

    conditions = [
        {
            "field": "text",
            "operator": "CONTAINS",
            "values": [query.lower()],
        }
    ]

    with console.status(f"[bold blue]Searching for '{query}'..."):
        keywords = client.find_targeting_keywords(campaign_id, conditions=conditions)

    if not keywords:
        console.print(f"[yellow]No keywords matching '{query}' found.[/yellow]")
        return

    table = Table(title=f"Keywords matching '{query}'", show_header=True)
    table.add_column("ID", style="cyan")
    table.add_column("Keyword")
    table.add_column("Match Type")
    table.add_column("Bid")
    table.add_column("Status")
    table.add_column("Ad Group ID")

    for kw in keywords:
        bid = kw.get("bidAmount", {})
        bid_str = f"${bid.get('amount', '?')}" if bid else "-"
        table.add_row(
            str(kw.get("id")),
            kw.get("text", ""),
            kw.get("matchType", ""),
            bid_str,
            kw.get("status", ""),
            str(kw.get("adGroupId", "")),
        )

    console.print(table)
    console.print(f"\n[dim]Total: {len(keywords)} keywords[/dim]")


@app.command("update-bids-bulk")
def update_bids_bulk(
    bid: float = typer.Option(..., "--bid", "-b", help="New bid amount (organization currency) for all keywords"),
    campaign_id: Optional[int] = typer.Option(None, "--campaign", "-c", help="Campaign ID"),
    ad_group_id: Optional[int] = typer.Option(None, "--ad-group", "-g", help="Ad group ID"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation prompt"),
):
    """Update all keyword bids in a campaign/ad group at once."""
    credentials = load_credentials()
    if not credentials:
        console.print("[red]No credentials configured. Run 'asa config setup' first.[/red]")
        raise typer.Exit(1)

    client = SearchAdsClient(credentials)

    # Select campaign if not provided
    if campaign_id is None:
        campaign = select_campaign(client)
        if not campaign:
            return
        campaign_id = campaign.get("id")

    # Select ad group if not provided
    if ad_group_id is None:
        ad_group = select_ad_group(client, campaign_id)
        if not ad_group:
            return
        ad_group_id = ad_group.get("id")

    # Get all keywords
    with console.status("[bold blue]Fetching keywords..."):
        keywords = client.get_keywords(campaign_id, ad_group_id)

    if not keywords:
        console.print("[yellow]No keywords found.[/yellow]")
        return

    currency = client.get_org_currency()

    # Show current bids
    table = Table(title="Current Bids", show_header=True)
    table.add_column("ID", style="cyan")
    table.add_column("Keyword")
    table.add_column("Current Bid")
    table.add_column("New Bid")
    table.add_column("Status")

    for kw in keywords:
        current_bid = kw.get("bidAmount", {})
        current_str = (
            f"{current_bid.get('amount', '?')} {current_bid.get('currency', '')}".strip()
            if current_bid
            else "-"
        )
        table.add_row(
            str(kw.get("id")),
            kw.get("text", ""),
            current_str,
            f"{bid:.2f} {currency}",
            kw.get("status", ""),
        )

    console.print(table)
    console.print(f"\n[bold]Updating {len(keywords)} keyword(s) to {bid:.2f} {currency}[/bold]")

    if not force and not Confirm.ask("\nProceed?"):
        console.print("[yellow]Cancelled.[/yellow]")
        return

    # Build bulk update payload
    updates = [
        {"id": kw.get("id"), "bidAmount": {"amount": str(bid), "currency": currency}}
        for kw in keywords
    ]

    with console.status("[bold blue]Updating bids..."):
        result = client.update_keywords_bulk(campaign_id, ad_group_id, updates)

    if result is not None:
        console.print(
            f"\n[bold green]Updated {len(keywords)} keyword bids to "
            f"{bid:.2f} {currency}.[/bold green]"
        )
    else:
        console.print("[red]Failed to update keyword bids.[/red]")
