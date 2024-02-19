from pydantic import Field

from .svg_graphic_element_base import SVGGraphicElementBase


class SVGEllipse(SVGGraphicElementBase):
    """A class to represent a SVG ellipse.

    Attributes:
        cx (float, optional): The x coordinate of the center of the ellipse. Defaults to 0.0.
        cy (float, optional): The y coordinate of the center of the ellipse. Defaults to 0.0.
        rx (float): The x radius of the ellipse. Must be positive.
        ry (float): The y radius of the ellipse. Must be positive.
    """

    cx: float = Field(
        default=0.0, description="The x coordinate of the center of the ellipse."
    )
    cy: float = Field(
        default=0.0, description="The y coordinate of the center of the ellipse."
    )
    rx: float = Field(gt=0.0, description="The x radius of the ellipse.")
    ry: float = Field(gt=0.0, description="The y radius of the ellipse.")

    def path_repr(self) -> str:
        """Return the SVG path representation of the ellipse.

        Returns:
            str: A string representing the SVG path representation of the ellipse.
        """
        path_str = (
            f"M {self.cx+self.rx},{self.cy} "
            f"A {self.rx},{self.ry} 0,1,0 {self.cx},{self.cy+self.ry} "
            f"A {self.rx},{self.ry} 0,1,0 {self.cx-self.rx},{self.cy} "
            f"A {self.rx},{self.ry} 0,1,0 {self.cx},{self.cy-self.ry} "
            f"A {self.rx},{self.ry} 0,1,0 {self.cx+self.rx},{self.cy} Z"
        )
        return path_str

    def svg_repr(self) -> str:
        """Return the SVG element representation of the ellipse.

        Returns:
            str: A string representing the SVG element representation of the ellipse.
        """
        return f'<ellipse cx="{self.cx}" cy="{self.cy}" rx="{self.rx}" ry="{self.ry}"/>'
