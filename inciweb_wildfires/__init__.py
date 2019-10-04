import requests
import time
from datetime import datetime, timezone
from geojson import Feature, FeatureCollection


def get_fires():
    """
    Get inciweb data for fires
    """
    url = 'https://inciweb.nwcg.gov/feeds/json/esri/'

    r = requests.get(url)
    content = r.json()['markers']
    print(content)

    collection = FeatureCollection([Feature(inciweb_id=d['id'], properties=d) for d in content])
    print(collection)
    return collection
