"""Release metadata and public version contract tests."""

import platform

from typer.testing import CliRunner

from asa_cli import __version__
from asa_cli.main import app
from scripts.check_release import validate


def test_release_metadata_is_internally_consistent():
    cli_version, sdk_version = validate(__version__)

    assert cli_version == "1.0.0"
    assert sdk_version == "1.109.0"


def test_version_reports_cli_sdk_and_python_versions():
    result = CliRunner().invoke(app, ["version"])

    assert result.exit_code == 0
    assert result.stdout == (
        f"asa 1.0.0 (apple-ads-platform 1.109.0, Python {platform.python_version()})\n"
    )
