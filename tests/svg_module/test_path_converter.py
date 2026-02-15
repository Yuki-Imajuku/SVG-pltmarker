"""Tests for SVG path conversion helpers."""

import re

import numpy as np
import pytest
from matplotlib.path import Path

from svg_pltmarker import PathConverter, get_marker_from_svg


def test_validate_point_count() -> None:
    PathConverter._validate_point_count([1.0, 2.0, 3.0, 4.0], "MoveTo", 2, 2)


@pytest.mark.parametrize(
    ("points", "minimum", "expected_message"),
    [
        ([1.0, 2.0, 3.0], 2, "MoveTo command requires point count to be a multiple of 2"),
        ([1.0, 2.0], 4, "MoveTo command requires at least 4 values"),
    ],
    ids=["invalid-multiple", "invalid-minimum"],
)
def test_validate_point_count_invalid(points: list[float], minimum: int, expected_message: str) -> None:
    with pytest.raises(ValueError, match=expected_message):
        PathConverter._validate_point_count(points, "MoveTo", 2, minimum)


@pytest.mark.parametrize(
    ("command_payload", "expected"),
    [
        (" 1e2, -2.5e-1 , .5 ", [100.0, -0.25, 0.5]),
        ("1-2", [1.0, -2.0]),
        ("+.5E+1 -.25", [5.0, -0.25]),
        ("", []),
    ],
    ids=["exponent", "adjacent-sign", "upper-exponent", "empty"],
)
def test_parse_path_numbers_valid(command_payload: str, expected: list[float]) -> None:
    assert PathConverter._parse_path_numbers(command_payload) == expected


@pytest.mark.parametrize(
    ("command_payload", "invalid_char"),
    [
        ("1;2", ";"),
        ("1,2x", "x"),
        ("1,2@", "@"),
    ],
    ids=["invalid-separator", "invalid-trailing", "invalid-token"],
)
def test_parse_path_numbers_reject_invalid_character(command_payload: str, invalid_char: str) -> None:
    with pytest.raises(ValueError, match=rf"Invalid SVG path command: {re.escape(invalid_char)}"):
        PathConverter._parse_path_numbers(command_payload)


@pytest.mark.parametrize(
    ("command_payload", "expected"),
    [
        ("10,10 0 0,1 20,30", [10.0, 10.0, 0.0, 0.0, 1.0, 20.0, 30.0]),
        ("10,10 0 01 20,30", [10.0, 10.0, 0.0, 0.0, 1.0, 20.0, 30.0]),
        ("10,10 0 10 20,30", [10.0, 10.0, 0.0, 1.0, 0.0, 20.0, 30.0]),
    ],
    ids=["comma-separated-flags", "adjacent-flags-01", "adjacent-flags-10"],
)
def test_parse_arc_numbers_valid(command_payload: str, expected: list[float]) -> None:
    assert PathConverter._parse_arc_numbers(command_payload) == expected


@pytest.mark.parametrize(
    ("command_payload", "invalid_char"),
    [
        ("10,10 0 2,1 20,30", "2"),
        ("10,10 0 0;1 20,30", ";"),
    ],
    ids=["invalid-flag", "invalid-flag-separator"],
)
def test_parse_arc_numbers_reject_invalid_flag(command_payload: str, invalid_char: str) -> None:
    with pytest.raises(ValueError, match=rf"Invalid SVG path command: {re.escape(invalid_char)}"):
        PathConverter._parse_arc_numbers(command_payload)


@pytest.mark.parametrize(
    ("command_payload", "expected"),
    [
        ("10,10 0", [10.0, 10.0, 0.0]),
        ("10,10 0 0,1", [10.0, 10.0, 0.0, 0.0, 1.0]),
    ],
    ids=["missing-flags", "missing-endpoint"],
)
def test_parse_arc_numbers_incomplete_segment_returns_partial_values(
    command_payload: str,
    expected: list[float],
) -> None:
    assert PathConverter._parse_arc_numbers(command_payload) == expected


