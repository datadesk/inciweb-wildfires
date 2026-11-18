"""Tests that call InciWeb's real website.

They are skipped by default because they can be slow, or fail when InciWeb is
down. Run them with ``make test-live`` or ``uv run pytest -m live``.
"""

from __future__ import annotations

import pytest

import inciweb_wildfires

pytestmark = pytest.mark.live


def test_live_incidents():
    data = inciweb_wildfires.get_incidents()
    assert data["type"] == "FeatureCollection"


def test_live_prescribed_fires():
    data = inciweb_wildfires.get_prescribed_fires()
    assert data["type"] == "FeatureCollection"
