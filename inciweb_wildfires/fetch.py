"""Download InciWeb's map data, with a timeout and retries."""

from __future__ import annotations

import json
import random
import sys
import time

import requests

from .errors import InciWebDataError, InciWebError

URL = "https://inciweb.wildfire.gov/api/map_data"
"""Where InciWeb publishes the list of every incident on its map."""

DEFAULT_TIMEOUT = 60.0
"""How many seconds to wait for InciWeb before giving up on one attempt."""

DEFAULT_TRIES = 4
"""How many times to try before raising an error."""

RETRY_STATUS_CODES = frozenset({408, 429})
"""Statuses worth another try. Every 5xx status is also worth another try."""


def download_rows(
    verbose: bool = False,
    timeout: float = DEFAULT_TIMEOUT,
    tries: int = DEFAULT_TRIES,
) -> list[dict[str, str]]:
    """Download every incident entry on InciWeb's map.

    A download is tried again when InciWeb cannot be reached, takes too long,
    or answers with a server error or "too many requests". The wait before each
    new try doubles, starting at 2 seconds. Any other bad status, such as "not
    found", fails right away.

    Args:
        verbose: Print each request to standard error. Defaults to False.
        timeout: Seconds to wait for InciWeb on each try. Defaults to 60.
        tries: How many tries to make in all. Defaults to 4.

    Returns:
        One dictionary for each entry, exactly as InciWeb sends it. Every value
        is text.

    Raises:
        InciWebError: If every try fails, or InciWeb answers with a status that
            is not worth trying again.
        InciWebDataError: If the answer is not a list of incident entries.

    Examples:
        >>> rows = download_rows()  # doctest: +SKIP
        >>> rows = download_rows(timeout=120, tries=2)  # doctest: +SKIP
    """
    problem = None
    for attempt in range(max(tries, 1)):
        if attempt:
            time.sleep(2**attempt + random.random())
        if verbose:
            print(f"Requesting {URL}", file=sys.stderr)
        try:
            response = requests.get(URL, timeout=timeout)
        except (requests.ConnectionError, requests.Timeout) as error:
            problem = InciWebError(
                f"Could not reach InciWeb at {URL}: {error}", url=URL
            )
            continue
        except requests.RequestException as error:
            raise InciWebError(f"Request to {URL} failed: {error}", url=URL) from error

        status = response.status_code
        if status >= 500 or status in RETRY_STATUS_CODES:
            problem = InciWebError(
                f"InciWeb sent back status {status} for {URL}",
                url=URL,
                status_code=status,
            )
            continue
        if status >= 400:
            raise InciWebError(
                f"InciWeb sent back status {status} for {URL}",
                url=URL,
                status_code=status,
            )
        return _read_rows(response.content)

    assert problem is not None
    raise problem


def _read_rows(content: bytes) -> list[dict[str, str]]:
    """Read the incident entries InciWeb sent back.

    Args:
        content: The bytes of the reply.

    Returns:
        The list of entries.

    Raises:
        InciWebDataError: If the reply is not JSON, or is not a list of
            entries that each have a "type".

    Examples:
        >>> _read_rows(b'[{"type": "Wildfire"}]')
        [{'type': 'Wildfire'}]
    """
    try:
        rows = json.loads(content)
    except ValueError as error:
        raise InciWebDataError(f"The reply from {URL} is not JSON", url=URL) from error
    if not isinstance(rows, list) or not all(
        isinstance(row, dict) and "type" in row for row in rows
    ):
        raise InciWebDataError(
            f"The reply from {URL} does not look like a list of incidents", url=URL
        )
    return rows
