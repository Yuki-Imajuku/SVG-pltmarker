import re

import numpy as np
from matplotlib.path import Path
from matplotlib.transforms import Affine2D

from .svg_module import SVGObject


class PathConverter:
    """A class to convert SVG path to matplotlib path."""

    @classmethod
    def svg2plt(cls, svg_path: str) -> Path:
        """Convert SVG path to matplotlib path.

        Attributes:
            svg_path (str): SVG path.

        Returns:
            Path: Matplotlib path.
        """
        vertices_list: list[list[float]] = []
        codes_list: list[np.uint8] = []

        # Find all command
        command_indices = [
            m.start() for m in re.finditer(r"[MmLlHhVvCcSsQqTtAaZz]", svg_path)
        ]
        assert len(command_indices) > 0, "No command found"
        assert (
            svg_path[command_indices[0]].upper() == "M"
        ), "First command must be MoveTo"
        command_indices.append(len(svg_path))  # Add the end of the path

        # Parse each command
        start_pos: complex = 0 + 0j  # Start position
        cur_pos = start_pos  # Current position
        before_command: str = ""  # Before command
        before_points: list[float] = []  # Before points list used in before_command
        for idx in range(len(command_indices) - 1):
            # Parse command
            command_str = svg_path[
                command_indices[idx] : command_indices[idx + 1]  # noqa: E203
            ].strip()
            svg_command = command_str[0].upper()
            is_absolute = command_str[0].isupper()
            if before_command == "Z":
                assert svg_command == "M", "Invalid SVG path as Z is not followed by M"
            points_list = [
                float(m) for m in re.findall(r"[-+]?\d*\.?\d+|\.\d+", command_str[1:])
            ]
            # Convert to matplotlib path
            if svg_command == "M":
                new_vertices, new_codes, cur_pos, start_pos = cls._convert_move_to(
                    points_list, is_absolute, cur_pos
                )
                vertices_list.extend(new_vertices)
                codes_list.extend(new_codes)
                before_command = "L"
            elif svg_command == "L":
                new_vertices, new_codes, cur_pos = cls._convert_line_to(
                    points_list, is_absolute, cur_pos
                )
                vertices_list.extend(new_vertices)
                codes_list.extend(new_codes)
                before_command = "L"
            elif svg_command == "H":
                new_vertices, new_codes, cur_pos = cls._convert_horizontal_line_to(
                    points_list, is_absolute, cur_pos
                )
                vertices_list.extend(new_vertices)
                codes_list.extend(new_codes)
                before_command = "L"
            elif svg_command == "V":
                new_vertices, new_codes, cur_pos = cls._convert_vertical_line_to(
                    points_list, is_absolute, cur_pos
                )
                vertices_list.extend(new_vertices)
                codes_list.extend(new_codes)
                before_command = "L"
            elif svg_command == "C":
                (
                    new_vertices,
                    new_codes,
                    cur_pos,
                    before_command,
                    before_points,
                ) = cls._convert_curve4(points_list, is_absolute, cur_pos)
                vertices_list.extend(new_vertices)
                codes_list.extend(new_codes)
            elif svg_command == "S":
                (
                    new_vertices,
                    new_codes,
                    cur_pos,
                    before_command,
                    before_points,
                ) = cls._convert_smooth_curve4(
                    points_list, is_absolute, cur_pos, before_command, before_points
                )
                vertices_list.extend(new_vertices)
                codes_list.extend(new_codes)
            elif svg_command == "Q":
                (
                    new_vertices,
                    new_codes,
                    cur_pos,
                    before_command,
                    before_points,
                ) = cls._convert_curve3(points_list, is_absolute, cur_pos)
                vertices_list.extend(new_vertices)
                codes_list.extend(new_codes)
            elif svg_command == "T":
                (
                    new_vertices,
                    new_codes,
                    cur_pos,
                    before_command,
                    before_points,
                ) = cls._convert_smooth_curve3(
                    points_list, is_absolute, cur_pos, before_command, before_points
                )
                vertices_list.extend(new_vertices)
                codes_list.extend(new_codes)
            elif svg_command == "A":
                new_vertices, new_codes, cur_pos = cls._convert_arc(
                    points_list, is_absolute, cur_pos
                )
                vertices_list.extend(new_vertices)
                codes_list.extend(new_codes)
                before_command = "A"
            elif svg_command == "Z":
                new_vertices, new_codes, cur_pos = cls._convert_close(start_pos)
                vertices_list.extend(new_vertices)
                codes_list.extend(new_codes)
                before_command = "Z"
            else:
                raise ValueError(f"Invalid SVG path command: {svg_command}")

        # Convert to matplotlib path
        # Normalize the path to [-0.5, 0.5] x [-0.5, 0.5] while keeping the aspect ratio
        # Flip the y-axis because of below reasons:
        # Matplotlib: 'O' is the bottom-left corner, SVG: 'O' is the top-left corner
        vertices = np.array(vertices_list)
        codes = np.array(codes_list, dtype=np.uint8)
        min_x, max_x = np.min(vertices[:, 0]), np.max(vertices[:, 0])
        min_y, max_y = np.min(vertices[:, 1]), np.max(vertices[:, 1])
        center_x, center_y = (max_x + min_x) / 2, (max_y + min_y) / 2
        size = max(max_x - min_x, max_y - min_y)
        if size == 0:
            size = 1
        vertices[:, 0] = (vertices[:, 0] - center_x) / size  # X-axis
        vertices[:, 1] = (center_y - vertices[:, 1]) / size  # Y-axis
        plt_path = Path(vertices=vertices, codes=codes, closed=False, readonly=True)
        return plt_path

    @staticmethod
    def _convert_move_to(
        points_list: list[float],
        is_absolute: bool,
        cur_pos: complex,
    ) -> tuple[list[list[float]], list[np.uint8], complex, complex]:
        """Convert SVG MoveTo (M/m) to matplotlib move.

        Attributes:
            points_list (list[float]): Points list.
            is_absolute (bool): Whether the move is absolute or relative.
            cur_pos (complex): Current position.

        Returns:
            list[list[float]]: Vertices list.
            list[np.uint8]: Codes list.
            complex: Next current position.
            complex: Start position.
        """
        assert len(points_list) % 2 == 0 and len(points_list) >= 2
        vertices_list: list[list[float]] = []
        codes_list: list[np.uint8] = []
        new_pos = cur_pos

        # First point
        if is_absolute:  # M
            new_pos = points_list[0] + points_list[1] * 1j
        else:  # m
            new_pos += points_list[0] + points_list[1] * 1j
        start_pos = new_pos  # Set start position
        vertices_list.append([new_pos.real, new_pos.imag])
        codes_list.append(Path.MOVETO)

        # Other points (consider as LineTo)
        for idx in range(2, len(points_list), 2):
            if is_absolute:  # M (consider as L)
                new_pos = points_list[idx] + points_list[idx + 1] * 1j
            else:  # m (consider as l)
                new_pos += points_list[idx] + points_list[idx + 1] * 1j
            vertices_list.append([new_pos.real, new_pos.imag])
            codes_list.append(Path.LINETO)

        return vertices_list, codes_list, new_pos, start_pos

    @staticmethod
    def _convert_line_to(
        points_list: list[float],
        is_absolute: bool,
        cur_pos: complex,
    ) -> tuple[list[list[float]], list[np.uint8], complex]:
        """Convert SVG LineTo (L/l) to matplotlib line.

        Attributes:
            points_list (list[float]): Points list.
            is_absolute (bool): Whether the move is absolute or relative.
            cur_pos (complex): Current position.

        Returns:
            list[list[float]]: Vertices list.
            list[np.uint8]: Codes list.
            complex: Next current position.
        """
        assert len(points_list) % 2 == 0 and len(points_list) >= 2
        vertices_list: list[list[float]] = []
        codes_list: list[np.uint8] = []
        new_pos = cur_pos

        # All points are considered as LineTo
        for idx in range(0, len(points_list), 2):
            if is_absolute:  # L
                new_pos = points_list[idx] + points_list[idx + 1] * 1j
            else:  # l
                new_pos += points_list[idx] + points_list[idx + 1] * 1j
            vertices_list.append([new_pos.real, new_pos.imag])
            codes_list.append(Path.LINETO)

        return vertices_list, codes_list, new_pos

    @staticmethod
    def _convert_horizontal_line_to(
        points_list: list[float],
        is_absolute: bool,
        cur_pos: complex,
    ) -> tuple[list[list[float]], list[np.uint8], complex]:
        """Convert SVG HorizontalLineTo (H/h) to matplotlib line.

        Attributes:
            points_list (list[float]): Points list.
            is_absolute (bool): Whether the move is absolute or relative.
            cur_pos (complex): Current position.

        Returns:
            list[list[float]]: Vertices list.
            list[np.uint8]: Codes list.
            complex: Next current position.
        """
        assert len(points_list) >= 1
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

        return vertices_list, codes_list, new_pos

    @staticmethod
    def _convert_vertical_line_to(
        points_list: list[float],
        is_absolute: bool,
        cur_pos: complex,
    ) -> tuple[list[list[float]], list[np.uint8], complex]:
        """Convert SVG VerticalLineTo (V/v) to matplotlib line.

        Attributes:
            points_list (list[float]): Points list.
            is_absolute (bool): Whether the move is absolute or relative.
            cur_pos (complex): Current position.

        Returns:
            list[list[float]]: Vertices list.
            list[np.uint8]: Codes list.
            complex: Next current position.
        """
        assert len(points_list) >= 1
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

        return vertices_list, codes_list, new_pos

    @staticmethod
    def _convert_curve4(
        points_list: list[float],
        is_absolute: bool,
        cur_pos: complex,
    ) -> tuple[list[list[float]], list[np.uint8], complex, str, list[float]]:
        """Convert SVG CurveTo (C/c) to matplotlib curve.

        Attributes:
            points_list (list[float]): Points list.
            is_absolute (bool): Whether the move is absolute or relative.
            cur_pos (complex): Current position.

        Returns:
            list[list[float]]: Vertices list.
            list[np.uint8]: Codes list.
            complex: Next current position.
            str: Current command.
            list[float]: Current command points list.
        """

        def to_vertices(
            control_pos1: complex, control_pos2: complex, new_pos: complex
        ) -> list[list[float]]:
            return [
                [control_pos1.real, control_pos1.imag],
                [control_pos2.real, control_pos2.imag],
                [new_pos.real, new_pos.imag],
            ]

        def to_command_points(
            control_pos1: complex, control_pos2: complex, new_pos: complex
        ) -> list[float]:
            return [
                control_pos1.real,
                control_pos1.imag,
                control_pos2.real,
                control_pos2.imag,
                new_pos.real,
                new_pos.imag,
            ]

        assert len(points_list) % 6 == 0 and len(points_list) >= 6
        vertices_list: list[list[float]] = []
        codes_list: list[np.uint8] = []
        new_pos = cur_pos
        new_command = "C"
        new_points: list[float] = []

        # All points are considered as CurveTo (represented by 3 points)
        for idx in range(0, len(points_list), 6):
            if is_absolute:  # C
                control_pos1 = points_list[idx] + points_list[idx + 1] * 1j
                control_pos2 = points_list[idx + 2] + points_list[idx + 3] * 1j
                new_pos = points_list[idx + 4] + points_list[idx + 5] * 1j
            else:  # c
                control_pos1 = new_pos + points_list[idx] + points_list[idx + 1] * 1j
                control_pos2 = (
                    new_pos + points_list[idx + 2] + points_list[idx + 3] * 1j
                )
                new_pos += points_list[idx + 4] + points_list[idx + 5] * 1j
            vertices_list.extend(to_vertices(control_pos1, control_pos2, new_pos))
            codes_list.extend([Path.CURVE4] * 3)
            new_points = to_command_points(control_pos1, control_pos2, new_pos)

        return vertices_list, codes_list, new_pos, new_command, new_points

    @staticmethod
    def _convert_smooth_curve4(
        points_list: list[float],
        is_absolute: bool,
        cur_pos: complex,
        before_command: str,
        before_points: list[float],
    ) -> tuple[list[list[float]], list[np.uint8], complex, str, list[float]]:
        """Convert SVG SmoothCurveTo (S/s) to matplotlib curve.

        Attributes:
            points_list (list[float]): Points list.
            is_absolute (bool): Whether the move is absolute or relative.
            cur_pos (complex): Current position.
            before_command (str): Before command.
            before_points (list[float]): Before points list.

        Returns:
            list[list[float]]: Vertices list.
            list[np.uint8]: Codes list.
            complex: Next current position.
            str: Current command.
            list[float]: Current command points list.
        """

        def to_vertices(
            control_pos1: complex, control_pos2: complex, new_pos: complex
        ) -> list[list[float]]:
            return [
                [control_pos1.real, control_pos1.imag],
                [control_pos2.real, control_pos2.imag],
                [new_pos.real, new_pos.imag],
            ]

        def to_command_points(
            control_pos1: complex, control_pos2: complex, new_pos: complex
        ) -> list[float]:
            return [
                control_pos1.real,
                control_pos1.imag,
                control_pos2.real,
                control_pos2.imag,
                new_pos.real,
                new_pos.imag,
            ]

        assert len(points_list) % 4 == 0 and len(points_list) >= 4
        vertices_list: list[list[float]] = []
        codes_list: list[np.uint8] = []
        new_pos = cur_pos
        new_command = before_command
        new_points = before_points

        # All points are considered as CurveTo (represented by 3 points)
        for idx in range(0, len(points_list), 4):
            control_pos1 = new_pos  # Regard start_pos as control_pos1
            if new_command == "C":  # Reflect control_pos2 of the previous curve
                assert len(new_points) == 6, "Invalid before_points"
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
        is_absolute: bool,
        cur_pos: complex,
    ) -> tuple[list[list[float]], list[np.uint8], complex, str, list[float]]:
        """Convert SVG CurveTo (Q/q) to matplotlib curve.

        Attributes:
            points_list (list[float]): Points list.
            is_absolute (bool): Whether the move is absolute or relative.
            cur_pos (complex): Current position.

        Returns:
            list[list[float]]: Vertices list.
            list[np.uint8]: Codes list.
            complex: Next current position.
            str: Current command.
            list[float]: Current command points list.
        """

        def to_vertices(control_pos: complex, new_pos: complex) -> list[list[float]]:
            return [
                [control_pos.real, control_pos.imag],
                [new_pos.real, new_pos.imag],
            ]

        def to_command_points(control_pos: complex, new_pos: complex) -> list[float]:
            return [control_pos.real, control_pos.imag, new_pos.real, new_pos.imag]

        assert len(points_list) % 4 == 0 and len(points_list) >= 4
        vertices_list: list[list[float]] = []
        codes_list: list[np.uint8] = []
        new_pos = cur_pos
        new_command = "Q"
        new_points: list[float] = []

        # All points are considered as CurveTo (represented by 2 points)
        for idx in range(0, len(points_list), 4):
            if is_absolute:  # Q
                control_pos = points_list[idx] + points_list[idx + 1] * 1j
                new_pos = points_list[idx + 2] + points_list[idx + 3] * 1j
            else:  # q
                control_pos = new_pos + points_list[idx] + points_list[idx + 1] * 1j
                new_pos += points_list[idx + 2] + points_list[idx + 3] * 1j
            vertices_list.extend(to_vertices(control_pos, new_pos))
            codes_list.extend([Path.CURVE3] * 2)
            new_points = to_command_points(control_pos, new_pos)

        return vertices_list, codes_list, new_pos, new_command, new_points

    @staticmethod
    def _convert_smooth_curve3(
        points_list: list[float],
        is_absolute: bool,
        cur_pos: complex,
        before_command: str,
        before_points: list[float],
    ) -> tuple[list[list[float]], list[np.uint8], complex, str, list[float]]:
        """Convert SVG SmoothCurveTo (T/t) to matplotlib curve.

        Attributes:
            points_list (list[float]): Points list.
            is_absolute (bool): Whether the move is absolute or relative.
            cur_pos (complex): Current position.
            before_command (str): Before command.
            before_points (list[float]): Before points list.

        Returns:
            list[list[float]]: Vertices list.
            list[np.uint8]: Codes list.
            complex: Next current position.
            str: Current command.
            list[float]: Current command points list.
        """

        def to_vertices(control_pos: complex, new_pos: complex) -> list[list[float]]:
            return [
                [control_pos.real, control_pos.imag],
                [new_pos.real, new_pos.imag],
            ]

        def to_command_points(control_pos: complex, new_pos: complex) -> list[float]:
            return [control_pos.real, control_pos.imag, new_pos.real, new_pos.imag]

        assert len(points_list) % 2 == 0 and len(points_list) >= 2
        vertices_list: list[list[float]] = []
        codes_list: list[np.uint8] = []
        new_pos = cur_pos
        new_command = before_command
        new_points = before_points

        # All points are considered as CurveTo (represented by 2 points)
        for idx in range(0, len(points_list), 2):
            control_pos = new_pos  # Regard start_pos as control_pos
            if new_command == "Q":  # Reflect control_pos of the previous curve
                assert len(new_points) == 4, "Invalid before_points"
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
    def _convert_arc(
        points_list: list[float],
        is_absolute: bool,
        cur_pos: complex,
    ) -> tuple[list[list[float]], list[np.uint8], complex]:
        """Convert SVG ArcTo (A/a) to matplotlib arc.

        Attributes:
            points_list (list[float]): Points list.
            is_absolute (bool): Whether the move is absolute or relative.
            cur_pos (complex): Current position.

        Returns:
            list[list[float]]: Vertices list.
            list[np.uint8]: Codes list.
            complex: Next current position.
        """

        # https://www.w3.org/TR/SVG/implnote.html#ArcConversionEndpointToCenter
        def endpoint_to_center(
            start: complex,
            end: complex,
            radius: complex,
            phi_deg: float,  # degree
            large_arc: bool,
            sweep: bool,
        ) -> tuple[complex, float, float]:
            phi_deg -= np.floor(phi_deg / 360) * 360  # Normalize phi_deg to [0, 360)
            phi = np.deg2rad(phi_deg)
            # Step 1: Compute (x1', y1') <- z
            z: complex = np.exp(-1j * phi) * (start - end) / 2
            # Step 2: Compute (cx', cy') <- c
            denom = radius.real**2 * z.imag**2 + radius.imag**2 * z.real**2
            num = max(0, radius.real**2 * radius.imag**2 - denom)
            try:
                k = np.sqrt(num / denom)
            except ZeroDivisionError:
                k = 0  # Maybe num == denom == 0
            if large_arc == sweep:
                k = -k
            c = k * (
                radius.real / radius.imag * z.imag
                - 1j * radius.imag / radius.real * z.real
            )
            # Step 3: Compute (cx, cy) from (cx', cy')
            center = np.exp(1j * phi) * c + (start + end) / 2
            # Step 4: Compute theta1 and delta_theta
            p1 = z - c
            theta1 = np.angle(
                p1.real / radius.real + 1j * p1.imag / radius.imag, deg=True
            )  # (-180, 180]
            p2 = -z - c
            theta2 = np.angle(
                p2.real / radius.real + 1j * p2.imag / radius.imag, deg=True
            )
            delta_theta = theta2 - theta1  # (-360, 360)
            if theta1 < 0:
                theta1 += 360  # [0, 360)
            if sweep and delta_theta < 0:
                delta_theta += 360
            elif not sweep and delta_theta > 0:
                delta_theta -= 360
            return center, theta1, delta_theta

        def to_path(
            center: complex,
            radius: complex,
            rotation: float,
            theta1: float,
            delta_theta: float,
        ) -> tuple[list[list[float]], list[np.uint8]]:
            reverse = delta_theta < 0
            if reverse:
                unit_arc = Path.arc(theta1 + delta_theta, theta1)
            else:
                unit_arc = Path.arc(theta1, theta1 + delta_theta)
            transform = (
                Affine2D()
                .scale(radius.real, radius.imag)
                .translate(center.real, center.imag)
                .rotate_deg_around(center.real, center.imag, rotation)
            )
            arc = transform.transform_path(unit_arc)
            vertice, code = arc.vertices, arc.codes
            if reverse:
                vertice = vertice[::-1]  # type: ignore
            return vertice, code  # type: ignore

        assert len(points_list) % 7 == 0 and len(points_list) >= 7
        vertices_list: list[list[float]] = []
        codes_list: list[np.uint8] = []
        new_pos = cur_pos

        # All points are considered as Arc (convert to curve4)
        for idx in range(0, len(points_list), 7):
            start_pos = new_pos
            if is_absolute:  # A
                new_pos = points_list[idx + 5] + points_list[idx + 6] * 1j
            else:  # a
                new_pos += points_list[idx + 5] + points_list[idx + 6] * 1j
            radius = points_list[idx] + points_list[idx + 1] * 1j
            if radius.real == 0 or radius.imag == 0:
                vertices_list.append([new_pos.real, new_pos.imag])
                codes_list.append(Path.LINETO)
                continue  # Regard as LineTo if rx or ry is 0
            center, theta1, delta_theta = endpoint_to_center(
                start_pos,
                new_pos,
                radius,
                points_list[idx + 2],
                bool(points_list[idx + 3]),
                bool(points_list[idx + 4]),
            )
            new_vertices, new_codes = to_path(
                center, radius, points_list[idx + 2], theta1, delta_theta
            )
            vertices_list.extend(new_vertices)
            codes_list.extend(new_codes)

        return vertices_list, codes_list, new_pos

    @staticmethod
    def _convert_close(
        start_pos: complex,
    ) -> tuple[list[list[float]], list[np.uint8], complex]:
        """Convert SVG ClosePath (Z/z) to matplotlib close.

        Attributes:
            start_pos (complex): Start position.
            is_final (bool): Whether the close is the final command.

        Returns:
            list[list[float]]: Vertices list.
            list[np.uint8]: Codes list.
            complex: Next current position.
        """
        # LineTo to the start position
        vertices_list = [[start_pos.real, start_pos.imag]]
        codes_list = [Path.LINETO]

        return vertices_list, codes_list, start_pos


def get_marker_from_svg(
    svgstr: str | None = None,
    filepath: str | None = None,
    url: str | None = None,
    **kwargs,
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
    svg = SVGObject(svgstr=svgstr, filepath=filepath, url=url, **kwargs)
    svg_elements_path_list = [element.path_repr() for element in svg.graphic_elements]
    return PathConverter.svg2plt("M 0.0,0.0 ".join(svg_elements_path_list))
