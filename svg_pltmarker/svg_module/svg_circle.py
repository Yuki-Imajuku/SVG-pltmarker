from pydantic import Field

from .svg_graphic_element_base import SVGGraphicElementBase


class SVGCircle(SVGGraphicElementBase):
    """A class to represent a SVG circle.

    Attributes:
        cx (float, optional): The x coordinate of the center of the circle. Defaults to 0.0.
        cy (float, optional): The y coordinate of the center of the circle. Defaults to 0.0.
        r (float): The radius of the circle. Must be positive.
    """

    cx: float = Field(
        default=0.0, description="The x coordinate of the center of the circle."
    )
    cy: float = Field(
        default=0.0, description="The y coordinate of the center of the circle."
    )
    r: float = Field(gt=0.0, description="The radius of the circle.")

    def path_repr(self) -> str:
        """Return the SVG path representation of the circle.

        Returns:
            str: A string representing the SVG path representation of the circle.
        """
        path_str = (
            f"M {self.cx+self.r},{self.cy} "
            f"A {self.r},{self.r} 0,1,0 {self.cx},{self.cy+self.r} "
            f"A {self.r},{self.r} 0,1,0 {self.cx-self.r},{self.cy} "
            f"A {self.r},{self.r} 0,1,0 {self.cx},{self.cy-self.r} "
            f"A {self.r},{self.r} 0,1,0 {self.cx+self.r},{self.cy} Z"
        )
        return path_str

    def svg_repr(self) -> str:
        """Return the SVG element representation of the circle.

        Returns:
            str: A string representing the SVG element representation of the circle.
        """
        return f'<circle cx="{self.cx}" cy="{self.cy}" r="{self.r}"/>'
