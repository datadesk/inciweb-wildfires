"""Offline tests of the optional ``get`` argument, with a fake request function."""

from __future__ import annotations

import json

import pytest
import requests

import inciweb_wildfires
from inciweb_wildfires import Fetcher, InciWebDataError, InciWebError, Reply, fetch


class Plain:
    """A reply with only a status code and bytes, nothing else."""

    def __init__(self, payload: object, status_code: int = 200) -> None:
        self.status_code = status_code
        self.content = json.dumps(payload).encode()


@pytest.fixture(autouse=True)
def no_waiting(monkeypatch):
    monkeypatch.setattr(fetch.time, "sleep", lambda seconds: None)


@pytest.fixture
def requests_must_not_run(monkeypatch):
    """Fail the test if the package falls back to ``requests.get``."""

    def boom(*args, **kwargs):
        raise AssertionError("requests.get was called")

    monkeypatch.setattr(fetch.requests, "get", boom)


def make_get(replies: list):
    calls: list[tuple[str, float]] = []

    def get(url: str, *, timeout: float) -> Reply:
        calls.append((url, timeout))
        reply = replies[len(calls) - 1]
        if isinstance(reply, Exception):
            raise reply
        return reply

    fetcher: Fetcher = get
    return fetcher, calls


def test_get_is_used_instead_of_requests(requests_must_not_run, sample_rows):
    get, calls = make_get([Plain(sample_rows)])
    data = inciweb_wildfires.get_incidents(get=get)
    assert len(data["features"]) == 2
    assert calls == [(fetch.URL, 60.0)]


def test_timeout_reaches_get(sample_rows):
    get, calls = make_get([Plain(sample_rows)])
    inciweb_wildfires.get_prescribed_fires(timeout=9, get=get)
    assert calls[0][1] == 9


def test_every_download_function_accepts_get(sample_rows):
    get, calls = make_get([Plain(sample_rows)] * 4)
    assert inciweb_wildfires.get_data("Wildfire", get=get)["features"]
    assert inciweb_wildfires.get_incidents(get=get)["features"]
    assert inciweb_wildfires.get_prescribed_fires(get=get)["features"]
    assert len(inciweb_wildfires.get_incident_records(get=get)) == 4
    assert len(calls) == 4


def test_retries_requests_errors_from_get(sample_rows):
    get, calls = make_get(
        [requests.Timeout("slow"), Plain([], 503), Plain(sample_rows)]
    )
    assert inciweb_wildfires.get_incidents(get=get)["features"]
    assert len(calls) == 3


def test_gives_up_with_inciweb_error(sample_rows):
    get, calls = make_get([Plain([], 500)] * 4)
    with pytest.raises(InciWebError, match="500"):
        inciweb_wildfires.get_incidents(get=get)
    assert len(calls) == 4


def test_not_found_is_not_retried():
    get, calls = make_get([Plain([], 404)])
    with pytest.raises(InciWebError, match="404"):
        inciweb_wildfires.get_incidents(get=get)
    assert len(calls) == 1


def test_bad_data_raises_data_error():
    get, _ = make_get([Plain({"oops": 1})])
    with pytest.raises(InciWebDataError):
        inciweb_wildfires.get_incidents(get=get)


def test_other_errors_pass_through():
    get, _ = make_get([KeyError("mine")])
    with pytest.raises(KeyError):
        inciweb_wildfires.get_incidents(get=get)


def test_default_still_uses_requests(monkeypatch, sample_rows):
    seen = []

    def fake(url, **kwargs):
        seen.append(url)
        return Plain(sample_rows)

    monkeypatch.setattr(fetch.requests, "get", fake)
    inciweb_wildfires.get_incidents()
    assert seen == [fetch.URL]
