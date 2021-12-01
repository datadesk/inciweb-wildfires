Download wildfire incidents data from [InciWeb](https://inciweb.nwcg.gov/).

Hourly scrapes powered by a GitHub Action are stored in the `data` directory.

## Installation

```sh
pipenv install inciweb-wildfires
```

## Command-line usage

```sh
Usage: inciwebwildfires [OPTIONS] COMMAND [ARGS]...

  A command-line interface for downloading wildfire incidents data from InciWeb.

  Returns GeoJSON.

Options:
  --help  Show this message and exit.

Commands:
  incidents  Download active fire incidents from InciWeb
```

Download active fire incidents from inciweb.

```sh
inciwebwildfires incidents
```

## Python usage

Import the library.

```python
>>> import inciweb_wildfires
```

Download a GeoJSON of active fire incidents.

```python
>>> data = inciweb_wildfires.get_incidents()
```

## Contributing

Install dependencies for development.

```sh
pipenv install --dev
```

Run tests.

```sh
make test
```

Shipping new version to PyPI. ::

```sh
make ship
```

## Developing the CLI

The command-line interface is implemented using Click and setuptools. To install it locally for development inside your virtual environment, run the following installation command, as `prescribed by the Click documentation <https://click.palletsprojects.com/en/7.x/setuptools/#setuptools-integration>`_. ::

```sh
pip install --editable .
```
