"""Offline tests of timeouts, retries and errors, with fake replies."""

from __future__ import annotations

import json

import pytest
import requests
from click.testing import CliRunner

import inciweb_wildfires
from inciweb_wildfires import InciWebDataError, InciWebError, fetch
from inciweb_wildfires.cli import cmd

from .conftest import FakeResponse


@pytest.fixture(autouse=True)
def no_waiting(monkeypatch):
    """Skip the pauses between tries so the tests run fast."""
    monkeypatch.setattr(fetch.time, "sleep", lambda seconds: None)


@pytest.fixture
def script(monkeypatch):
    """Make ``requests.get`` play back a list of replies, one for each call.

    An item that is an exception is raised, and any other item is returned.
    """

    class Script:
        replies: list = []
        urls: list[str] = []
        kwargs: dict = {}

    play = Script()
    play.urls = []

    def get(url, **kwargs):
        play.urls.append(url)
        play.kwargs = kwargs
        reply = play.replies[len(play.urls) - 1]
        if isinstance(reply, Exception):
            raise reply
        return reply

    monkeypatch.setattr(fetch.requests, "get", get)
    return play


@pytest.fixture
def good(sample_rows):
    return FakeResponse(sample_rows)


def test_timeout_is_sent(script, good):
    script.replies = [good]
    inciweb_wildfires.get_incidents()
    assert script.kwargs["timeout"] == 60.0


def test_custom_timeout_is_sent(script, good):
    script.replies = [good]
    inciweb_wildfires.get_incidents(timeout=5)
    assert script.kwargs["timeout"] == 5


@pytest.mark.parametrize(
    "failure",
    [
        requests.ConnectionError("no route"),
        requests.Timeout("too slow"),
        FakeResponse([], status_code=503),
        FakeResponse([], status_code=502),
        FakeResponse([], status_code=429),
    ],
)
def test_retries_then_succeeds(script, good, failure):
    script.replies = [failure, good]
    data = inciweb_wildfires.get_incidents()
    assert len(data["features"]) == 2
    assert len(script.urls) == 2


def test_gives_up_with_a_clear_error(script):
    script.replies = [FakeResponse([], status_code=503)] * 4
    with pytest.raises(InciWebError, match="503") as caught:
        inciweb_wildfires.get_incidents()
    assert caught.value.status_code == 503
    assert caught.value.url == fetch.URL
    assert len(script.urls) == 4


def test_network_failure_after_every_try(script):
    script.replies = [requests.ConnectionError("no route")] * 4
    with pytest.raises(InciWebError, match="Could not reach InciWeb"):
        inciweb_wildfires.get_incidents()


def test_not_found_is_not_retried(script):
    script.replies = [FakeResponse([], status_code=404)]
    with pytest.raises(InciWebError, match="404"):
        inciweb_wildfires.get_incidents()
    assert len(script.urls) == 1


def test_other_request_errors_fail_at_once(script):
    script.replies = [requests.exceptions.InvalidURL("bad")]
    with pytest.raises(InciWebError, match="failed"):
        inciweb_wildfires.get_incidents()
    assert len(script.urls) == 1


def test_not_json_is_a_data_error(script):
    reply = FakeResponse([])
    reply.content = b"<html>maintenance</html>"
    script.replies = [reply]
    with pytest.raises(InciWebDataError, match="not JSON"):
        inciweb_wildfires.get_incidents()


def test_wrong_shape_is_a_data_error(script):
    script.replies = [FakeResponse({"error": "nope"})]
    with pytest.raises(InciWebDataError, match="list of incidents"):
        inciweb_wildfires.get_incident_records()


def test_a_bad_entry_is_a_data_error_and_a_value_error(script, sample_rows):
    sample_rows[0]["long_deg"] = "far"
    script.replies = [FakeResponse(sample_rows)] * 2
    with pytest.raises(ValueError):
        inciweb_wildfires.get_incidents()
    with pytest.raises(InciWebDataError):
        inciweb_wildfires.get_incident_records()


def test_a_missing_field_is_a_data_error(script, sample_rows):
    del sample_rows[0]["size"]
    script.replies = [FakeResponse(sample_rows)]
    with pytest.raises(InciWebDataError):
        inciweb_wildfires.get_incident_records()


def test_verbose_writes_to_stderr_only(script, good, capsys):
    script.replies = [good]
    inciweb_wildfires.get_incidents(verbose=True)
    captured = capsys.readouterr()
    assert fetch.URL in captured.err
    assert captured.out == ""


def test_cli_verbose_keeps_stdout_clean_json(script, good):
    script.replies = [good]
    result = CliRunner().invoke(cmd, ["incidents", "--verbose"])
    assert result.exit_code == 0
    assert fetch.URL in result.stderr
    assert json.loads(result.stdout)["type"] == "FeatureCollection"


def test_cli_timeout_is_passed(script, good):
    script.replies = [good]
    result = CliRunner().invoke(cmd, ["prescribed-fires", "--timeout", "7"])
    assert result.exit_code == 0
    assert script.kwargs["timeout"] == 7


def test_cli_error_is_one_plain_line(script):
    script.replies = [FakeResponse([], status_code=404)]
    result = CliRunner().invoke(cmd, ["incidents"])
    assert result.exit_code == 1
    assert result.stderr.startswith("Error: InciWeb sent back status 404")
    assert "Traceback" not in result.stderr


@pytest.mark.parametrize("name", ["prescribed-fires", "prescribed_fires"])
def test_cli_prescribed_fires_error_is_one_plain_line(script, name):
    script.replies = [FakeResponse([], status_code=404)]
    result = CliRunner().invoke(cmd, [name])
    assert result.exit_code == 1
    assert result.stderr.startswith("Error: InciWeb sent back status 404")


@pytest.mark.parametrize("name", ["incidents", "prescribed-fires"])
def test_cli_rejects_a_timeout_under_one_second(script, name):
    result = CliRunner().invoke(cmd, [name, "--timeout", "0"])
    assert result.exit_code == 2
    assert script.urls == []


def test_cli_prescribed_fires_verbose_keeps_stdout_clean_json(script, good):
    script.replies = [good]
    result = CliRunner().invoke(cmd, ["prescribed_fires", "--verbose"])
    assert result.exit_code == 0
    assert fetch.URL in result.stderr
    assert len(json.loads(result.stdout)["features"]) == 2


def test_tries_can_be_limited(script):
    script.replies = [FakeResponse([], status_code=503)] * 2
    with pytest.raises(InciWebError):
        fetch.download_rows(tries=2)
    assert len(script.urls) == 2


def test_an_entry_without_a_type_is_a_data_error(script):
    script.replies = [FakeResponse([{"title": "no type"}])]
    with pytest.raises(InciWebDataError, match="list of incidents"):
        inciweb_wildfires.get_incidents()
