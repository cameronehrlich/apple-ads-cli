"""Automated campaign optimization commands."""

import json
from datetime import datetime, timedelta
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm
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

app = typer.Typer(help="Automated campaign optimization")
console = Console()


def format_currency(amount: float) -> str:
    """Format currency for display."""
    return f"${amount:,.2f}"


def _resolve_app_name() -> Optional[str]:
    """Get the app_name for campaign scoping (None if single-app)."""
    if not is_multi_app():
        return None
    app_config = get_current_app_config()
    return app_config.app_name if app_config else None


def get_campaigns_indexed(
    client: SearchAdsClient,
    app_name: Optional[str] = None,
) -> tuple[dict[CampaignType, dict], list[tuple[dict, CampaignType]]]:
    """Get all campaigns, indexed by type and as a list.

    Returns (campaigns_by_type, managed_list) where:
    - campaigns_by_type: dict mapping CampaignType to campaign dict
    - managed_list: list of (campaign, type) tuples for all managed campaigns

    This fetches campaigns once and organizes them for different use cases.
    """
    campaigns = client.get_campaigns()
    by_type: dict[CampaignType, dict] = {}
    managed: list[tuple[dict, CampaignType]] = []

    for c in campaigns:
        ctype = detect_campaign_type(c.get("name", ""), app_name=app_name)
        if not ctype:
            continue
        if ctype in by_type:
            first_name = by_type[ctype].get("name", "?")
            second_name = c.get("name", "?")
            raise ValueError(
                f"Multiple {ctype.value} campaigns matched: {first_name}, {second_name}"
            )
        by_type[ctype] = c
        managed.append((c, ctype))

    return by_type, managed


class AnalysisResult:
    """Results from search term analysis."""

    def __init__(self):
        self.winners: list[dict] = []
        self.losers: list[dict] = []
        self.total_terms: int = 0
        self.skipped_no_text: int = 0
        self.skipped_no_activity: int = 0


def analyze_search_terms(
    client: SearchAdsClient,
    campaign_id: int,
    days: int,
    cpa_threshold: float,
    min_installs: int,
    min_spend: float,
    min_impressions: int = 0,
    exclude_terms: Optional[list[str]] = None,
) -> AnalysisResult:
    """Analyze search terms and categorize into winners and losers.

    Returns AnalysisResult with:
    - winners: terms with installs >= min_installs AND CPA <= cpa_threshold
    - losers: terms with spend >= min_spend AND installs == 0
    - stats about skipped terms

    Args:
        min_impressions: Minimum impressions required to consider a term (default 0)
        exclude_terms: List of terms to exclude from analysis (case-insensitive)
    """
    end = datetime.now()
    start = end - timedelta(days=days)

    report_data = client.get_search_terms_report(campaign_id, start, end)

    result = AnalysisResult()
    result.total_terms = len(report_data)

    # Normalize exclude terms for case-insensitive matching
    exclude_set = {t.lower() for t in (exclude_terms or [])}

    for row in report_data:
        metadata = row.get("metadata", {})
        metrics = row.get("total", {})

        impressions = metrics.get("impressions", 0)
        taps = metrics.get("taps", 0)
        installs = metrics.get("totalInstalls", 0) or metrics.get("tapInstalls", 0)
        spend_data = metrics.get("localSpend")
        spend = float(spend_data.get("amount", 0)) if isinstance(spend_data, dict) else 0.0

        term_text = metadata.get("searchTermText") or metadata.get("keyword") or ""
        if not term_text:
            result.skipped_no_text += 1
            continue

        # Skip excluded terms
        if term_text.lower() in exclude_set:
            continue

        if impressions == 0 and taps == 0 and spend == 0:
            result.skipped_no_activity += 1
            continue

        # Skip terms below minimum impressions threshold
        if impressions < min_impressions:
            continue

        term_data = {
            "term": term_text,
            "source": metadata.get("searchTermSource", "?"),
            "impressions": impressions,
            "taps": taps,
            "installs": installs,
            "spend": spend,
            "cpa": (spend / installs) if installs > 0 else float("inf"),
        }

        if installs >= min_installs and term_data["cpa"] <= cpa_threshold:
            result.winners.append(term_data)
        elif installs == 0 and spend >= min_spend:
            result.losers.append(term_data)

    result.winners.sort(key=lambda x: x["cpa"])
    result.losers.sort(key=lambda x: -x["spend"])

    return result


