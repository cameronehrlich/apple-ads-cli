"""Reporting commands."""

import json
from contextlib import nullcontext
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from ..api import SearchAdsClient
from ..config import (
    CampaignType,
    get_current_app_config,
    is_multi_app,
    load_credentials,
    parse_campaign_name,
)
from ..reporting import (
    CompleteDateWindow,
    complete_date_window,
    machine_report,
    normalize_performance_row,
    parse_impression_share_csv,
    performance_totals,
)

app = typer.Typer(help="Reporting and analytics commands")
console = Console()


def _resolve_window(days: int, start_date: Optional[str], end_date: Optional[str]) -> CompleteDateWindow:
    try:
        return complete_date_window(days, start_date, end_date)
    except ValueError as exc:
        raise typer.BadParameter(str(exc)) from exc


def _status(message: str, *, json_output: bool):
    return nullcontext() if json_output else console.status(message)


def _print_json(payload: dict) -> None:
    typer.echo(json.dumps(payload, indent=2, sort_keys=True, allow_nan=False))


def format_currency(amount: float, currency: str = "USD") -> str:
    """Format currency for display."""
    return f"${amount:,.2f}"


def format_number(num: float) -> str:
    """Format number with commas."""
    if num >= 1000:
        return f"{num:,.0f}"
    return f"{num:.2f}" if num % 1 else str(int(num))


def _resolve_app_name() -> Optional[str]:
    """Get the app_name for campaign scoping (None if single-app)."""
    if not is_multi_app():
        return None
    app_config = get_current_app_config()
    return app_config.app_name if app_config else None


def get_campaign_type_label(campaign_name: str, app_name: Optional[str] = None) -> str:
    """Get campaign type label from name, supporting both simple and managed naming."""
    parsed = parse_campaign_name(campaign_name, app_name=app_name)
    if parsed:
        return parsed[1].value.upper()
    # Support simple naming (Brand, Category, Competitor, Discovery)
    name_lower = campaign_name.lower()
    for ctype in ["brand", "category", "competitor", "discovery"]:
        if ctype in name_lower:
            return ctype.upper()
    return campaign_name[:15]


@app.command("summary")
def report_summary(
    days: int = typer.Option(30, "--days", "-d", help="Number of days to report"),
    start_date: Optional[str] = typer.Option(
        None, "--start", "--start-date", help="Inclusive start date (YYYY-MM-DD)"
    ),
    end_date: Optional[str] = typer.Option(
        None, "--end", "--end-date", help="Inclusive complete end date (YYYY-MM-DD)"
    ),
    all_campaigns: bool = typer.Option(
        True, "--all/--managed-only", "-a", help="Include all campaigns (default) or only managed"
    ),
    json_output: bool = typer.Option(False, "--json", help="Emit stable machine-readable JSON"),
):
    """Show campaign performance over exact completed calendar dates."""
    credentials = load_credentials()
    if not credentials:
        console.print("[red]No credentials configured. Run 'asa config setup' first.[/red]")
        raise typer.Exit(1)

    client = SearchAdsClient(credentials)

    window = _resolve_window(days, start_date, end_date)
    start, end = window.as_datetimes()

    if not json_output:
        console.print(
            Panel(
                f"[bold]Performance Summary[/bold]\n"
                f"{window.start.isoformat()} to {window.end.isoformat()}",
                expand=False,
            )
        )

    with _status("[bold blue]Fetching campaigns...", json_output=json_output):
        campaigns = client.get_campaigns()

    app_name = _resolve_app_name()

    # Filter campaigns to current app first (in multi-app mode)
    if app_name:
        campaigns = [c for c in campaigns if parse_campaign_name(c.get("name", ""), app_name=app_name)]

    # Filter campaigns based on flag
    if all_campaigns:
        campaign_list = [(c, get_campaign_type_label(c.get("name", ""), app_name=app_name)) for c in campaigns]
    else:
        # Only managed campaigns with specific naming
        managed = [(c, parse_campaign_name(c.get("name", ""), app_name=app_name)) for c in campaigns]
        campaign_list = [(c, p[1].value.upper()) for c, p in managed if p]

    if not campaign_list:
        if json_output:
            _print_json(
                machine_report(
                    "summary", window, [], totals=performance_totals([]), time_zone="UTC"
                )
            )
        else:
            console.print("[yellow]No campaigns found.[/yellow]")
        return

    table = Table(title="Campaign Performance", show_header=True, header_style="bold magenta")
    table.add_column("Campaign")
    table.add_column("Status")
    table.add_column("Impressions", justify="right")
    table.add_column("Taps", justify="right")
    table.add_column("TTR", justify="right")
    table.add_column("Installs", justify="right")
    table.add_column("CVR", justify="right")
    table.add_column("Spend", justify="right")
    table.add_column("CPA", justify="right")

    totals = {
        "impressions": 0,
        "taps": 0,
        "installs": 0,
        "spend": 0.0,
    }

    machine_rows = []
    for campaign, ctype_label in campaign_list:
        campaign_id = campaign.get("id")
        campaign_name = campaign.get("name", "Unknown")

        with _status(
            f"[bold blue]Fetching {campaign_name} report...", json_output=json_output
        ):
            report_data = client.get_campaign_report(campaign_id, start, end, granularity="DAILY")

        # Aggregate metrics
        impressions = 0
        taps = 0
        installs = 0
        spend = 0.0

        for row in report_data:
            # Metrics are in 'total' key, not 'metadata'
            metrics = row.get("total", {})
            impressions += metrics.get("impressions", 0)
            taps += metrics.get("taps", 0)
            installs += metrics.get("totalInstalls", 0) or metrics.get("tapInstalls", 0)
            spend_data = metrics.get("localSpend", {})
            spend += float(spend_data.get("amount", 0)) if spend_data else 0

        # Calculate rates
        ttr = (taps / impressions * 100) if impressions > 0 else 0
        cvr = (installs / taps * 100) if taps > 0 else 0
        cpa = (spend / installs) if installs > 0 else 0

        status = campaign.get("displayStatus", "UNKNOWN")
        status_style = "green" if status == "RUNNING" else "yellow" if status == "PAUSED" else "red"

        machine_rows.append(
            {
                "campaign_id": campaign_id,
                "campaign_name": campaign_name,
                "campaign_type": ctype_label.lower(),
                "status": status,
                "impressions": impressions,
                "taps": taps,
                "installs": installs,
                "spend": spend,
                "avg_cpt": spend / taps if taps else None,
                "cpa": spend / installs if installs else None,
                "ttr": taps / impressions if impressions else None,
                "conversion_rate": installs / taps if taps else None,
            }
        )

        table.add_row(
            ctype_label,
            f"[{status_style}]{status}[/{status_style}]",
            format_number(impressions),
            format_number(taps),
            f"{ttr:.2f}%",
            format_number(installs),
            f"{cvr:.2f}%",
            format_currency(spend),
            format_currency(cpa) if installs > 0 else "-",
        )

        # Accumulate totals
        totals["impressions"] += impressions
        totals["taps"] += taps
        totals["installs"] += installs
        totals["spend"] += spend

    # Add totals row
    total_ttr = (
        (totals["taps"] / totals["impressions"] * 100) if totals["impressions"] > 0 else 0
    )
    total_cvr = (totals["installs"] / totals["taps"] * 100) if totals["taps"] > 0 else 0
    total_cpa = (totals["spend"] / totals["installs"]) if totals["installs"] > 0 else 0

    table.add_row(
        "[bold]TOTAL[/bold]",
        "",
        f"[bold]{format_number(totals['impressions'])}[/bold]",
        f"[bold]{format_number(totals['taps'])}[/bold]",
        f"[bold]{total_ttr:.2f}%[/bold]",
        f"[bold]{format_number(totals['installs'])}[/bold]",
        f"[bold]{total_cvr:.2f}%[/bold]",
        f"[bold]{format_currency(totals['spend'])}[/bold]",
        f"[bold]{format_currency(total_cpa)}[/bold]" if totals["installs"] > 0 else "-",
    )

    if json_output:
        machine_rows.sort(key=lambda row: (row["campaign_name"] or "", row["campaign_id"] or 0))
        _print_json(
            machine_report(
                "summary",
                window,
                machine_rows,
                totals=performance_totals(machine_rows),
                time_zone="UTC",
            )
        )
    else:
        console.print(table)


