"""The inciweb-wildfires command-line interface."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import click

from inciweb_wildfires import InciWebError, get_incidents, get_prescribed_fires
from inciweb_wildfires.fetch import DEFAULT_TIMEOUT


def _common_options(func: Callable[..., Any]) -> Callable[..., Any]:
    """Add the options both download commands share.

    Args:
        func: The click command function to decorate.

    Returns:
        The same function with the timeout and verbose options attached.
    """
    decorators = [
        click.option(
            "--timeout",
            default=DEFAULT_TIMEOUT,
            show_default=True,
            type=click.FloatRange(min=1),
            help="Seconds to wait for InciWeb on each try",
        ),
        click.option("--verbose", is_flag=True, help="Print each request to stderr"),
    ]
    for decorator in reversed(decorators):
        func = decorator(func)
    return func


@click.group()
def cmd():
    """
    A command-line interface for downloading wildfire incidents data from InciWeb.

    Returns GeoJSON.
    """
    pass


@cmd.command(help="Download active fire incidents from InciWeb")
@_common_options
def incidents(timeout, verbose):
    try:
        data = get_incidents(verbose=verbose, timeout=timeout)
    except InciWebError as error:
        raise click.ClickException(str(error)) from error
    click.echo(data)


@cmd.command(help="Download prescribed fire incidents from InciWeb")
@_common_options
def prescribed_fires(timeout, verbose):
    try:
        data = get_prescribed_fires(verbose=verbose, timeout=timeout)
    except InciWebError as error:
        raise click.ClickException(str(error)) from error
    click.echo(data)


# The old documentation spelled this command with an underscore, which Click
# 7 and newer no longer accepts on its own. Keep that spelling working.
cmd.add_command(prescribed_fires, name="prescribed_fires")


if __name__ == "__main__":
    cmd()
