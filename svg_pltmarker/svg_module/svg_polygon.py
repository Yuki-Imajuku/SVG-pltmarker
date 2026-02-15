"""SVG polygon model."""

from pydantic import Field

from svg_pltmarker.svg_module._point_path_utils import point_list_to_path
from svg_pltmarker.svg_module.svg_graphic_element_base import SVGGraphicElementBase


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
        return point_list_to_path(self.points, element_name="polygon", closed=True)

    def svg_repr(self) -> str:
        """Return the SVG element representation of the polygon.

        Returns:
            str: A string representing the SVG element representation of the polygon.

        """
        return f'<polygon points="{self.points}"/>'
