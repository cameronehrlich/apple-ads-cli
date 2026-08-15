"""CLI namespace for opinionated workflows above raw SDK resources."""

import typer

from . import campaigns

app = typer.Typer(
    name="workflows",
    help="Opinionated, evidence-gated workflows built on Platform API v1.",
    no_args_is_help=True,
)
app.add_typer(campaigns.app, name="campaigns", help="Campaign planning and auditing")
