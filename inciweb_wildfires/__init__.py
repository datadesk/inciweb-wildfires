import requests
from geojson import Feature, FeatureCollection, Point


def get_inicidents():
    """
    Get active incidents data from InciWeb.

    Returns GeoJson FeatureCollection.
    """
    # Get the data
    url = 'https://inciweb.nwcg.gov/feeds/json/esri/'
    r = requests.get(url)
    content = r.json()['markers']

    # Convert to GeoJSON features
    feature_list = []
    for d in content:
        p = Point(
            map(float, (d['lng'], d['lat']))
        )
        f = Feature(geometry=p, properties=d)
        feature_list.append(f)

    # Return the GeoJSON feature collection
    return FeatureCollection(feature_list)
