"""Regression coverage for the explicit v5 CLI and import namespaces."""

from typer.main import get_command
from typer.testing import CliRunner

from asa_cli import api as compatibility_api
from asa_cli.main import app
from asa_cli.platform.cli import PLATFORM_COMMAND_GROUPS
from asa_cli.v5 import api as v5_api
from asa_cli.v5.cli import V5_COMMAND_GROUPS

runner = CliRunner()


def test_v5_namespace_contains_every_legacy_command_group():
    root_command = get_command(app)
    v5_command = root_command.commands["v5"]

    expected_groups = {name for name, _, _ in V5_COMMAND_GROUPS}
    assert expected_groups <= set(v5_command.commands)
    assert {name for name, _, _ in PLATFORM_COMMAND_GROUPS} <= set(root_command.commands)


def test_v5_nested_help_is_available():
    result = runner.invoke(app, ["v5", "campaigns", "--help"])

    assert result.exit_code == 0
    assert "list" in result.stdout
    assert "create" in result.stdout
    assert "audit" in result.stdout


def test_root_command_groups_are_the_platform_api_default():
    result = runner.invoke(app, ["--help"])

    assert result.exit_code == 0
    assert "v5" in result.stdout
    assert "campaigns" in result.stdout
    assert "ad-accounts" in result.stdout
    assert "insights" in result.stdout
    assert "deprecated" not in result.stdout.lower()


def test_root_campaigns_dispatches_to_platform_api_not_v5():
    result = runner.invoke(app, ["campaigns", "--help"])

    assert result.exit_code == 0
    assert "get" in result.stdout
    assert "query" in result.stdout
    assert "create" in result.stdout
    assert "audit" not in result.stdout


def test_legacy_api_module_reexports_canonical_v5_client():
    assert compatibility_api.API_BASE_URL == v5_api.API_BASE_URL
    assert compatibility_api.REQUEST_TIMEOUT == v5_api.REQUEST_TIMEOUT
    assert compatibility_api.SearchAdsAPIError is v5_api.SearchAdsAPIError
    assert compatibility_api.SearchAdsClient is v5_api.SearchAdsClient
