# inciweb-wildfires

Download wildfire incidents data from [InciWeb](https://inciweb.nwcg.gov/).

```{contents} Table of contents
:local:
:depth: 2
```

## Installation

```sh
pipenv install inciweb-wildfires
```

## Command-line usage

```sh
Usage: inciweb-wildfires [OPTIONS] COMMAND [ARGS]...

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

Download prescribed fire incidents from inciweb.
```sh
inciwebwildfires prescribed_fires
```


## Python usage

Import the library.

```python
import inciweb_wildfires
```

Download a GeoJSON of active fire incidents.

```python
data = inciweb_wildfires.get_incidents()
```

## Contributing

Install dependencies for development.

```sh
pipenv install --dev
```

Run tests.

```sh
pipenv run python test.py
```

## Developing the CLI

The command-line interface is implemented using Click and setuptools. To install it locally for development inside your virtual environment, run the following installation command, as [prescribed by the Click documentation](https://click.palletsprojects.com/en/7.x/setuptools/#setuptools-integration).

```sh
pipenv run pip install --editable .
```

## Links

* Docs: [palewi.re/docs/inciweb-wildfires/](https://palewi.re/docs/inciweb-wildfires/)
* Issues: [github.com/datadesk/inciweb-wildfires/issues](https://github.com/datadesk/inciweb-wildfires/issues)
* Packaging: [pypi.python.org/pypi/inciweb-wildfires](https://pypi.python.org/pypi/inciweb-wildfires)
* Testing: [github.com/datadesk/inciweb-wildfires/actions](https://github.com/datadesk/inciweb-wildfires/actions)