@app.command("keywords")
def report_keywords(
    campaign_id: Optional[int] = typer.Option(None, "--campaign", "-c", help="Campaign ID"),
    days: int = typer.Option(30, "--days", "-d", help="Number of days"),
    start_date: Optional[str] = typer.Option(
        None, "--start", "--start-date", help="Inclusive start date (YYYY-MM-DD)"
    ),
    end_date: Optional[str] = typer.Option(
        None, "--end", "--end-date", help="Inclusive complete end date (YYYY-MM-DD)"
    ),
    min_impressions: int = typer.Option(0, "--min-impressions", help="Minimum impressions filter"),
    sort_by: str = typer.Option("spend", "--sort", "-s", help="Sort by: spend, impressions, taps, installs, cpa"),
    limit: int = typer.Option(50, "--limit", "-l", help="Max keywords to show"),
    all_campaigns: bool = typer.Option(False, "--all", "-a", help="Report every scoped campaign"),
    include_zero: bool = typer.Option(
        False,
        "--include-zero",
        help="Merge complete targeting-keyword inventory, including zero-activity rows",
    ),
    json_output: bool = typer.Option(False, "--json", help="Emit stable machine-readable JSON"),
):
    """Show keyword performance over exact completed calendar dates."""
    credentials = load_credentials()
    if not credentials:
        console.print("[red]No credentials configured. Run 'asa config setup' first.[/red]")
        raise typer.Exit(1)

    client = SearchAdsClient(credentials)
    window = _resolve_window(days, start_date, end_date)
    start, end = window.as_datetimes()
    app_name = _resolve_app_name()

    campaigns = client.get_campaigns()
    if app_name:
        campaigns = [
            campaign
            for campaign in campaigns
            if parse_campaign_name(campaign.get("name", ""), app_name=app_name)
        ]
    if campaign_id is not None:
        campaigns = [campaign for campaign in campaigns if campaign.get("id") == campaign_id]
        if not campaigns:
            console.print(f"[red]Campaign {campaign_id} not found in the current app scope.[/red]")
            raise typer.Exit(1)
    elif not all_campaigns and not json_output:
        if not campaigns:
            console.print("[yellow]No campaigns found.[/yellow]")
            return
        table = Table(show_header=True)
        table.add_column("#", style="cyan")
        table.add_column("Type")
        table.add_column("Name")
        for idx, campaign in enumerate(campaigns, 1):
            table.add_row(
                str(idx),
                get_campaign_type_label(campaign.get("name", ""), app_name=app_name),
                campaign.get("name", "")[:50],
            )
        console.print(table)
        from rich.prompt import Prompt

        choice = Prompt.ask("Select campaign number")
        if not choice.isdigit() or not (1 <= int(choice) <= len(campaigns)):
            console.print("[red]Invalid selection.[/red]")
            raise typer.Exit(1)
        campaigns = [campaigns[int(choice) - 1]]
    elif not all_campaigns and json_output:
        raise typer.BadParameter("Machine output requires --campaign or --all")

    keywords: list[dict] = []
    for campaign in campaigns:
        cid = campaign.get("id")
        with _status(
            f"[bold blue]Fetching {campaign.get('name', cid)} keyword report...",
            json_output=json_output,
        ):
            report_data = client.get_keyword_report(cid, start, end)

        report_by_id = {
            row.get("metadata", {}).get("keywordId"): row
            for row in report_data
            if row.get("metadata", {}).get("keywordId") is not None
        }
        report_by_key = {
            (
                row.get("metadata", {}).get("adGroupId"),
                row.get("metadata", {}).get("keyword"),
                row.get("metadata", {}).get("matchType"),
            ): row
            for row in report_data
        }

        if include_zero:
            for ad_group in client.get_ad_groups(cid):
                for inventory_keyword in client.get_keywords(cid, ad_group.get("id")):
                    source_row = report_by_id.get(inventory_keyword.get("id")) or report_by_key.get(
                        (
                            ad_group.get("id"),
                            inventory_keyword.get("text"),
                            inventory_keyword.get("matchType"),
                        )
                    ) or {"metadata": {}, "total": {}}
                    keywords.append(
                        normalize_performance_row(
                            source_row,
                            kind="keyword",
                            campaign=campaign,
                            ad_group=ad_group,
                            inventory=inventory_keyword,
                        )
                    )
        else:
            keywords.extend(
                normalize_performance_row(row, kind="keyword", campaign=campaign)
                for row in report_data
            )

    keywords = [row for row in keywords if row["impressions"] >= min_impressions]

    # Sort
    sort_key = {
        "spend": lambda x: -x["spend"],
        "impressions": lambda x: -x["impressions"],
        "taps": lambda x: -x["taps"],
        "installs": lambda x: -x["installs"],
        "cpa": lambda x: x["cpa"] if x["cpa"] is not None else 999999,
    }.get(sort_by, lambda x: -x["spend"])

    keywords.sort(key=sort_key)
    if not include_zero and limit > 0:
        keywords = keywords[:limit]

    if json_output:
        keywords.sort(
            key=lambda row: (
                row.get("campaign_name") or "",
                row.get("ad_group_name") or "",
                row.get("keyword") or "",
                row.get("match_type") or "",
                row.get("keyword_id") or 0,
            )
        )
        _print_json(
            machine_report(
                "keywords",
                window,
                keywords,
                totals=performance_totals(keywords),
                inventory_complete=include_zero and min_impressions == 0,
                time_zone="UTC",
            )
        )
        return

    if not keywords:
        console.print("[yellow]No keyword data found.[/yellow]")
        return

    console.print(
        Panel(
            f"[bold]Keyword Performance[/bold]\n"
            f"{window.start.isoformat()} to {window.end.isoformat()} • "
            f"Sorted by {sort_by} • Min impressions: {min_impressions}",
            expand=False,
        )
    )

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Keyword")
    table.add_column("Match", style="dim")
    table.add_column("Impr", justify="right")
    table.add_column("Taps", justify="right")
    table.add_column("TTR", justify="right")
    table.add_column("Inst", justify="right")
    table.add_column("CVR", justify="right")
    table.add_column("Spend", justify="right")
    table.add_column("CPA", justify="right")

    for kw in keywords:
        cpa_str = format_currency(kw["cpa"]) if kw["cpa"] is not None else "-"
        table.add_row(
            (kw["keyword"] or "?")[:30],
            (kw["match_type"] or "?")[:5],
            format_number(kw["impressions"]),
            format_number(kw["taps"]),
            f"{kw['ttr'] * 100:.1f}%" if kw["ttr"] is not None else "-",
            format_number(kw["installs"]),
            f"{kw['conversion_rate'] * 100:.1f}%"
            if kw["conversion_rate"] is not None
            else "-",
            format_currency(kw["spend"]),
            cpa_str,
        )

    console.print(table)


