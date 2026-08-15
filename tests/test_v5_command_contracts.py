"""Focused CLI contracts for the frozen v5 campaign and keyword workflows."""

from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from asa_cli.commands import campaigns, keywords
from asa_cli.config import AppConfig

runner = CliRunner()


def campaign(campaign_id: int, name: str) -> dict:
    return {
        "id": campaign_id,
        "name": name,
        "status": "ENABLED",
        "displayStatus": "RUNNING",
        "countriesOrRegions": ["US"],
        "dailyBudgetAmount": {"amount": "10", "currency": "USD"},
    }


def test_campaign_setup_dry_run_does_not_construct_a_client():
    app_config = AppConfig(app_id=554594252, app_name="Stitch It")

    with (
        patch.object(campaigns, "load_credentials", return_value=object()),
        patch.object(campaigns, "get_current_app_config", return_value=app_config),
        patch.object(campaigns, "is_multi_app", return_value=False),
        patch.object(campaigns, "SearchAdsClient") as client_type,
    ):
        result = runner.invoke(campaigns.app, ["setup", "--dry-run"])

    assert result.exit_code == 0, result.output
    assert "Dry run - no changes made" in result.output
    client_type.assert_not_called()


def test_campaign_list_reads_and_filters_to_managed_campaigns_by_default():
    client = MagicMock()
    client.get_campaigns.return_value = [
        campaign(1, "Brand"),
        campaign(9, "Unrelated experiment"),
    ]

    with (
        patch.object(campaigns, "load_credentials", return_value=object()),
        patch.object(campaigns, "SearchAdsClient", return_value=client),
        patch.object(campaigns, "_resolve_app_name", return_value=None),
    ):
        result = runner.invoke(campaigns.app, ["list"])

    assert result.exit_code == 0, result.output
    assert "Brand" in result.output
    assert "Unrelated experiment" not in result.output
    client.get_campaigns.assert_called_once_with()


def test_campaign_audit_reads_without_mutating():
    client = MagicMock()
    client.get_campaigns.return_value = [campaign(1, "Brand")]

    with (
        patch.object(campaigns, "load_credentials", return_value=object()),
        patch.object(campaigns, "SearchAdsClient", return_value=client),
        patch.object(campaigns, "_resolve_app_name", return_value=None),
    ):
        result = runner.invoke(campaigns.app, ["audit"])

    assert result.exit_code == 0, result.output
    assert "Missing category campaign" in result.output
    client.pause_campaign.assert_not_called()
    client.enable_campaign.assert_not_called()
    client.create_campaign.assert_not_called()


def test_campaign_pause_and_enable_target_only_the_requested_id():
    client = MagicMock()
    client.pause_campaign.return_value = True
    client.enable_campaign.return_value = True

    with (
        patch.object(campaigns, "load_credentials", return_value=object()),
        patch.object(campaigns, "SearchAdsClient", return_value=client),
        patch.object(campaigns, "_resolve_app_name", return_value=None),
    ):
        paused = runner.invoke(campaigns.app, ["pause", "42"])
        enabled = runner.invoke(campaigns.app, ["enable", "43"])

    assert paused.exit_code == 0, paused.output
    assert enabled.exit_code == 0, enabled.output
    client.pause_campaign.assert_called_once_with(42)
    client.enable_campaign.assert_called_once_with(43)


def keyword_client() -> MagicMock:
    client = MagicMock()
    client.get_campaigns.return_value = [
        campaign(2, "Category"),
        campaign(4, "Discovery"),
    ]
    client.get_campaign.return_value = campaign(2, "Category")
    return client


def invoke_keyword_dry_run(args: list[str]) -> tuple[object, MagicMock]:
    client = keyword_client()
    with (
        patch.object(keywords, "load_credentials", return_value=object()),
        patch.object(keywords, "SearchAdsClient", return_value=client),
        patch.object(keywords, "_resolve_app_name", return_value=None),
    ):
        result = runner.invoke(keywords.app, args)
    return result, client


def assert_no_keyword_mutations(client: MagicMock) -> None:
    client.add_keywords.assert_not_called()
    client.add_negative_keywords.assert_not_called()


def test_keyword_add_dry_run_preserves_routing_without_mutation():
    result, client = invoke_keyword_dry_run(
        ["add", "long screenshot", "--type", "category", "--dry-run"]
    )

    assert result.exit_code == 0, result.output
    assert "Add as EXACT to Category" in result.output
    assert "Add as BROAD to Discovery" in result.output
    assert_no_keyword_mutations(client)


def test_negative_keyword_dry_run_does_not_mutate():
    result, client = invoke_keyword_dry_run(
        ["add-negatives", "free,trial", "--campaign", "2", "--dry-run"]
    )

    assert result.exit_code == 0, result.output
    assert "Campaigns: 1" in result.output
    assert_no_keyword_mutations(client)


def test_keyword_promotion_dry_run_does_not_mutate():
    result, client = invoke_keyword_dry_run(
        ["promote", "long screenshot", "--target", "category", "--dry-run"]
    )

    assert result.exit_code == 0, result.output
    assert "Add as EXACT to Category" in result.output
    assert "Add as NEGATIVE to Discovery" in result.output
    assert_no_keyword_mutations(client)
