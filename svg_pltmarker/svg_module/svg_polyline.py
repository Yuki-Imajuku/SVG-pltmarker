"""SVG polyline model."""

from pydantic import Field

from svg_pltmarker.svg_module._point_path_utils import point_list_to_path
from svg_pltmarker.svg_module.svg_graphic_element_base import SVGGraphicElementBase


class SVGPolyline(SVGGraphicElementBase):
    """A class to represent a SVG polyline.

    Attributes:
        points (str): The points of the polyline.

    """

    points: str = Field(description="The points of the polyline.")

    def path_repr(self) -> str:
        """Return the SVG path representation of the polyline.

        Returns:
            str: A string representing the SVG path representation of the polyline.

        """
        return point_list_to_path(self.points, element_name="polyline", closed=False)

    def svg_repr(self) -> str:
        """Return the SVG element representation of the polyline.

        Returns:
            str: A string representing the SVG element representation of the polyline.

        """
        return f'<polyline points="{self.points}"/>'
