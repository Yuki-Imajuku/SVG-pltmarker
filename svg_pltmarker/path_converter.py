"""Utilities for converting SVG paths into matplotlib markers."""

import re
from collections.abc import Callable

import numpy as np
from matplotlib.path import Path
from matplotlib.transforms import Affine2D

from svg_pltmarker.consts import (
    PATH_ARC_ANGLE_INDEX,
    PATH_ARC_END_X_INDEX,
    PATH_ARC_END_Y_INDEX,
    PATH_ARC_FLAG_LARGE_INDEX,
    PATH_ARC_FLAG_SWEEP_INDEX,
    PATH_ARC_POINTS,
    PATH_ARC_RADIUS_X_INDEX,
    PATH_ARC_RADIUS_Y_INDEX,
    PATH_COMMAND_PATTERN,
    PATH_COMMAND_POINTS,
    PATH_CURVE3_POINTS,
    PATH_CURVE4_POINTS,
    PATH_FULL_ROTATION_DEGREE,
    PATH_NUMBER_PATTERN,
)
from svg_pltmarker.svg_module import SVGObject

PathCommand = tuple[
    list[list[float]],  # vertices list
    list[np.uint8],  # codes list
    complex,  # current position
    str,  # before command
    list[float],  # before points list used in before command
]
PathCommandHandler = Callable[..., PathCommand]


