from pydantic import validator

from .svg_graphic_element_base import SVGGraphicElementBase


class SVGEllipse(SVGGraphicElementBase):
    """A class to represent a SVG ellipse.

    Attributes:
        cx (float, optional): The x coordinate of the center of the ellipse. Defaults to 0.0.
        cy (float, optional): The y coordinate of the center of the ellipse. Defaults to 0.0.
        rx (float): The x radius of the ellipse. Must be positive.
        ry (float): The y radius of the ellipse. Must be positive.
    """

    cx: float = 0.0
    cy: float = 0.0
    rx: float
    ry: float

    @validator("rx")
    def rx_validator(cls, value: float) -> float:
        assert value > 0, "rx must be positive"
        return value

    @validator("ry")
    def ry_validator(cls, value: float) -> float:
        assert value > 0, "ry must be positive"
        return value

    def path_repr(self) -> str:
        """Return the SVG path representation of the ellipse.

        Returns:
            str: A string representing the SVG path representation of the circle.
        """
        return (
            f"M {self.cx - self.rx} {self.cy} "
            f"A {self.rx} {self.ry} 0 1 0 {self.cx + self.rx} {self.cy} "
            f"A {self.rx} {self.ry} 0 1 0 {self.cx - self.rx} {self.cy} Z"
        )

    def svg_repr(self) -> str:
        """Return the SVG element representation of the ellipse.

        Returns:
            str: A string representing the SVG element representation of the ellipse.
        """
        return f'<ellipse cx="{self.cx}" cy="{self.cy}" rx="{self.rx}" ry="{self.ry}"/>'
