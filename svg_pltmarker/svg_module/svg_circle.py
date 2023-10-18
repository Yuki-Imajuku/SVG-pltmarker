from pydantic import validator

from .svg_graphic_element_base import SVGGraphicElementBase


class SVGCircle(SVGGraphicElementBase):
    """A class to represent a SVG circle.

    Attributes:
        cx (float, optional): The x coordinate of the center of the circle. Defaults to 0.0.
        cy (float, optional): The y coordinate of the center of the circle. Defaults to 0.0.
        r (float): The radius of the circle. Must be positive.
    """

    cx: float = 0.0
    cy: float = 0.0
    r: float

    @validator("r")
    def r_validator(cls, value: float) -> float:
        assert value > 0, "r must be positive"
        return value

    def path_repr(self) -> str:
        """Return the SVG path representation of the circle.

        Returns:
            str: A string representing the SVG path representation of the circle.
        """
        return (
            f"M {self.cx} {self.cy} "
            f"m -{self.r}, 0 "
            f"a {self.r},{self.r} 0 1,0 {self.r*2},0 "
            f"a {self.r},{self.r} 0 1,0 -{self.r*2},0"
        )

    def svg_repr(self) -> str:
        """Return the SVG element representation of the circle.

        Returns:
            str: A string representing the SVG element representation of the circle.
        """
        return f'<circle cx="{self.cx}" cy="{self.cy}" r="{self.r}"/>'
