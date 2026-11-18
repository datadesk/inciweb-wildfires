"""Download wildfire incidents data from InciWeb."""

from __future__ import annotations

from geojson import Feature, FeatureCollection, Point

from .coords import convert_coords, to_point
from .fetch import download_rows
from .records import Incident

__all__ = [
    "Incident",
    "convert_coords",
    "get_data",
    "get_incident_records",
    "get_incidents",
    "get_prescribed_fires",
]


def get_data(t) -> FeatureCollection:
    """
    Get all incidents data from InciWeb.

    Passes in 't' parameter used to specify type of data (Wildfire, Prescribed Fire)
    Incident Types

    Args:
        t: The type of incident to keep, either "Wildfire" or "Prescribed Fire".

    Returns:
        A GeoJSON FeatureCollection with one point for each incident of that
        type. The properties are InciWeb's own fields, as text.

    Examples:
        >>> data = get_data("Wildfire")  # doctest: +SKIP
    """
    data = download_rows()

    # Loop through all the placemarks
    feature_list = []
    for d in data:
        # Only type specified
        if d["type"] == t:
            # Reformat as GeoJSON
            p = Point(to_point(d))
            f = Feature(geometry=p, properties=d)
            # Add it to the list
            feature_list.append(f)
    # Pass it out
    return FeatureCollection(feature_list)


def get_incidents() -> FeatureCollection:
    """Get all active wildfire incidents from InciWeb.

    Returns:
        A GeoJSON FeatureCollection with one point for each wildfire.

    Examples:
        >>> data = get_incidents()  # doctest: +SKIP
    """
    return get_data("Wildfire")


def get_prescribed_fires() -> FeatureCollection:
    """Get all active prescribed fire incidents from InciWeb.

    Returns:
        A GeoJSON FeatureCollection with one point for each prescribed fire.

    Examples:
        >>> data = get_prescribed_fires()  # doctest: +SKIP
    """
    return get_data("Prescribed Fire")


def get_incident_records(t: str | None = None) -> list[Incident]:
    """Get incidents from InciWeb as typed records instead of GeoJSON.

    Each record has its numbers and dates already parsed. See ``Incident`` for
    every field.

    Args:
        t: The type of incident to keep, either "Wildfire" or "Prescribed Fire".
            Defaults to None, which keeps every type.

    Returns:
        A list of ``Incident`` records.

    Raises:
        AssertionError: If InciWeb answers with an error status.
        KeyError: If an entry is missing a field.
        ValueError: If a number or time in an entry cannot be read.

    Examples:
        >>> records = get_incident_records("Wildfire")  # doctest: +SKIP
        >>> for incident in records:  # doctest: +SKIP
        ...     print(incident.title, incident.size, incident.percent_contained)
    """
    return [
        Incident.from_row(r) for r in download_rows() if t is None or r["type"] == t
    ]
