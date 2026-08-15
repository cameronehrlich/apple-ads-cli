"""Configuration commands shared by the Platform API and legacy workflows."""

import json

import typer

from ..commands.config import (
    add_app,
    list_apps,
    remove_app,
    setup_config,
    show_config,
    switch_app,
)
from .runtime import PlatformAPIError, invoke

app = typer.Typer(help="Credentials, ad-account context, and local app configuration.")

app.command("setup")(setup_config)
app.command("show")(show_config)
app.command("add-app")(add_app)
app.command("list-apps")(list_apps)
app.command("switch")(switch_app)
app.command("remove-app")(remove_app)


@app.command("test")
def test_platform_connection() -> None:
    """Authenticate with the official SDK and read the current API user."""
    try:
        invoke("get_me", context="none")
    except PlatformAPIError as exc:
        typer.echo(
            json.dumps(
                {
                    "error": {
                        "message": str(exc),
                        "status": exc.status,
                        "body": exc.body,
                    }
                },
                indent=2,
                sort_keys=True,
            ),
            err=True,
        )
        raise typer.Exit(1) from exc

    typer.echo(
        json.dumps(
            {"connection": "ok", "sdkMethod": "get_me"},
            indent=2,
            sort_keys=True,
        )
    )
