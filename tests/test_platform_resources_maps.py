"""Coverage and CLI contracts for Maps and asset Platform API resources."""

from click import unstyle
from typer.testing import CliRunner

from asa_cli.platform.resources import (
    assets,
    business_brands,
    business_categories,
    geos,
    location_groups,
    locations,
)

runner = CliRunner()

MODULES = (
    assets,
    business_brands,
    business_categories,
    geos,
    location_groups,
    locations,
)


def test_maps_resource_modules_cover_assigned_methods_exactly_once():
    methods = [method for module in MODULES for method in module.SDK_METHODS]
    specs = [spec for module in MODULES for spec in module.COMMAND_SPECS]

    assert len(methods) == 17
    assert len(methods) == len(set(methods))
    assert {spec.sdk_method for spec in specs} == set(methods)
    assert len(specs) == len(methods)


def test_search_geos_exposes_required_supply_source_and_enum_filter():
    result = runner.invoke(geos.app, ["search", "--help"])

    assert result.exit_code == 0
    help_text = unstyle(result.stdout)
    assert "--supply-source" in help_text
    assert "required" in help_text.lower()
    assert "--entity" in help_text
    assert "--ad-account" in help_text


def test_asset_upload_has_explicit_multipart_parameters_and_safety_gate(
    monkeypatch,
    tmp_path,
):
    calls = []
    asset_file = tmp_path / "brand.png"
    asset_file.write_bytes(b"\x89PNG\r\n\x1a\n\x00\x00\x00\x0d")
    monkeypatch.setattr(
        "asa_cli.platform.command_factory.invoke",
        lambda method_name, **kwargs: calls.append((method_name, kwargs)) or {"sent": True},
    )

    help_result = runner.invoke(assets.app, ["upload", "--help"])
    preview = runner.invoke(
        assets.app,
        [
            "upload",
            "--file",
            str(asset_file),
            "--promoted-object-id",
            "brand-1",
            "--promoted-object-type",
            "BUSINESS_BRAND",
            "--ad-account",
            "123",
        ],
    )

    assert help_result.exit_code == 0
    help_text = unstyle(help_result.stdout)
    assert "--file" in help_text
    assert "--promoted-object-id" in help_text
    assert "--promoted-object-type" in help_text
    assert "--confirm" in help_text
    assert preview.exit_code == 0
    assert '"sdk_method": "upload_asset"' in preview.stdout
    assert "Mutation not sent" in preview.stderr
    assert calls == []


def test_asset_upload_rejects_missing_file_before_preview():
    result = runner.invoke(
        assets.app,
        [
            "upload",
            "--file",
            "/definitely/missing/brand.png",
            "--promoted-object-id",
            "brand-1",
            "--promoted-object-type",
            "BUSINESS_BRAND",
            "--ad-account",
            "123",
        ],
    )

    assert result.exit_code == 2
    stderr = unstyle(result.stderr)
    assert "Invalid value for '--file'" in stderr
    assert "/definitely/missing/brand.png" in stderr


def test_asset_upload_rejects_unrecognized_file_content(tmp_path):
    asset_file = tmp_path / "not-an-image.png"
    asset_file.write_text("not an image", encoding="utf-8")

    result = runner.invoke(
        assets.app,
        [
            "upload",
            "--file",
            str(asset_file),
            "--promoted-object-id",
            "brand-1",
            "--promoted-object-type",
            "BUSINESS_BRAND",
            "--ad-account",
            "123",
        ],
    )

    assert result.exit_code == 1
    assert "PNG, JPEG, HEIC" in result.stderr
