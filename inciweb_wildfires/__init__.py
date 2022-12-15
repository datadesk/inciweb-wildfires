import requests
from bs4 import BeautifulSoup
from geojson import Feature, FeatureCollection, Point


def get_incidents():
    """
    Get active incidents data from InciWeb.

    Returns GeoJson FeatureCollection.
    """
    url = "https://inciweb.nwcg.gov/feeds/maps/placemarks.kml"
    r = requests.get(url)
    soup = BeautifulSoup(r.content, "xml")
    folder_list = soup.find_all("Folder")
    feature_list = []
    for folder in folder_list:
        d = dict(name=folder.find("name").text, url=folder.find("Placemark").a["href"])
        coords = folder.find("Point").find("coordinates").text.split(",")
        p = Point(map(_safe_float, coords))
        f = Feature(geometry=p, properties=d)
        feature_list.append(f)

    return FeatureCollection(feature_list)


def _safe_float(v):
    v = v.strip()
    # Fix the weird points that end with an extra "."
    v = ".".join(v.split(".")[:2])
    return float(v)
