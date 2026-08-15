"""Release metadata and public version contract tests."""

import platform
import tomllib
from importlib.metadata import version
from pathlib import Path

from click import unstyle
from typer.testing import CliRunner

from asa_cli import __version__
from asa_cli.main import app
from scripts.check_release import CANONICAL_REPOSITORY, validate

ROOT = Path(__file__).resolve().parents[1]


def test_release_metadata_is_internally_consistent():
    cli_version, sdk_version = validate(__version__)

    assert cli_version == "1.1.1"
    assert sdk_version == "1.109.0"


def test_version_reports_cli_sdk_and_python_versions():
    result = CliRunner().invoke(app, ["version"])

    assert result.exit_code == 0
    assert unstyle(result.stdout) == (
        f"asa 1.1.1 (apple-ads-platform 1.109.0, Python {platform.python_version()})\n"
    )


def test_cli_framework_version_is_pinned_to_the_verified_command_tree():
    project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))["project"]

    assert "typer==0.24.0" in project["dependencies"]
    assert "click==8.3.1" in project["dependencies"]
    assert version("typer") == "0.24.0"
    assert version("click") == "8.3.1"


def test_public_metadata_uses_the_canonical_repository_without_renaming_the_cli():
    project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))["project"]

    assert project["name"] == "asa-cli"
    assert project["scripts"] == {"asa": "asa_cli.main:app"}
    assert project["urls"] == {
        "Homepage": CANONICAL_REPOSITORY,
        "Documentation": f"{CANONICAL_REPOSITORY}#readme",
        "Issues": f"{CANONICAL_REPOSITORY}/issues",
        "Releases": f"{CANONICAL_REPOSITORY}/releases",
    }

    skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    agent_metadata = (ROOT / "agents" / "openai.yaml").read_text(encoding="utf-8")
    assert "name: apple-ads-cli\n" in skill
    assert "$apple-ads-cli" in agent_metadata
