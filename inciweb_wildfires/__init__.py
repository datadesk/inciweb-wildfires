import requests
from bs4 import BeautifulSoup
from geojson import Feature, FeatureCollection, Point


def get_incidents() -> FeatureCollection:
    """
    Get active incidents data from InciWeb.

    Returns GeoJson FeatureCollection.
    """
    # Get the URL
    url = "https://inciweb.nwcg.gov/feeds/maps/placemarks.kml"
    r = requests.get(url)

    # Make sure it came back kosher
    try:
        assert r.ok
    except AssertionError:
        raise AssertionError(f"Request failed with status code {r.status_code}")

    # Parse the KML
    soup = BeautifulSoup(r.content, "xml")
    folder_list = soup.find_all("Folder")

    # Loop through all the placemarks
    feature_list = []
    for folder in folder_list:
        # Pull out the properties
        d = dict(name=folder.find("name").text, url=folder.find("Placemark").a["href"])

        # Grab the coordinates
        coords = folder.find("Point").find("coordinates").text.split(",")

        # Reformat as GeoJSON
        try:
            p = Point(map(_safe_float, coords))
        except Exception:
            # If the point cannot be converted, skip it.
            # Inciweb does sometimes ship malformed data
            print(f"Point {coords} could not be parsed. Skipping this feature.")
            continue
        f = Feature(geometry=p, properties=d)

        # Add it to the list
        feature_list.append(f)

    # Pass it out
    return FeatureCollection(feature_list)


def _safe_float(v: str) -> float:
    """Handle the flawed coordinates published by InciWeb."""
    # Strip the front and back
    v = v.strip()
    # Fix the weird points that end with an extra "."
    v = ".".join(v.split(".")[:2])
    # Delete any empty spaces
    v = v.replace(" ", "")
    # Cast to float
    return float(v)
