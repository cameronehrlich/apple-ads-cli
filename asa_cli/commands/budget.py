"""Budget management commands."""

from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from ..config import detect_campaign_type, get_current_app_config, is_multi_app, load_credentials
from ..v5.api import SearchAdsClient

app = typer.Typer(help="Budget management commands")
console = Console()


def _resolve_app_name() -> Optional[str]:
    """Get the app_name for campaign scoping (None if single-app)."""
    if not is_multi_app():
        return None
    app_config = get_current_app_config()
    return app_config.app_name if app_config else None


@app.command("list")
def list_budget_orders():
    """List all budget orders."""
    credentials = load_credentials()
    if not credentials:
        console.print("[red]No credentials configured. Run 'asa config setup' first.[/red]")
        raise typer.Exit(1)

    client = SearchAdsClient(credentials)

    with console.status("[bold blue]Fetching budget orders..."):
        budget_orders = client.get_budget_orders()

    if not budget_orders:
        console.print("[yellow]No budget orders found.[/yellow]")
        return

    table = Table(title="Budget Orders", show_header=True, header_style="bold magenta")
    table.add_column("ID", style="cyan")
    table.add_column("Name")
    table.add_column("Order Number")
    table.add_column("Budget")
    table.add_column("Start Date")
    table.add_column("End Date")
    table.add_column("Status")

    for bo in budget_orders:
        budget = bo.get("budget", {})
        amount = budget.get("amount", "?")
        currency = budget.get("currency", "USD")
        status = bo.get("status", "UNKNOWN")

        status_style = "green" if status == "ACTIVE" else "yellow" if status == "PAUSED" else "red"

        table.add_row(
            str(bo.get("id", "")),
            bo.get("name", ""),
            str(bo.get("orderNumber", "")),
            f"${amount} {currency}",
            bo.get("startDate", ""),
            bo.get("endDate", ""),
            f"[{status_style}]{status}[/{status_style}]",
        )

    console.print(table)
    console.print(f"\n[dim]Total: {len(budget_orders)} budget orders[/dim]")


@app.command("get")
def get_budget_order(
    budget_order_id: int = typer.Argument(..., help="Budget order ID"),
):
    """Show details of a specific budget order."""
    credentials = load_credentials()
    if not credentials:
        console.print("[red]No credentials configured. Run 'asa config setup' first.[/red]")
        raise typer.Exit(1)

    client = SearchAdsClient(credentials)

    with console.status("[bold blue]Fetching budget order..."):
        bo = client.get_budget_order(budget_order_id)

    if not bo:
        console.print(f"[red]Budget order {budget_order_id} not found.[/red]")
        raise typer.Exit(1)

    budget = bo.get("budget", {})
    amount = budget.get("amount", "?")
    currency = budget.get("currency", "USD")

    console.print(Panel(f"[bold]Budget Order: {bo.get('name', '')}[/bold]", expand=False))
    console.print(f"  ID:           [cyan]{bo.get('id', '')}[/cyan]")
    console.print(f"  Order Number: [cyan]{bo.get('orderNumber', '')}[/cyan]")
    console.print(f"  Budget:       [cyan]${amount} {currency}[/cyan]")
    console.print(f"  Start Date:   [cyan]{bo.get('startDate', '')}[/cyan]")
    console.print(f"  End Date:     [cyan]{bo.get('endDate', '')}[/cyan]")
    console.print(f"  Status:       [cyan]{bo.get('status', '')}[/cyan]")


