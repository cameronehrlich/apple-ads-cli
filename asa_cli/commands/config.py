"""Configuration commands."""

import typer
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm
from rich.table import Table

from ..config import (
    CONFIG_FILE,
    CREDENTIALS_FILE,
    get_app_slug,
    load_app_config,
    load_credentials,
    load_multi_app_config,
    prompt_for_app_config,
    prompt_for_credentials,
    save_app_config,
    save_credentials,
    save_multi_app_config,
)

app = typer.Typer(help="Configuration management commands")
console = Console()


@app.command("setup")
def setup_config(
    credentials_only: bool = typer.Option(False, "--credentials", "-c", help="Only configure credentials"),
    app_only: bool = typer.Option(False, "--app", "-a", help="Only configure app settings"),
):
    """Set up API credentials and app configuration."""
    if not app_only:
        console.print(Panel("[bold]Step 1: API Credentials[/bold]", expand=False))

        existing_creds = load_credentials()
        if existing_creds:
            console.print("[yellow]Existing credentials found.[/yellow]")
            console.print(f"  Org ID: {existing_creds.org_id}")
            console.print(f"  Client ID: {existing_creds.client_id[:20]}...")

            if not Confirm.ask("Overwrite existing credentials?"):
                if credentials_only:
                    return
            else:
                credentials = prompt_for_credentials()
                save_credentials(credentials)
        else:
            credentials = prompt_for_credentials()
            save_credentials(credentials)

    if credentials_only:
        console.print("\n[green]Credentials configured![/green]")
        return

    if not credentials_only:
        console.print(Panel("\n[bold]Step 2: App Configuration[/bold]", expand=False))

        existing_config = load_app_config()
        if existing_config:
            console.print("[yellow]Existing app config found.[/yellow]")
            console.print(f"  App Name: {existing_config.app_name}")
            console.print(f"  App ID: {existing_config.app_id}")
            console.print(f"  Countries: {', '.join(existing_config.default_countries)}")

            if not Confirm.ask("Overwrite existing config?"):
                if app_only:
                    return
            else:
                config = prompt_for_app_config()
                save_app_config(config)
        else:
            config = prompt_for_app_config()
            save_app_config(config)

    console.print("\n[bold green]Configuration complete![/bold green]")
    console.print("\nNext steps:")
    console.print("  1. Run [cyan]asa campaigns audit[/cyan] to check existing campaigns")
    console.print("  2. Run [cyan]asa campaigns setup[/cyan] to create the 4-campaign structure")


@app.command("show")
def show_config():
    """Display current configuration."""
    credentials = load_credentials()
    app_config = load_app_config()
    multi = load_multi_app_config()

    console.print(Panel("[bold]Current Configuration[/bold]", expand=False))

    # Credentials
    console.print("\n[bold]API Credentials:[/bold]")
    if credentials:
        table = Table(show_header=False, box=None)
        table.add_column("Key", style="cyan")
        table.add_column("Value")

        table.add_row("Org ID", str(credentials.org_id))
        table.add_row("Client ID", credentials.client_id[:30] + "...")
        table.add_row("Team ID", credentials.team_id)
        table.add_row("Key ID", credentials.key_id)
        table.add_row("Private Key", credentials.private_key_path)
        table.add_row("Config File", str(CREDENTIALS_FILE))

        console.print(table)
    else:
        console.print("[yellow]  Not configured. Run 'asa config setup'.[/yellow]")

    # App config
    console.print("\n[bold]App Configuration:[/bold]")
    if app_config:
        table = Table(show_header=False, box=None)
        table.add_column("Key", style="cyan")
        table.add_column("Value")

        table.add_row("App Name", app_config.app_name)
        table.add_row("App ID", str(app_config.app_id))
        table.add_row("Countries", ", ".join(app_config.default_countries))
        table.add_row("Default Bid", f"${app_config.default_bid}")
        table.add_row("CPA Goal", f"${app_config.default_cpa_goal}" if app_config.default_cpa_goal else "Not set")
        table.add_row("Config File", str(CONFIG_FILE))

        console.print(table)

        if len(multi.apps) > 1:
            console.print(f"\n[dim]Showing active app. Run 'asa config list-apps' to see all {len(multi.apps)} apps.[/dim]")
    else:
        console.print("[yellow]  Not configured. Run 'asa config setup'.[/yellow]")


