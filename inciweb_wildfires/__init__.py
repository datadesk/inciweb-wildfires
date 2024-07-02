"""Download wildfire incidents data from InciWeb."""

from __future__ import annotations

import requests
from geojson import Feature, FeatureCollection, Point


def get_data(t) -> FeatureCollection:
    """
    Get all incidents data from InciWeb.

    Passes in 't' parameter used to specify type of data (Wildfire, Prescribed Fire)
    Incident Types

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
        # Only type specified
        if d['type'] == t:
            # Reformat as GeoJSON
            x = convert_coords(d["long_deg"], d["long_min"], d["long_sec"])
            y = convert_coords(d["lat_deg"], d["lat_min"], d["lat_sec"])
            if x > 0:
                x = -x
            p = Point((x, y))
            f = Feature(geometry=p, properties=d)
            # Add it to the list
            feature_list.append(f)
        else:
            continue
    # Pass it out
    return FeatureCollection(feature_list)


def get_incidents() -> FeatureCollection:
    """
    Get all active wildfire incidents from InciWeb.
    Returns GeoJson FeatureCollection.
    """
    features = get_data("Wildfire")

    # Pass it out
    return features


def get_prescribed_fires() -> FeatureCollection:
    """
    Get all active prescribed fire incidents from InciWeb.
    Returns GeoJson FeatureCollection.
    """
    features = get_data("Prescribed Fire")

    # Pass it out
    return features


def convert_coords(deg: str, min: str, sec: str) -> float:
    """Handle the flawed coordinates published by InciWeb."""
    # if there's a degree symbol, remove it
    deg = deg.replace('º', '')
    if not min.strip():
        min = '0'
    if not sec.strip():
        sec = '0'
    return float(deg) + (float(min) / 60) + (float(sec) / 3600)