def display_optimization_summary(
    winners: list[dict],
    losers: list[dict],
    discovery_campaign: dict,
    target_campaign: dict,
    days: int,
) -> None:
    """Display the optimization summary with rich tables."""
    console.print(
        Panel(
            f"[bold]ASA Optimization Report[/bold]\nLast {days} days",
            expand=False,
            border_style="cyan",
        )
    )

    console.print(f"\nDiscovery Campaign: [cyan]{discovery_campaign.get('name')}[/cyan]")
    console.print(f"Target Campaign: [cyan]{target_campaign.get('name')}[/cyan]")

    console.print(f"\n[bold green]📈 WINNERS TO PROMOTE ({len(winners)} terms)[/bold green]")
    if winners:
        table = Table(show_header=True, header_style="bold")
        table.add_column("Search Term")
        table.add_column("Installs", justify="right")
        table.add_column("Spend", justify="right")
        table.add_column("CPA", justify="right")

        for w in winners[:20]:
            table.add_row(
                w["term"][:35],
                str(w["installs"]),
                format_currency(w["spend"]),
                format_currency(w["cpa"]),
            )

        if len(winners) > 20:
            table.add_row(f"... and {len(winners) - 20} more", "", "", "")

        console.print(table)
    else:
        console.print("[dim]No terms meet the winner criteria.[/dim]")

    console.print(f"\n[bold red]🚫 TERMS TO BLOCK ({len(losers)} terms)[/bold red]")
    if losers:
        table = Table(show_header=True, header_style="bold")
        table.add_column("Search Term")
        table.add_column("Installs", justify="right")
        table.add_column("Spend", justify="right")
        table.add_column("Impressions", justify="right")

        for loser in losers[:20]:
            table.add_row(
                loser["term"][:35],
                str(loser["installs"]),
                format_currency(loser["spend"]),
                str(loser["impressions"]),
            )

        if len(losers) > 20:
            table.add_row(f"... and {len(losers) - 20} more", "", "", "")

        console.print(table)
    else:
        console.print("[dim]No terms meet the negative criteria.[/dim]")


def execute_promotions(
    client: SearchAdsClient,
    winners: list[dict],
    target_campaign: dict,
    discovery_campaign: dict,
) -> tuple[int, int]:
    """Promote winning keywords to target campaign.

    Returns (success_count, failure_count).
    """
    if not winners:
        return 0, 0

    target_id = target_campaign.get("id")
    discovery_id = discovery_campaign.get("id")

    ad_groups = client.get_ad_groups(target_id)
    exact_ad_group = next(
        (ag for ag in ad_groups if "Exact" in ag.get("name", "")),
        ad_groups[0] if ad_groups else None,
    )

    if not exact_ad_group:
        console.print("[red]No ad group found in target campaign.[/red]")
        return 0, len(winners)

    keyword_list = [w["term"] for w in winners]

    with console.status("[bold blue]Adding keywords to target campaign..."):
        added, errors = client.add_keywords(
            campaign_id=target_id,
            ad_group_id=exact_ad_group.get("id"),
            keywords=keyword_list,
            match_type=MatchType.EXACT,
        )

    added_terms = {
        str(item.get("text", "")).strip().lower()
        for item in added
        if item.get("text")
    }
    all_duplicates = bool(errors) and all(
        error.get("messageCode") == "DUPLICATE_KEYWORD" for error in errors
    )

    if added:
        console.print(f"[green]✓ Added {len(added)} keywords to {target_campaign.get('name')}[/green]")
    elif all_duplicates:
        console.print(
            f"[dim]↳ {len(errors)} keywords already exist in "
            f"{target_campaign.get('name')}[/dim]"
        )
    else:
        message = errors[0].get("message", "Unknown error") if errors else "Unknown error"
        console.print(f"[red]✗ Failed: {message}[/red]")
        return 0, len(winners)

    safe_terms = (
        keyword_list
        if all_duplicates
        else [term for term in keyword_list if term.strip().lower() in added_terms]
    )
    if not safe_terms:
        console.print("[yellow]No confirmed promotions to negate in Discovery.[/yellow]")
        return 0, len(winners)

    with console.status("[bold blue]Adding negatives to Discovery..."):
        neg_added, neg_errors = client.add_negative_keywords(discovery_id, safe_terms)

    if neg_added and len(neg_added) > 0:
        console.print(f"[green]✓ Added {len(neg_added)} negatives to Discovery[/green]")
    elif neg_errors:
        # Check if all errors are duplicates (which is fine)
        negatives_are_duplicates = all(
            error.get("messageCode") == "DUPLICATE_KEYWORD" for error in neg_errors
        )
        if negatives_are_duplicates:
            console.print(f"[dim]↳ {len(neg_errors)} negatives already exist in Discovery[/dim]")
        else:
            console.print(f"[yellow]⚠ Could not add negatives to Discovery: {neg_errors[0].get('message', 'Unknown error')}[/yellow]")
    else:
        console.print("[yellow]⚠ Could not add negatives to Discovery[/yellow]")

    promoted_count = len(safe_terms)
    return promoted_count, len(winners) - promoted_count


