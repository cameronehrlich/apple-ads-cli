"""Apple Ads CLI entry point."""

import typer
from rich.console import Console
from rich.panel import Panel

from . import __version__
from .config import set_current_app
from .platform.cli import app as platform_app
from .platform.cli import register_platform_commands
from .platform.config_cli import app as config_app
from .v5.cli import app as v5_app
from .workflows.cli import app as workflows_app

app = typer.Typer(
    name="asa",
    help="Apple Ads Platform API v1, legacy v5, and opinionated workflows.",
    no_args_is_help=True,
    rich_markup_mode="rich",
)
console = Console()

# Platform API v1 is the default resource surface. The legacy implementation is
# frozen under the explicit v5 namespace.
app.add_typer(config_app, name="config", help="Credentials and local app configuration")
register_platform_commands(app)
app.add_typer(v5_app, name="v5", help="Legacy Campaign Management API v5 commands")
app.add_typer(
    workflows_app,
    name="workflows",
    help="Opinionated workflows built on Platform API v1",
)
app.add_typer(
    platform_app,
    name="platform",
    help="Temporary explicit alias for the default Platform API v1 commands",
    hidden=True,
)


@app.command("version")
def version() -> None:
    """Show version information."""
    console.print(f"ASA CLI version {__version__}")


@app.command("help")
def help_command() -> None:
    """Show the command architecture and representative examples."""
    help_text = """
[bold cyan]Apple Ads CLI[/bold cyan]

[bold]Platform API v1 — default[/bold]
  Exact official-SDK wrappers, one command per endpoint:
    [cyan]asa campaigns get --id CAMPAIGN_ID[/cyan]
    [cyan]asa campaigns query --file query.json[/cyan]
    [cyan]asa insights impression-share --file request.json[/cyan]
    [cyan]asa insights search-term-popularity --file request.json[/cyan]
    [cyan]asa recommendations daily-budget-query --file request.json[/cyan]

  Mutations preview by default and require [cyan]--confirm[/cyan]:
    [cyan]asa campaigns create --file campaign.json[/cyan]
    [cyan]asa campaigns create --file campaign.json --confirm[/cyan]

[bold]Opinionated workflows[/bold]
    [cyan]asa workflows campaigns audit[/cyan]
    [cyan]asa workflows campaigns plan-four-structure[/cyan]

[bold]Legacy Campaign Management API v5[/bold]
  The previous implementation remains explicit and unchanged:
    [cyan]asa v5 campaigns list[/cyan]
    [cyan]asa v5 reports summary[/cyan]
    [cyan]asa v5 optimize --dry-run[/cyan]

[bold]Configuration and discovery[/bold]
    [cyan]asa config setup[/cyan]
    [cyan]asa config test[/cyan]
    [cyan]asa <resource> <action> --help[/cyan]
    [cyan]python scripts/lookup_command.py "search term popularity"[/cyan]
"""
    console.print(Panel(help_text, title="ASA CLI Help", border_style="cyan"))


@app.callback()
def main(
    app_slug: str | None = typer.Option(
        None,
        "--app",
        "-A",
        help="App slug to operate on; overrides the active local app.",
        envvar="ASA_APP",
    ),
) -> None:
    """Manage Apple Ads through Platform API v1, workflows, or explicit v5."""
    if app_slug:
        set_current_app(app_slug)


if __name__ == "__main__":
    app()
