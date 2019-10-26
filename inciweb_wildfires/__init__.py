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
    return FeatureCollection([Feature(geometry={'type': 'Point', 'coordinates': [float(d['lng']), float(d['lat'])]}, fireName=d['name'].split(' Fire')[0], inciweb_id=d['id'], properties=d) for d in content])
