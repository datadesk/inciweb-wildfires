"""Shared test setup. The offline tests never talk to the real InciWeb."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
import requests

DATA_DIR = Path(__file__).parent / "data"


class FakeResponse:
    """A stand-in for a ``requests`` response."""

    def __init__(self, payload: object, status_code: int = 200) -> None:
        self.status_code = status_code
        self.ok = status_code < 400
        self.content = json.dumps(payload).encode()
        self._payload = payload

    def json(self) -> object:
        return self._payload


@pytest.fixture
def sample_rows() -> list[dict[str, str]]:
    """A small saved copy of what InciWeb's map data looks like."""
    return json.loads((DATA_DIR / "map_data.json").read_text())


@pytest.fixture
def fake_inciweb(monkeypatch: pytest.MonkeyPatch, sample_rows):
    """Make ``requests.get`` return the saved sample instead of calling InciWeb."""
    calls: list[str] = []

    def fake_get(url: str, *args, **kwargs) -> FakeResponse:
        calls.append(url)
        return FakeResponse(sample_rows)

    monkeypatch.setattr(requests, "get", fake_get)
    return calls
