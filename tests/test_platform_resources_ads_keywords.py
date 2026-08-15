"""Coverage for roadmap-3dyz.4 Platform API resource registries."""

from types import ModuleType

import pytest
from typer.testing import CliRunner

from asa_cli.platform.manifest_specs import load_manifest, specs_from_manifest
from asa_cli.platform.resources import (
    ads,
    creatives,
    keywords,
    negative_keywords,
    product_pages,
    rejection_reasons,
    shared_budgets,
)

runner = CliRunner()

RESOURCE_MODULES: tuple[tuple[str, ModuleType], ...] = (
    ("ads", ads),
    ("keywords", keywords),
    ("negative-keywords", negative_keywords),
    ("creatives", creatives),
    ("product-pages", product_pages),
    ("rejection-reasons", rejection_reasons),
    ("shared-budgets", shared_budgets),
)


def test_resource_registries_cover_each_assigned_manifest_method_exactly_once():
    operations = load_manifest()["operations"]
    all_registered_methods = []

    for resource_family, module in RESOURCE_MODULES:
        manifest_methods = {
            operation["sdk_method"]
            for operation in operations
            if operation["resource_family"] == resource_family
        }
        assert set(module.SDK_METHODS) == manifest_methods
        assert {spec.sdk_method for spec in module.COMMAND_SPECS} == manifest_methods
        assert len(module.COMMAND_SPECS) == len(module.SDK_METHODS)
        all_registered_methods.extend(module.SDK_METHODS)

    assert len(all_registered_methods) == 35
    assert len(set(all_registered_methods)) == 35


def test_manifest_adapter_derives_parameters_models_context_and_mutations():
    update_keyword = next(
        spec for spec in keywords.COMMAND_SPECS if spec.sdk_method == "keywords_id_put"
    )
    get_rejection = next(
        spec
        for spec in rejection_reasons.COMMAND_SPECS
        if spec.sdk_method == "rejection_reasons_apps_rejection_reason_id_get"
    )
    create_shared_budget = next(
        spec
        for spec in shared_budgets.COMMAND_SPECS
        if spec.sdk_method == "shared_budgets_post"
    )

    assert [(item.name, item.annotation) for item in update_keyword.parameters] == [
        ("id", str)
    ]
    assert update_keyword.body is not None
    assert update_keyword.body.parameter == "keyword_update"
    assert update_keyword.body.model == "KeywordUpdate"
    assert update_keyword.context == "required"
    assert update_keyword.mutation == "update"

    assert [(item.name, item.annotation) for item in get_rejection.parameters] == [
        ("rejection_reason_id", int)
    ]
    assert create_shared_budget.context == "none"
    assert create_shared_budget.mutation == "create"
    assert create_shared_budget.body is not None
    assert create_shared_budget.body.model == "SharedBudgetCreate"


def test_read_command_dispatches_to_its_sdk_method_once(monkeypatch):
    calls = []
    monkeypatch.setattr(
        "asa_cli.platform.command_factory.invoke",
        lambda method_name, **kwargs: calls.append((method_name, kwargs)) or {"ok": True},
    )

    result = runner.invoke(
        ads.app,
        ["get", "--id", "ad-123", "--ad-account", "account-123"],
    )

    assert result.exit_code == 0
    assert '"ok": true' in result.stdout
    assert calls == [
        (
            "ads_id_get",
            {
                "arguments": {"id": "ad-123"},
                "context": "required",
                "ad_account_id": "account-123",
            },
        )
    ]


def test_mutation_previews_exact_sdk_method_without_invoking(monkeypatch):
    calls = []
    monkeypatch.setattr(
        "asa_cli.platform.command_factory.invoke",
        lambda method_name, **kwargs: calls.append((method_name, kwargs)),
    )

    result = runner.invoke(
        negative_keywords.app,
        ["delete", "--id", "negative-123", "--ad-account", "account-123"],
    )

    assert result.exit_code == 0
    assert '"sdk_method": "negative_keywords_id_delete"' in result.stdout
    assert '"mutation": "delete"' in result.stdout
    assert calls == []


def test_shared_budget_context_options_match_manifest():
    get_help = runner.invoke(shared_budgets.app, ["get", "--help"])
    create_help = runner.invoke(shared_budgets.app, ["create", "--help"])

    assert get_help.exit_code == 0
    assert "--ad-account" in get_help.stdout
    assert create_help.exit_code == 0
    assert "--ad-account" not in create_help.stdout
    assert "--file" in create_help.stdout
    assert "--confirm" in create_help.stdout


def test_manifest_adapter_rejects_duplicate_or_wrong_family_methods():
    with pytest.raises(ValueError, match="Duplicate SDK method"):
        specs_from_manifest(
            resource_family="ads",
            sdk_methods=("ads_id_get", "ads_id_get"),
            command_names={"ads_id_get": "get"},
        )

    with pytest.raises(ValueError, match="belongs to ads"):
        specs_from_manifest(
            resource_family="keywords",
            sdk_methods=("ads_id_get",),
            command_names={"ads_id_get": "get"},
        )


def test_manifest_adapter_preserves_repeated_query_parameter_types():
    search_apps = specs_from_manifest(
        resource_family="apps",
        sdk_methods=("search_apps",),
        command_names={"search_apps": "search"},
    )[0]
    store_fronts = next(
        parameter for parameter in search_apps.parameters if parameter.name == "store_fronts"
    )

    assert store_fronts.annotation == list[str]
    assert store_fronts.required is False
    assert store_fronts.default is None
