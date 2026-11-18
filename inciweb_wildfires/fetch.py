"""Download InciWeb's map data."""

from __future__ import annotations

import requests

URL = "https://inciweb.wildfire.gov/api/map_data"
"""Where InciWeb publishes the list of every incident on its map."""


def download_rows() -> list[dict[str, str]]:
    """Download every incident entry on InciWeb's map.

    Returns:
        One dictionary for each entry, exactly as InciWeb sends it. Every value
        is text.

    Raises:
        AssertionError: If InciWeb answers with an error status.

    Examples:
        >>> rows = download_rows()  # doctest: +SKIP
        >>> rows[0]["title"]  # doctest: +SKIP
        'Babylon Fire'
    """
    r = requests.get(URL)
    # Make sure it came back kosher
    if not r.ok:
        raise AssertionError(f"Request failed with status code {r.status_code}")
    return r.json()
