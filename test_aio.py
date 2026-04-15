import pytest
import respx
from httpx import Response

from inciweb_wildfires.aio import get_data, get_incidents, get_prescribed_fires

MOCK_DATA = [
    {
        "type": "Wildfire",
        "long_deg": "118",
        "long_min": "30",
        "long_sec": "0",
        "lat_deg": "34",
        "lat_min": "0",
        "lat_sec": "0",
        "name": "Test Wildfire",
    },
    {
        "type": "Prescribed Fire",
        "long_deg": "120",
        "long_min": "15",
        "long_sec": "0",
        "lat_deg": "37",
        "lat_min": "0",
        "lat_sec": "0",
        "name": "Test Prescribed Fire",
    },
]


@pytest.fixture
def mock_api():
    with respx.mock:
        respx.get("https://inciweb.wildfire.gov/api/map_data").mock(
            return_value=Response(200, json=MOCK_DATA)
        )
        yield


@pytest.mark.asyncio
async def test_get_data_wildfire(mock_api):
    result = await get_data("Wildfire")
    assert result["type"] == "FeatureCollection"
    assert len(result["features"]) == 1
    assert result["features"][0]["properties"]["name"] == "Test Wildfire"


@pytest.mark.asyncio
async def test_get_data_prescribed_fire(mock_api):
    result = await get_data("Prescribed Fire")
    assert result["type"] == "FeatureCollection"
    assert len(result["features"]) == 1
    assert result["features"][0]["properties"]["name"] == "Test Prescribed Fire"


@pytest.mark.asyncio
async def test_get_incidents(mock_api):
    result = await get_incidents()
    assert result["type"] == "FeatureCollection"
    assert len(result["features"]) == 1
    assert result["features"][0]["properties"]["type"] == "Wildfire"


@pytest.mark.asyncio
async def test_get_prescribed_fires(mock_api):
    result = await get_prescribed_fires()
    assert result["type"] == "FeatureCollection"
    assert len(result["features"]) == 1
    assert result["features"][0]["properties"]["type"] == "Prescribed Fire"


@pytest.mark.asyncio
async def test_coordinates_are_negative(mock_api):
    """Longitude should always be negative (western hemisphere)."""
    result = await get_incidents()
    lon, lat = result["features"][0]["geometry"]["coordinates"]
    assert lon < 0
    assert lat > 0


@pytest.mark.asyncio
async def test_http_error_raises():
    with respx.mock:
        respx.get("https://inciweb.wildfire.gov/api/map_data").mock(
            return_value=Response(500)
        )
        with pytest.raises(AssertionError, match="status code 500"):
            await get_data("Wildfire")