def test_parse_arc_numbers_reject_invalid_number_start() -> None:
    with pytest.raises(ValueError, match=r"Invalid SVG path command: x"):
        PathConverter._parse_arc_numbers("x")


def test_extract_command_strings() -> None:
    command_str_list = PathConverter._extract_command_strings("M 0,0 L 10,10 H 20 V 30 C 1,1 2,2 3,3 4,4 5,5 6,6 Z")
    assert command_str_list == [
        "M 0,0",
        "L 10,10",
        "H 20",
        "V 30",
        "C 1,1 2,2 3,3 4,4 5,5 6,6",
        "Z",
    ]


def test_extract_command_strings_without_commands() -> None:
    with pytest.raises(ValueError, match="No command found"):
        PathConverter._extract_command_strings("0,0 10,10")


def test_normalize_vertices() -> None:
    path = PathConverter._normalize_vertices(
        [[0.0, 0.0], [2.0, 2.0]],
        [Path.MOVETO, Path.LINETO],
    )
    assert np.asarray(path.vertices).tolist() == [[-0.5, 0.5], [0.5, -0.5]]


def test_normalize_vertices_with_zero_size() -> None:
    path = PathConverter._normalize_vertices([[1.0, 2.0]], [Path.MOVETO])
    assert np.asarray(path.vertices).tolist() == [[0.0, 0.0]]


def test_convert_move_to_with_absolute_and_relative_points() -> None:
    absolute_vertices, absolute_codes, absolute_pos, absolute_command, absolute_points = PathConverter._convert_move_to(
        [5.0, 10.0, 20.0, 30.0],
        is_absolute=True,
        cur_pos=0.0 + 0.0j,
    )
    assert absolute_vertices == [[5.0, 10.0], [20.0, 30.0]]
    assert absolute_codes == [Path.MOVETO, Path.LINETO]
    assert absolute_pos == 20.0 + 30.0j
    assert absolute_command == "L"
    assert absolute_points == []

    relative_vertices, relative_codes, relative_pos, relative_command, relative_points = PathConverter._convert_move_to(
        [1.0, 2.0, 3.0, 4.0],
        is_absolute=False,
        cur_pos=1.0 + 1.0j,
    )
    assert relative_vertices == [[2.0, 3.0], [5.0, 7.0]]
    assert relative_codes == [Path.MOVETO, Path.LINETO]
    assert relative_pos == 5.0 + 7.0j
    assert relative_command == "L"
    assert relative_points == []


def test_convert_line_to_with_absolute_and_relative_points() -> None:
    absolute_vertices, absolute_codes, absolute_pos, _, _ = PathConverter._convert_line_to(
        [0.0, 10.0, 20.0, 30.0],
        is_absolute=True,
        cur_pos=5.0 + 5.0j,
    )
    assert absolute_vertices == [[0.0, 10.0], [20.0, 30.0]]
    assert absolute_codes == [Path.LINETO, Path.LINETO]
    assert absolute_pos == 20.0 + 30.0j

    relative_vertices, relative_codes, relative_pos, _, _ = PathConverter._convert_line_to(
        [2.0, 3.0, 4.0, 5.0],
        is_absolute=False,
        cur_pos=1.0 + 1.0j,
    )
    assert relative_vertices == [[3.0, 4.0], [7.0, 9.0]]
    assert relative_codes == [Path.LINETO, Path.LINETO]
    assert relative_pos == 7.0 + 9.0j


