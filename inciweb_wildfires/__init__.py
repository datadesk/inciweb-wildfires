import requests
from bs4 import BeautifulSoup
from geojson import Feature, FeatureCollection, Point


def get_incidents():
    """
    Get active incidents data from InciWeb.

    Returns GeoJson FeatureCollection.
    """
    # Get the URL
    url = "https://inciweb.nwcg.gov/feeds/maps/placemarks.kml"
    r = requests.get(url)

    # Parse the KML
    soup = BeautifulSoup(r.content, "xml")
    folder_list = soup.find_all("Folder")

    # Loop through all the placemarks
    feature_list = []
    for folder in folder_list:
        # Pull out the properties
        d = dict(
            name=folder.find("name").text,
            url=folder.find("Placemark").a["href"]
        )
        
        # Grab the coordinates
        coords = folder.find("Point").find("coordinates").text.split(",")
        
        # Reformat as GeoJSON
        p = Point(map(_safe_float, coords))
        f = Feature(geometry=p, properties=d)
        feature_list.append(f)
    
    # Pass it out
    return FeatureCollection(feature_list)


def _safe_float(v):
    """Handle the flawed coordinates published by Inciweb."""
    v = v.strip()
    # Fix the weird points that end with an extra "."
    v = ".".join(v.split(".")[:2])
    return float(v)