@app.command("adgroups")
def report_adgroups(
    campaign_id: Optional[int] = typer.Option(None, "--campaign", "-c", help="Campaign ID"),
    days: int = typer.Option(30, "--days", "-d", help="Number of days"),
    start_date: Optional[str] = typer.Option(
        None, "--start", "--start-date", help="Inclusive start date (YYYY-MM-DD)"
    ),
    end_date: Optional[str] = typer.Option(
        None, "--end", "--end-date", help="Inclusive complete end date (YYYY-MM-DD)"
    ),
    all_campaigns: bool = typer.Option(False, "--all", "-a", help="Show ad groups for all campaigns"),
):
    """Show ad group performance report."""
    credentials = load_credentials()
    if not credentials:
        console.print("[red]No credentials configured. Run 'asa config setup' first.[/red]")
        raise typer.Exit(1)

    client = SearchAdsClient(credentials)

    window = _resolve_window(days, start_date, end_date)
    start, end = window.as_datetimes()

    # Get campaigns to report on
    campaigns_to_report = []
    app_name = _resolve_app_name()

    def _filter_by_app(campaigns: list) -> list:
        if app_name:
            return [c for c in campaigns if parse_campaign_name(c.get("name", ""), app_name=app_name)]
        return campaigns

    if all_campaigns:
        campaigns = _filter_by_app(client.get_campaigns())
        campaigns_to_report = campaigns
    elif campaign_id:
        campaign = client.get_campaign(campaign_id)
        if campaign:
            campaigns_to_report = [campaign]
        else:
            console.print(f"[red]Campaign {campaign_id} not found.[/red]")
            raise typer.Exit(1)
    else:
        # Interactive selection
        campaigns = _filter_by_app(client.get_campaigns())
        if not campaigns:
            console.print("[yellow]No campaigns found.[/yellow]")
            return

        table = Table(show_header=True)
        table.add_column("#", style="cyan")
        table.add_column("Type")
        table.add_column("Name")

        for idx, c in enumerate(campaigns, 1):
            ctype = get_campaign_type_label(c.get("name", ""), app_name=app_name)
            table.add_row(str(idx), ctype, c.get("name", "")[:50])

        console.print(table)

        from rich.prompt import Prompt

        choice = Prompt.ask("Select campaign number (or 'all')")
        if choice.lower() == "all":
            campaigns_to_report = campaigns
        elif choice.isdigit() and 1 <= int(choice) <= len(campaigns):
            campaigns_to_report = [campaigns[int(choice) - 1]]
        else:
            console.print("[red]Invalid selection.[/red]")
            return

    console.print(
        Panel(
            f"[bold]Ad Group Performance[/bold]\n"
            f"{window.start.isoformat()} to {window.end.isoformat()}",
            expand=False,
        )
    )

    for campaign in campaigns_to_report:
        cid = campaign.get("id")
        cname = campaign.get("name", "Unknown")
        ctype = get_campaign_type_label(cname, app_name=_resolve_app_name())

        with console.status(f"[bold blue]Fetching {cname} ad group report..."):
            report_data = client.get_ad_group_report(cid, start, end)

        if not report_data:
            console.print(f"[yellow]{ctype}: No ad group data[/yellow]")
            continue

        table = Table(title=f"{ctype} - Ad Groups", show_header=True, header_style="bold magenta")
        table.add_column("Ad Group")
        table.add_column("Status")
        table.add_column("Impr", justify="right")
        table.add_column("Taps", justify="right")
        table.add_column("TTR", justify="right")
        table.add_column("Inst", justify="right")
        table.add_column("CVR", justify="right")
        table.add_column("Spend", justify="right")
        table.add_column("CPA", justify="right")

        campaign_totals = {"impressions": 0, "taps": 0, "installs": 0, "spend": 0.0}

        for row in report_data:
            metadata = row.get("metadata", {})
            metrics = row.get("total", {})

            ag_name = metadata.get("adGroupName", "Unknown")
            ag_status = metadata.get("adGroupStatus", "?")

            impressions = metrics.get("impressions", 0)
            taps = metrics.get("taps", 0)
            installs = metrics.get("totalInstalls", 0) or metrics.get("tapInstalls", 0)
            spend_data = metrics.get("localSpend", {})
            spend = float(spend_data.get("amount", 0)) if spend_data else 0

            ttr = (taps / impressions * 100) if impressions > 0 else 0
            cvr = (installs / taps * 100) if taps > 0 else 0
            cpa = (spend / installs) if installs > 0 else 0

            status_style = "green" if ag_status == "ENABLED" else "yellow" if ag_status == "PAUSED" else "dim"

            table.add_row(
                ag_name[:25],
                f"[{status_style}]{ag_status}[/{status_style}]",
                format_number(impressions),
                format_number(taps),
                f"{ttr:.1f}%",
                format_number(installs),
                f"{cvr:.1f}%",
                format_currency(spend),
                format_currency(cpa) if installs > 0 else "-",
            )

            campaign_totals["impressions"] += impressions
            campaign_totals["taps"] += taps
            campaign_totals["installs"] += installs
            campaign_totals["spend"] += spend

        # Add campaign totals
        total_ttr = (campaign_totals["taps"] / campaign_totals["impressions"] * 100) if campaign_totals["impressions"] > 0 else 0
        total_cvr = (campaign_totals["installs"] / campaign_totals["taps"] * 100) if campaign_totals["taps"] > 0 else 0
        total_cpa = (campaign_totals["spend"] / campaign_totals["installs"]) if campaign_totals["installs"] > 0 else 0

        table.add_row(
            "[bold]Total[/bold]",
            "",
            f"[bold]{format_number(campaign_totals['impressions'])}[/bold]",
            f"[bold]{format_number(campaign_totals['taps'])}[/bold]",
            f"[bold]{total_ttr:.1f}%[/bold]",
            f"[bold]{format_number(campaign_totals['installs'])}[/bold]",
            f"[bold]{total_cvr:.1f}%[/bold]",
            f"[bold]{format_currency(campaign_totals['spend'])}[/bold]",
            f"[bold]{format_currency(total_cpa)}[/bold]" if campaign_totals["installs"] > 0 else "-",
        )

        console.print(table)
        console.print()