def test_convert_horizontal_and_vertical_line_to_with_absolute_and_relative_points() -> None:
    horizontal_absolute, horizontal_codes, horizontal_absolute_pos, _, _ = PathConverter._convert_horizontal_line_to(
        [10.0, -5.0],
        is_absolute=True,
        cur_pos=3.0 + 7.0j,
    )
    assert horizontal_absolute == [[10.0, 7.0], [-5.0, 7.0]]
    assert horizontal_codes == [Path.LINETO, Path.LINETO]
    assert horizontal_absolute_pos == -5.0 + 7.0j

    horizontal_relative, _, horizontal_relative_pos, _, _ = PathConverter._convert_horizontal_line_to(
        [2.0, -3.0],
        is_absolute=False,
        cur_pos=3.0 + 7.0j,
    )
    assert horizontal_relative == [[5.0, 7.0], [2.0, 7.0]]
    assert horizontal_relative_pos == 2.0 + 7.0j

    vertical_absolute, _, vertical_absolute_pos, _, _ = PathConverter._convert_vertical_line_to(
        [4.0, -2.0],
        is_absolute=True,
        cur_pos=3.0 + 7.0j,
    )
    assert vertical_absolute == [[3.0, 4.0], [3.0, -2.0]]
    assert vertical_absolute_pos == 3.0 - 2.0j

    vertical_relative, _, vertical_relative_pos, _, _ = PathConverter._convert_vertical_line_to(
        [2.0, -1.0],
        is_absolute=False,
        cur_pos=3.0 + 7.0j,
    )
    assert vertical_relative == [[3.0, 9.0], [3.0, 8.0]]
    assert vertical_relative_pos == 3.0 + 8.0j


def test_convert_curve4_absolute_and_relative() -> None:
    absolute_vertices, absolute_codes, absolute_pos, absolute_command, absolute_points = PathConverter._convert_curve4(
        [1.0, 2.0, 3.0, 4.0, 5.0, 6.0],
        is_absolute=True,
        cur_pos=0.0 + 0.0j,
    )
    assert absolute_vertices == [[1.0, 2.0], [3.0, 4.0], [5.0, 6.0]]
    assert absolute_codes == [Path.CURVE4] * 3
    assert absolute_pos == 5.0 + 6.0j
    assert absolute_command == "C"
    assert absolute_points == [1.0, 2.0, 3.0, 4.0, 5.0, 6.0]

    relative_vertices, _, relative_pos, relative_command, relative_points = PathConverter._convert_curve4(
        [1.0, 1.0, 2.0, 2.0, 3.0, 3.0],
        is_absolute=False,
        cur_pos=1.0 + 1.0j,
    )
    assert relative_vertices == [[2.0, 2.0], [3.0, 3.0], [4.0, 4.0]]
    assert relative_pos == 4.0 + 4.0j
    assert relative_command == "C"
    assert relative_points == [2.0, 2.0, 3.0, 3.0, 4.0, 4.0]


def test_convert_smooth_curve4_reflects_previous_control_point() -> None:
    vertices, codes, pos, command, points = PathConverter._convert_smooth_curve4(
        [10.0, 11.0, 12.0, 13.0],
        is_absolute=True,
        cur_pos=0.0 + 0.0j,
        before_command="C",
        before_points=[1.0, 2.0, 3.0, 4.0, 5.0, 6.0],
    )
    assert vertices == [[7.0, 8.0], [10.0, 11.0], [12.0, 13.0]]
    assert codes == [Path.CURVE4, Path.CURVE4, Path.CURVE4]
    assert pos == 12.0 + 13.0j
    assert command == "C"
    assert points == [7.0, 8.0, 10.0, 11.0, 12.0, 13.0]


def test_convert_smooth_curve4_reflects_previous_control_point_relative() -> None:
    vertices, codes, pos, command, points = PathConverter._convert_smooth_curve4(
        [1.0, 2.0, 3.0, 4.0],
        is_absolute=False,
        cur_pos=10.0 + 10.0j,
        before_command="C",
        before_points=[1.0, 2.0, 3.0, 4.0, 5.0, 6.0],
    )
    assert vertices == [[7.0, 8.0], [11.0, 12.0], [13.0, 14.0]]
    assert codes == [Path.CURVE4, Path.CURVE4, Path.CURVE4]
    assert pos == 13.0 + 14.0j
    assert command == "C"
    assert points == [7.0, 8.0, 11.0, 12.0, 13.0, 14.0]

    vertices_without_control, _, _, _, _ = PathConverter._convert_smooth_curve4(
        [8.0, 9.0, 10.0, 11.0],
        is_absolute=True,
        cur_pos=1.0 + 2.0j,
        before_command="L",
        before_points=[],
    )
    assert vertices_without_control == [[1.0, 2.0], [8.0, 9.0], [10.0, 11.0]]


