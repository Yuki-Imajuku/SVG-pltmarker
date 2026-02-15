"""Internal helpers for point-list based SVG elements."""

import re

from svg_pltmarker.consts import PATH_NUMBER_PATTERN, POINT_PAIR_COUNT


def normalize_number_token(value: str) -> str:
    """Normalize SVG number tokens."""
    if value.endswith("."):
        return value[:-1]
    return value


def point_list_to_path(points: str, *, element_name: str, closed: bool) -> str:
    """Convert a point-list string into an SVG path command string."""
    matches = list(re.finditer(PATH_NUMBER_PATTERN, points))
    cursor = 0
    for match in matches:
        separator = points[cursor : match.start()]
        invalid = re.search(r"[^\s,]", separator)
        if invalid is not None:
            msg = f"Invalid {element_name} points: contains invalid character '{invalid.group()}'."
            raise ValueError(msg)
        cursor = match.end()
    invalid = re.search(r"[^\s,]", points[cursor:])
    if invalid is not None:
        msg = f"Invalid {element_name} points: contains invalid character '{invalid.group()}'."
        raise ValueError(msg)

    points_list = [match.group() for match in matches]
    if len(points_list) % POINT_PAIR_COUNT != 0:
        msg = f"Invalid {element_name} points: x/y pairs are required."
        raise ValueError(msg)
    if len(points_list) < POINT_PAIR_COUNT:
        # SVG 1.1 allows a single coordinate pair for polyline/polygon points.
        msg = f"Invalid {element_name} points: at least 1 pair is required."
        raise ValueError(msg)

    normalized = [normalize_number_token(value) for value in points_list]
    commands = [f"M {normalized[0]},{normalized[1]}"]
    commands.extend(
        f"L {normalized[index]},{normalized[index + 1]}"
        for index in range(POINT_PAIR_COUNT, len(normalized), POINT_PAIR_COUNT)
    )

    if closed:
        commands.append("Z")
    return " ".join(commands)
