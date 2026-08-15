"""Coverage for Platform reports, insights, recommendations, and audit registries."""

from types import ModuleType

from typer.testing import CliRunner

from asa_cli.platform.manifest_specs import load_manifest
from asa_cli.platform.resources import (
    change_history,
    insights,
    recommendations,
    reports_apps,
    reports_business_brands,
    suggestions,
)

runner = CliRunner()

RESOURCE_MODULES: tuple[tuple[str, ModuleType], ...] = (
    ("reports-apps", reports_apps),
    ("reports-business-brands", reports_business_brands),
    ("insights", insights),
    ("recommendations", recommendations),
    ("suggestions", suggestions),
    ("change-history", change_history),
)


def test_resource_registries_cover_assigned_manifest_methods_exactly_once():
    operations = load_manifest()["operations"]
    registered_methods = []

    for resource_family, module in RESOURCE_MODULES:
        manifest_methods = {
            operation["sdk_method"]
            for operation in operations
            if operation["resource_family"] == resource_family
        }
        assert set(module.SDK_METHODS) == manifest_methods
        assert {spec.sdk_method for spec in module.COMMAND_SPECS} == manifest_methods
        assert len(module.COMMAND_SPECS) == len(module.SDK_METHODS)
        registered_methods.extend(module.SDK_METHODS)

    assert len(registered_methods) == 24
    assert len(set(registered_methods)) == 24


def test_each_module_exposes_one_unique_command_per_sdk_method():
    for _resource_family, module in RESOURCE_MODULES:
        assert set(module.COMMAND_NAMES) == set(module.SDK_METHODS)
        assert [spec.sdk_method for spec in module.COMMAND_SPECS] == list(
            module.SDK_METHODS
        )
        assert {spec.name for spec in module.COMMAND_SPECS} == set(
            module.COMMAND_NAMES.values()
        )
        assert {command.name for command in module.app.registered_commands} == set(
            module.COMMAND_NAMES.values()
        )


def test_report_and_insight_request_models_are_derived_from_manifest():
    app_reports = {spec.sdk_method: spec for spec in reports_apps.COMMAND_SPECS}
    brand_reports = {
        spec.sdk_method: spec for spec in reports_business_brands.COMMAND_SPECS
    }
    insight_specs = {spec.sdk_method: spec for spec in insights.COMMAND_SPECS}

    assert app_reports["apps_campaign_reports"].body.model == "AppsReportingRequest"
    assert (
        brand_reports["brands_search_term_reports"].body.model
        == "BrandsReportingRequest"
    )
    assert (
        insight_specs["impression_share_query"].body.model
        == "ImpressionShareQueryRequest"
    )
    assert (
        insight_specs["search_term_popularity_query"].body.model
        == "SearchTermPopularityQueryRequest"
    )
    assert all(
        spec.context == "required" and spec.mutation == "read"
        for module in (reports_apps, reports_business_brands, insights)
        for spec in module.COMMAND_SPECS
    )


def test_recommendation_mutation_kinds_are_exact():
    specs = {spec.sdk_method: spec for spec in recommendations.COMMAND_SPECS}

    assert specs["query_daily_budget_recommendations"].mutation == "read"
    assert specs["apply_daily_budget_recommendations"].mutation == "apply"
    assert specs["dismiss_daily_budget_recommendations"].mutation == "dismiss"
    assert specs["query_target_cpa_recommendations"].mutation == "read"
    assert specs["apply_target_cpa_recommendations"].mutation == "apply"
    assert specs["dismiss_target_cpa_recommendations"].mutation == "dismiss"


def test_change_detail_parameters_preserve_path_and_pagination_types():
    get_details = next(
        spec
        for spec in change_history.COMMAND_SPECS
        if spec.sdk_method == "get_change_details"
    )

    assert [(parameter.name, parameter.annotation, parameter.required) for parameter in get_details.parameters] == [
        ("detail_id", str, True),
        ("limit", int, False),
        ("offset", int, False),
    ]
    assert get_details.context == "required"
    assert get_details.mutation == "read"


def test_insight_read_command_dispatches_to_exact_sdk_method(monkeypatch):
    calls = []
    monkeypatch.setattr(
        "asa_cli.platform.command_factory.invoke",
        lambda method_name, **kwargs: calls.append((method_name, kwargs)) or {"ok": True},
    )
    monkeypatch.setattr(
        "asa_cli.platform.command_factory.read_json_payload",
        lambda _path: {"timeRange": {"start": "2026-08-02", "end": "2026-08-08", "granularity": "WEEKLY_SUN_SAT"}},
    )
    monkeypatch.setattr(
        "asa_cli.platform.command_factory.hydrate_model",
        lambda model, payload, **_kwargs: {"model": model, "payload": payload},
    )

    result = runner.invoke(
        insights.app,
        [
            "search-term-popularity",
            "--file",
            "request.json",
            "--ad-account",
            "account-123",
        ],
    )

    assert result.exit_code == 0
    assert '"ok": true' in result.stdout
    assert calls == [
        (
            "search_term_popularity_query",
            {
                "arguments": {
                    "search_term_popularity_query_request": {
                        "model": "SearchTermPopularityQueryRequest",
                        "payload": {
                            "timeRange": {
                                "start": "2026-08-02",
                                "end": "2026-08-08",
                                "granularity": "WEEKLY_SUN_SAT",
                            }
                        },
                    }
                },
                "context": "required",
                "ad_account_id": "account-123",
            },
        )
    ]


def test_recommendation_apply_previews_without_invoking(monkeypatch):
    calls = []
    monkeypatch.setattr(
        "asa_cli.platform.command_factory.invoke",
        lambda method_name, **kwargs: calls.append((method_name, kwargs)),
    )
    monkeypatch.setattr(
        "asa_cli.platform.command_factory.read_json_payload",
        lambda _path: {"recommendationIds": ["recommendation-123"]},
    )
    monkeypatch.setattr(
        "asa_cli.platform.command_factory.hydrate_model",
        lambda model, payload, **_kwargs: {"model": model, "payload": payload},
    )

    result = runner.invoke(
        recommendations.app,
        [
            "daily-budget-apply",
            "--file",
            "request.json",
            "--ad-account",
            "account-123",
        ],
    )

    assert result.exit_code == 0
    assert '"sdk_method": "apply_daily_budget_recommendations"' in result.stdout
    assert '"mutation": "apply"' in result.stdout
    assert calls == []
