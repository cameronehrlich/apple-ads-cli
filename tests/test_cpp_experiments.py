"""Tests for narrow custom-product-page experiment workflows."""

import json
from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from asa_cli.commands.ads import app

runner = CliRunner()


def manifest_payload(ad_id=None):
    return {
        "schema_version": 1,
        "experiment_id": "cpp-long-pages",
        "hypothesis": "A focused page improves conversion for long screenshot searches.",
        "adam_id": 123,
        "custom_product_page_id": "pp-long",
        "campaign_id": 10,
        "ad_group_id": 20,
        "treatment": {
            "name": "Long pages CPP",
            "creative_id": 30,
            "ad_id": ad_id,
            "initial_status": "PAUSED",
        },
    }


def write_manifest(tmp_path, ad_id=None):
    path = tmp_path / "experiment.json"
    path.write_text(json.dumps(manifest_payload(ad_id=ad_id)))
    return path


def valid_creative():
    return {
        "id": 30,
        "adamId": 123,
        "productPageId": "pp-long",
        "state": "VALID",
    }


def test_experiment_defaults_to_read_only_dry_run(tmp_path):
    manifest = write_manifest(tmp_path)
    client = MagicMock()
    client.get_creative.return_value = valid_creative()

    with (
        patch("asa_cli.commands.ads.load_credentials", return_value=object()),
        patch("asa_cli.commands.ads.SearchAdsClient", return_value=client),
    ):
        result = runner.invoke(app, ["experiment", str(manifest), "--json"])

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["action"] == "dry_run"
    assert payload["mutated"] is False
    client.create_ad.assert_not_called()


def test_experiment_apply_requires_immediate_attachment_readback(tmp_path):
    manifest = write_manifest(tmp_path)
    client = MagicMock()
    client.get_creative.return_value = valid_creative()
    client.create_ad.return_value = {"id": 50}
    client.get_ad.return_value = {
        "id": 50,
        "name": "Long pages CPP",
        "creativeId": 30,
        "status": "PAUSED",
    }

    with (
        patch("asa_cli.commands.ads.load_credentials", return_value=object()),
        patch("asa_cli.commands.ads.SearchAdsClient", return_value=client),
    ):
        result = runner.invoke(
            app, ["experiment", str(manifest), "--apply", "--json"]
        )

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["action"] == "created_and_verified"
    assert payload["apple_ads"]["ad_id"] == 50
    client.get_ad.assert_called_once_with(10, 20, 50)


def test_experiment_apply_fails_when_readback_mismatches(tmp_path):
    manifest = write_manifest(tmp_path)
    client = MagicMock()
    client.get_creative.return_value = valid_creative()
    client.create_ad.return_value = {"id": 50}
    client.get_ad.return_value = {
        "id": 50,
        "name": "Long pages CPP",
        "creativeId": 999,
        "status": "PAUSED",
    }

    with (
        patch("asa_cli.commands.ads.load_credentials", return_value=object()),
        patch("asa_cli.commands.ads.SearchAdsClient", return_value=client),
    ):
        result = runner.invoke(app, ["experiment", str(manifest), "--apply"])

    assert result.exit_code == 1
    assert "unverified" in result.output
