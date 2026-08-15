"""Read exact public command contracts from the registered Typer trees."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import click
from typer.main import get_command


def _display_default(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, (str, int, float, bool)):
        return str(value)
    if isinstance(value, (list, tuple)):
        return ",".join(map(str, value))
    return repr(value)


@dataclass(frozen=True)
class RuntimeParameter:
    kind: str
    name: str
    declarations: tuple[str, ...]
    required: bool
    type_name: str
    default: str | None
    envvar: str | None
    help: str


@dataclass(frozen=True)
class RuntimeCommand:
    path: str
    usage: str
    help: str
    parameters: tuple[RuntimeParameter, ...]
    sdk_method: str | None = None
    resource: str | None = None

    @property
    def searchable_text(self) -> str:
        parameter_text = " ".join(
            " ".join((*parameter.declarations, parameter.name, parameter.help))
            for parameter in self.parameters
        )
        return f"{self.path} {self.help} {parameter_text}".lower()


def _runtime_parameter(parameter: click.Parameter) -> RuntimeParameter:
    if isinstance(parameter, click.Option):
        declarations = (*parameter.opts, *parameter.secondary_opts)
        help_text = parameter.help or ""
        envvar_value = parameter.envvar
        envvar = ",".join(envvar_value) if isinstance(envvar_value, list) else envvar_value
        kind = "option"
    else:
        declarations = (parameter.human_readable_name,)
        help_text = ""
        envvar = parameter.envvar
        kind = "argument"
    type_name = getattr(parameter.type, "name", None) or str(parameter.type)
    if parameter.multiple:
        type_name = f"list[{type_name}]"
    return RuntimeParameter(
        kind=kind,
        name=parameter.name or parameter.human_readable_name,
        declarations=declarations,
        required=bool(parameter.required),
        type_name=type_name,
        default=_display_default(parameter.default),
        envvar=envvar,
        help=help_text,
    )


def _runtime_command(
    command: click.Command,
    *,
    path: str,
    sdk_method: str | None = None,
    resource: str | None = None,
) -> RuntimeCommand:
    context = click.Context(command, info_name=path)
    usage = command.get_usage(context).strip()
    parameters = list(command.params)
    help_option = command.get_help_option(context)
    if help_option is not None:
        parameters.append(help_option)
    return RuntimeCommand(
        path=path,
        usage=usage,
        help=command.help or command.short_help or "",
        parameters=tuple(_runtime_parameter(parameter) for parameter in parameters),
        sdk_method=sdk_method,
        resource=resource,
    )


def platform_registrations() -> dict[str, RuntimeCommand]:
    """Map every canonical SDK method to its default public v1 command."""
    from asa_cli.platform.cli import PLATFORM_RESOURCES

    registrations: dict[str, RuntimeCommand] = {}
    command_paths: set[str] = set()
    for resource, module, _help_text in PLATFORM_RESOURCES:
        group = get_command(module.app)
        if not isinstance(group, click.Group):
            raise ValueError(f"Platform resource is not a command group: {resource}")
        command_names = module.COMMAND_NAMES
        if set(command_names) != set(module.SDK_METHODS):
            raise ValueError(f"Platform command names do not cover {resource} exactly")
        for sdk_method in module.SDK_METHODS:
            if sdk_method in registrations:
                raise ValueError(f"Duplicate Platform SDK registration: {sdk_method}")
            command_name = command_names[sdk_method]
            command = group.commands.get(command_name)
            if command is None:
                raise ValueError(
                    f"Platform command is not registered: {resource} {command_name}"
                )
            path = f"asa {resource} {command_name}"
            if path in command_paths:
                raise ValueError(f"Duplicate Platform command path: {path}")
            command_paths.add(path)
            registrations[sdk_method] = _runtime_command(
                command,
                path=path,
                sdk_method=sdk_method,
                resource=resource,
            )
    return registrations


def _leaf_commands(command: click.Command, *, prefix: str) -> list[RuntimeCommand]:
    if isinstance(command, click.Group) and command.commands:
        leaves: list[RuntimeCommand] = []
        for name, child in sorted(command.commands.items()):
            if child.hidden:
                continue
            leaves.extend(_leaf_commands(child, prefix=f"{prefix} {name}"))
        return leaves
    if command.hidden:
        return []
    return [_runtime_command(command, path=prefix)]


def v5_commands() -> tuple[RuntimeCommand, ...]:
    """Return every public command leaf under the frozen ``asa v5`` tree."""
    from asa_cli.v5.cli import app

    commands = tuple(_leaf_commands(get_command(app), prefix="asa v5"))
    paths = [command.path for command in commands]
    if len(paths) != len(set(paths)):
        raise ValueError("Duplicate public v5 command path")
    return commands


def workflow_commands() -> tuple[RuntimeCommand, ...]:
    """Return optional future ``asa workflows`` commands when that tree exists."""
    try:
        from asa_cli.workflows.cli import app
    except ImportError:
        return ()
    commands = tuple(_leaf_commands(get_command(app), prefix="asa workflows"))
    paths = [command.path for command in commands]
    if len(paths) != len(set(paths)):
        raise ValueError("Duplicate public workflow command path")
    return commands


def search_runtime_commands(
    commands: tuple[RuntimeCommand, ...], query: str
) -> list[RuntimeCommand]:
    normalized_query = query.lower().replace("-", " ").replace("_", " ")
    tokens = [token for token in normalized_query.split() if token]
    scored: list[tuple[int, RuntimeCommand]] = []
    for command in commands:
        corpus = command.searchable_text.replace("-", " ").replace("_", " ")
        if normalized_query in corpus:
            score = 100 + len(tokens)
        else:
            matched = sum(token in corpus for token in tokens)
            if not matched:
                continue
            score = matched * 10 - (len(tokens) - matched) * 3
        scored.append((score, command))
    if not scored:
        return []
    best = max(score for score, _command in scored)
    return [command for score, command in scored if score == best]