def test_convert_smooth_curve4_with_invalid_before_points() -> None:
    with pytest.raises(ValueError, match="Invalid before_points for SmoothCurveTo"):
        PathConverter._convert_smooth_curve4(
            [1.0, 2.0, 3.0, 4.0],
            is_absolute=False,
            cur_pos=1.0 + 1.0j,
            before_command="C",
            before_points=[1.0, 2.0, 3.0],
        )


def test_convert_curve3_absolute_and_relative() -> None:
    absolute_vertices, absolute_codes, absolute_pos, absolute_command, absolute_points = PathConverter._convert_curve3(
        [1.0, 2.0, 3.0, 4.0],
        is_absolute=True,
        cur_pos=0.0 + 0.0j,
    )
    assert absolute_vertices == [[1.0, 2.0], [3.0, 4.0]]
    assert absolute_codes == [Path.CURVE3] * 2
    assert absolute_pos == 3.0 + 4.0j
    assert absolute_command == "Q"
    assert absolute_points == [1.0, 2.0, 3.0, 4.0]

    relative_vertices, _, relative_pos, _, _ = PathConverter._convert_curve3(
        [2.0, 2.0, 3.0, 4.0],
        is_absolute=False,
        cur_pos=1.0 + 1.0j,
    )
    assert relative_vertices == [[3.0, 3.0], [4.0, 5.0]]
    assert relative_pos == 4.0 + 5.0j


def test_convert_smooth_curve3_reflects_previous_control_point() -> None:
    vertices, codes, pos, command, points = PathConverter._convert_smooth_curve3(
        [10.0, 12.0],
        is_absolute=True,
        cur_pos=6.0 + 6.0j,
        before_command="Q",
        before_points=[1.0, 2.0, 3.0, 4.0],
    )
    assert vertices == [[5.0, 6.0], [10.0, 12.0]]
    assert codes == [Path.CURVE3, Path.CURVE3]
    assert pos == 10.0 + 12.0j
    assert command == "Q"
    assert points == [5.0, 6.0, 10.0, 12.0]

    vertices_without_control, _, _, _, _ = PathConverter._convert_smooth_curve3(
        [8.0, 9.0],
        is_absolute=False,
        cur_pos=1.0 + 2.0j,
        before_command="L",
        before_points=[],
    )
    assert vertices_without_control == [[1.0, 2.0], [9.0, 11.0]]


def test_convert_smooth_curve3_with_invalid_before_points() -> None:
    with pytest.raises(ValueError, match="Invalid before_points for SmoothCurveTo"):
        PathConverter._convert_smooth_curve3(
            [1.0, 2.0],
            is_absolute=False,
            cur_pos=1.0 + 1.0j,
            before_command="Q",
            before_points=[1.0, 2.0, 3.0],
        )


def test_convert_arc_zero_radius_uses_line() -> None:
    vertices, codes, pos, _, _ = PathConverter._convert_arc(
        [0.0, 2.0, 0.0, 1.0, 1.0, 10.0, 20.0],
        is_absolute=True,
        cur_pos=1.0 + 2.0j,
    )
    assert vertices == [[10.0, 20.0]]
    assert codes == [Path.LINETO]
    assert pos == 10.0 + 20.0j


def test_convert_arc_returns_arc_path() -> None:
    vertices, codes, pos, command, points = PathConverter._convert_arc(
        [10.0, 5.0, 0.0, 0.0, 1.0, 20.0, 30.0],
        is_absolute=True,
        cur_pos=0.0 + 0.0j,
    )
    assert len(vertices) == len(codes)
    assert len(vertices) > 1
    assert codes[0] == Path.MOVETO
    assert pos == 20.0 + 30.0j
    assert command == "A"
    assert points == []


def test_convert_arc_with_reverse_arc_rotation() -> None:
    _, reverse_codes, _, command, _ = PathConverter._convert_arc(
        [1.0, 1.0, 0.0, 0.0, 0.0, 10.0, 0.0],
        is_absolute=True,
        cur_pos=0.0 + 0.0j,
    )
    assert command == "A"
    assert reverse_codes[0] == Path.MOVETO


