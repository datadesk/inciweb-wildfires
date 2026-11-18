# inciweb-wildfires

Download wildfire incidents from [InciWeb](https://inciweb.wildfire.gov/), the interagency incident information system, as GeoJSON or typed Python records.

**An incident on InciWeb is an information page that fire agencies post and update.** It can lag behind events or differ from other sources, and its figures, such as size and percent contained, are what an agency reported and they change. InciWeb's own disclaimer says: "Information posted on this website is for information purposes only. For official information, contact the Wildfire Agency in the local area."

## Install

```sh
uv add inciweb-wildfires
```

## Use it from the command line

```sh
inciweb-wildfires incidents > incidents.json
inciweb-wildfires prescribed-fires --timeout 30
```

`incidents` gives wildfires and `prescribed-fires` gives fires lit on purpose. Both take `--timeout` and `--verbose`, and `--verbose` writes to stderr so the JSON stays clean.

## Use it from Python

```python
import inciweb_wildfires

data = inciweb_wildfires.get_incidents()  # GeoJSON
records = inciweb_wildfires.get_incident_records("Wildfire")  # typed records
print(records[0].title, records[0].size, records[0].percent_contained)
```

## Use your own request function

Pass a helper as `get` to send the web request your own way. It is called like `get(url, timeout=seconds)` and must return something with a `status_code` and `content` as bytes. The `Fetcher` and `Reply` types are exported so a type checker can check yours. The timeout and retries still work.

```python
import requests

import inciweb_wildfires
from inciweb_wildfires import Reply


def my_get(url: str, *, timeout: float) -> Reply:
    return requests.get(url, timeout=timeout, headers={"User-Agent": "my-project"})


data = inciweb_wildfires.get_incidents(get=my_get)
```

## Working on the code

This repository's scraped data files are saved in its history, so copy only the latest version:

```bash
git clone --depth 1 https://github.com/datadesk/inciweb-wildfires.git
make install
make check
```

The tests run offline against a small saved sample. `make check` also measures test coverage and fails if it drops under 95 percent, counting branches as well as lines. `make test-fast` skips the coverage step. `make test-live` calls the real InciWeb.

## Things to know

* **Incidents are agency reports.** The documentation explains each field and what it does not tell you.
* **Downloads retry.** A request waits 60 seconds, then tries again on network errors and server errors, and raises `inciweb_wildfires.InciWebError` if it still fails.
* **The data comes from InciWeb.** This package is not run by InciWeb or the agencies that post to it.
* **AI helped write this package.** AI tools assisted in writing its code, tests and documentation. A person directed and reviewed the work.

The documentation has the full field reference.

### Links

* Docs: [palewi.re/docs/inciweb-wildfires/](https://palewi.re/docs/inciweb-wildfires/)
* Issues: [github.com/datadesk/inciweb-wildfires/issues](https://github.com/datadesk/inciweb-wildfires/issues)
* Packaging: [pypi.python.org/pypi/inciweb-wildfires](https://pypi.python.org/pypi/inciweb-wildfires)
* Testing: [github.com/datadesk/inciweb-wildfires/actions](https://github.com/datadesk/inciweb-wildfires/actions)