@app.command("impression-share")
def report_impression_share(
    campaign_id: Optional[int] = typer.Option(
        None, "--campaign", "-c", help="Resolve the advertised app from a campaign"
    ),
    adam_id: Optional[int] = typer.Option(None, "--adam-id", help="Filter to an App Store Adam ID"),
    countries: Optional[str] = typer.Option(
        None, "--countries", help="Comma-separated country or region codes"
    ),
    days: int = typer.Option(30, "--days", "-d", help="Number of completed days (max 30)"),
    start_date: Optional[str] = typer.Option(
        None, "--start", "--start-date", help="Inclusive start date (YYYY-MM-DD)"
    ),
    end_date: Optional[str] = typer.Option(
        None, "--end", "--end-date", help="Inclusive complete end date (YYYY-MM-DD)"
    ),
    report_id: Optional[str] = typer.Option(
        None, "--report-id", help="Reuse an existing custom report instead of creating one"
    ),
    all_apps: bool = typer.Option(False, "--all", help="Do not filter the organization by app"),
    wait: bool = typer.Option(True, "--wait/--no-wait", help="Wait for and download report results"),
    poll_interval: float = typer.Option(5.0, "--poll-interval", min=1.0, help="Polling seconds"),
    timeout: int = typer.Option(300, "--timeout", min=1, help="Maximum wait seconds"),
    limit: int = typer.Option(0, "--limit", "-l", help="Max rows (0 means all)"),
    json_output: bool = typer.Option(False, "--json", help="Emit stable machine-readable JSON"),
):
    """Fetch Apple's true async impression-share report and download its CSV."""
    import time as _time

    credentials = load_credentials()
    if not credentials:
        console.print("[red]No credentials configured. Run 'asa config setup' first.[/red]")
        raise typer.Exit(1)

    client = SearchAdsClient(credentials)
    window = _resolve_window(days, start_date, end_date)
    if window.days > 30:
        raise typer.BadParameter("Apple impression-share custom reports are limited to 30 days")

    resolved_adam_id = adam_id
    if campaign_id is not None:
        campaign = client.get_campaign(campaign_id)
        if not campaign:
            console.print(f"[red]Campaign {campaign_id} not found.[/red]")
            raise typer.Exit(1)
        resolved_adam_id = resolved_adam_id or campaign.get("adamId")

    if not all_apps and resolved_adam_id is None:
        app_config = get_current_app_config()
        resolved_adam_id = app_config.app_id if app_config else None
    if not all_apps and resolved_adam_id is None:
        raise typer.BadParameter("Use --adam-id, --campaign, or configure a current app")

    conditions = []
    if not all_apps:
        conditions.append(
            {"field": "adamId", "operator": "IN", "values": [str(resolved_adam_id)]}
        )
    if countries:
        country_values = sorted(
            {country.strip().upper() for country in countries.split(",") if country.strip()}
        )
        if country_values:
            conditions.append(
                {"field": "countryOrRegion", "operator": "IN", "values": country_values}
            )

    if report_id:
        report = client.get_custom_report(report_id)
        report_start = report.get("startTime")
        report_end = report.get("endTime")
        if report_start and report_end:
            report_window = _resolve_window(1, report_start, report_end)
            if (start_date or end_date) and report_window != window:
                raise typer.BadParameter(
                    "The existing report date window does not match --start/--end"
                )
            window = report_window
    else:
        report_name = f"asa-cli IS {window.end.isoformat()}"[:50]
        report = client.create_custom_report(
            report_name,
            window.start.isoformat(),
            window.end.isoformat(),
            conditions=conditions or None,
        )

    if wait:
        deadline = _time.monotonic() + timeout
        while report.get("state") not in ("COMPLETED", "FAILED"):
            if _time.monotonic() >= deadline:
                console.print(
                    f"[red]Report {report.get('id')} did not complete within {timeout}s.[/red]"
                )
                raise typer.Exit(1)
            _time.sleep(poll_interval)
            report = client.get_custom_report(str(report.get("id")))

    state = report.get("state", "UNKNOWN")
    if state == "FAILED":
        console.print(f"[red]Impression-share report {report.get('id')} failed.[/red]")
        raise typer.Exit(1)

    rows: list[dict] = []
    if state == "COMPLETED":
        download_uri = report.get("downloadUri")
        if not download_uri:
            console.print("[red]Completed report did not include a download URI.[/red]")
            raise typer.Exit(1)
        rows = parse_impression_share_csv(client.download_custom_report(download_uri))
        if limit > 0:
            rows = rows[:limit]

    payload = machine_report(
        "impression_share",
        window,
        rows,
        time_zone="ORTZ",
        extra={
            "report": {
                "id": report.get("id"),
                "name": report.get("name"),
                "state": state,
            },
            "selector": report.get("selector") or {"conditions": conditions},
        },
    )
    if json_output:
        _print_json(payload)
        return

    if state != "COMPLETED":
        console.print(
            f"[yellow]Report {report.get('id')} is {state}. Re-run with "
            f"--report-id {report.get('id')}.[/yellow]"
        )
        return

    console.print(
        Panel(
            f"[bold]Apple Impression Share[/bold]\n"
            f"{window.start.isoformat()} to {window.end.isoformat()} • {len(rows)} rows",
            expand=False,
        )
    )
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Date")
    table.add_column("Country")
    table.add_column("Search term")
    table.add_column("Share", justify="right")
    table.add_column("Rank", justify="right")
    table.add_column("Popularity", justify="right")
    for row in rows:
        low = row.get("low_impression_share")
        high = row.get("high_impression_share")
        share = f"{low:.0%}–{high:.0%}" if low is not None and high is not None else "-"
        table.add_row(
            row.get("date") or "-",
            row.get("country_or_region") or "-",
            row.get("search_term") or "-",
            share,
            row.get("rank") or "-",
            str(row.get("search_popularity") or "-"),
        )
    console.print(table)


