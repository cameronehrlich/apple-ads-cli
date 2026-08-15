"""One-to-one Platform API suggestion commands."""

import typer

from ..command_factory import register_commands
from ..manifest_specs import specs_from_manifest

SDK_METHODS = (
    "query_category_suggestions",
    "query_keyword_suggestions",
    "query_phrase_suggestions",
    "query_target_cpa_suggestion",
)
COMMAND_NAMES = {
    "query_category_suggestions": "categories",
    "query_keyword_suggestions": "keywords",
    "query_phrase_suggestions": "phrases",
    "query_target_cpa_suggestion": "target-cpa",
}
COMMAND_SPECS = specs_from_manifest(
    resource_family="suggestions",
    sdk_methods=SDK_METHODS,
    command_names=COMMAND_NAMES,
)

app = typer.Typer(help="Keyword, phrase, category, and target-CPA suggestions.")
register_commands(app, COMMAND_SPECS)
