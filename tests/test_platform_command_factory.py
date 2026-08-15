"""Contract tests for manifest-backed Platform API command generation."""

from types import SimpleNamespace

import typer
from click import unstyle
from typer.testing import CliRunner

from asa_cli.platform.command_factory import (
    BodySpec,
    CommandSpec,
    ParameterSpec,
    register_commands,
)
from asa_cli.platform.resources.campaigns import app as campaigns_app

runner = CliRunner()


def build_app(*specs: CommandSpec) -> typer.Typer:
    app = typer.Typer()

    @app.callback()
    def root() -> None:
        """Test command group."""

    register_commands(app, specs)
    return app


def test_read_command_exposes_exact_options_and_dispatches_once(monkeypatch):
    calls = []

    def fake_invoke(method_name, **kwargs):
        calls.append((method_name, kwargs))
        return {"ok": True}

    monkeypatch.setattr("asa_cli.platform.command_factory.invoke", fake_invoke)
    app = build_app(
        CommandSpec(
            name="get",
            sdk_method="campaigns_id_get",
            help="Get a campaign.",
            parameters=(ParameterSpec("id", "--id", help="Campaign ID"),),
        )
    )

    help_result = runner.invoke(app, ["get", "--help"])
    assert help_result.exit_code == 0
    help_text = unstyle(help_result.stdout)
    assert "--id" in help_text
    assert "--ad-account" in help_text

    result = runner.invoke(app, ["get", "--id", "42", "--ad-account", "123"])

    assert result.exit_code == 0
    assert '"ok": true' in result.stdout
    assert calls == [
        (
            "campaigns_id_get",
            {
                "arguments": {"id": "42"},
                "context": "required",
                "ad_account_id": "123",
            },
        )
    ]


def test_mutation_previews_by_default_and_requires_confirmation(monkeypatch):
    calls = []
    monkeypatch.setattr(
        "asa_cli.platform.command_factory.invoke",
        lambda method_name, **kwargs: calls.append((method_name, kwargs)) or {"sent": True},
    )
    app = build_app(
        CommandSpec(
            name="delete",
            sdk_method="campaigns_id_delete",
            help="Delete a campaign.",
            parameters=(ParameterSpec("id", "--id"),),
            mutation="delete",
        )
    )

    preview = runner.invoke(app, ["delete", "--id", "42", "--ad-account", "123"])
    assert preview.exit_code == 0
    assert '"dry_run": true' in preview.stdout
    assert "Mutation not sent" in preview.stderr
    assert calls == []

    confirmed = runner.invoke(
        app,
        ["delete", "--id", "42", "--ad-account", "123", "--confirm"],
    )
    assert confirmed.exit_code == 0
    assert '"sent": true' in confirmed.stdout
    assert [call[0] for call in calls] == ["campaigns_id_delete"]


def test_request_file_is_hydrated_into_official_model(monkeypatch, tmp_path):
    request_file = tmp_path / "request.json"
    request_file.write_text('{"name":"Launch"}', encoding="utf-8")
    model = SimpleNamespace(
        model_dump=lambda **kwargs: {"name": "Launch"},
    )
    hydrated = []

    def fake_hydrate(model_name, payload, *, many=False):
        hydrated.append((model_name, payload, many))
        return model

    monkeypatch.setattr("asa_cli.platform.command_factory.hydrate_model", fake_hydrate)
    monkeypatch.setattr(
        "asa_cli.platform.command_factory.invoke",
        lambda method_name, **kwargs: {"body_type": type(kwargs["arguments"]["body"]).__name__},
    )
    app = build_app(
        CommandSpec(
            name="create",
            sdk_method="campaigns_post",
            help="Create a campaign.",
            body=BodySpec("body", "CampaignCreate"),
            mutation="create",
        )
    )

    result = runner.invoke(
        app,
        [
            "create",
            "--file",
            str(request_file),
            "--ad-account",
            "123",
            "--confirm",
        ],
    )

    assert result.exit_code == 0
    assert hydrated == [("CampaignCreate", {"name": "Launch"}, False)]
    assert '"body_type": "SimpleNamespace"' in result.stdout


def test_invalid_request_file_returns_structured_cli_error(tmp_path):
    request_file = tmp_path / "request.json"
    request_file.write_text("not-json", encoding="utf-8")
    app = build_app(
        CommandSpec(
            name="create",
            sdk_method="campaigns_post",
            help="Create a campaign.",
            body=BodySpec("body", "CampaignCreate"),
            mutation="create",
        )
    )

    result = runner.invoke(app, ["create", "--file", str(request_file), "--confirm"])

    assert result.exit_code == 1
    assert '"error"' in result.stderr
    assert "Invalid JSON" in result.stderr


def test_duplicate_command_names_are_rejected():
    app = typer.Typer()
    spec = CommandSpec(name="list", sdk_method="campaigns_get", help="List campaigns.")

    try:
        register_commands(app, (spec, spec))
    except ValueError as exc:
        assert str(exc) == "Duplicate command name: list"
    else:  # pragma: no cover - protects the registry invariant
        raise AssertionError("duplicate command name was accepted")


def test_no_context_operation_omits_account_option(monkeypatch):
    monkeypatch.setattr(
        "asa_cli.platform.command_factory.invoke",
        lambda method_name, **kwargs: {"context": kwargs["context"]},
    )
    app = build_app(
        CommandSpec(
            name="countries",
            sdk_method="countries_or_regions_get",
            help="List supported countries.",
            context="none",
        )
    )

    help_result = runner.invoke(app, ["countries", "--help"])
    result = runner.invoke(app, ["countries"])

    assert help_result.exit_code == 0
    assert "--ad-account" not in help_result.stdout
    assert result.exit_code == 0
    assert '"context": "none"' in result.stdout


def test_real_sdk_campaign_body_hydrates_during_safe_preview(tmp_path):
    request_file = tmp_path / "campaign.json"
    request_file.write_text(
        """{
          "adAccountId": 123,
          "name": "Launch",
          "billingEvent": "TAPS",
          "promotedObjectType": "APPSTORE_APP",
          "promotedObjectId": "987654321",
          "dailyBudget": {"value": {"amount": "25.00", "currency": "USD"}},
          "targeting": {}
        }""",
        encoding="utf-8",
    )

    result = runner.invoke(
        campaigns_app,
        [
            "create",
            "--file",
            str(request_file),
            "--ad-account",
            "123",
        ],
    )

    assert result.exit_code == 0
    assert '"sdk_method": "campaigns_post"' in result.stdout
    assert '"ad_account_id": "123"' in result.stdout
    assert '"adAccountId": 123' in result.stdout
    assert '"billingEvent": "TAPS"' in result.stdout
    assert "Mutation not sent" in result.stderr


def test_preview_rejects_body_account_that_differs_from_context(tmp_path):
    request_file = tmp_path / "campaign.json"
    request_file.write_text(
        """{
          "adAccountId": 999,
          "name": "Launch",
          "billingEvent": "TAPS",
          "promotedObjectType": "APPSTORE_APP",
          "promotedObjectId": "987654321",
          "dailyBudget": {"value": {"amount": "25.00"}},
          "targeting": {}
        }""",
        encoding="utf-8",
    )

    result = runner.invoke(
        campaigns_app,
        ["create", "--file", str(request_file), "--ad-account", "123"],
    )

    assert result.exit_code == 1
    assert "does not match" in result.stderr