@app.command("search-terms")
def report_search_terms(
    campaign_id: Optional[int] = typer.Option(None, "--campaign", "-c", help="Campaign ID"),
    days: int = typer.Option(14, "--days", "-d", help="Number of days"),
    start_date: Optional[str] = typer.Option(
        None, "--start", "--start-date", help="Inclusive start date (YYYY-MM-DD)"
    ),
    end_date: Optional[str] = typer.Option(
        None, "--end", "--end-date", help="Inclusive complete end date (YYYY-MM-DD)"
    ),
    min_impressions: int = typer.Option(10, "--min-impressions", help="Minimum impressions filter"),
    show_winners: bool = typer.Option(False, "--winners", "-w", help="Show potential keywords to promote"),
    show_negatives: bool = typer.Option(False, "--negatives", "-n", help="Show potential negative keywords"),
    limit: int = typer.Option(50, "--limit", "-l", help="Max terms to show"),
    json_output: bool = typer.Option(False, "--json", help="Emit stable machine-readable JSON"),
):
    """Show search terms over exact completed calendar dates."""
    credentials = load_credentials()
    if not credentials:
        console.print("[red]No credentials configured. Run 'asa config setup' first.[/red]")
        raise typer.Exit(1)

    client = SearchAdsClient(credentials)

    window = _resolve_window(days, start_date, end_date)
    start, end = window.as_datetimes()

    # Find Discovery campaign if not specified
    if campaign_id is None:
        campaigns = client.get_campaigns()
        app_name = _resolve_app_name()

        # Filter to current app in multi-app mode
        if app_name:
            campaigns = [c for c in campaigns if parse_campaign_name(c.get("name", ""), app_name=app_name)]

        discovery = None
        for c in campaigns:
            name = c.get("name", "")
            parsed = parse_campaign_name(name, app_name=app_name)
            # Support both managed naming and simple naming (e.g., "Discovery")
            if (parsed and parsed[1] == CampaignType.DISCOVERY) or "discovery" in name.lower():
                discovery = c
                break

        if discovery:
            campaign_id = discovery.get("id")
            if not json_output:
                console.print(f"Using Discovery campaign: {discovery.get('name')}")
        else:
            # Select any campaign
            if not campaigns:
                console.print("[yellow]No campaigns found.[/yellow]")
                return

            if json_output:
                raise typer.BadParameter(
                    "No Discovery campaign was found; machine output requires --campaign"
                )

            from rich.prompt import Prompt

            table = Table(show_header=True)
            table.add_column("#", style="cyan")
            table.add_column("Type")
            table.add_column("Name")

            for idx, c in enumerate(campaigns, 1):
                ctype = get_campaign_type_label(c.get("name", ""), app_name=app_name)
                table.add_row(str(idx), ctype, c.get("name", "")[:50])

            console.print(table)
            choice = Prompt.ask("Select campaign number")
            if not choice.isdigit() or not (1 <= int(choice) <= len(campaigns)):
                console.print("[red]Invalid selection.[/red]")
                return
            campaign_id = campaigns[int(choice) - 1].get("id")

    campaign = client.get_campaign(campaign_id) or {"id": campaign_id}
    with _status("[bold blue]Fetching search terms report...", json_output=json_output):
        report_data = client.get_search_terms_report(campaign_id, start, end)

    if not report_data:
        if json_output:
            _print_json(
                machine_report(
                    "search_terms", window, [], totals=performance_totals([])
                )
            )
        else:
            console.print("[yellow]No search term data found.[/yellow]")
        return

    terms = [
        normalize_performance_row(row, kind="search_term", campaign=campaign)
        for row in report_data
    ]
    terms = [term for term in terms if term["impressions"] >= min_impressions]

    if show_winners:
        # Filter to terms with installs and reasonable CPA
        winners = [t for t in terms if t["installs"] >= 1]
        winners.sort(key=lambda x: x["cpa"] if x["cpa"] is not None else 999999)
        terms = winners[:limit]
        title = "Potential Keywords to Promote"
    elif show_negatives:
        # Filter to terms with spend but no installs
        losers = [t for t in terms if t["installs"] == 0 and t["spend"] > 0]
        losers.sort(key=lambda x: -x["spend"])
        terms = losers[:limit]
        title = "Potential Negative Keywords"
    else:
        terms.sort(key=lambda x: -x["spend"])
        terms = terms[:limit]
        title = "Search Terms"

    if json_output:
        terms.sort(
            key=lambda row: (
                row.get("campaign_name") or "",
                row.get("ad_group_name") or "",
                row.get("search_term") or "",
                row.get("keyword_id") or 0,
            )
        )
        _print_json(
            machine_report(
                "search_terms",
                window,
                terms,
                totals=performance_totals(terms),
                time_zone="ORTZ",
                extra={
                    "filter": "winners"
                    if show_winners
                    else "negatives"
                    if show_negatives
                    else "all"
                },
            )
        )
        return

    console.print(
        Panel(
            f"[bold]{title}[/bold]\n{window.start.isoformat()} to {window.end.isoformat()} "
            f"• Min impressions: {min_impressions}",
            expand=False,
        )
    )

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Search Term")
    table.add_column("Source", style="dim")
    table.add_column("Impr", justify="right")
    table.add_column("Taps", justify="right")
    table.add_column("Inst", justify="right")
    table.add_column("Spend", justify="right")
    table.add_column("CPA", justify="right")

    for t in terms:
        cpa_str = format_currency(t["cpa"]) if t["cpa"] is not None else "-"

        # Color code based on performance
        if t["installs"] > 0 and t["cpa"] is not None:
            term_style = "green" if t["cpa"] < 5 else "yellow" if t["cpa"] < 10 else ""
        elif t["spend"] > 1 and t["installs"] == 0:
            term_style = "red"
        else:
            term_style = ""

        term_text = t["search_term"] or "?"
        term_display = f"[{term_style}]{term_text[:35]}[/{term_style}]" if term_style else term_text[:35]

        table.add_row(
            term_display,
            (t["source"] or "?")[:10],
            format_number(t["impressions"]),
            format_number(t["taps"]),
            format_number(t["installs"]),
            format_currency(t["spend"]),
            cpa_str,
        )

    console.print(table)

    if show_winners and terms:
        console.print("\n[bold]To promote these keywords:[/bold]")
        keyword_list = ",".join([t["search_term"] for t in terms[:10] if t["search_term"]])
        console.print(f'[cyan]asa keywords promote "{keyword_list}" --target category[/cyan]')
    elif show_negatives and terms:
        console.print("\n[bold]To add as negatives:[/bold]")
        keyword_list = ",".join([t["search_term"] for t in terms[:10] if t["search_term"]])
        console.print(f'[cyan]asa keywords add-negatives "{keyword_list}" --all[/cyan]')


