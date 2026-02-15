"""SVG circle model."""

from pydantic import Field

from svg_pltmarker.svg_module._ellipse_path_utils import ellipse_arc_path
from svg_pltmarker.svg_module.svg_graphic_element_base import SVGGraphicElementBase


class SVGCircle(SVGGraphicElementBase):
    """A class to represent a SVG circle.

    Attributes:
        cx (float, optional): The x coordinate of the center of the circle. Defaults to 0.0.
        cy (float, optional): The y coordinate of the center of the circle. Defaults to 0.0.
        r (float): The radius of the circle. Must be positive.

    """

    cx: float = Field(default=0.0, description="The x coordinate of the center of the circle.")
    cy: float = Field(default=0.0, description="The y coordinate of the center of the circle.")
    r: float = Field(gt=0.0, description="The radius of the circle.")

    def path_repr(self) -> str:
        """Return the SVG path representation of the circle.

        Returns:
            str: A string representing the SVG path representation of the circle.

        """
        return ellipse_arc_path(self.cx, self.cy, self.r, self.r)

    def svg_repr(self) -> str:
        """Return the SVG element representation of the circle.

        Returns:
            str: A string representing the SVG element representation of the circle.

        """
        return f'<circle cx="{self.cx}" cy="{self.cy}" r="{self.r}"/>'
