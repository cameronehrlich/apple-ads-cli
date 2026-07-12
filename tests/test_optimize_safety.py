"""Command-level safety tests for campaign optimization."""

import json
from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from asa_cli.commands import optimize
from asa_cli.config import CampaignType

runner = CliRunner()


def campaign(campaign_id: int, name: str) -> dict:
    return {"id": campaign_id, "name": name, "status": "RUNNING"}


def report_row(term: str, installs: int, spend: float) -> dict:
    return {
        "metadata": {"searchTermText": term, "searchTermSource": "BROAD"},
        "total": {
            "impressions": 100,
            "taps": 10,
            "totalInstalls": installs,
            "localSpend": {"amount": str(spend)},
        },
    }


class FakeClient:
    """Read fixture that records attempted campaign mutations."""

    def __init__(self, _credentials):
        self.mutations: list[tuple[str, int, list[str]]] = []
        self.rows = [report_row("winner", 3, 1.20), report_row("waste", 0, 2.00)]

    def get_campaigns(self):
        return [
            campaign(1, "StitchIt - Brand"),
            campaign(2, "StitchIt - Category"),
            campaign(3, "StitchIt - Competitor"),
            campaign(4, "StitchIt - Discovery"),
        ]

    def get_search_terms_report(self, _campaign_id, _start, _end):
        return self.rows

    def get_ad_groups(self, campaign_id):
        return [{"id": campaign_id * 10, "name": "Exact"}]

    def add_keywords(self, campaign_id, ad_group_id, keywords, match_type):
        del ad_group_id, match_type
        self.mutations.append(("keywords", campaign_id, keywords))
        return ([{"id": 10, "text": term} for term in keywords], [])

    def add_negative_keywords(self, campaign_id, keywords):
        self.mutations.append(("negatives", campaign_id, keywords))
        return ([{"id": 20, "text": term} for term in keywords], [])


def invoke_with_fake_client(args: list[str], *, rows=None):
    fake = FakeClient(object())
    if rows is not None:
        fake.rows = rows
    with (
        patch.object(optimize, "load_credentials", return_value=object()),
        patch.object(optimize, "SearchAdsClient", return_value=fake),
        patch.object(optimize, "_resolve_app_name", return_value="StitchIt"),
    ):
        result = runner.invoke(optimize.app, args)
    return result, fake


def test_duplicate_campaign_types_fail_closed():
    client = FakeClient(object())
    client.get_campaigns = lambda: [
        campaign(1, "StitchIt - Category"),
        campaign(2, "StitchIt - Category v2"),
    ]

    with pytest.raises(ValueError, match="Multiple category campaigns matched"):
        optimize.get_campaigns_indexed(client, app_name="StitchIt")


def test_partial_promotion_only_negates_confirmed_added_terms():
    class PartialClient(FakeClient):
        def add_keywords(self, campaign_id, ad_group_id, keywords, match_type):
            del campaign_id, ad_group_id, keywords, match_type
            return ([{"id": 10, "text": "safe term"}], [{"messageCode": "INVALID"}])

    client = PartialClient(object())
    promoted, failed = optimize.execute_promotions(
        client,
        [{"term": "safe term"}, {"term": "failed term"}],
        campaign(2, "StitchIt - Category"),
        campaign(4, "StitchIt - Discovery"),
    )

    assert client.mutations == [("negatives", 4, ["safe term"])]
    assert (promoted, failed) == (1, 1)


def test_dry_run_never_calls_mutation_methods():
    result, fake = invoke_with_fake_client(["--dry-run"])

    assert result.exit_code == 0, result.output
    assert fake.mutations == []


def test_json_never_calls_mutation_methods_and_is_valid_json():
    result, fake = invoke_with_fake_client(["--json"])

    assert result.exit_code == 0, result.output
    assert fake.mutations == []
    assert json.loads(result.output)["settings"]["negative_scope"] == "discovery"


def test_default_negative_scope_only_mutates_discovery():
    result, fake = invoke_with_fake_client(
        ["--auto-approve"],
        rows=[report_row("waste", 0, 2.00)],
    )

    assert result.exit_code == 0, result.output
    assert fake.mutations == [("negatives", 4, ["waste"])]


def test_managed_negative_scope_is_explicit():
    result, fake = invoke_with_fake_client(
        ["--auto-approve", "--negative-scope", "managed"],
        rows=[report_row("waste", 0, 2.00)],
    )

    assert result.exit_code == 0, result.output
    assert [mutation[1] for mutation in fake.mutations] == [1, 2, 3, 4]


def test_duplicate_campaign_error_prevents_command_mutations():
    fake = FakeClient(object())
    fake.get_campaigns = lambda: [
        campaign(2, "StitchIt - Category"),
        campaign(5, "StitchIt - Category v2"),
    ]
    with (
        patch.object(optimize, "load_credentials", return_value=object()),
        patch.object(optimize, "SearchAdsClient", return_value=fake),
        patch.object(optimize, "_resolve_app_name", return_value="StitchIt"),
    ):
        result = runner.invoke(optimize.app, ["--auto-approve"])

    assert result.exit_code == 1
    assert "Multiple category campaigns matched" in result.output
    assert fake.mutations == []


def test_discovery_scope_uses_campaign_type_contract():
    assert CampaignType.DISCOVERY.value == "discovery"