@app.command("custom")
def report_custom(
    days: int = typer.Option(30, "--days", "-d", help="Number of days (max 30)"),
    start_date: Optional[str] = typer.Option(
        None, "--start", "--start-date", help="Inclusive start date (YYYY-MM-DD)"
    ),
    end_date: Optional[str] = typer.Option(
        None, "--end", "--end-date", help="Inclusive complete end date (YYYY-MM-DD)"
    ),
    name: str = typer.Option("Impression Share Report", "--name", "-n", help="Report name"),
):
    """Create a custom impression share report, poll until complete, and display results."""
    import time as _time

    credentials = load_credentials()
    if not credentials:
        console.print("[red]No credentials configured. Run 'asa config setup' first.[/red]")
        raise typer.Exit(1)

    client = SearchAdsClient(credentials)

    window = _resolve_window(days, start_date, end_date)
    if window.days > 30:
        raise typer.BadParameter("Apple impression-share custom reports are limited to 30 days")
    start_str = window.start.isoformat()
    end_str = window.end.isoformat()

    console.print(
        Panel(
            f"[bold]Custom Report[/bold]\n{start_str} to {end_str}",
            expand=False,
        )
    )

    with console.status("[bold blue]Creating custom report..."):
        report = client.create_custom_report(name, start_str, end_str)

    if not report:
        console.print("[red]Failed to create custom report.[/red]")
        raise typer.Exit(1)

    report_id = report.get("id")
    state = report.get("state", "UNKNOWN")
    console.print(f"Report created: [cyan]{report_id}[/cyan] (state: {state})")

    # Poll until complete (max 5 minutes)
    max_polls = 30
    poll_count = 0

    with console.status("[bold blue]Waiting for report to complete...") as status:
        while state not in ("COMPLETED", "FAILED") and poll_count < max_polls:
            _time.sleep(10)
            poll_count += 1
            status.update(f"[bold blue]Polling report status... ({poll_count}/{max_polls})")
            report = client.get_custom_report(report_id)
            if not report:
                console.print("[red]Failed to fetch report status.[/red]")
                raise typer.Exit(1)
            state = report.get("state", "UNKNOWN")

    if state == "FAILED":
        console.print("[red]Report generation failed.[/red]")
        raise typer.Exit(1)

    if state != "COMPLETED":
        console.print(f"[yellow]Report still processing after {max_polls * 10}s (state: {state}).[/yellow]")
        console.print(f"Check later with: [cyan]asa reports custom-get {report_id}[/cyan]")
        return

    download_uri = report.get("downloadUri")
    if download_uri:
        console.print(f"[green]Report complete![/green] Download: {download_uri}")
    else:
        console.print("[green]Report complete![/green]")

    # Display available report data
    table = Table(title="Custom Report Results", show_header=True, header_style="bold magenta")
    table.add_column("Field")
    table.add_column("Value")

    for key, value in report.items():
        if key != "downloadUri":
            table.add_row(str(key), str(value)[:80])

    console.print(table)


@app.command("custom-list")
def report_custom_list():
    """List all custom reports."""
    credentials = load_credentials()
    if not credentials:
        console.print("[red]No credentials configured. Run 'asa config setup' first.[/red]")
        raise typer.Exit(1)

    client = SearchAdsClient(credentials)

    with console.status("[bold blue]Fetching custom reports..."):
        reports = client.get_all_custom_reports()

    if not reports:
        console.print("[yellow]No custom reports found.[/yellow]")
        return

    table = Table(title="Custom Reports", show_header=True, header_style="bold magenta")
    table.add_column("ID")
    table.add_column("Name")
    table.add_column("State")
    table.add_column("Start")
    table.add_column("End")
    table.add_column("Granularity")

    for report in reports:
        state = report.get("state", "?")
        state_style = (
            "green" if state == "COMPLETED"
            else "yellow" if state == "QUEUED"
            else "blue" if state == "RUNNING"
            else "red"
        )

        table.add_row(
            str(report.get("id", "?")),
            report.get("name", "?")[:30],
            f"[{state_style}]{state}[/{state_style}]",
            report.get("startTime", "?")[:10],
            report.get("endTime", "?")[:10],
            report.get("granularity", "?"),
        )

    console.print(table)


@app.command("custom-get")
def report_custom_get(
    report_id: str = typer.Argument(..., help="Custom report ID"),
):
    """Get a specific custom report status and results."""
    credentials = load_credentials()
    if not credentials:
        console.print("[red]No credentials configured. Run 'asa config setup' first.[/red]")
        raise typer.Exit(1)

    client = SearchAdsClient(credentials)

    with console.status("[bold blue]Fetching custom report..."):
        report = client.get_custom_report(report_id)

    if not report:
        console.print(f"[red]Custom report {report_id} not found.[/red]")
        raise typer.Exit(1)

    state = report.get("state", "UNKNOWN")
    state_style = (
        "green" if state == "COMPLETED"
        else "yellow" if state == "QUEUED"
        else "blue" if state == "RUNNING"
        else "red"
    )

    console.print(Panel(
        f"[bold]Custom Report: {report.get('name', '?')}[/bold]\n"
        f"State: [{state_style}]{state}[/{state_style}]",
        expand=False,
    ))

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Field")
    table.add_column("Value")

    for key, value in report.items():
        table.add_row(str(key), str(value)[:100])

    console.print(table)

    if state == "COMPLETED" and report.get("downloadUri"):
        console.print(f"\n[green]Download URI:[/green] {report['downloadUri']}")


