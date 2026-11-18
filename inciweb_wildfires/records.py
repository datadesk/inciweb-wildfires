"""Typed records for the incidents InciWeb publishes."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import UTC, datetime

from .coords import to_point

SITE = "https://inciweb.wildfire.gov"
"""The InciWeb website, which the incident page addresses start from."""

_CREATED = re.compile(r'datetime="([^"]+)"')


def _number(text: str) -> float | None:
    """Read a number InciWeb wrote as text, or None if it left it blank.

    Args:
        text: The text, such as "107189", "1,500" or "".

    Returns:
        The number, or None for blank text.

    Raises:
        ValueError: If the text is not blank and not a number.

    Examples:
        >>> _number("1,500")
        1500.0
        >>> _number("") is None
        True
    """
    text = text.strip().replace(",", "")
    return float(text) if text else None


def _created(text: str) -> datetime:
    """Read the creation time out of the little HTML tag InciWeb sends.

    Args:
        text: Text like ``<time datetime="2022-10-06T11:44:14-04:00">2022-10-06</time>``.

    Returns:
        The time, in UTC.

    Raises:
        ValueError: If the text has no time in it.

    Examples:
        >>> _created('<time datetime="2022-10-06T11:44:14-04:00">2022-10-06</time>')
        datetime.datetime(2022, 10, 6, 15, 44, 14, tzinfo=datetime.timezone.utc)
    """
    match = _CREATED.search(text)
    if not match:
        raise ValueError(f"No time found in {text!r}")
    return datetime.fromisoformat(match.group(1)).astimezone(UTC)


@dataclass(frozen=True, slots=True)
class Incident:
    """One incident entry on InciWeb.

    InciWeb is the interagency information page for wildfires and other fire
    incidents. An entry is a page that fire agencies write and update by hand,
    so it can lag behind events or disagree with other sources. The size and
    containment are the numbers the agencies reported and they change.

    Attributes:
        id: InciWeb's number for the incident.
        title: The incident's name, such as "Babylon Fire".
        unit_code: The code of the agency unit in charge, such as "UTMLF".
        unit_title: The unit code and the name together, as InciWeb shows them.
        incident_type: "Wildfire" or "Prescribed Fire".
        is_active: True if InciWeb marks the incident as active.
        longitude: Degrees east of the prime meridian, negative in the west.
        latitude: Degrees north of the equator.
        size: How big the incident is, in the unit named by ``size_unit``.
            None if the agency left it blank.
        size_unit: The unit for ``size``, such as "Acres". None if blank.
        percent_contained: The share of the fire's edge that is contained, from
            0 to 100. InciWeb calls it "Percent of Perimeter Contained". None
            if the agency left it blank.
        created_at: When the InciWeb page was created, in UTC.
        changed: When the page was last changed, in InciWeb's own words, such
            as "1 day 20 hours ago". It is relative to when InciWeb sent the
            data, so it is kept as text.
        path: The incident page's path on InciWeb, such as "/utmlf-babylon-fire".
        description: A short description, which can contain HTML. Blank if none.
        overview_html: The incident overview, as HTML.

    Examples:
        >>> row = {
        ...     "id": "328260",
        ...     "title": "Babylon Fire",
        ...     "field_title_and_unit": "UTMLF Babylon Fire",
        ...     "field_unit_code": "UTMLF",
        ...     "type": "Wildfire",
        ...     "field_active": "1",
        ...     "long_deg": "109", "long_min": "10", "long_sec": "30",
        ...     "lat_deg": "40", "lat_min": "28", "lat_sec": "31",
        ...     "size": "107189",
        ...     "measurement_type": "Acres",
        ...     "field_percent_of_perimeter": "100",
        ...     "created": '<time datetime="2026-06-26T18:00:00-06:00">2026-06-26</time>',
        ...     "changed": "3 months ago",
        ...     "urlPath": "/utmlf-babylon-fire",
        ...     "field_incident_description": "",
        ...     "field_incident_overview": "<p>Text</p>",
        ... }
        >>> incident = Incident.from_row(row)
        >>> incident.size, incident.percent_contained
        (107189.0, 100.0)
        >>> incident.url
        'https://inciweb.wildfire.gov/utmlf-babylon-fire'
    """

    id: int
    title: str
    unit_code: str
    unit_title: str
    incident_type: str
    is_active: bool
    longitude: float
    latitude: float
    size: float | None
    size_unit: str | None
    percent_contained: float | None
    created_at: datetime
    changed: str
    path: str
    description: str
    overview_html: str

    @property
    def url(self) -> str:
        """The address of the incident's page on InciWeb."""
        return f"{SITE}{self.path}"

    @classmethod
    def from_row(cls, row: dict[str, str]) -> Incident:
        """Make a record from one entry of InciWeb's map data.

        Args:
            row: One entry, as InciWeb sends it. Every value is text.

        Returns:
            The record, with numbers and times already parsed.

        Raises:
            KeyError: If the row is missing a field.
            ValueError: If a number or time cannot be read.

        Examples:
            >>> Incident.from_row({})  # doctest: +SKIP
        """
        longitude, latitude = to_point(row)
        return cls(
            id=int(row["id"]),
            title=row["title"],
            unit_code=row["field_unit_code"],
            unit_title=row["field_title_and_unit"],
            incident_type=row["type"],
            is_active=row["field_active"] == "1",
            longitude=longitude,
            latitude=latitude,
            size=_number(row["size"]),
            size_unit=row["measurement_type"].strip() or None,
            percent_contained=_number(row["field_percent_of_perimeter"]),
            created_at=_created(row["created"]),
            changed=row["changed"],
            path=row["urlPath"],
            description=row["field_incident_description"],
            overview_html=row["field_incident_overview"],
        )
