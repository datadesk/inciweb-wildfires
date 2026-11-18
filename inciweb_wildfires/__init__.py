"""Download wildfire incidents data from InciWeb."""

from __future__ import annotations

from geojson import Feature, FeatureCollection, Point

from .coords import convert_coords, to_point
from .errors import InciWebDataError, InciWebError
from .fetch import DEFAULT_TIMEOUT, Fetcher, Reply, download_rows
from .records import Incident

__all__ = [
    "Fetcher",
    "Incident",
    "InciWebDataError",
    "InciWebError",
    "Reply",
    "convert_coords",
    "get_data",
    "get_incident_records",
    "get_incidents",
    "get_prescribed_fires",
]


def get_data(
    t,
    verbose: bool = False,
    timeout: float = DEFAULT_TIMEOUT,
    *,
    get: Fetcher | None = None,
) -> FeatureCollection:
    """
    Get all incidents data from InciWeb.

    Passes in 't' parameter used to specify type of data (Wildfire, Prescribed Fire)
    Incident Types

    Args:
        t: The type of incident to keep, either "Wildfire" or "Prescribed Fire".
        verbose: Print each request to standard error. Defaults to False.
        timeout: Seconds to wait for InciWeb on each try. Defaults to 60.
        get: A function that makes the web request, such as ``requests.get``
            (the default). Pass your own to add retries, logging or custom
            headers. It is called as ``get(url, timeout=seconds)``.

    Returns:
        A GeoJSON FeatureCollection with one point for each incident of that
        type. The properties are InciWeb's own fields, as text.

    Raises:
        InciWebError: If InciWeb cannot be reached after several tries, or
            answers with an error.
        InciWebDataError: If an entry is missing a field or has a coordinate
            that cannot be read. This is also a ``ValueError``.

    Examples:
        >>> data = get_data("Wildfire")  # doctest: +SKIP
    """
    data = download_rows(verbose=verbose, timeout=timeout, get=get)

    # Loop through all the placemarks
    feature_list = []
    for d in data:
        # Only type specified
        if d["type"] == t:
            # Reformat as GeoJSON
            try:
                p = Point(to_point(d))
            except (KeyError, ValueError) as error:
                raise InciWebDataError(
                    f"Could not read the location of an incident: {error!r}"
                ) from error
            f = Feature(geometry=p, properties=d)
            # Add it to the list
            feature_list.append(f)
    # Pass it out
    return FeatureCollection(feature_list)


def get_incidents(
    verbose: bool = False,
    timeout: float = DEFAULT_TIMEOUT,
    *,
    get: Fetcher | None = None,
) -> FeatureCollection:
    """Get all active wildfire incidents from InciWeb.

    Args:
        verbose: Print each request to standard error. Defaults to False.
        timeout: Seconds to wait for InciWeb on each try. Defaults to 60.
        get: A function that makes the web request, such as ``requests.get``
            (the default). Pass your own to add retries, logging or custom
            headers. It is called as ``get(url, timeout=seconds)``.

    Returns:
        A GeoJSON FeatureCollection with one point for each wildfire.

    Raises:
        InciWebError: If InciWeb cannot be reached after several tries, or
            answers with an error.

    Examples:
        >>> data = get_incidents()  # doctest: +SKIP
    """
    return get_data("Wildfire", verbose=verbose, timeout=timeout, get=get)


def get_prescribed_fires(
    verbose: bool = False,
    timeout: float = DEFAULT_TIMEOUT,
    *,
    get: Fetcher | None = None,
) -> FeatureCollection:
    """Get all active prescribed fire incidents from InciWeb.

    Args:
        verbose: Print each request to standard error. Defaults to False.
        timeout: Seconds to wait for InciWeb on each try. Defaults to 60.
        get: A function that makes the web request, such as ``requests.get``
            (the default). Pass your own to add retries, logging or custom
            headers. It is called as ``get(url, timeout=seconds)``.

    Returns:
        A GeoJSON FeatureCollection with one point for each prescribed fire.

    Raises:
        InciWebError: If InciWeb cannot be reached after several tries, or
            answers with an error.

    Examples:
        >>> data = get_prescribed_fires()  # doctest: +SKIP
    """
    return get_data("Prescribed Fire", verbose=verbose, timeout=timeout, get=get)


def get_incident_records(
    t: str | None = None,
    verbose: bool = False,
    timeout: float = DEFAULT_TIMEOUT,
    *,
    get: Fetcher | None = None,
) -> list[Incident]:
    """Get incidents from InciWeb as typed records instead of GeoJSON.

    Each record has its numbers and dates already parsed. See ``Incident`` for
    every field.

    Args:
        t: The type of incident to keep, either "Wildfire" or "Prescribed Fire".
            Defaults to None, which keeps every type.
        verbose: Print each request to standard error. Defaults to False.
        timeout: Seconds to wait for InciWeb on each try. Defaults to 60.
        get: A function that makes the web request, such as ``requests.get``
            (the default). Pass your own to add retries, logging or custom
            headers. It is called as ``get(url, timeout=seconds)``.

    Returns:
        A list of ``Incident`` records.

    Raises:
        InciWebError: If InciWeb cannot be reached after several tries, or
            answers with an error.
        InciWebDataError: If an entry is missing a field or has a number or
            time that cannot be read. This is also a ``ValueError``.

    Examples:
        >>> records = get_incident_records("Wildfire")  # doctest: +SKIP
        >>> for incident in records:  # doctest: +SKIP
        ...     print(incident.title, incident.size, incident.percent_contained)
    """
    rows = download_rows(verbose=verbose, timeout=timeout, get=get)
    try:
        return [Incident.from_row(r) for r in rows if t is None or r["type"] == t]
    except (KeyError, ValueError) as error:
        raise InciWebDataError(f"Could not read an incident: {error!r}") from error