@app.command("ads")
def report_ads(
    campaign_id: Optional[int] = typer.Option(None, "--campaign", "-c", help="Campaign ID"),
    days: int = typer.Option(14, "--days", "-d", help="Number of days"),
    start_date: Optional[str] = typer.Option(
        None, "--start", "--start-date", help="Inclusive start date (YYYY-MM-DD)"
    ),
    end_date: Optional[str] = typer.Option(
        None, "--end", "--end-date", help="Inclusive complete end date (YYYY-MM-DD)"
    ),
    all_campaigns: bool = typer.Option(False, "--all", "-a", help="Show ad report for all campaigns"),
    json_output: bool = typer.Option(False, "--json", help="Emit stable machine-readable JSON"),
):
    """Show ad performance over exact completed calendar dates."""
    credentials = load_credentials()
    if not credentials:
        console.print("[red]No credentials configured. Run 'asa config setup' first.[/red]")
        raise typer.Exit(1)

    client = SearchAdsClient(credentials)

    window = _resolve_window(days, start_date, end_date)
    start, end = window.as_datetimes()

    # Get campaigns to report on
    campaigns_to_report = []
    app_name = _resolve_app_name()

    def _filter_by_app(campaigns: list) -> list:
        if app_name:
            return [c for c in campaigns if parse_campaign_name(c.get("name", ""), app_name=app_name)]
        return campaigns

    if all_campaigns:
        campaigns = _filter_by_app(client.get_campaigns())
        campaigns_to_report = campaigns
    elif campaign_id:
        campaign = client.get_campaign(campaign_id)
        if campaign:
            campaigns_to_report = [campaign]
        else:
            console.print(f"[red]Campaign {campaign_id} not found.[/red]")
            raise typer.Exit(1)
    else:
        # Interactive selection
        campaigns = _filter_by_app(client.get_campaigns())
        if not campaigns:
            console.print("[yellow]No campaigns found.[/yellow]")
            return

        if json_output:
            raise typer.BadParameter("Machine output requires --campaign or --all")

        table = Table(show_header=True)
        table.add_column("#", style="cyan")
        table.add_column("Type")
        table.add_column("Name")

        for idx, c in enumerate(campaigns, 1):
            ctype = get_campaign_type_label(c.get("name", ""), app_name=app_name)
            table.add_row(str(idx), ctype, c.get("name", "")[:50])

        console.print(table)

        from rich.prompt import Prompt

        choice = Prompt.ask("Select campaign number (or 'all')")
        if choice.lower() == "all":
            campaigns_to_report = campaigns
        elif choice.isdigit() and 1 <= int(choice) <= len(campaigns):
            campaigns_to_report = [campaigns[int(choice) - 1]]
        else:
            console.print("[red]Invalid selection.[/red]")
            return

    if not json_output:
        console.print(
            Panel(
                f"[bold]Ad Performance Report[/bold]\n"
                f"{window.start.isoformat()} to {window.end.isoformat()}",
                expand=False,
            )
        )

    machine_rows = []
    for campaign in campaigns_to_report:
        cid = campaign.get("id")
        cname = campaign.get("name", "Unknown")
        ctype = get_campaign_type_label(cname, app_name=_resolve_app_name())

        with _status(
            f"[bold blue]Fetching {cname} ad report...", json_output=json_output
        ):
            report_data = client.get_ad_report(cid, start, end)

        if not report_data:
            if not json_output:
                console.print(f"[yellow]{ctype}: No ad data[/yellow]")
            continue

        machine_rows.extend(
            normalize_performance_row(row, kind="ad", campaign=campaign)
            for row in report_data
        )

        table = Table(title=f"{ctype} - Ads", show_header=True, header_style="bold magenta")
        table.add_column("Ad Name")
        table.add_column("Status")
        table.add_column("Impr", justify="right")
        table.add_column("Taps", justify="right")
        table.add_column("TTR", justify="right")
        table.add_column("Inst", justify="right")
        table.add_column("CVR", justify="right")
        table.add_column("Spend", justify="right")
        table.add_column("CPA", justify="right")

        for row in report_data:
            metadata = row.get("metadata", {})
            metrics = row.get("total", {})

            ad_name = metadata.get("adName", "Unknown")
            ad_status = metadata.get("adStatus", "?")

            impressions = metrics.get("impressions", 0)
            taps = metrics.get("taps", 0)
            installs = metrics.get("totalInstalls", 0) or metrics.get("tapInstalls", 0)
            spend_data = metrics.get("localSpend", {})
            spend = float(spend_data.get("amount", 0)) if spend_data else 0

            ttr = (taps / impressions * 100) if impressions > 0 else 0
            cvr = (installs / taps * 100) if taps > 0 else 0
            cpa = (spend / installs) if installs > 0 else 0

            status_style = "green" if ad_status == "ENABLED" else "yellow" if ad_status == "PAUSED" else "dim"

            table.add_row(
                ad_name[:30],
                f"[{status_style}]{ad_status}[/{status_style}]",
                format_number(impressions),
                format_number(taps),
                f"{ttr:.1f}%",
                format_number(installs),
                f"{cvr:.1f}%",
                format_currency(spend),
                format_currency(cpa) if installs > 0 else "-",
            )

        if not json_output:
            console.print(table)
            console.print()

    if json_output:
        machine_rows.sort(
            key=lambda row: (
                row.get("campaign_name") or "",
                row.get("ad_group_name") or "",
                row.get("ad_name") or "",
                row.get("ad_id") or 0,
            )
        )
        _print_json(
            machine_report(
                "ads",
                window,
                machine_rows,
                totals=performance_totals(machine_rows),
                time_zone="UTC",
            )
        )