@app.command("status")
def budget_status():
    """Campaign budget health dashboard."""
    credentials = load_credentials()
    if not credentials:
        console.print("[red]No credentials configured. Run 'asa config setup' first.[/red]")
        raise typer.Exit(1)

    client = SearchAdsClient(credentials)
    app_name = _resolve_app_name()

    with console.status("[bold blue]Fetching campaign budget status..."):
        statuses = client.get_campaign_budget_status()

    if not statuses:
        console.print("[yellow]No campaigns found.[/yellow]")
        return

    # Filter to current app if multi-app
    if app_name:
        statuses = [
            s for s in statuses
            if detect_campaign_type(s.get("name", ""), app_name=app_name) is not None
        ]

    table = Table(
        title="Campaign Budget Health",
        show_header=True,
        header_style="bold magenta",
    )
    table.add_column("Campaign", max_width=35)
    table.add_column("Type", style="green")
    table.add_column("Daily Budget", justify="right")
    table.add_column("Lifetime Budget", justify="right")
    table.add_column("Total Spend", justify="right")
    table.add_column("Status")
    table.add_column("Display Status")

    for entry in statuses:
        name = entry.get("name", "")
        ctype = detect_campaign_type(name, app_name=app_name)
        ctype_str = ctype.value.upper() if ctype else "-"

        daily = entry.get("dailyBudgetAmount") or {}
        daily_amount = daily.get("amount", "-")
        daily_currency = daily.get("currency", "")
        daily_str = f"${daily_amount} {daily_currency}".strip() if daily_amount != "-" else "[dim]-[/dim]"

        lifetime = entry.get("budgetAmount") or {}
        lifetime_amount = lifetime.get("amount", "-")
        lifetime_currency = lifetime.get("currency", "")
        lifetime_str = f"${lifetime_amount} {lifetime_currency}".strip() if lifetime_amount != "-" else "[dim]-[/dim]"

        total_spend = entry.get("totalSpend", 0.0)
        spend_str = f"${total_spend:,.2f}"

        status = entry.get("status", "UNKNOWN")
        display_status = entry.get("displayStatus", "UNKNOWN")

        # Color-code status
        if status == "ENABLED":
            status_style = "green"
        elif status == "PAUSED":
            status_style = "yellow"
        else:
            status_style = "red"

        # Color-code display status for budget issues
        display_lower = display_status.lower()
        if "exhaust" in display_lower or "budget" in display_lower and "limit" in display_lower:
            display_style = "red"
        elif "pause" in display_lower or "limit" in display_lower:
            display_style = "yellow"
        elif display_status == "RUNNING":
            display_style = "green"
        else:
            display_style = "white"

        display_name = name[:35] + "..." if len(name) > 35 else name

        table.add_row(
            display_name,
            ctype_str,
            daily_str,
            lifetime_str,
            spend_str,
            f"[{status_style}]{status}[/{status_style}]",
            f"[{display_style}]{display_status}[/{display_style}]",
        )

    console.print(table)
    console.print(f"\n[dim]Total: {len(statuses)} campaigns[/dim]")


@app.command("create")
def create_budget_order(
    name: str = typer.Option(..., "--name", "-n", help="Budget order name"),
    budget: float = typer.Option(..., "--budget", "-b", help="Budget amount (organization currency)"),
    start_date: str = typer.Option(..., "--start", "-s", help="Start date (YYYY-MM-DD)"),
    end_date: str = typer.Option(..., "--end", "-e", help="End date (YYYY-MM-DD)"),
    client_name: Optional[str] = typer.Option(None, "--client-name", help="Client name"),
    primary_buyer_email: Optional[str] = typer.Option(None, "--email", help="Primary buyer email"),
):
    """Create a new budget order."""
    credentials = load_credentials()
    if not credentials:
        console.print("[red]No credentials configured. Run 'asa config setup' first.[/red]")
        raise typer.Exit(1)

    client = SearchAdsClient(credentials)
    currency = client.get_org_currency()

    kwargs = {}
    if client_name:
        kwargs["clientName"] = client_name
    if primary_buyer_email:
        kwargs["primaryBuyerEmail"] = primary_buyer_email

    console.print(f"\nCreating budget order: [cyan]{name}[/cyan]")
    console.print(f"  Budget:     [cyan]{budget:,.2f} {currency}[/cyan]")
    console.print(f"  Start Date: [cyan]{start_date}[/cyan]")
    console.print(f"  End Date:   [cyan]{end_date}[/cyan]")

    with console.status("[bold blue]Creating budget order..."):
        bo = client.create_budget_order(
            name=name,
            budget=budget,
            start_date=start_date,
            end_date=end_date,
            **kwargs,
        )

    if bo:
        console.print("\n[green]Budget order created successfully![/green]")
        console.print(f"  ID: [cyan]{bo.get('id')}[/cyan]")
        console.print(f"  Name: [cyan]{bo.get('name')}[/cyan]")
    else:
        console.print("[red]Failed to create budget order.[/red]")
        raise typer.Exit(1)
