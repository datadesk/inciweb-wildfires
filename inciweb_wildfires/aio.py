"""Async versions of InciWeb wildfire data functions."""

from __future__ import annotations

import httpx
from geojson import Feature, FeatureCollection, Point

from inciweb_wildfires import convert_coords


async def get_data(t) -> FeatureCollection:
    """
    Get all incidents data from InciWeb.

    Passes in 't' parameter used to specify type of data (Wildfire, Prescribed Fire)
    Incident Types

    Returns GeoJson FeatureCollection.
    """
    url = "https://inciweb.wildfire.gov/api/map_data"
    async with httpx.AsyncClient() as client:
        r = await client.get(url)

    try:
        r.raise_for_status()
    except httpx.HTTPStatusError as e:
        raise AssertionError(f"Request failed with status code {r.status_code}") from e

    data = r.json()

    feature_list = []
    for d in data:
        if d["type"] == t:
            x = convert_coords(d["long_deg"], d["long_min"], d["long_sec"])
            y = convert_coords(d["lat_deg"], d["lat_min"], d["lat_sec"])
            if x > 0:
                x = -x
            p = Point((x, y))
            f = Feature(geometry=p, properties=d)
            feature_list.append(f)
    return FeatureCollection(feature_list)


async def get_incidents() -> FeatureCollection:
    """
    Get all active wildfire incidents from InciWeb.
    Returns GeoJson FeatureCollection.
    """
    return await get_data("Wildfire")


async def get_prescribed_fires() -> FeatureCollection:
    """
    Get all active prescribed fire incidents from InciWeb.
    Returns GeoJson FeatureCollection.
    """
    return await get_data("Prescribed Fire")
