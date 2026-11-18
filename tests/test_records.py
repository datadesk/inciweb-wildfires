"""Offline tests for the typed incident records."""

from __future__ import annotations

from datetime import UTC, timedelta

import pytest

import inciweb_wildfires
from inciweb_wildfires import Incident


def test_all_records(fake_inciweb, sample_rows):
    records = inciweb_wildfires.get_incident_records()
    assert [r.id for r in records] == [int(r["id"]) for r in sample_rows]


def test_records_can_be_limited_to_a_type(fake_inciweb):
    records = inciweb_wildfires.get_incident_records("Prescribed Fire")
    assert len(records) == 2
    assert {r.incident_type for r in records} == {"Prescribed Fire"}


def test_record_fields_are_parsed(sample_rows):
    row = sample_rows[0]
    incident = Incident.from_row(row)
    assert incident.size == float(row["size"])
    assert incident.size_unit == "Acres"
    assert incident.percent_contained == float(row["field_percent_of_perimeter"])
    assert incident.is_active is True
    assert incident.longitude < 0 < incident.latitude
    assert incident.url == "https://inciweb.wildfire.gov" + row["urlPath"]
    assert incident.created_at.tzinfo is UTC
    assert incident.created_at.utcoffset() == timedelta(0)


def test_record_matches_the_geojson_point(fake_inciweb):
    feature = inciweb_wildfires.get_incidents()["features"][0]
    incident = inciweb_wildfires.get_incident_records("Wildfire")[0]
    # GeoJSON rounds to six decimals; the record keeps every digit.
    assert (incident.longitude, incident.latitude) == pytest.approx(
        feature["geometry"]["coordinates"], abs=1e-6
    )


def test_blank_numbers_become_none(sample_rows):
    row = dict(
        sample_rows[2], size="", field_percent_of_perimeter="", measurement_type=""
    )
    incident = Incident.from_row(row)
    assert incident.size is None
    assert incident.percent_contained is None
    assert incident.size_unit is None


def test_created_time_is_converted_to_utc(sample_rows):
    row = dict(
        sample_rows[0],
        created='<time datetime="2022-10-06T11:44:14-04:00">2022-10-06</time>\n',
    )
    assert Incident.from_row(row).created_at.isoformat() == "2022-10-06T15:44:14+00:00"


def test_bad_values_raise_value_error(sample_rows):
    with pytest.raises(ValueError):
        Incident.from_row(dict(sample_rows[0], size="big"))
    with pytest.raises(ValueError):
        Incident.from_row(dict(sample_rows[0], created="never"))
