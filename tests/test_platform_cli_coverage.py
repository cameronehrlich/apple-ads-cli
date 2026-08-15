"""End-to-end completeness gates for the default Platform API command surface."""

import inspect
import json

from typer.main import get_command

from asa_cli.main import app
from asa_cli.platform.cli import PLATFORM_RESOURCES
from asa_cli.platform.command_factory import build_callback
from asa_cli.platform.manifest_specs import MANIFEST_PATH


def test_default_cli_covers_all_99_manifest_methods_exactly_once():
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    manifest_methods = {operation["sdk_method"] for operation in manifest["operations"]}
    registered_methods = [
        method
        for _name, module, _help in PLATFORM_RESOURCES
        for method in module.SDK_METHODS
    ]
    registered_specs = [
        spec
        for _name, module, _help in PLATFORM_RESOURCES
        for spec in module.COMMAND_SPECS
    ]

    assert manifest["sdk"]["canonical_method_count"] == 99
    assert len(manifest_methods) == 99
    assert len(registered_methods) == 99
    assert len(set(registered_methods)) == 99
    assert set(registered_methods) == manifest_methods
    assert {spec.sdk_method for spec in registered_specs} == manifest_methods


def test_every_resource_family_is_registered_at_the_root():
    root_command = get_command(app)
    resource_names = {name for name, _module, _help in PLATFORM_RESOURCES}

    assert len(resource_names) == 24
    assert resource_names <= set(root_command.commands)
    assert "v5" in root_command.commands


def test_command_paths_are_unique_within_each_resource():
    paths = [
        (name, spec.name)
        for name, module, _help in PLATFORM_RESOURCES
        for spec in module.COMMAND_SPECS
    ]

    assert len(paths) == 99
    assert len(set(paths)) == 99


def test_every_mutation_has_preview_and_confirmation_options():
    for _name, module, _help in PLATFORM_RESOURCES:
        for spec in module.COMMAND_SPECS:
            parameters = inspect.signature(build_callback(spec)).parameters
            if spec.mutation == "read":
                assert "dry_run" not in parameters
                assert "confirm" not in parameters
            else:
                assert "dry_run" in parameters
                assert "confirm" in parameters
