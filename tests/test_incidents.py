"""Offline tests for the download functions and the command line."""

from __future__ import annotations

import json

import pytest
from click.testing import CliRunner

import inciweb_wildfires
from inciweb_wildfires import convert_coords
from inciweb_wildfires.cli import cmd


def test_get_incidents_returns_only_wildfires(fake_inciweb):
    data = inciweb_wildfires.get_incidents()
    assert data["type"] == "FeatureCollection"
    assert len(data["features"]) == 2
    assert {f["properties"]["type"] for f in data["features"]} == {"Wildfire"}
    assert fake_inciweb == ["https://inciweb.wildfire.gov/api/map_data"]


def test_get_prescribed_fires_returns_only_prescribed_fires(fake_inciweb):
    data = inciweb_wildfires.get_prescribed_fires()
    assert len(data["features"]) == 2
    assert {f["properties"]["type"] for f in data["features"]} == {"Prescribed Fire"}


def test_get_data_unknown_type_is_empty(fake_inciweb):
    assert inciweb_wildfires.get_data("Nothing")["features"] == []


def test_points_are_longitude_then_latitude_in_the_western_hemisphere(fake_inciweb):
    feature = inciweb_wildfires.get_incidents()["features"][0]
    props = feature["properties"]
    x, y = feature["geometry"]["coordinates"]
    assert x == pytest.approx(
        -convert_coords(props["long_deg"], props["long_min"], props["long_sec"])
    )
    assert y == pytest.approx(
        convert_coords(props["lat_deg"], props["lat_min"], props["lat_sec"])
    )
    assert x < 0 < y


def test_properties_are_the_untouched_source_row(fake_inciweb, sample_rows):
    feature = inciweb_wildfires.get_incidents()["features"][0]
    assert feature["properties"] == sample_rows[0]


def test_convert_coords():
    assert convert_coords("40", "30", "0") == 40.5
    assert convert_coords("40", " ", "") == 40.0
    assert convert_coords("105º", "0", "36") == pytest.approx(105.01)


def test_cli_incidents(fake_inciweb):
    result = CliRunner().invoke(cmd, ["incidents"])
    assert result.exit_code == 0
    assert len(json.loads(result.output)["features"]) == 2


def test_cli_prescribed_fires(fake_inciweb):
    result = CliRunner().invoke(cmd, ["prescribed-fires"])
    assert result.exit_code == 0
    assert len(json.loads(result.output)["features"]) == 2