class PathConverter:
    """A class to convert SVG path to matplotlib path."""

    @staticmethod
    def _validate_point_count(points_list: list[float], command: str, stride: int, minimum: int) -> None:
        if len(points_list) % stride != 0:
            msg = f"{command} command requires point count to be a multiple of {stride}."
            raise ValueError(msg)
        if len(points_list) < minimum:
            msg = f"{command} command requires at least {minimum} values."
            raise ValueError(msg)

    @staticmethod
    def _parse_number_at(command_payload: str, cursor: int) -> tuple[float, int]:
        match = re.match(PATH_NUMBER_PATTERN, command_payload[cursor:])
        if match is None:
            msg = f"Invalid SVG path command: {command_payload[cursor]}"
            raise ValueError(msg)
        return float(match.group()), cursor + len(match.group())

    @staticmethod
    def _skip_separators(command_payload: str, cursor: int) -> int:
        while cursor < len(command_payload) and command_payload[cursor] in ", \t\r\n":
            cursor += 1
        return cursor

    @staticmethod
    def _parse_path_numbers(command_payload: str) -> list[float]:
        matches = list(re.finditer(PATH_NUMBER_PATTERN, command_payload))
        cursor = 0
        for match in matches:
            separator = command_payload[cursor : match.start()]
            invalid = re.search(r"[^\s,]", separator)
            if invalid is not None:
                msg = f"Invalid SVG path command: {invalid.group()}"
                raise ValueError(msg)
            cursor = match.end()
        invalid = re.search(r"[^\s,]", command_payload[cursor:])
        if invalid is not None:
            msg = f"Invalid SVG path command: {invalid.group()}"
            raise ValueError(msg)
        return [float(match.group()) for match in matches]

    @classmethod
    def _parse_arc_numbers(cls, command_payload: str) -> list[float]:
        values: list[float] = []
        cursor = 0

        while True:
            cursor = cls._skip_separators(command_payload, cursor)
            if cursor >= len(command_payload):
                return values

            # Arc parameter order:
            # rx ry x-axis-rotation large-arc-flag sweep-flag x y
            for _ in range(3):
                value, cursor = cls._parse_number_at(command_payload, cursor)
                values.append(value)
                cursor = cls._skip_separators(command_payload, cursor)

            for _ in range(2):
                cursor = cls._skip_separators(command_payload, cursor)
                if cursor >= len(command_payload):
                    return values
                flag = command_payload[cursor]
                if flag not in {"0", "1"}:
                    msg = f"Invalid SVG path command: {flag}"
                    raise ValueError(msg)
                values.append(float(flag))
                cursor += 1

            for _ in range(2):
                cursor = cls._skip_separators(command_payload, cursor)
                if cursor >= len(command_payload):
                    return values
                value, cursor = cls._parse_number_at(command_payload, cursor)
                values.append(value)

    @classmethod
    def _extract_command_strings(cls, svg_path: str) -> list[str]:
        command_indices = [match.start() for match in re.finditer(PATH_COMMAND_PATTERN, svg_path)]
        if not command_indices:
            msg = "No command found"
            raise ValueError(msg)
        command_indices.append(len(svg_path))
        return [
            svg_path[command_indices[idx] : command_indices[idx + 1]].strip() for idx in range(len(command_indices) - 1)
        ]

    @staticmethod
    def _normalize_vertices(
        vertices_list: list[list[float]],
        codes_list: list[np.uint8],
    ) -> Path:
        """Convert to matplotlib path.

        Normalize the path to [-0.5, 0.5] x [-0.5, 0.5] while keeping the aspect ratio.
        Flip the y-axis because of below reasons:
        Matplotlib: 'O' is the bottom-left corner, SVG: 'O' is the top-left corner
        """
        vertices = np.array(vertices_list)
        codes = np.array(codes_list, dtype=np.uint8)
        min_x, max_x = np.min(vertices[:, 0]), np.max(vertices[:, 0])
        min_y, max_y = np.min(vertices[:, 1]), np.max(vertices[:, 1])
        center_x, center_y = (max_x + min_x) / 2, (max_y + min_y) / 2
        size = max(max_x - min_x, max_y - min_y)
        if size == 0:
            size = 1

        vertices[:, 0] = (vertices[:, 0] - center_x) / size
        vertices[:, 1] = (center_y - vertices[:, 1]) / size
        return Path(vertices=vertices, codes=codes, closed=False, readonly=True)

    @classmethod
    def svg2plt(cls, svg_path: str) -> Path:
        """Convert SVG path to matplotlib path.

        Args:
            svg_path (str): SVG path.

        Returns:
            Path: Matplotlib path.

        """
        command_str_list = cls._extract_command_strings(svg_path)
        if command_str_list[0][0].upper() != "M":
            msg = "First command must be MoveTo"
            raise ValueError(msg)
        command_handlers: dict[str, PathCommandHandler] = {
            "M": cls._convert_move_to,
            "L": cls._convert_line_to,
            "H": cls._convert_horizontal_line_to,
            "V": cls._convert_vertical_line_to,
            "C": cls._convert_curve4,
            "Q": cls._convert_curve3,
            "A": cls._convert_arc,
        }
        smooth_command_handlers: dict[str, PathCommandHandler] = {
            "S": cls._convert_smooth_curve4,
            "T": cls._convert_smooth_curve3,
        }

        vertices_list: list[list[float]] = []
        codes_list: list[np.uint8] = []

        # Find all commands in the path
        start_pos = 0 + 0j  # Start position
        cur_pos = start_pos  # Current position
        before_command = ""  # Before command
        before_points: list[float] = []  # Before points list used in before_command

        for command_str in command_str_list:
            svg_command = command_str[0].upper()
            is_absolute = command_str[0].isupper()
            if before_command == "Z" and svg_command != "M":
                msg = "Invalid SVG path as Z is not followed by M"
                raise ValueError(msg)
            if svg_command == "A":
                points_list = cls._parse_arc_numbers(command_str[1:])
            else:
                points_list = cls._parse_path_numbers(command_str[1:])
            # Convert to matplotlib path
            if svg_command == "Z":
                new_vertices, new_codes, cur_pos, before_command, before_points = cls._convert_close(start_pos)
            elif svg_command in smooth_command_handlers:
                convert = smooth_command_handlers[svg_command]
                new_vertices, new_codes, cur_pos, before_command, before_points = convert(
                    points_list,
                    is_absolute=is_absolute,
                    cur_pos=cur_pos,
                    before_command=before_command,
                    before_points=before_points,
                )
            else:
                convert = command_handlers.get(svg_command)
                if convert is None:
                    msg = f"Invalid SVG path command: {svg_command}"
                    raise ValueError(msg)
                new_vertices, new_codes, cur_pos, before_command, before_points = convert(
                    points_list,
                    is_absolute=is_absolute,
                    cur_pos=cur_pos,
                )

            vertices_list.extend(new_vertices)
            codes_list.extend(new_codes)

            if svg_command == "M":
                start_pos = new_vertices[0][0] + new_vertices[0][1] * 1j

        return cls._normalize_vertices(vertices_list=vertices_list, codes_list=codes_list)

    @staticmethod
    def _convert_move_to(
        points_list: list[float],
        *,
        is_absolute: bool,
        cur_pos: complex,
    ) -> PathCommand:
        """Convert SVG MoveTo (M/m) to matplotlib move."""
        PathConverter._validate_point_count(points_list, "MoveTo", PATH_COMMAND_POINTS, PATH_COMMAND_POINTS)

        vertices_list: list[list[float]] = []
        codes_list: list[np.uint8] = []
        new_pos = cur_pos
        # First point
        if is_absolute:  # M
            new_pos = points_list[0] + points_list[1] * 1j
        else:  # m
            new_pos += points_list[0] + points_list[1] * 1j
        vertices_list.append([new_pos.real, new_pos.imag])
        codes_list.append(Path.MOVETO)

        for idx in range(PATH_COMMAND_POINTS, len(points_list), PATH_COMMAND_POINTS):
            if is_absolute:  # M (consider as L)
                new_pos = points_list[idx] + points_list[idx + 1] * 1j
            else:  # m (consider as l)
                new_pos += points_list[idx] + points_list[idx + 1] * 1j
            vertices_list.append([new_pos.real, new_pos.imag])
            codes_list.append(Path.LINETO)

        return vertices_list, codes_list, new_pos, "L", []

    @staticmethod
    def _convert_line_to(
        points_list: list[float],
        *,
        is_absolute: bool,
        cur_pos: complex,
    ) -> PathCommand:
        """Convert SVG LineTo (L/l) to matplotlib line."""
        PathConverter._validate_point_count(points_list, "LineTo", PATH_COMMAND_POINTS, PATH_COMMAND_POINTS)

        vertices_list: list[list[float]] = []
        codes_list: list[np.uint8] = []
        new_pos = cur_pos

        # All points are considered as LineTo
        for idx in range(0, len(points_list), PATH_COMMAND_POINTS):
            if is_absolute:  # L
                new_pos = points_list[idx] + points_list[idx + 1] * 1j
            else:  # l
                new_pos += points_list[idx] + points_list[idx + 1] * 1j
            vertices_list.append([new_pos.real, new_pos.imag])
            codes_list.append(Path.LINETO)

        return vertices_list, codes_list, new_pos, "L", []

    @staticmethod
    def _convert_horizontal_line_to(
        points_list: list[float],
        *,
        is_absolute: bool,
        cur_pos: complex,
    ) -> PathCommand:
        """Convert SVG HorizontalLineTo (H/h) to matplotlib line."""
        PathConverter._validate_point_count(points_list, "HorizontalLineTo", 1, 1)

        vertices_list: list[list[float]] = []
        codes_list: list[np.uint8] = []
        new_pos = cur_pos

        # All points are considered as LineTo
        for point in points_list:
            if is_absolute:  # H
                new_pos = point + cur_pos.imag * 1j
            else:  # h
                new_pos += point
            vertices_list.append([new_pos.real, new_pos.imag])
            codes_list.append(Path.LINETO)

        return vertices_list, codes_list, new_pos, "L", []

    @staticmethod
    def _convert_vertical_line_to(
        points_list: list[float],
        *,
        is_absolute: bool,
        cur_pos: complex,
    ) -> PathCommand:
        """Convert SVG VerticalLineTo (V/v) to matplotlib line."""
        PathConverter._validate_point_count(points_list, "VerticalLineTo", 1, 1)

        vertices_list: list[list[float]] = []
        codes_list: list[np.uint8] = []
        new_pos = cur_pos

        # All points are considered as LineTo
        for point in points_list:
            if is_absolute:  # V
                new_pos = cur_pos.real + point * 1j
            else:  # v
                new_pos += point * 1j
            vertices_list.append([new_pos.real, new_pos.imag])
            codes_list.append(Path.LINETO)

        return vertices_list, codes_list, new_pos, "L", []

    @staticmethod
    def _convert_curve4(
        points_list: list[float],
        *,
        is_absolute: bool,
        cur_pos: complex,
    ) -> PathCommand:
        """Convert SVG CurveTo (C/c) to matplotlib curve."""

        def to_vertices(
            control_pos1: complex,
            control_pos2: complex,
            new_pos_local: complex,
        ) -> list[list[float]]:
            return [
                [control_pos1.real, control_pos1.imag],
                [control_pos2.real, control_pos2.imag],
                [new_pos_local.real, new_pos_local.imag],
            ]

        def to_command_points(
            control_pos1: complex,
            control_pos2: complex,
            new_pos_local: complex,
        ) -> list[float]:
            return [
                control_pos1.real,
                control_pos1.imag,
                control_pos2.real,
                control_pos2.imag,
                new_pos_local.real,
                new_pos_local.imag,
            ]

        PathConverter._validate_point_count(points_list, "CurveTo", PATH_CURVE4_POINTS, PATH_CURVE4_POINTS)

        vertices_list: list[list[float]] = []
        codes_list: list[np.uint8] = []
        new_pos = cur_pos
        new_points: list[float] = []

        # All points are considered as CurveTo (represented by 3 points)
        for idx in range(0, len(points_list), PATH_CURVE4_POINTS):
            if is_absolute:
                control_pos1 = points_list[idx] + points_list[idx + 1] * 1j
                control_pos2 = points_list[idx + 2] + points_list[idx + 3] * 1j
                new_pos = points_list[idx + 4] + points_list[idx + 5] * 1j
            else:
                control_pos1 = new_pos + points_list[idx] + points_list[idx + 1] * 1j
                control_pos2 = new_pos + points_list[idx + 2] + points_list[idx + 3] * 1j
                new_pos += points_list[idx + 4] + points_list[idx + 5] * 1j
            vertices_list.extend(to_vertices(control_pos1, control_pos2, new_pos))
            codes_list.extend([Path.CURVE4] * 3)
            new_points = to_command_points(control_pos1, control_pos2, new_pos)

        return vertices_list, codes_list, new_pos, "C", new_points

    @staticmethod
    def _convert_smooth_curve4(
        points_list: list[float],
        *,
        is_absolute: bool,
        cur_pos: complex,
        before_command: str,
        before_points: list[float],
    ) -> PathCommand:
        """Convert SVG SmoothCurveTo (S/s) to matplotlib curve."""

        def to_vertices(
            control_pos1: complex,
            control_pos2: complex,
            new_pos_local: complex,
        ) -> list[list[float]]:
            return [
                [control_pos1.real, control_pos1.imag],
                [control_pos2.real, control_pos2.imag],
                [new_pos_local.real, new_pos_local.imag],
            ]

        def to_command_points(
            control_pos1: complex,
            control_pos2: complex,
            new_pos_local: complex,
        ) -> list[float]:
            return [
                control_pos1.real,
                control_pos1.imag,
                control_pos2.real,
                control_pos2.imag,
                new_pos_local.real,
                new_pos_local.imag,
            ]

        PathConverter._validate_point_count(
            points_list, "SmoothCurveTo", PATH_COMMAND_POINTS * 2, PATH_COMMAND_POINTS * 2
        )

        vertices_list: list[list[float]] = []
        codes_list: list[np.uint8] = []
        new_pos = cur_pos
        new_command = before_command
        new_points = before_points

        # All points are considered as CurveTo (represented by 3 points)
        for idx in range(0, len(points_list), PATH_CURVE3_POINTS):
            control_pos1 = new_pos  # Regard start_pos as control_pos1
            if new_command == "C":  # Reflect control_pos2 of the previous curve
                if len(new_points) != PATH_CURVE4_POINTS:
                    msg = "Invalid before_points for SmoothCurveTo"
                    raise ValueError(msg)
                start_pos = new_points[4] + new_points[5] * 1j
                before_control_pos2 = new_points[2] + new_points[3] * 1j
                control_pos1 = 2 * start_pos - before_control_pos2

            if is_absolute:  # S
                control_pos2 = points_list[idx] + points_list[idx + 1] * 1j
                new_pos = points_list[idx + 2] + points_list[idx + 3] * 1j
            else:  # s
                control_pos2 = new_pos + points_list[idx] + points_list[idx + 1] * 1j
                new_pos += points_list[idx + 2] + points_list[idx + 3] * 1j
            vertices_list.extend(to_vertices(control_pos1, control_pos2, new_pos))
            codes_list.extend([Path.CURVE4] * 3)
            new_command = "C"
            new_points = to_command_points(control_pos1, control_pos2, new_pos)

        return vertices_list, codes_list, new_pos, new_command, new_points

    @staticmethod
    def _convert_curve3(
        points_list: list[float],
        *,
        is_absolute: bool,
        cur_pos: complex,
    ) -> PathCommand:
        """Convert SVG CurveTo (Q/q) to matplotlib curve."""

        def to_vertices(control_pos: complex, new_pos_local: complex) -> list[list[float]]:
            return [[control_pos.real, control_pos.imag], [new_pos_local.real, new_pos_local.imag]]

        def to_command_points(control_pos: complex, new_pos_local: complex) -> list[float]:
            return [control_pos.real, control_pos.imag, new_pos_local.real, new_pos_local.imag]

        PathConverter._validate_point_count(points_list, "CurveTo", PATH_CURVE3_POINTS, PATH_CURVE3_POINTS)

        vertices_list: list[list[float]] = []
        codes_list: list[np.uint8] = []
        new_pos = cur_pos
        new_points: list[float] = []

        # All points are considered as CurveTo (represented by 2 points)
        for idx in range(0, len(points_list), PATH_CURVE3_POINTS):
            if is_absolute:  # Q
                control_pos = points_list[idx] + points_list[idx + 1] * 1j
                new_pos = points_list[idx + 2] + points_list[idx + 3] * 1j
            else:  # q
                control_pos = new_pos + points_list[idx] + points_list[idx + 1] * 1j
                new_pos += points_list[idx + 2] + points_list[idx + 3] * 1j
            vertices_list.extend(to_vertices(control_pos, new_pos))
            codes_list.extend([Path.CURVE3] * 2)
            new_points = to_command_points(control_pos, new_pos)

        return vertices_list, codes_list, new_pos, "Q", new_points

    @staticmethod
    def _convert_smooth_curve3(
        points_list: list[float],
        *,
        is_absolute: bool,
        cur_pos: complex,
        before_command: str,
        before_points: list[float],
    ) -> PathCommand:
        """Convert SVG SmoothCurveTo (T/t) to matplotlib curve."""

        def to_vertices(control_pos: complex, new_pos_local: complex) -> list[list[float]]:
            return [[control_pos.real, control_pos.imag], [new_pos_local.real, new_pos_local.imag]]

        def to_command_points(control_pos: complex, new_pos_local: complex) -> list[float]:
            return [control_pos.real, control_pos.imag, new_pos_local.real, new_pos_local.imag]

        PathConverter._validate_point_count(points_list, "SmoothCurveTo", PATH_COMMAND_POINTS, PATH_COMMAND_POINTS)

        vertices_list: list[list[float]] = []
        codes_list: list[np.uint8] = []
        new_pos = cur_pos
        new_command = before_command
        new_points = before_points

        # All points are considered as CurveTo (represented by 2 points)
        for idx in range(0, len(points_list), PATH_COMMAND_POINTS):
            control_pos = new_pos  # Regard start_pos as control_pos
            if new_command == "Q":  # Reflect control_pos of the previous curve
                if len(new_points) != PATH_CURVE3_POINTS:
                    msg = "Invalid before_points for SmoothCurveTo"
                    raise ValueError(msg)
                start_pos = new_points[2] + new_points[3] * 1j
                before_control_pos = new_points[0] + new_points[1] * 1j
                control_pos = 2 * start_pos - before_control_pos
            if is_absolute:  # T
                new_pos = points_list[idx] + points_list[idx + 1] * 1j
            else:  # t
                new_pos += points_list[idx] + points_list[idx + 1] * 1j
            vertices_list.extend(to_vertices(control_pos, new_pos))
            codes_list.extend([Path.CURVE3] * 2)
            new_command = "Q"
            new_points = to_command_points(control_pos, new_pos)

        return vertices_list, codes_list, new_pos, new_command, new_points

    @staticmethod
    def _arc_endpoint_to_center(
        start: complex,
        end: complex,
        radius: complex,
        phi_deg: float,
        arc_flags: tuple[bool, bool],
    ) -> tuple[complex, float, float]:
        """Convert arc endpoint parameters to arc center and angle range."""
        large_arc, sweep = arc_flags
        phi_deg %= PATH_FULL_ROTATION_DEGREE  # Normalize phi_deg to [0, 360)
        phi = np.deg2rad(phi_deg)
        # Assumes radius.real != 0 and radius.imag != 0.
        # _convert_arc guards zero radii and treats those segments as LineTo.

        # Step 1: Compute (x1', y1') <- z
        z = np.exp(-1j * phi) * (start - end) / 2
        # Step 2: Compute (cx', cy') <- c
        denom = radius.real**2 * z.imag**2 + radius.imag**2 * z.real**2
        num = max(0.0, radius.real**2 * radius.imag**2 - denom)
        k = np.sqrt(num / denom) if denom > 0 else 0
        if large_arc == sweep:
            k = -k
        center_offset = k * (radius.real / radius.imag * z.imag - 1j * radius.imag / radius.real * z.real)

        # Step 3: Compute (cx, cy) from (cx', cy')
        center = np.exp(1j * phi) * center_offset + (start + end) / 2
        # Step 4: Compute theta1 and delta_theta
        point1 = z - center_offset
        theta1 = np.angle(point1.real / radius.real + 1j * point1.imag / radius.imag, deg=True)  # (-180, 180]
        point2 = -z - center_offset
        theta2 = np.angle(point2.real / radius.real + 1j * point2.imag / radius.imag, deg=True)
        delta_theta = theta2 - theta1  # (-360, 360)
        if theta1 < 0:
            theta1 += PATH_FULL_ROTATION_DEGREE
        if sweep and delta_theta < 0:
            delta_theta += PATH_FULL_ROTATION_DEGREE
        elif not sweep and delta_theta > 0:
            delta_theta -= PATH_FULL_ROTATION_DEGREE

        return center, theta1, delta_theta

    @staticmethod
    def _arc_to_path(
        center: complex,
        radius: complex,
        rotation: float,
        theta1: float,
        delta_theta: float,
    ) -> tuple[list[list[float]], list[np.uint8]]:
        """Convert arc geometry to path vertices and codes."""
        reverse = delta_theta < 0
        unit_arc = Path.arc(theta1 + delta_theta, theta1) if reverse else Path.arc(theta1, theta1 + delta_theta)
        transform = (
            Affine2D()
            .scale(radius.real, radius.imag)
            .translate(center.real, center.imag)
            .rotate_deg_around(center.real, center.imag, rotation)
        )
        arc = transform.transform_path(unit_arc)
        vertices = np.asarray(arc.vertices).tolist()
        codes = np.asarray(arc.codes).tolist()
        codes = [np.uint8(code) for code in codes]
        if reverse:
            # Reverse curve direction while preserving matplotlib's
            # MOVETO + CURVE4* code layout for the reordered vertices.
            vertices = list(reversed(vertices))
            codes = [np.uint8(Path.MOVETO), *([np.uint8(Path.CURVE4)] * (len(vertices) - 1))]
        return vertices, codes

    @staticmethod
    def _convert_arc(
        points_list: list[float],
        *,
        is_absolute: bool,
        cur_pos: complex,
    ) -> PathCommand:
        """Convert SVG ArcTo (A/a) to matplotlib arc."""
        PathConverter._validate_point_count(points_list, "ArcTo", PATH_ARC_POINTS, PATH_ARC_POINTS)

        vertices_list: list[list[float]] = []
        codes_list: list[np.uint8] = []
        new_pos = cur_pos

        # All points are considered as Arc (convert to curve4)
        for idx in range(0, len(points_list), PATH_ARC_POINTS):
            start_pos = new_pos
            if is_absolute:  # A
                new_pos = points_list[idx + PATH_ARC_END_X_INDEX] + points_list[idx + PATH_ARC_END_Y_INDEX] * 1j
            else:  # a
                new_pos += points_list[idx + PATH_ARC_END_X_INDEX] + points_list[idx + PATH_ARC_END_Y_INDEX] * 1j
            radius = points_list[idx + PATH_ARC_RADIUS_X_INDEX] + points_list[idx + PATH_ARC_RADIUS_Y_INDEX] * 1j
            if radius.real == 0 or radius.imag == 0:
                vertices_list.append([new_pos.real, new_pos.imag])
                codes_list.append(Path.LINETO)
                continue  # Regard as LineTo if rx or ry is 0
            phi_deg = points_list[idx + PATH_ARC_ANGLE_INDEX]
            flags = (
                points_list[idx + PATH_ARC_FLAG_LARGE_INDEX] != 0.0,
                points_list[idx + PATH_ARC_FLAG_SWEEP_INDEX] != 0.0,
            )
            center, theta1, delta_theta = PathConverter._arc_endpoint_to_center(
                start_pos,
                new_pos,
                radius,
                phi_deg,
                flags,
            )
            new_vertices, new_codes = PathConverter._arc_to_path(center, radius, phi_deg, theta1, delta_theta)
            vertices_list.extend(new_vertices)
            codes_list.extend(new_codes)

        return vertices_list, codes_list, new_pos, "A", []

    @staticmethod
    def _convert_close(start_pos: complex) -> PathCommand:
        """Convert SVG ClosePath (Z/z) to matplotlib close."""
        # Intentionally keep LINETO for compatibility with existing marker paths.
        # CLOSEPOLY may be revisited in a future major behavior update.
        vertices_list = [[start_pos.real, start_pos.imag]]
        codes_list = [Path.LINETO]

        return vertices_list, codes_list, start_pos, "Z", []


def get_marker_from_svg(
    svgstr: str | None = None,
    filepath: str | None = None,
    url: str | None = None,
) -> Path:
    """Get a matplotlib marker from an SVG style string, file, or URL.

    An end-to-end function taking an SVG style string, file, or URL and returns a matplotlib marker.

    Args:
        svgstr (str, optional): The SVG string. Defaults to None.
        filepath (str, optional): The path to the SVG file. Defaults to None.
        url (str, optional): The URL to the SVG file. Defaults to None.

    Raises:
        ExpatError: Invalid SVG file.
        FileNotFoundError: File not found.
        IndexError: SVG element not found.
        URLError: URL not found.
        ValueError: Either svgstr, filepath, or url must be specified.

    Returns:
        Path: The matplotlib marker.

    """
    svg = SVGObject(svgstr=svgstr, filepath=filepath, url=url)
    svg_elements_path_list = [element.path_repr() for element in svg.graphic_elements]
    return PathConverter.svg2plt("M 0.0,0.0 ".join(svg_elements_path_list))
