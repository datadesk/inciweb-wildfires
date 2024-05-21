import click

from inciweb_wildfires import get_incidents, get_prescribed_fires


@click.group()
def cmd():
    """
    A command-line interface for downloading wildfire incidents data from InciWeb.

    Returns GeoJSON.
    """
    pass


@cmd.command(help="Download active fire incidents from InciWeb")
def incidents():
    click.echo(get_incidents())


@cmd.command(help="Download prescribed fire incidents from InciWeb")
def prescribed_fires():
    click.echo(get_prescribed_fires())


if __name__ == "__main__":
    cmd()
