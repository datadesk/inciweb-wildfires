# inciweb-wildfires

Download wildfire incidents from [InciWeb](https://inciweb.wildfire.gov/), the interagency incident information system, as GeoJSON or typed Python records.

```{contents} Table of contents
:local:
:depth: 2
```

## Read this first

**An incident on InciWeb is an information page that fire agencies write and update. It is not a measurement, and it is not the final word.**

* InciWeb describes itself as "an interagency all-risk incident information management system" built to give the public "a single source of incident related information".
* InciWeb also calls itself "a standardized reporting tool for the Public Affairs community", so the information is posted by the agencies, not measured by InciWeb. The size and the percent contained are what an agency reported, they change as the incident goes on, and a page can lag behind events.
* InciWeb is not the only source, and it can differ from others, such as satellite detections, state agencies or the national fire reporting system. Check a figure against another source before you rely on it.
* We could not verify which fires get a page, so do not treat this list as a count of every fire.

InciWeb's own disclaimer, quoted from [its About page](https://inciweb.wildfire.gov/about), says:

> Information posted on this website is for information purposes only. For official information, contact the Wildfire Agency in the local area.

This package is not run by InciWeb, the agencies that post to it or the federal government. It only downloads what InciWeb publishes. We did not find a separate terms of use or a credit line on InciWeb's website. When you publish a figure, say it came from InciWeb and name the agency or unit in charge, which is in the `unit_code` field.

## Installation

```bash
uv add inciweb-wildfires
```

Python 3.11 or newer is required.

## Quick start

From the shell, print GeoJSON for the active wildfires.

```bash
inciweb-wildfires incidents > incidents.json
```

From Python, ask for typed records and read their fields.

```python
import inciweb_wildfires

for incident in inciweb_wildfires.get_incident_records("Wildfire"):
    print(incident.title, incident.size, incident.percent_contained, incident.url)
```

## Command-line usage

```text
Usage: inciweb-wildfires [OPTIONS] COMMAND [ARGS]...

  A command-line interface for downloading wildfire incidents data from
  InciWeb.

  Returns GeoJSON.

Options:
  --help  Show this message and exit.

Commands:
  incidents         Download active fire incidents from InciWeb
  prescribed-fires  Download prescribed fire incidents from InciWeb
```

The command can also be run as `inciwebwildfires`. The old spelling `prescribed_fires` still works too.

Download the wildfires.

```bash
inciweb-wildfires incidents > incidents.json
```

Download the prescribed fires, which are fires lit on purpose to manage land.

```bash
inciweb-wildfires prescribed-fires > prescribed.json
```

Both commands take two options.

| Option | What it does |
| --- | --- |
| `--timeout SECONDS` | How long to wait for InciWeb on each try. The default is 60. |
| `--verbose` | Print each request to the error stream (stderr). The GeoJSON on standard output stays clean, so you can still save it to a file. |

If InciWeb cannot be reached, or answers with an error, the command prints one line that starts with `Error:` and exits with code 1.

## Python usage

Import the library.

```python
import inciweb_wildfires
```

Download a GeoJSON of the wildfires. Each point is an incident, and its properties are InciWeb's own fields, all as text.

```python
data = inciweb_wildfires.get_incidents()
```

Download the prescribed fires.

```python
data = inciweb_wildfires.get_prescribed_fires()
```

Or ask for typed records, where numbers are numbers and the creation time is a real date and time in UTC. Pass `"Wildfire"` or `"Prescribed Fire"` to keep one type, or nothing to keep every type InciWeb sends.

```python
records = inciweb_wildfires.get_incident_records("Wildfire")
print(records[0].title, records[0].created_at)
```

### Waiting and retrying

Every download function takes `timeout` (seconds, 60 by default) and `verbose` (print each request to stderr). A download is tried again, up to four tries in all, when InciWeb cannot be reached, takes too long, or answers with a server error or "too many requests". If it still fails, the package raises `inciweb_wildfires.InciWebError`, which has `url` and `status_code` attributes. If the data arrives but cannot be read, it raises `inciweb_wildfires.InciWebDataError`, which is also a `ValueError`.

```python
try:
    data = inciweb_wildfires.get_incidents(timeout=30)
except inciweb_wildfires.InciWebError as error:
    print("Could not get InciWeb:", error)
```

### Use your own request function

If your project sends every web request through its own helper, pass it as `get`. It is called like `get(url, timeout=seconds)` and must return something with a `status_code` and the `content` as bytes. The timeout and the retries still work, and failures still raise `InciWebError`.

```python
import requests

import inciweb_wildfires
from inciweb_wildfires import Reply


def my_get(url: str, *, timeout: float) -> Reply:
    print("Asking for", url)
    return requests.get(url, timeout=timeout, headers={"User-Agent": "my-project"})


data = inciweb_wildfires.get_incidents(get=my_get)
```

The `Fetcher` and `Reply` types describe this, so a type checker can confirm your function fits. If your function raises one of the `requests` library's errors, the package tries again, just as it does for its own requests. Any other error is passed on to you.

## Field reference

`get_incident_records` returns `Incident` records. The GeoJSON functions keep InciWeb's original names and text, shown in the last column. We compared these against a real download from InciWeb and against an incident's web page.

| Record field | InciWeb's field | What it is |
| --- | --- | --- |
| `id` | `id` | InciWeb's number for the incident. |
| `title` | `title` | The incident's name, such as "Babylon Fire". |
| `unit_code` | `field_unit_code` | The code of the agency unit in charge, such as `UTMLF`. |
| `unit_title` | `field_title_and_unit` | The unit code and the name together, as InciWeb shows them. |
| `incident_type` | `type` | "Wildfire" or "Prescribed Fire". InciWeb's map can also show "Burned Area Response" and "Other". |
| `is_active` | `field_active` | True if InciWeb marks the incident active. |
| `longitude`, `latitude` | `long_deg`, `long_min`, `long_sec`, `lat_deg`, `lat_min`, `lat_sec` | The point InciWeb shows, turned into decimal degrees. InciWeb writes every longitude as a positive number, so the package makes it negative. |
| `size` | `size` | How big the incident is. None when the agency left it blank, which happens, for example, on some prescribed fires. |
| `size_unit` | `measurement_type` | The unit for the size, almost always "Acres". |
| `percent_contained` | `field_percent_of_perimeter` | The share of the fire's edge that is contained, 0 to 100. InciWeb's page calls it "Percent of Perimeter Contained". None when blank. |
| `created_at` | `created` | When the InciWeb page was created, in UTC. This is not when the fire started. |
| `changed` | `changed` | When the page was last changed, in InciWeb's words, such as "1 day 20 hours ago". It is relative to the moment of download, so it is kept as text. |
| `path`, `url` | `urlPath` | The incident's page on InciWeb. |
| `description` | `field_incident_description` | A short description. It can contain HTML and is often blank. |
| `overview_html` | `field_incident_overview` | The incident overview, as HTML. |

The map data does not include the cause, the number of people working the fire or the date the fire started. They are on each incident's own page.

## Working on the code

The tests do not need the internet. They read a small saved sample of InciWeb's data from `tests/data`. A separate set of tests that call the real website only runs when you ask for it with `make test-live`.

```bash
make install     # install everything for development
make check       # lint, type check and offline tests
make test-live   # call InciWeb's real website
make build       # build the package without uploading it
```

This repository's scraped data files are saved in its history, so copy only the latest version:

```bash
git clone --depth 1 https://github.com/datadesk/inciweb-wildfires.git
```

## Links

* Docs: [palewi.re/docs/inciweb-wildfires/](https://palewi.re/docs/inciweb-wildfires/)
* Issues: [github.com/datadesk/inciweb-wildfires/issues](https://github.com/datadesk/inciweb-wildfires/issues)
* Packaging: [pypi.python.org/pypi/inciweb-wildfires](https://pypi.python.org/pypi/inciweb-wildfires)
* Testing: [github.com/datadesk/inciweb-wildfires/actions](https://github.com/datadesk/inciweb-wildfires/actions)
