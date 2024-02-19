import warnings

from pydantic import Field

from .svg_graphic_element_base import SVGGraphicElementBase


class SVGRect(SVGGraphicElementBase):
    """A class to represent a SVG rectangle.

    Attributes:
        x (float, optional): The x coordinate of the rectangle. Defaults to 0.0.
        y (float, optional): The y coordinate of the rectangle. Defaults to 0.0.
        width (float): The width of the rectangle. Must be positive.
        height (float): The height of the rectangle. Must be positive.
        rx (float, optional): The x radius of the rectangle. Defaults to 0.0. Must be non-negative.
        ry (float, optional): The y radius of the rectangle. Defaults to 0.0. Must be non-negative.
    """

    x: float = Field(default=0.0, description="The x coordinate of the rectangle.")
    y: float = Field(default=0.0, description="The y coordinate of the rectangle.")
    width: float = Field(gt=0.0, description="The width of the rectangle.")
    height: float = Field(gt=0.0, description="The height of the rectangle.")
    rx: float = Field(
        default=0.0,
        ge=0.0,
        validate_default=True,
        description="The x radius of the rectangle.",
    )
    ry: float = Field(
        default=0.0,
        ge=0.0,
        validate_default=True,
        description="The y radius of the rectangle.",
    )

    def model_post_init(self, *args, **kwargs) -> None:
        """Post initialization method to validate the radius of the rectangle."""
        if self.rx > self.width / 2:
            self.rx = self.width / 2
            warnings.warn("rx is greater than half of width.")
        if self.ry > self.height / 2:
            self.ry = self.height / 2
            warnings.warn("ry is greater than half of height.")
        if self.rx > 0 and self.ry == 0:
            self.ry = self.rx
        if self.ry > 0 and self.rx == 0:
            self.rx = self.ry

    def path_repr(self) -> str:
        """Return the SVG path representation of the rectangle.

        Returns:
            str: A string representing the SVG path representation of the rectangle.
        """
        add_arc = self.rx > 0 and self.ry > 0
        path_str = (
            f"M {self.x + self.rx},{self.y} L {self.x + self.width - self.rx},{self.y} "
        )
        if add_arc:
            path_str += (
                f"A {self.rx},{self.ry} 0,0,1 {self.x + self.width},{self.y + self.ry} "
            )
        path_str += f"L {self.x + self.width},{self.y + self.height - self.ry} "
        if add_arc:
            path_str += f"A {self.rx},{self.ry} 0,0,1 {self.x + self.width - self.rx},{self.y + self.height} "
        path_str += f"L {self.x + self.rx},{self.y + self.height} "
        if add_arc:
            path_str += f"A {self.rx},{self.ry} 0,0,1 {self.x},{self.y + self.height - self.ry} "
        path_str += f"L {self.x},{self.y + self.ry} "
        if add_arc:
            path_str += f"A {self.rx},{self.ry} 0,0,1 {self.x + self.rx},{self.y} "
        path_str += "Z"
        return path_str

    def svg_repr(self) -> str:
        """Return the SVG element representation of the rectangle.

        Returns:
            str: A string representing the SVG element representation of the rectangle.
        """
        return (
            f'<rect x="{self.x}" y="{self.y}" width="{self.width}" height="{self.height}" '
            f'rx="{self.rx}" ry="{self.ry}" />'
        )