@app.command("bid-recommendations")
def report_bid_recommendations(
    campaign_id: Optional[int] = typer.Option(None, "--campaign", "-c", help="Campaign ID"),
    days: int = typer.Option(14, "--days", "-d", help="Number of days"),
    start_date: Optional[str] = typer.Option(
        None, "--start", "--start-date", help="Inclusive start date (YYYY-MM-DD)"
    ),
    end_date: Optional[str] = typer.Option(
        None, "--end", "--end-date", help="Inclusive complete end date (YYYY-MM-DD)"
    ),
    all_campaigns: bool = typer.Option(False, "--all", "-a", help="Show bids for all campaigns"),
):
    """Show Apple's suggested bid amounts vs current bids for keywords.

    For each campaign and ad group, fetches the keyword report with bid
    recommendation insights. Displays a color-coded table showing where
    your bids are below Apple's suggestions.
    """
    credentials = load_credentials()
    if not credentials:
        console.print("[red]No credentials configured. Run 'asa config setup' first.[/red]")
        raise typer.Exit(1)

    client = SearchAdsClient(credentials)

    window = _resolve_window(days, start_date, end_date)
    start, end = window.as_datetimes()

    # Get campaigns to report on
    campaigns_to_report = []
    app_name = _resolve_app_name()

    def _filter_by_app(campaigns: list) -> list:
        if app_name:
            return [c for c in campaigns if parse_campaign_name(c.get("name", ""), app_name=app_name)]
        return campaigns

    if all_campaigns:
        campaigns = _filter_by_app(client.get_campaigns())
        campaigns_to_report = campaigns
    elif campaign_id:
        campaign = client.get_campaign(campaign_id)
        if campaign:
            campaigns_to_report = [campaign]
        else:
            console.print(f"[red]Campaign {campaign_id} not found.[/red]")
            raise typer.Exit(1)
    else:
        # Interactive selection
        campaigns = _filter_by_app(client.get_campaigns())
        if not campaigns:
            console.print("[yellow]No campaigns found.[/yellow]")
            return

        table = Table(show_header=True)
        table.add_column("#", style="cyan")
        table.add_column("Type")
        table.add_column("Name")

        for idx, c in enumerate(campaigns, 1):
            ctype = get_campaign_type_label(c.get("name", ""), app_name=app_name)
            table.add_row(str(idx), ctype, c.get("name", "")[:50])

        console.print(table)

        from rich.prompt import Prompt

        choice = Prompt.ask("Select campaign number (or 'all')")
        if choice.lower() == "all":
            campaigns_to_report = campaigns
        elif choice.isdigit() and 1 <= int(choice) <= len(campaigns):
            campaigns_to_report = [campaigns[int(choice) - 1]]
        else:
            console.print("[red]Invalid selection.[/red]")
            return

    console.print(
        Panel(
            f"[bold]Bid Recommendations[/bold]\n"
            f"{window.start.isoformat()} to {window.end.isoformat()}",
            expand=False,
        )
    )

    total_keywords = 0
    below_suggestion = 0

    for campaign in campaigns_to_report:
        cid = campaign.get("id")
        cname = campaign.get("name", "Unknown")
        ctype = get_campaign_type_label(cname, app_name=_resolve_app_name())

        # Get ad groups for this campaign
        with console.status(f"[bold blue]Fetching ad groups for {cname}..."):
            ad_groups = client.get_ad_groups(cid)

        if not ad_groups:
            console.print(f"[yellow]{ctype}: No ad groups found[/yellow]")
            continue

        for ag in ad_groups:
            ag_id = ag.get("id")
            ag_name = ag.get("name", "Unknown")

            with console.status(f"[bold blue]Fetching keyword report for {cname} / {ag_name}..."):
                report_data = client.get_keyword_adgroup_report(cid, ag_id, start, end)

            if not report_data:
                continue

            # Build keyword rows with bid recommendations
            rows = []
            for row in report_data:
                metadata = row.get("metadata", {})
                insights = row.get("insights", {})
                metrics = row.get("total", {})

                keyword = metadata.get("keyword", "?")
                keyword_id = metadata.get("keywordId")

                # Current bid from metadata
                bid_data = metadata.get("bidAmount", {})
                current_bid = float(bid_data.get("amount", 0)) if bid_data else 0

                # Suggested bid from insights
                bid_rec = insights.get("bidRecommendation", {})
                suggested_data = bid_rec.get("suggestedBidAmount", {})
                suggested_bid = float(suggested_data.get("amount", 0)) if suggested_data else 0

                impressions = metrics.get("impressions", 0)
                taps = metrics.get("taps", 0)
                installs = metrics.get("totalInstalls", 0) or metrics.get("tapInstalls", 0)

                rows.append({
                    "keyword": keyword,
                    "keyword_id": keyword_id,
                    "current_bid": current_bid,
                    "suggested_bid": suggested_bid,
                    "difference": suggested_bid - current_bid,
                    "impressions": impressions,
                    "taps": taps,
                    "installs": installs,
                })

            if not rows:
                continue

            # Sort by difference (biggest gap first)
            rows.sort(key=lambda x: -x["difference"])

            table = Table(
                title=f"{ctype} / {ag_name} - Bid Recommendations",
                show_header=True,
                header_style="bold magenta",
            )
            table.add_column("Keyword")
            table.add_column("Current Bid", justify="right")
            table.add_column("Suggested Bid", justify="right")
            table.add_column("Difference", justify="right")
            table.add_column("Impr", justify="right")
            table.add_column("Taps", justify="right")
            table.add_column("Inst", justify="right")

            for r in rows:
                total_keywords += 1
                diff = r["difference"]

                # Color code: green if current >= suggested, red if significantly below
                if diff <= 0:
                    bid_style = "green"
                elif diff < 0.50:
                    bid_style = "yellow"
                    below_suggestion += 1
                else:
                    bid_style = "red"
                    below_suggestion += 1

                diff_str = f"[{bid_style}]{'+' if diff <= 0 else ''}{format_currency(abs(diff))}[/{bid_style}]"
                if diff > 0:
                    diff_str = f"[{bid_style}]-{format_currency(diff)}[/{bid_style}]"

                current_str = format_currency(r["current_bid"]) if r["current_bid"] > 0 else "-"
                suggested_str = format_currency(r["suggested_bid"]) if r["suggested_bid"] > 0 else "-"

                table.add_row(
                    r["keyword"][:30],
                    current_str,
                    suggested_str,
                    diff_str,
                    format_number(r["impressions"]),
                    format_number(r["taps"]),
                    format_number(r["installs"]),
                )

            console.print(table)
            console.print()

    # Summary
    if total_keywords > 0:
        console.print(
            Panel(
                f"[bold]Summary[/bold]\n"
                f"Total keywords: {total_keywords}\n"
                f"Below suggestion: [{'red' if below_suggestion > 0 else 'green'}]"
                f"{below_suggestion}[/{'red' if below_suggestion > 0 else 'green'}]\n"
                f"At or above: [green]{total_keywords - below_suggestion}[/green]",
                expand=False,
            )
        )
    else:
        console.print("[yellow]No keyword bid data found.[/yellow]")
