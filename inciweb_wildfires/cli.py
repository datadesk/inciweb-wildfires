import click
from inciweb_wildfires import get_fires


@click.group()
def cmd():
    """
    A command-line interface for downloading wildfire data from inciweb.
    Returns GeoJSON.
    """
    pass


@cmd.command(help="Get active fire data from inciweb")
def fires():
    click.echo(get_fires())


if __name__ == '__main__':
    cmd()
