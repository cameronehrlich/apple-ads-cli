"""Coverage tests for core Platform API resource command registries."""

from __future__ import annotations

from typer.testing import CliRunner

from asa_cli.platform.manifest_specs import load_manifest
from asa_cli.platform.resources import access, ad_accounts, ad_groups, apps, campaigns

runner = CliRunner()

RESOURCE_MODULES = {
    "access": access,
    "ad-accounts": ad_accounts,
    "apps": apps,
    "campaigns": campaigns,
    "ad-groups": ad_groups,
}

EXPECTED_METHODS = {
    "access": {
        "get_advertiser_resources",
        "orgs_id_get",
        "get_me",
        "get_user_acls",
    },
    "ad-accounts": {
        "ad_accounts_id_get",
        "ad_accounts_post",
        "ad_accounts_id_put",
    },
    "apps": {
        "get_app_details_by_adam_id",
        "search_apps",
        "eligibilities_apps_query_post",
        "query_app_locale_details",
        "query_supported_app_languages",
    },
    "campaigns": {
        "campaigns_id_get",
        "campaigns_query_post",
        "campaigns_post",
        "campaigns_id_put",
        "campaigns_id_delete",
        "campaigns_id_legacy_app_limited_status_reason_details_get",
    },
    "ad-groups": {
        "adgroups_id_get",
        "adgroups_query_post",
        "adgroups_post",
        "adgroups_id_put",
        "adgroups_id_delete",
    },
}


def test_core_resource_files_cover_their_manifest_families_exactly():
    manifest_methods = {
        family: {
            operation["sdk_method"]
            for operation in load_manifest()["operations"]
            if operation["resource_family"] == family
        }
        for family in RESOURCE_MODULES
    }

    assert manifest_methods == EXPECTED_METHODS
    for family, module in RESOURCE_MODULES.items():
        assert set(module.SDK_METHODS) == EXPECTED_METHODS[family]


def test_core_resource_registries_cover_23_unique_methods_once():
    methods = [
        method
        for module in RESOURCE_MODULES.values()
        for method in module.SDK_METHODS
    ]

    assert len(methods) == len(set(methods)) == 23


def test_each_resource_exposes_one_command_per_declared_method():
    for module in RESOURCE_MODULES.values():
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


def test_every_core_resource_command_has_renderable_help():
    for module in RESOURCE_MODULES.values():
        result = runner.invoke(module.app, ["--help"])
        assert result.exit_code == 0, result.output
        for command_name in module.COMMAND_NAMES.values():
            result = runner.invoke(module.app, [command_name, "--help"])
            assert result.exit_code == 0, result.output


def test_access_and_app_query_parameters_are_derived_from_the_manifest():
    access_specs = {spec.sdk_method: spec for spec in access.COMMAND_SPECS}
    advertiser_resources = access_specs["get_advertiser_resources"]
    assert advertiser_resources.context == "none"
    assert advertiser_resources.parameters[0].name == "resource_type"
    assert advertiser_resources.parameters[0].required is True

    app_specs = {spec.sdk_method: spec for spec in apps.COMMAND_SPECS}
    app_search = app_specs["search_apps"]
    store_fronts = next(
        parameter
        for parameter in app_search.parameters
        if parameter.name == "store_fronts"
    )
    assert store_fronts.annotation == list[str]
    assert store_fronts.required is False


def test_mutation_and_context_metadata_reaches_command_specs():
    ad_account_specs = {spec.sdk_method: spec for spec in ad_accounts.COMMAND_SPECS}
    assert ad_account_specs["ad_accounts_post"].context == "none"
    assert ad_account_specs["ad_accounts_post"].mutation == "create"
    assert ad_account_specs["ad_accounts_id_put"].mutation == "update"

    campaign_specs = {spec.sdk_method: spec for spec in campaigns.COMMAND_SPECS}
    assert campaign_specs["campaigns_query_post"].mutation == "read"
    assert campaign_specs["campaigns_id_delete"].mutation == "delete"
    assert all(spec.context == "required" for spec in campaign_specs.values())
