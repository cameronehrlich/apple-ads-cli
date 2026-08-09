"""Ad variation, creative, and CPP experiment commands."""

import json
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.prompt import Confirm
from rich.table import Table

from ..api import SearchAdsClient
from ..config import get_current_app_config, load_credentials
from ..experiments import CPPExperimentManifest, load_experiment_manifest

app = typer.Typer(help="Ad variation and creative management commands")
console = Console()


@app.command("list")
def list_ads(
    campaign_id: Optional[int] = typer.Option(None, "--campaign", "-c", help="Campaign ID"),
    ad_group_id: Optional[int] = typer.Option(None, "--adgroup", "-g", help="Ad group ID"),
):
    """List all ads. Provide campaign + ad group for a specific group, or search across all."""
    credentials = load_credentials()
    if not credentials:
        console.print("[red]No credentials configured. Run 'asa config setup' first.[/red]")
        raise typer.Exit(1)

    client = SearchAdsClient(credentials)

    if campaign_id and ad_group_id:
        with console.status("[bold blue]Fetching ads..."):
            ads = client.get_ads(campaign_id, ad_group_id)
    else:
        with console.status("[bold blue]Finding ads..."):
            ads = client.find_ads(campaign_id=campaign_id)

    if not ads:
        console.print("[yellow]No ads found.[/yellow]")
        return

    table = Table(title="Ads", show_header=True, header_style="bold magenta")
    table.add_column("ID", style="cyan")
    table.add_column("Name")
    table.add_column("Status")
    table.add_column("Creative ID")
    table.add_column("Creative Type")

    for ad in ads:
        status = ad.get("status", "UNKNOWN")
        status_style = "green" if status == "ENABLED" else "yellow" if status == "PAUSED" else "red"

        table.add_row(
            str(ad.get("id", "")),
            ad.get("name", "Unknown"),
            f"[{status_style}]{status}[/{status_style}]",
            str(ad.get("creativeId", "")),
            ad.get("creativeType", "-"),
        )

    console.print(table)
    console.print(f"\n[dim]Total: {len(ads)} ads[/dim]")


