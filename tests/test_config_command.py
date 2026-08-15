"""Command-level tests for configuration health checks."""

from unittest.mock import patch

from typer.testing import CliRunner

from asa_cli.commands.config import app
from asa_cli.config import Credentials, MultiAppConfig
from asa_cli.v5.api import SearchAdsAPIError

runner = CliRunner()


def test_config_test_exits_nonzero_when_campaign_read_fails():
    credentials = Credentials(
        org_id=123456,
        client_id="test_client",
        team_id="test_team",
        key_id="test_key",
        private_key_path="/path/to/key.pem",
    )

    with patch("asa_cli.commands.config.load_credentials", return_value=credentials):
        with patch(
            "asa_cli.v5.api.SearchAdsClient.get_campaigns",
            side_effect=SearchAdsAPIError("service unavailable"),
        ):
            result = runner.invoke(app, ["test"])

    assert result.exit_code == 1
    assert "Connection failed: service unavailable" in result.output
    assert "Connection successful" not in result.output


def test_config_show_displays_ad_account_id_when_configured():
    credentials = Credentials(
        org_id=123456,
        ad_account_id="account-123",
        client_id="test_client",
        team_id="test_team",
        key_id="test_key",
        private_key_path="/path/to/key.pem",
    )

    with patch("asa_cli.commands.config.load_credentials", return_value=credentials):
        with patch("asa_cli.commands.config.load_app_config", return_value=None):
            with patch(
                "asa_cli.commands.config.load_multi_app_config",
                return_value=MultiAppConfig(),
            ):
                result = runner.invoke(app, ["show"])

    assert result.exit_code == 0
    assert "Ad Account ID" in result.output
    assert "account-123" in result.output
