"""Tests for the Platform API configuration command surface."""

from typer.testing import CliRunner

from asa_cli.platform.config_cli import app
from asa_cli.platform.runtime import PlatformAPIError

runner = CliRunner()


def test_platform_config_test_uses_context_free_get_me(monkeypatch):
    calls = []

    def fake_invoke(method_name, **kwargs):
        calls.append((method_name, kwargs))
        return {"data": {"id": "user-1"}}

    monkeypatch.setattr("asa_cli.platform.config_cli.invoke", fake_invoke)

    result = runner.invoke(app, ["test"])

    assert result.exit_code == 0
    assert '"connection": "ok"' in result.stdout
    assert '"sdkMethod": "get_me"' in result.stdout
    assert "user-1" not in result.stdout
    assert calls == [("get_me", {"context": "none"})]


def test_platform_config_test_returns_structured_error(monkeypatch):
    def fail(*args, **kwargs):
        raise PlatformAPIError("authentication failed", status=401, body={"code": "UNAUTHORIZED"})

    monkeypatch.setattr("asa_cli.platform.config_cli.invoke", fail)

    result = runner.invoke(app, ["test"])

    assert result.exit_code == 1
    assert "authentication failed" in result.stderr
    assert '"status": 401' in result.stderr
