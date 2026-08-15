"""CLI coverage for multi-app configuration and the root app override."""

from unittest.mock import patch

from typer.testing import CliRunner

from asa_cli.commands import config as config_commands
from asa_cli.config import AppConfig, MultiAppConfig
from asa_cli.main import app as root_app

runner = CliRunner()


def app_config(app_id: int, name: str) -> AppConfig:
    return AppConfig(
        app_id=app_id,
        app_name=name,
        default_countries=["US"],
        default_bid=1.5,
    )


def test_add_app_saves_new_app_and_selects_the_first_app():
    multi = MultiAppConfig()
    stitch_it = app_config(554594252, "Stitch It")

    with (
        patch.object(config_commands, "prompt_for_app_config", return_value=stitch_it),
        patch.object(config_commands, "load_multi_app_config", return_value=multi),
        patch.object(config_commands, "save_multi_app_config") as save,
    ):
        result = runner.invoke(config_commands.app, ["add-app"])

    assert result.exit_code == 0, result.output
    saved = save.call_args.args[0]
    assert saved.active_app == "stitchit"
    assert saved.apps == {"stitchit": stitch_it}


def test_list_apps_reports_all_apps_and_active_selection():
    multi = MultiAppConfig(
        active_app="stitchit",
        apps={
            "stitchit": app_config(554594252, "Stitch It"),
            "faxit": app_config(1534309058, "Fax It"),
        },
    )

    with patch.object(config_commands, "load_multi_app_config", return_value=multi):
        result = runner.invoke(config_commands.app, ["list-apps"])

    assert result.exit_code == 0, result.output
    assert "Stitch It" in result.output
    assert "Fax It" in result.output
    assert "Active app: stitchit" in result.output


def test_switch_app_persists_requested_selection():
    multi = MultiAppConfig(
        active_app="stitchit",
        apps={
            "stitchit": app_config(554594252, "Stitch It"),
            "faxit": app_config(1534309058, "Fax It"),
        },
    )

    with (
        patch.object(config_commands, "load_multi_app_config", return_value=multi),
        patch.object(config_commands, "save_multi_app_config") as save,
    ):
        result = runner.invoke(config_commands.app, ["switch", "faxit"])

    assert result.exit_code == 0, result.output
    assert save.call_args.args[0].active_app == "faxit"


def test_remove_active_app_selects_remaining_app_without_prompt():
    multi = MultiAppConfig(
        active_app="stitchit",
        apps={
            "stitchit": app_config(554594252, "Stitch It"),
            "faxit": app_config(1534309058, "Fax It"),
        },
    )

    with (
        patch.object(config_commands, "load_multi_app_config", return_value=multi),
        patch.object(config_commands, "save_multi_app_config") as save,
    ):
        result = runner.invoke(config_commands.app, ["remove-app", "stitchit", "--force"])

    assert result.exit_code == 0, result.output
    saved = save.call_args.args[0]
    assert saved.active_app == "faxit"
    assert set(saved.apps) == {"faxit"}


def test_root_app_option_reaches_the_global_app_selector():
    with patch("asa_cli.main.set_current_app") as select_app:
        result = runner.invoke(root_app, ["--app", "stitchit", "version"])

    assert result.exit_code == 0, result.output
    select_app.assert_called_once_with("stitchit")
