"""Turn the coordinates InciWeb publishes into numbers."""

from __future__ import annotations


def convert_coords(deg: str, min: str, sec: str) -> float:
    """Handle the flawed coordinates published by InciWeb.

    InciWeb gives each coordinate as three pieces of text: degrees, minutes and
    seconds. The degrees sometimes carry a degree symbol, and the minutes or
    seconds are sometimes blank. A blank counts as zero.

    Args:
        deg: Whole degrees, such as "40" or "105º".
        min: Minutes, such as "33". Blank counts as zero.
        sec: Seconds, such as "32" or "8.9". Blank counts as zero.

    Returns:
        The coordinate in decimal degrees, always zero or greater.

    Examples:
        >>> convert_coords("40", "30", "0")
        40.5
        >>> convert_coords("105º", "", "")
        105.0
    """
    # if there's a degree symbol, remove it
    deg = deg.replace("º", "")
    if not min.strip():
        min = "0"
    if not sec.strip():
        sec = "0"
    return float(deg) + (float(min) / 60) + (float(sec) / 3600)


def to_point(row: dict[str, str]) -> tuple[float, float]:
    """Work out the longitude and latitude of one InciWeb row.

    InciWeb gives positive degrees for every longitude, even though every
    incident is in the western hemisphere, so the longitude is made negative.

    Args:
        row: One entry from InciWeb's map data, with the ``long_deg``,
            ``long_min``, ``long_sec``, ``lat_deg``, ``lat_min`` and
            ``lat_sec`` keys.

    Returns:
        A ``(longitude, latitude)`` pair in decimal degrees.

    Raises:
        KeyError: If the row is missing one of the keys.
        ValueError: If a piece of the coordinate is not a number.

    Examples:
        >>> row = {
        ...     "long_deg": "105", "long_min": "5", "long_sec": "10",
        ...     "lat_deg": "40", "lat_min": "33", "lat_sec": "32",
        ... }
        >>> lon, lat = to_point(row)
        >>> round(lon, 4), round(lat, 4)
        (-105.0861, 40.5589)
    """
    x = convert_coords(row["long_deg"], row["long_min"], row["long_sec"])
    y = convert_coords(row["lat_deg"], row["lat_min"], row["lat_sec"])
    if x > 0:
        x = -x
    return x, y
