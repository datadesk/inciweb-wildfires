"""Download wildfire incidents data from InciWeb."""

from __future__ import annotations

import requests
from geojson import Feature, FeatureCollection, Point


def get_incidents() -> FeatureCollection:
    """
    Get active incidents data from InciWeb.

    Returns GeoJson FeatureCollection.
    """
    # Get the URL
    url = "https://inciweb.wildfire.gov/api/map_data"
    r = requests.get(url)

    # Make sure it came back kosher
    try:
        assert r.ok
    except AssertionError:
        raise AssertionError(f"Request failed with status code {r.status_code}")

    # Get the JSON data
    data = r.json()

    # Loop through all the placemarks
    feature_list = []
    for d in data:
        # Reformat as GeoJSON
        x = convert_coords(d["long_deg"], d["long_min"], d["long_sec"])
        y = convert_coords(d["lat_deg"], d["lat_min"], d["lat_sec"])
        if x > 0:
            x = -x
        p = Point((x, y))
        f = Feature(geometry=p, properties=d)

        # Add it to the list
        feature_list.append(f)

    # Pass it out
    return FeatureCollection(feature_list)


def convert_coords(deg: str, min: str, sec: str) -> float:
    """Handle the flawed coordinates published by InciWeb."""
    if not min.strip():
        min = '0'
    if not sec.strip():
        sec = '0'
    return float(deg) + (float(min) / 60) + (float(sec) / 3600)
