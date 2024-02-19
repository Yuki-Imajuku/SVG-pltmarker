import re

from pydantic import Field

from .svg_graphic_element_base import SVGGraphicElementBase


class SVGPolygon(SVGGraphicElementBase):
    """A class to represent a SVG polygon.

    Attributes:
        points (str): The points of the polygon.
    """

    points: str = Field(description="The points of the polygon.")

    def path_repr(self) -> str:
        """Return the SVG path representation of the polygon.

        Returns:
            str: A string representing the SVG path representation of the polygon.
        """
        points_list = re.findall(r"[-+]?\d*\.?\d+|\.\d+", self.points)
        assert len(points_list) % 2 == 0 and len(points_list) >= 4
        path_str = f"M {points_list[0]},{points_list[1]} "
        for i in range(2, len(points_list), 2):
            path_str += f"L {points_list[i]},{points_list[i + 1]} "
        path_str += "Z"
        return path_str

    def svg_repr(self) -> str:
        """Return the SVG element representation of the polygon.

        Returns:
            str: A string representing the SVG element representation of the polygon.
        """
        return f'<polygon points="{self.points}"/>'