def execute_negatives(
    client: SearchAdsClient,
    losers: list[dict],
    managed_campaigns: list[tuple[dict, CampaignType]],
) -> tuple[int, int]:
    """Block losing keywords across all managed campaigns.

    Returns (campaigns_succeeded, campaigns_failed).
    """
    if not losers:
        return 0, 0

    keyword_list = [loser["term"] for loser in losers]
    success_count = 0
    failure_count = 0

    for campaign, _campaign_type in managed_campaigns:
        cid = campaign.get("id")
        cname = campaign.get("name")

        with console.status(f"[bold blue]Adding negatives to {cname}..."):
            added, errors = client.add_negative_keywords(cid, keyword_list)

        if added and len(added) > 0:
            console.print(f"[green]✓ Added {len(added)} negatives to {cname}[/green]")
            success_count += 1
        elif errors:
            all_duplicates = all(e.get("messageCode") == "DUPLICATE_KEYWORD" for e in errors)
            if all_duplicates:
                console.print(f"[dim]↳ {len(errors)} negatives already exist in {cname}[/dim]")
                success_count += 1  # Count as success since keywords are blocked
            else:
                console.print(f"[red]✗ Failed to add negatives to {cname}: {errors[0].get('message', 'Unknown')}[/red]")
                failure_count += 1
        else:
            console.print(f"[red]✗ Failed to add negatives to {cname}[/red]")
            failure_count += 1

    return success_count, failure_count


