from pydantic import Field

from .svg_graphic_element_base import SVGGraphicElementBase


class SVGLine(SVGGraphicElementBase):
    """A class to represent a SVG line.

    Attributes:
        x1 (float, optional): The x coordinate of the start of the line. Defaults to 0.0.
        y1 (float, optional): The y coordinate of the start of the line. Defaults to 0.0.
        x2 (float, optional): The x coordinate of the end of the line. Defaults to 0.0.
        y2 (float, optional): The y coordinate of the end of the line. Defaults to 0.0.
    """

    x1: float = Field(
        default=0.0, description="The x coordinate of the start of the line."
    )
    y1: float = Field(
        default=0.0, description="The y coordinate of the start of the line."
    )
    x2: float = Field(
        default=0.0, description="The x coordinate of the end of the line."
    )
    y2: float = Field(
        default=0.0, description="The y coordinate of the end of the line."
    )

    def path_repr(self) -> str:
        """Return the SVG path representation of the line.

        Returns:
            str: A string representing the SVG path representation of the line.
        """
        return f"M {self.x1},{self.y1} L {self.x2},{self.y2}"

    def svg_repr(self) -> str:
        """Return the SVG element representation of the line.

        Returns:
            str: A string representing the SVG element representation of the line.
        """
        return f'<line x1="{self.x1}" y1="{self.y1}" x2="{self.x2}" y2="{self.y2}"/>'
