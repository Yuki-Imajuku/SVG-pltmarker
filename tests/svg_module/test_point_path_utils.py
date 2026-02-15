import pytest

from svg_pltmarker.svg_module._point_path_utils import normalize_number_token, point_list_to_path


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("21.", "21"),
        ("0.", "0"),
        ("21.0", "21.0"),
        ("1e2", "1e2"),
        ("-.5", "-.5"),
    ],
    ids=["trailing-dot", "zero-dot", "decimal", "exponent", "signed-fraction"],
)
def test_normalize_number_token(value: str, expected: str) -> None:
    assert normalize_number_token(value) == expected


@pytest.mark.parametrize(
    ("points", "element_name", "closed_flag", "expected"),
    [
        ("1e2,0 2e2,1e1", "polyline", 0, "M 1e2,0 L 2e2,1e1"),
        ("150,0", "polygon", 1, "M 150,0 Z"),
        (" 0,0\n 10,10\t20,20 ", "polyline", 0, "M 0,0 L 10,10 L 20,20"),
        ("+21.,-90 79-90.", "polygon", 1, "M +21,-90 L 79,-90 Z"),
    ],
    ids=["exponent", "single-pair-closed", "mixed-whitespace", "adjacent-sign"],
)
def test_point_list_to_path_valid(points: str, element_name: str, closed_flag: int, expected: str) -> None:
    assert point_list_to_path(points, element_name=element_name, closed=bool(closed_flag)) == expected


@pytest.mark.parametrize(
    ("points", "element_name", "invalid_char"),
    [
        ("0,100;50,25", "polyline", ";"),
        ("0,100 50,25x", "polygon", "x"),
        ("0,100 @ 50,25", "polyline", "@"),
    ],
    ids=["invalid-separator", "invalid-trailing", "invalid-token"],
)
def test_point_list_to_path_reject_invalid_character(points: str, element_name: str, invalid_char: str) -> None:
    with pytest.raises(
        ValueError,
        match=rf"Invalid {element_name} points: contains invalid character '{invalid_char}'\.",
    ):
        point_list_to_path(points, element_name=element_name, closed=False)


@pytest.mark.parametrize(
    ("points", "expected_message"),
    [
        ("0,100 50", r"Invalid polyline points: x/y pairs are required\."),
        ("", r"Invalid polyline points: at least 1 pair is required\."),
    ],
    ids=["odd-count", "empty"],
)
def test_point_list_to_path_reject_invalid_count(points: str, expected_message: str) -> None:
    with pytest.raises(ValueError, match=expected_message):
        point_list_to_path(points, element_name="polyline", closed=False)
