"""Command-level tests for configuration health checks."""

from unittest.mock import patch

from typer.testing import CliRunner

from asa_cli.api import SearchAdsAPIError
from asa_cli.commands.config import app
from asa_cli.config import Credentials

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
            "asa_cli.api.SearchAdsClient.get_campaigns",
            side_effect=SearchAdsAPIError("service unavailable"),
        ):
            result = runner.invoke(app, ["test"])

    assert result.exit_code == 1
    assert "Connection failed: service unavailable" in result.output
    assert "Connection successful" not in result.output