def test_convert_arc_relative_uses_new_position() -> None:
    vertices, codes, pos, command, points = PathConverter._convert_arc(
        [0.0, 2.0, 0.0, 0.0, 1.0, 4.0, -4.0],
        is_absolute=False,
        cur_pos=1.0 + 1.0j,
    )
    assert vertices == [[5.0, -3.0]]
    assert codes == [Path.LINETO]
    assert pos == 5.0 - 3.0j
    assert command == "A"
    assert points == []


def test_convert_close_command() -> None:
    vertices, codes, pos, command, points = PathConverter._convert_close(3.0 + 4.0j)
    assert vertices == [[3.0, 4.0]]
    assert codes == [Path.LINETO]
    assert pos == 3.0 + 4.0j
    assert command == "Z"
    assert points == []


def test_convert_arc_to_path_reverses_negative_delta() -> None:
    forward_vertices, forward_codes = PathConverter._arc_to_path(0.0 + 0.0j, 1.0 + 1.0j, 0.0, 0.0, 90.0)
    reverse_vertices, reverse_codes = PathConverter._arc_to_path(0.0 + 0.0j, 1.0 + 1.0j, 0.0, 0.0, -90.0)
    assert forward_vertices[0] == [1.0, 0.0]
    assert reverse_vertices[0] == [1.0, 0.0]
    assert forward_vertices != reverse_vertices
    assert forward_codes[0] == Path.MOVETO
    assert reverse_codes[0] == Path.MOVETO
    assert reverse_codes == [Path.MOVETO, *([Path.CURVE4] * (len(reverse_vertices) - 1))]
    assert reverse_vertices[-1][1] < 0.0


def test_arc_endpoint_to_center_keeps_phi_in_range_and_handles_degenerate_case() -> None:
    center_zero, theta_zero, delta_zero = PathConverter._arc_endpoint_to_center(
        0.0 + 0.0j,
        0.0 + 0.0j,
        1.0 + 2.0j,
        450.0,
        (True, False),
    )
    assert center_zero == 0.0 + 0.0j
    assert theta_zero == 0.0
    assert delta_zero == 0.0

    center, _, delta = PathConverter._arc_endpoint_to_center(
        0.0 + 0.0j,
        10.0 + 0.0j,
        1.0 + 1.0j,
        45.0,
        (False, False),
    )
    assert center == 5.0 + 0.0j
    assert delta < 0.0


