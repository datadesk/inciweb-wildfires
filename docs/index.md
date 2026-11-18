# inciweb-wildfires

Download wildfire incidents data from [InciWeb](https://inciweb.nwcg.gov/).

```{contents} Table of contents
:local:
:depth: 2
```

## Installation

```sh
uv add inciweb-wildfires
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
inciwebwildfires prescribed-fires
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
make install
```

Run tests.

```sh
make check
```

## Links

* Docs: [palewi.re/docs/inciweb-wildfires/](https://palewi.re/docs/inciweb-wildfires/)
* Issues: [github.com/datadesk/inciweb-wildfires/issues](https://github.com/datadesk/inciweb-wildfires/issues)
* Packaging: [pypi.python.org/pypi/inciweb-wildfires](https://pypi.python.org/pypi/inciweb-wildfires)
* Testing: [github.com/datadesk/inciweb-wildfires/actions](https://github.com/datadesk/inciweb-wildfires/actions)
