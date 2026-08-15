"""ACL, user management, and app search commands."""

from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from ..config import get_current_app_config, load_credentials
from ..v5.api import SearchAdsClient

app = typer.Typer(help="ACL, user, and app search commands")
console = Console()


@app.command("list")
def list_acls():
    """Show organizations and roles for the current user."""
    credentials = load_credentials()
    if not credentials:
        console.print("[red]No credentials configured. Run 'asa config setup' first.[/red]")
        raise typer.Exit(1)

    client = SearchAdsClient(credentials)

    with console.status("[bold blue]Fetching ACLs..."):
        acls = client.get_acls()

    if not acls:
        console.print("[yellow]No organizations found.[/yellow]")
        return

    table = Table(title="Organizations & Roles", show_header=True, header_style="bold magenta")
    table.add_column("Org ID", style="cyan")
    table.add_column("Org Name")
    table.add_column("Role")
    table.add_column("Currency")
    table.add_column("Payment Model")

    for acl in acls:
        org_name = acl.get("orgName", "-")
        org_id = str(acl.get("orgId", "-"))
        role_names = ", ".join(acl.get("roleNames", []))
        currency = acl.get("currency", "-")
        payment_model = acl.get("paymentModel", "-")

        table.add_row(org_id, org_name, role_names, currency, payment_model)

    console.print(table)
    console.print(f"\n[dim]Total: {len(acls)} organizations[/dim]")


@app.command("me")
def show_me():
    """Show current user info."""
    credentials = load_credentials()
    if not credentials:
        console.print("[red]No credentials configured. Run 'asa config setup' first.[/red]")
        raise typer.Exit(1)

    client = SearchAdsClient(credentials)

    with console.status("[bold blue]Fetching user info..."):
        user_info = client.get_me()

    if not user_info:
        console.print("[yellow]No user info returned.[/yellow]")
        return

    table = Table(title="Current User", show_header=True, header_style="bold magenta")
    table.add_column("Field", style="cyan")
    table.add_column("Value")

    for key, value in user_info.items():
        table.add_row(str(key), str(value))

    console.print(table)


@app.command("search-apps")
def search_apps(
    query: str = typer.Argument(..., help="Search query for iOS apps"),
    owned_only: bool = typer.Option(True, "--owned/--all", help="Show only owned apps or all"),
    limit: int = typer.Option(20, "--limit", "-l", help="Maximum results"),
):
    """Search for iOS apps on the App Store."""
    credentials = load_credentials()
    if not credentials:
        console.print("[red]No credentials configured. Run 'asa config setup' first.[/red]")
        raise typer.Exit(1)

    client = SearchAdsClient(credentials)

    with console.status(f"[bold blue]Searching apps for '{query}'..."):
        apps = client.search_apps(query, return_owned=owned_only, limit=limit)

    if not apps:
        console.print(f"[yellow]No apps found for '{query}'.[/yellow]")
        return

    table = Table(title=f"App Search: '{query}'", show_header=True, header_style="bold magenta")
    table.add_column("Adam ID", style="cyan")
    table.add_column("Name")
    table.add_column("Developer")
    table.add_column("Country")

    for app_record in apps:
        adam_id = str(app_record.get("adamId", "-"))
        name = app_record.get("appName", "-")
        developer = app_record.get("developerName", "-")
        country = app_record.get("countryOrRegionCodes", ["-"])
        country_str = ", ".join(country) if isinstance(country, list) else str(country)

        table.add_row(adam_id, name[:40], developer[:30], country_str[:20])

    console.print(table)
    console.print(f"\n[dim]Total: {len(apps)} results[/dim]")


@app.command("eligibility")
def check_eligibility(
    adam_id: Optional[int] = typer.Option(
        None, "--app-id", "-a", help="Apple App ID (defaults to active app)"
    ),
):
    """Check app advertising eligibility."""
    credentials = load_credentials()
    app_config = get_current_app_config()

    if not credentials:
        console.print("[red]No credentials configured. Run 'asa config setup' first.[/red]")
        raise typer.Exit(1)

    resolved_id = adam_id or (app_config.app_id if app_config else None)
    if not resolved_id:
        console.print("[red]No app ID provided and no active app configured.[/red]")
        raise typer.Exit(1)

    client = SearchAdsClient(credentials)

    with console.status(f"[bold blue]Checking eligibility for app {resolved_id}..."):
        eligibility = client.get_app_eligibility(resolved_id)

    if not eligibility:
        console.print(f"[yellow]No eligibility data returned for app {resolved_id}.[/yellow]")
        return

    table = Table(
        title=f"Eligibility: App {resolved_id}", show_header=True, header_style="bold magenta"
    )
    table.add_column("Condition", style="cyan")
    table.add_column("Status")

    if isinstance(eligibility, list):
        for item in eligibility:
            condition = item.get("condition", "-")
            status = item.get("status", "-")
            status_style = "green" if status == "ELIGIBLE" else "red"
            table.add_row(condition, f"[{status_style}]{status}[/{status_style}]")
    elif isinstance(eligibility, dict):
        for key, value in eligibility.items():
            table.add_row(str(key), str(value))

    console.print(table)


@app.command("countries")
def list_countries(
    filter_codes: Optional[str] = typer.Option(
        None, "--filter", "-f", help="Comma-separated country codes to filter"
    ),
):
    """Show supported countries/regions for advertising."""
    credentials = load_credentials()
    if not credentials:
        console.print("[red]No credentials configured. Run 'asa config setup' first.[/red]")
        raise typer.Exit(1)

    client = SearchAdsClient(credentials)

    countries_filter = None
    if filter_codes:
        countries_filter = [c.strip().upper() for c in filter_codes.split(",")]

    with console.status("[bold blue]Fetching supported countries..."):
        countries = client.get_supported_countries(countries=countries_filter)

    if not countries:
        console.print("[yellow]No supported countries found.[/yellow]")
        return

    table = Table(
        title="Supported Countries/Regions", show_header=True, header_style="bold magenta"
    )
    table.add_column("Code", style="cyan")
    table.add_column("Name")

    for country in countries:
        code = country.get("countryOrRegion", "-")
        name = country.get("displayName", "-")
        table.add_row(code, name)

    console.print(table)
    console.print(f"\n[dim]Total: {len(countries)} countries/regions[/dim]")