def test_arc_endpoint_to_center_normalizes_positive_delta_when_sweep_is_false(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    angle_values = iter([10.0, 20.0])

    def _mock_angle(*_args: object, **_kwargs: object) -> float:
        return next(angle_values)

    monkeypatch.setattr("svg_pltmarker.path_converter.np.angle", _mock_angle)
    _, _, delta = PathConverter._arc_endpoint_to_center(
        0.0 + 0.0j,
        10.0 + 0.0j,
        5.0 + 5.0j,
        0.0,
        (False, False),
    )
    assert delta == -350.0


def test_svg2plt_full_command_chain() -> None:
    marker = PathConverter.svg2plt("M 0,0 L 10,0 H 20 V 5 C 1,1 2,2 3,3 S 4,4 5,5 Q 6,6 7,7 T 8,8 A 5 3 0 0 1 9,9 Z")
    marker_codes = np.asarray(marker.codes)
    assert marker_codes[0] == Path.MOVETO
    assert marker_codes[-1] == Path.LINETO
    assert np.asarray(marker.vertices).shape[1] == 2


@pytest.mark.parametrize(
    ("svg_path", "expected_message"),
    [
        ("0,0 1,1", "No command found"),
        ("   ", "No command found"),
        ("L 1,1", "First command must be MoveTo"),
    ],
    ids=["no-command", "whitespace-only", "first-not-move"],
)
def test_svg2plt_reject_invalid_initial_input(svg_path: str, expected_message: str) -> None:
    with pytest.raises(ValueError, match=expected_message):
        PathConverter.svg2plt(svg_path)


def test_svg2plt_reject_invalid_command_character() -> None:
    with pytest.raises(ValueError, match="Invalid SVG path command: X"):
        PathConverter.svg2plt("M 0,0 X 1,1")


def test_svg2plt_reject_unregistered_command_handler(monkeypatch: pytest.MonkeyPatch) -> None:
    def _mock_extract_command_strings(_cls: type[PathConverter], _svg_path: str) -> list[str]:
        return ["M 0,0", "R 1,1"]

    monkeypatch.setattr(PathConverter, "_extract_command_strings", classmethod(_mock_extract_command_strings))
    with pytest.raises(ValueError, match="Invalid SVG path command: R"):
        PathConverter.svg2plt("M 0,0 R 1,1")


@pytest.mark.parametrize(
    ("svg_path", "invalid_char"),
    [
        ("M 0,0;1,1", ";"),
        ("M 0,0 e 1,1", "e"),
        ("M 0,0 @ 1,1", "@"),
    ],
    ids=["semicolon", "stray-letter", "stray-symbol"],
)
def test_svg2plt_reject_invalid_separator_character(svg_path: str, invalid_char: str) -> None:
    with pytest.raises(ValueError, match=rf"Invalid SVG path command: {re.escape(invalid_char)}"):
        PathConverter.svg2plt(svg_path)


def test_svg2plt_reject_following_close_with_non_move() -> None:
    with pytest.raises(ValueError, match="Invalid SVG path as Z is not followed by M"):
        PathConverter.svg2plt("M 0,0 Z L 1,0")


def test_svg2plt_allows_move_after_close() -> None:
    marker = PathConverter.svg2plt("M 0,0 L 1,0 Z M 2,0 L 3,0")
    assert np.asarray(marker.codes).tolist() == [Path.MOVETO, Path.LINETO, Path.LINETO, Path.MOVETO, Path.LINETO]


def test_svg2plt_with_relative_commands() -> None:
    marker = PathConverter.svg2plt("m 0,0 l 10,0 h 10 v 10")
    assert np.asarray(marker.codes).tolist() == [Path.MOVETO, Path.LINETO, Path.LINETO, Path.LINETO]


@pytest.mark.parametrize(
    "svg_path",
    [
        "M 0,0 A 10,10 0 1,1 10,0",
        "M 0,0 A 10,10 0 11 10,0",
        "M 0,0 A 10,10 0 01 10,0",
    ],
    ids=["comma-separated-flags", "adjacent-flags-11", "adjacent-flags-01"],
)
def test_svg2plt_with_large_arc_flag(svg_path: str) -> None:
    marker = PathConverter.svg2plt(svg_path)
    marker_codes = np.asarray(marker.codes).tolist()
    assert marker_codes[0] == Path.MOVETO
    assert Path.CURVE4 in marker_codes


def test_svg2plt_with_exponent_numbers() -> None:
    marker = PathConverter.svg2plt("M 1e2,0 L 2e2,1e1")
    assert np.asarray(marker.codes).tolist() == [Path.MOVETO, Path.LINETO]


def test_svg2plt_close_uses_first_move_to_position() -> None:
    marker = PathConverter.svg2plt("M 0,0 1,0 Z")
    marker_vertices = np.asarray(marker.vertices)
    assert marker_vertices[0].tolist() == [-0.5, 0.0]
    assert marker_vertices[-1].tolist() == [-0.5, 0.0]


def test_svg2plt_invalid_point_count() -> None:
    with pytest.raises(ValueError, match="LineTo command requires point count to be a multiple of 2"):
        PathConverter.svg2plt("M 0,0 L 1")


def test_get_marker_from_svg() -> None:
    marker = get_marker_from_svg(svgstr='<svg xmlns="http://www.w3.org/2000/svg"><path d="M 0,0 L 1,1"/></svg>')
    assert isinstance(marker, Path)
    assert np.asarray(marker.codes)[0] == Path.MOVETO