@app.command("test")
def test_connection():
    """Test API access; exits nonzero on authentication or transport failure."""
    credentials = load_credentials()
    if not credentials:
        console.print("[red]No credentials configured. Run 'asa config setup' first.[/red]")
        raise typer.Exit(1)

    console.print("[bold]Testing API connection...[/bold]\n")

    try:
        from ..api import SearchAdsClient

        client = SearchAdsClient(credentials)

        with console.status("[bold blue]Connecting to Apple Search Ads API..."):
            campaigns = client.get_campaigns()

        console.print("[green]Connection successful![/green]")
        console.print(f"  Organization ID: {credentials.org_id}")
        console.print(f"  Total campaigns: {len(campaigns)}")

    except ImportError as e:
        console.print(f"[red]Missing dependency: {e}[/red]")
        console.print("  Run: pip install -e . (from the apple-search-ads directory)")
        raise typer.Exit(1) from e
    except Exception as e:
        console.print(f"[red]Connection failed: {e}[/red]")
        console.print("\nTroubleshooting:")
        console.print("  1. Verify your credentials in Apple Ads dashboard")
        console.print("  2. Ensure private key file exists and is readable")
        console.print("  3. Check that your API user has appropriate permissions")
        raise typer.Exit(1) from e


@app.command("add-app")
def add_app():
    """Add a new app to the multi-app configuration."""
    config = prompt_for_app_config()
    slug = get_app_slug(config.app_name)

    multi = load_multi_app_config()

    if slug in multi.apps:
        if not Confirm.ask(f"App '{slug}' already exists. Overwrite?"):
            console.print("[yellow]Cancelled.[/yellow]")
            return

    multi.apps[slug] = config
    if multi.active_app is None or len(multi.apps) == 1:
        multi.active_app = slug

    save_multi_app_config(multi)
    console.print(f"\n[green]Added app '{config.app_name}' (slug: {slug})[/green]")

    if multi.active_app == slug:
        console.print(f"[cyan]Active app set to: {slug}[/cyan]")
    else:
        console.print(f"[dim]Active app is: {multi.active_app}. Switch with 'asa config switch {slug}'.[/dim]")


@app.command("list-apps")
def list_apps():
    """List all configured apps."""
    multi = load_multi_app_config()

    if not multi.apps:
        console.print("[yellow]No apps configured. Run 'asa config setup' or 'asa config add-app'.[/yellow]")
        return

    table = Table(title="Configured Apps", show_header=True, header_style="bold magenta")
    table.add_column("Slug", style="cyan")
    table.add_column("App Name")
    table.add_column("App ID")
    table.add_column("Countries")
    table.add_column("Default Bid")
    table.add_column("Active")

    for slug, app_config in multi.apps.items():
        is_active = slug == multi.active_app
        active_marker = "[green]<--[/green]" if is_active else ""

        table.add_row(
            slug,
            app_config.app_name,
            str(app_config.app_id),
            ", ".join(app_config.default_countries),
            f"${app_config.default_bid}",
            active_marker,
        )

    console.print(table)
    console.print(f"\n[dim]Active app: {multi.active_app}[/dim]")
    console.print("[dim]Use 'asa config switch <slug>' to change active app.[/dim]")
    console.print("[dim]Use 'asa --app <slug> <command>' to run a command for a specific app.[/dim]")


@app.command("switch")
def switch_app(
    slug: str = typer.Argument(..., help="App slug to switch to"),
):
    """Switch the active app."""
    multi = load_multi_app_config()

    if slug not in multi.apps:
        console.print(f"[red]App '{slug}' not found.[/red]")
        if multi.apps:
            console.print(f"[yellow]Available apps: {', '.join(multi.apps.keys())}[/yellow]")
        raise typer.Exit(1)

    multi.active_app = slug
    save_multi_app_config(multi)
    app_config = multi.apps[slug]
    console.print(f"[green]Switched active app to: {app_config.app_name} ({slug})[/green]")


@app.command("remove-app")
def remove_app(
    slug: str = typer.Argument(..., help="App slug to remove"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation"),
):
    """Remove an app from the configuration."""
    multi = load_multi_app_config()

    if slug not in multi.apps:
        console.print(f"[red]App '{slug}' not found.[/red]")
        if multi.apps:
            console.print(f"[yellow]Available apps: {', '.join(multi.apps.keys())}[/yellow]")
        raise typer.Exit(1)

    app_config = multi.apps[slug]
    console.print(f"Removing app: {app_config.app_name} ({slug})")
    console.print(f"  App ID: {app_config.app_id}")

    if not force and not Confirm.ask("[red]This will remove all app settings. Continue?[/red]"):
        console.print("[yellow]Cancelled.[/yellow]")
        return

    del multi.apps[slug]

    # Update active_app if we removed the active one
    if multi.active_app == slug:
        if multi.apps:
            multi.active_app = next(iter(multi.apps))
            console.print(f"[yellow]Active app switched to: {multi.active_app}[/yellow]")
        else:
            multi.active_app = None

    save_multi_app_config(multi)
    console.print(f"[green]Removed app '{slug}'.[/green]")
