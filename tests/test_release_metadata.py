"""Release metadata and public version contract tests."""

import platform
import tomllib
from importlib.metadata import version
from pathlib import Path

from click import unstyle
from typer.testing import CliRunner

from asa_cli import __version__
from asa_cli.main import app
from scripts.check_release import validate

ROOT = Path(__file__).resolve().parents[1]


def test_release_metadata_is_internally_consistent():
    cli_version, sdk_version = validate(__version__)

    assert cli_version == "1.1.0"
    assert sdk_version == "1.109.0"


def test_version_reports_cli_sdk_and_python_versions():
    result = CliRunner().invoke(app, ["version"])

    assert result.exit_code == 0
    assert unstyle(result.stdout) == (
        f"asa 1.1.0 (apple-ads-platform 1.109.0, Python {platform.python_version()})\n"
    )


def test_cli_framework_version_is_pinned_to_the_verified_command_tree():
    project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))["project"]

    assert "typer==0.24.0" in project["dependencies"]
    assert "click==8.3.1" in project["dependencies"]
    assert version("typer") == "0.24.0"
    assert version("click") == "8.3.1"