@app.callback(invoke_without_command=True)
def optimize_cmd(
    ctx: typer.Context,
    days: int = typer.Option(14, "--days", "-d", help="Days to analyze"),
    cpa_threshold: float = typer.Option(
        5.00, "--cpa-threshold", "-c", help="Max CPA for winners (USD)"
    ),
    min_installs: int = typer.Option(
        2, "--min-installs", "-i", help="Min installs to promote"
    ),
    min_spend: float = typer.Option(
        1.00, "--min-spend", "-s", help="Min spend to consider blocking (USD)"
    ),
    min_impressions: int = typer.Option(
        0, "--min-impressions", help="Min impressions to consider a term"
    ),
    exclude_terms: Optional[str] = typer.Option(
        None, "--exclude", "-e", help="Comma-separated terms to exclude from analysis"
    ),
    dry_run: bool = typer.Option(
        False, "--dry-run", "-n", help="Preview changes without applying"
    ),
    auto_approve: bool = typer.Option(
        False, "--auto-approve", "-y", help="Skip confirmation prompts"
    ),
    target: str = typer.Option(
        "category",
        "--target",
        "-t",
        help="Target campaign for promotions: brand, category, competitor",
    ),
    negative_scope: str = typer.Option(
        "discovery",
        "--negative-scope",
        help="Where to add loser negatives: discovery or managed",
    ),
    output_json: bool = typer.Option(
        False, "--json", help="Output results as JSON (implies --dry-run)"
    ),
):
    """Run automated optimization on Discovery campaign.

    This command performs the weekly ASA optimization workflow:

    1. Pull search terms from Discovery campaign
    2. Identify winners (good CPA, installs) to promote
    3. Identify losers (spend, no installs) to block
    4. Execute changes (with dry-run support)

    \b
    Examples:
        asa v5 optimize --dry-run           # Preview changes
        asa v5 optimize --days 7            # Analyze last 7 days
        asa v5 optimize --cpa-threshold 3   # Stricter winner criteria
        asa v5 optimize --auto-approve      # Skip confirmation
        asa v5 optimize --json              # Output as JSON
        asa v5 optimize --min-impressions 10  # Only terms with 10+ impressions
        asa v5 optimize --exclude "test,demo" # Exclude specific terms
    """
    if ctx.invoked_subcommand is not None:
        return

    # JSON output implies dry-run
    if output_json:
        dry_run = True

    # Parse exclude terms
    exclude_list = [t.strip() for t in (exclude_terms or "").split(",") if t.strip()]

    credentials = load_credentials()
    if not credentials:
        if output_json:
            print(json.dumps({"error": "No credentials configured"}))
        else:
            console.print("[red]No credentials configured. Run 'asa config setup' first.[/red]")
        raise typer.Exit(1)

    target_type_map = {
        "brand": CampaignType.BRAND,
        "category": CampaignType.CATEGORY,
        "competitor": CampaignType.COMPETITOR,
    }

    if target.lower() not in target_type_map:
        if output_json:
            print(json.dumps({"error": f"Invalid target type: {target}"}))
        else:
            console.print(f"[red]Invalid target type: {target}. Use brand, category, or competitor.[/red]")
        raise typer.Exit(1)

    target_type = target_type_map[target.lower()]

    negative_scope = negative_scope.lower()
    if negative_scope not in {"discovery", "managed"}:
        if output_json:
            print(json.dumps({"error": f"Invalid negative scope: {negative_scope}"}))
        else:
            console.print("[red]Invalid negative scope. Use discovery or managed.[/red]")
        raise typer.Exit(1)

    client = SearchAdsClient(credentials)
    app_name = _resolve_app_name()

    if not output_json:
        with console.status("[bold blue]Finding campaigns..."):
            try:
                campaigns_by_type, managed_campaigns = get_campaigns_indexed(
                    client, app_name=app_name
                )
            except ValueError as error:
                console.print(f"[red]{error}[/red]")
                raise typer.Exit(1) from error
            discovery_campaign = campaigns_by_type.get(CampaignType.DISCOVERY)
            target_campaign = campaigns_by_type.get(target_type)
    else:
        try:
            campaigns_by_type, managed_campaigns = get_campaigns_indexed(
                client, app_name=app_name
            )
        except ValueError as error:
            print(json.dumps({"error": str(error)}))
            raise typer.Exit(1) from error
        discovery_campaign = campaigns_by_type.get(CampaignType.DISCOVERY)
        target_campaign = campaigns_by_type.get(target_type)

    if not discovery_campaign:
        if output_json:
            print(json.dumps({"error": "No Discovery campaign found"}))
        else:
            console.print("[red]No Discovery campaign found.[/red]")
            console.print("[yellow]Tip: Create a campaign with 'Discovery' in the name.[/yellow]")
        raise typer.Exit(1)

    if not target_campaign:
        if output_json:
            print(json.dumps({"error": f"No {target_type.value} campaign found"}))
        else:
            console.print(f"[red]No {target_type.value} campaign found.[/red]")
            console.print(f"[yellow]Tip: Create a campaign with '{target_type.value}' in the name.[/yellow]")
        raise typer.Exit(1)

    if not output_json:
        settings_text = (
            f"[bold]Optimization Settings[/bold]\n"
            f"Days: {days} | CPA Threshold: {format_currency(cpa_threshold)} | "
            f"Min Installs: {min_installs} | Min Spend: {format_currency(min_spend)}"
        )
        if min_impressions > 0:
            settings_text += f" | Min Impressions: {min_impressions}"
        if exclude_list:
            settings_text += f"\nExcluding: {', '.join(exclude_list)}"
        console.print(Panel(settings_text, expand=False))

    if not output_json:
        with console.status("[bold blue]Analyzing search terms..."):
            analysis = analyze_search_terms(
                client,
                discovery_campaign.get("id"),
                days,
                cpa_threshold,
                min_installs,
                min_spend,
                min_impressions,
                exclude_list if exclude_list else None,
            )
    else:
        analysis = analyze_search_terms(
            client,
            discovery_campaign.get("id"),
            days,
            cpa_threshold,
            min_installs,
            min_spend,
            min_impressions,
            exclude_list if exclude_list else None,
        )

    winners = analysis.winners
    losers = analysis.losers

    # JSON output mode
    if output_json:
        output_data = {
            "settings": {
                "days": days,
                "cpa_threshold": cpa_threshold,
                "min_installs": min_installs,
                "min_spend": min_spend,
                "min_impressions": min_impressions,
                "exclude_terms": exclude_list,
                "target_campaign": target_type.value,
                "negative_scope": negative_scope,
            },
            "campaigns": {
                "discovery": {
                    "id": discovery_campaign.get("id"),
                    "name": discovery_campaign.get("name"),
                },
                "target": {
                    "id": target_campaign.get("id"),
                    "name": target_campaign.get("name"),
                },
            },
            "analysis": {
                "total_terms": analysis.total_terms,
                "skipped_no_text": analysis.skipped_no_text,
                "skipped_no_activity": analysis.skipped_no_activity,
            },
            "winners": [
                {
                    "term": w["term"],
                    "installs": w["installs"],
                    "spend": w["spend"],
                    "cpa": w["cpa"] if w["cpa"] != float("inf") else None,
                    "impressions": w["impressions"],
                    "taps": w["taps"],
                }
                for w in winners
            ],
            "losers": [
                {
                    "term": loser["term"],
                    "spend": loser["spend"],
                    "impressions": loser["impressions"],
                    "taps": loser["taps"],
                }
                for loser in losers
            ],
        }
        print(json.dumps(output_data, indent=2))
        return

    display_optimization_summary(
        winners, losers, discovery_campaign, target_campaign, days
    )

    analyzed_count = analysis.total_terms - analysis.skipped_no_text - analysis.skipped_no_activity
    console.print(f"\n[dim]Analysis: {analysis.total_terms} terms from API, "
                  f"{analyzed_count} analyzed, "
                  f"{analysis.skipped_no_text} skipped (no text), "
                  f"{analysis.skipped_no_activity} skipped (no activity)[/dim]")

    if not winners and not losers:
        console.print("\n[yellow]No optimization actions to take.[/yellow]")
        if analysis.skipped_no_text > 0:
            console.print("[dim]Note: Some Search Match terms don't expose their text in Apple's API.[/dim]")
        return

    if dry_run:
        console.print("\n[yellow][DRY RUN] No changes applied. Remove --dry-run to execute.[/yellow]")
        return

    if not auto_approve:
        console.print()
        if not Confirm.ask(
            f"[bold]Apply changes?[/bold] "
            f"({len(winners)} promotions, {len(losers)} negatives)"
        ):
            console.print("[yellow]Cancelled.[/yellow]")
            return

    console.print("\n[bold]Executing optimization...[/bold]\n")

    promoted = failed_promo = 0
    neg_success = neg_failed = 0

    if winners:
        promoted, failed_promo = execute_promotions(
            client, winners, target_campaign, discovery_campaign
        )

    if losers:
        negative_campaigns = (
            [(discovery_campaign, CampaignType.DISCOVERY)]
            if negative_scope == "discovery"
            else managed_campaigns
        )
        neg_success, neg_failed = execute_negatives(client, losers, negative_campaigns)

    console.print("\n[bold green]Optimization complete![/bold green]")

    summary_parts = []
    if promoted > 0:
        summary_parts.append(f"{promoted} keywords promoted to {target_type.value}")
    if neg_success > 0:
        summary_parts.append(f"{len(losers)} terms blocked across {neg_success} campaigns")

    if summary_parts:
        console.print(f"Summary: {' • '.join(summary_parts)}")

    if failed_promo > 0 or neg_failed > 0:
        console.print(f"[yellow]Failures: {failed_promo} promotions, {neg_failed} campaign blocks[/yellow]")