@app.command("create")
def create_ad(
    campaign_id: int = typer.Option(..., "--campaign", "-c", help="Campaign ID"),
    ad_group_id: int = typer.Option(..., "--adgroup", "-g", help="Ad group ID"),
    creative_id: int = typer.Option(..., "--creative", help="Creative ID"),
    name: str = typer.Argument(..., help="Ad name"),
    status: str = typer.Option("ENABLED", "--status", "-s", help="Initial status (ENABLED or PAUSED)"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Validate and show the attachment only"),
):
    """Create an ad and require immediate readback of its attachment."""
    credentials = load_credentials()
    if not credentials:
        console.print("[red]No credentials configured. Run 'asa config setup' first.[/red]")
        raise typer.Exit(1)

    status_upper = status.upper()
    if status_upper not in ("ENABLED", "PAUSED"):
        console.print("[red]Status must be ENABLED or PAUSED.[/red]")
        raise typer.Exit(1)

    client = SearchAdsClient(credentials)

    console.print("\nCreating ad:")
    console.print(f"  Name: [cyan]{name}[/cyan]")
    console.print(f"  Campaign: [cyan]{campaign_id}[/cyan]")
    console.print(f"  Ad Group: [cyan]{ad_group_id}[/cyan]")
    console.print(f"  Creative: [cyan]{creative_id}[/cyan]")
    console.print(f"  Status: [cyan]{status_upper}[/cyan]")

    creative = client.get_creative(creative_id)
    if not creative:
        console.print(f"[red]Creative {creative_id} was not found or could not be read.[/red]")
        raise typer.Exit(1)

    if dry_run:
        console.print("[yellow]Dry run: no ad was created.[/yellow]")
        return

    with console.status("[bold blue]Creating ad..."):
        ad = client.create_ad(
            campaign_id=campaign_id,
            ad_group_id=ad_group_id,
            creative_id=creative_id,
            name=name,
            status=status_upper,
        )

    if not ad or not ad.get("id"):
        console.print("[red]Failed to create ad.[/red]")
        raise typer.Exit(1)

    verified = client.get_ad(campaign_id, ad_group_id, ad.get("id"))
    expected = {
        "name": name,
        "creativeId": creative_id,
        "status": status_upper,
    }
    if not verified or any(verified.get(key) != value for key, value in expected.items()):
        console.print(
            "[red]Ad creation returned, but immediate readback did not confirm name, "
            "creative, and status. Treat the mutation as unverified.[/red]"
        )
        raise typer.Exit(1)

    console.print("\n[green]Ad created and verified.[/green]")
    console.print(f"  ID: [cyan]{verified.get('id')}[/cyan]")
    console.print(f"  Name: [cyan]{verified.get('name')}[/cyan]")


def _load_manifest_or_exit(path: Path) -> CPPExperimentManifest:
    try:
        return load_experiment_manifest(path)
    except ValueError as exc:
        raise typer.BadParameter(str(exc)) from exc


def _validate_cpp_creative(
    client: SearchAdsClient, manifest: CPPExperimentManifest
) -> dict:
    creative = client.get_creative(manifest.treatment.creative_id)
    if not creative:
        raise ValueError(
            f"Creative {manifest.treatment.creative_id} was not found or could not be read"
        )
    if str(creative.get("adamId")) != str(manifest.adam_id):
        raise ValueError("Creative Adam ID does not match the experiment manifest")
    if creative.get("productPageId") != manifest.custom_product_page_id:
        raise ValueError("Creative is not linked to the manifest custom product page")
    if creative.get("state") not in (None, "VALID"):
        raise ValueError(f"Creative is not valid (state: {creative.get('state')})")
    return creative


@app.command("experiment")
def apply_experiment(
    manifest_path: Path = typer.Argument(
        ..., exists=True, readable=True, help="Versioned CPP experiment JSON manifest"
    ),
    apply: bool = typer.Option(
        False, "--apply", help="Create the treatment ad; default is read-only dry run"
    ),
    json_output: bool = typer.Option(False, "--json", help="Emit stable machine-readable JSON"),
):
    """Validate or attach an existing ASC custom product page creative.

    App Store Connect authoring remains outside this command. Without
    ``--apply`` this command performs read-only validation only.
    """
    credentials = load_credentials()
    if not credentials:
        console.print("[red]No credentials configured. Run 'asa config setup' first.[/red]")
        raise typer.Exit(1)

    manifest = _load_manifest_or_exit(manifest_path)
    client = SearchAdsClient(credentials)
    try:
        creative = _validate_cpp_creative(client, manifest)
    except ValueError as exc:
        console.print(f"[red]{exc}[/red]")
        raise typer.Exit(1) from exc

    treatment = manifest.treatment
    verified_ad = None
    action = "validated"
    if treatment.ad_id is not None:
        verified_ad = client.get_ad(
            manifest.campaign_id, manifest.ad_group_id, treatment.ad_id
        )
        if not verified_ad or verified_ad.get("creativeId") != treatment.creative_id:
            console.print(
                "[red]Manifest treatment ad readback did not confirm the expected creative.[/red]"
            )
            raise typer.Exit(1)
        action = "already_attached"
    elif apply:
        created = client.create_ad(
            manifest.campaign_id,
            manifest.ad_group_id,
            treatment.creative_id,
            treatment.name,
            treatment.initial_status,
        )
        if not created or not created.get("id"):
            console.print("[red]Apple Ads did not return a created treatment ad.[/red]")
            raise typer.Exit(1)
        verified_ad = client.get_ad(
            manifest.campaign_id, manifest.ad_group_id, created.get("id")
        )
        expected = {
            "name": treatment.name,
            "creativeId": treatment.creative_id,
            "status": treatment.initial_status,
        }
        if not verified_ad or any(
            verified_ad.get(field) != value for field, value in expected.items()
        ):
            console.print(
                "[red]Treatment ad creation returned, but readback did not confirm the "
                "manifest attachment. Treat the mutation as unverified.[/red]"
            )
            raise typer.Exit(1)
        action = "created_and_verified"
    else:
        action = "dry_run"

    payload = {
        "schema_version": 1,
        "experiment_id": manifest.experiment_id,
        "action": action,
        "mutated": action == "created_and_verified",
        "hypothesis": manifest.hypothesis,
        "app_store": {
            "adam_id": manifest.adam_id,
            "custom_product_page_id": manifest.custom_product_page_id,
        },
        "apple_ads": {
            "campaign_id": manifest.campaign_id,
            "ad_group_id": manifest.ad_group_id,
            "creative_id": creative.get("id"),
            "ad_id": verified_ad.get("id") if verified_ad else None,
            "status": verified_ad.get("status") if verified_ad else treatment.initial_status,
        },
    }
    if json_output:
        typer.echo(json.dumps(payload, indent=2, sort_keys=True, allow_nan=False))
    else:
        console.print(
            f"[green]Experiment {manifest.experiment_id}: {action.replace('_', ' ')}.[/green]"
        )
        if action == "dry_run":
            console.print("[yellow]No Apple Ads mutation was performed. Use --apply to attach.[/yellow]")


@app.command("delete")
def delete_ad(
    ad_id: int = typer.Argument(..., help="Ad ID to delete"),
    campaign_id: int = typer.Option(..., "--campaign", "-c", help="Campaign ID"),
    ad_group_id: int = typer.Option(..., "--adgroup", "-g", help="Ad group ID"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation prompt"),
):
    """Delete an ad. WARNING: This is irreversible."""
    credentials = load_credentials()
    if not credentials:
        console.print("[red]No credentials configured. Run 'asa config setup' first.[/red]")
        raise typer.Exit(1)

    client = SearchAdsClient(credentials)

    # Get ad info for confirmation
    ad = client.get_ad(campaign_id, ad_group_id, ad_id)
    if not ad:
        console.print(f"[red]Ad {ad_id} not found.[/red]")
        raise typer.Exit(1)

    console.print("\n[bold red]WARNING: About to delete ad:[/bold red]")
    console.print(f"  Name: {ad.get('name', 'Unknown')}")
    console.print(f"  ID: {ad_id}")

    if not force and not Confirm.ask("\n[red]This is irreversible. Continue?[/red]"):
        console.print("[yellow]Cancelled.[/yellow]")
        return

    with console.status("[bold blue]Deleting ad..."):
        if client.delete_ad(campaign_id, ad_group_id, ad_id):
            console.print(f"[green]Ad {ad_id} deleted.[/green]")
        else:
            console.print(f"[red]Failed to delete ad {ad_id}.[/red]")
            raise typer.Exit(1)


@app.command("creatives")
def list_creatives(
    creative_id: Optional[int] = typer.Option(None, "--id", help="Get a specific creative by ID"),
):
    """List creatives or get details for a specific creative."""
    credentials = load_credentials()
    if not credentials:
        console.print("[red]No credentials configured. Run 'asa config setup' first.[/red]")
        raise typer.Exit(1)

    client = SearchAdsClient(credentials)

    if creative_id:
        with console.status("[bold blue]Fetching creative..."):
            creative = client.get_creative(creative_id)

        if not creative:
            console.print(f"[red]Creative {creative_id} not found.[/red]")
            raise typer.Exit(1)

        console.print("\n[bold]Creative Details[/bold]")
        console.print(f"  ID: [cyan]{creative.get('id')}[/cyan]")
        console.print(f"  Name: [cyan]{creative.get('name', 'Unknown')}[/cyan]")
        console.print(f"  Type: [cyan]{creative.get('type', '-')}[/cyan]")
        console.print(f"  State: [cyan]{creative.get('state', '-')}[/cyan]")
        console.print(f"  Adam ID: [cyan]{creative.get('adamId', '-')}[/cyan]")

        product_page_id = creative.get("productPageId")
        if product_page_id:
            console.print(f"  Product Page ID: [cyan]{product_page_id}[/cyan]")

        return

    with console.status("[bold blue]Fetching creatives..."):
        creatives = client.get_creatives()

    if not creatives:
        console.print("[yellow]No creatives found.[/yellow]")
        return

    table = Table(title="Creatives", show_header=True, header_style="bold magenta")
    table.add_column("ID", style="cyan")
    table.add_column("Name")
    table.add_column("Type")
    table.add_column("State")
    table.add_column("Adam ID")

    for creative in creatives:
        state = creative.get("state", "UNKNOWN")
        state_style = "green" if state == "VALID" else "yellow" if state == "PENDING" else "red"

        table.add_row(
            str(creative.get("id", "")),
            creative.get("name", "Unknown"),
            creative.get("type", "-"),
            f"[{state_style}]{state}[/{state_style}]",
            str(creative.get("adamId", "")),
        )

    console.print(table)
    console.print(f"\n[dim]Total: {len(creatives)} creatives[/dim]")


@app.command("product-pages")
def list_product_pages(
    adam_id: Optional[int] = typer.Option(None, "--adam-id", "-a", help="App Adam ID (uses current app if not set)"),
):
    """List custom product pages for an app."""
    credentials = load_credentials()
    if not credentials:
        console.print("[red]No credentials configured. Run 'asa config setup' first.[/red]")
        raise typer.Exit(1)

    app_config = get_current_app_config()

    resolved_adam_id = adam_id
    if not resolved_adam_id:
        if not app_config:
            console.print("[red]No app configured. Use --adam-id or run 'asa config setup'.[/red]")
            raise typer.Exit(1)
        resolved_adam_id = app_config.app_id

    client = SearchAdsClient(credentials)

    with console.status("[bold blue]Fetching product pages..."):
        pages = client.get_product_pages(resolved_adam_id)

    if not pages:
        console.print("[yellow]No custom product pages found.[/yellow]")
        return

    table = Table(title="Custom Product Pages", show_header=True, header_style="bold magenta")
    table.add_column("ID", style="cyan")
    table.add_column("Name")
    table.add_column("State")
    table.add_column("Visible")

    for page in pages:
        state = page.get("state", "UNKNOWN")
        state_style = "green" if state == "VISIBLE" else "yellow"

        table.add_row(
            str(page.get("id", "")),
            page.get("name", "Unknown"),
            f"[{state_style}]{state}[/{state_style}]",
            str(page.get("isVisible", "-")),
        )

    console.print(table)
    console.print(f"\n[dim]Total: {len(pages)} product pages[/dim]")


@app.command("rejections")
def show_rejections():
    """Show product page rejection reasons."""
    credentials = load_credentials()
    if not credentials:
        console.print("[red]No credentials configured. Run 'asa config setup' first.[/red]")
        raise typer.Exit(1)

    client = SearchAdsClient(credentials)

    with console.status("[bold blue]Fetching rejection reasons..."):
        reasons = client.find_rejection_reasons()

    if not reasons:
        console.print("[green]No rejection reasons found. All clear![/green]")
        return

    table = Table(title="Rejection Reasons", show_header=True, header_style="bold magenta")
    table.add_column("Creative ID", style="cyan")
    table.add_column("Reason")
    table.add_column("Comment")

    for reason in reasons:
        table.add_row(
            str(reason.get("creativeId", "")),
            reason.get("reasonText", "-"),
            reason.get("comment", "-"),
        )

    console.print(table)
    console.print(f"\n[dim]Total: {len(reasons)} rejection reasons[/dim]")
