import warnings

from pydantic import validator

from .svg_graphic_element_base import SVGGraphicElementBase


class SVGRect(SVGGraphicElementBase):
    """A class to represent a SVG rectangle.

    Attributes:
        x (float, optional): The x coordinate of the rectangle. Defaults to 0.0.
        y (float, optional): The y coordinate of the rectangle. Defaults to 0.0.
        width (float): The width of the rectangle. Must be positive.
        height (float): The height of the rectangle. Must be positive.
        rx (float, optional): The x radius of the rectangle. Defaults to 0.0.
        ry (float, optional): The y radius of the rectangle. Defaults to 0.0.
    """

    x: float = 0.0
    y: float = 0.0
    width: float
    height: float
    rx: float = 0.0
    ry: float = 0.0

    @validator("width")
    def width_validator(cls, value: float) -> float:
        assert value > 0, "width must be positive"
        return value

    @validator("height")
    def height_validator(cls, value: float) -> float:
        assert value > 0, "height must be positive"
        return value

    @validator("rx")
    def rx_validator(cls, value: float, values: dict) -> float:
        assert value >= 0, "rx must be non-negative"
        if value > values["width"] / 2:
            value = values["width"] / 2
            warnings.warn("rx is greater than half of width")
        return value

    @validator("ry")
    def ry_validator(cls, value: float, values: dict) -> float:
        assert value >= 0, "ry must be non-negative"
        if value > values["height"] / 2:
            value = values["height"] / 2
            warnings.warn("ry is greater than half of height")
        return value

    def path_repr(self) -> str:
        """Return the SVG path representation of the rectangle.

        Returns:
            str: A string representing the SVG path representation of the rectangle.
        """
        return (
            f"M {self.x + self.rx} {self.y} "
            f"L {self.x + self.width - self.rx} {self.y} "
            f"A {self.rx} {self.ry} 0 0 1 {self.x + self.width} {self.y + self.ry} "
            f"L {self.x + self.width} {self.y + self.height - self.ry} "
            f"A {self.rx} {self.ry} 0 0 1 {self.x + self.width - self.rx} {self.y + self.height} "
            f"L {self.x + self.rx} {self.y + self.height} "
            f"A {self.rx} {self.ry} 0 0 1 {self.x} {self.y + self.height - self.ry} "
            f"L {self.x} {self.y + self.ry} "
            f"A {self.rx} {self.ry} 0 0 1 {self.x + self.rx} {self.y}"
        )

    def svg_repr(self) -> str:
        """Return the SVG element representation of the rectangle.

        Returns:
            str: A string representing the SVG element representation of the rectangle.
        """
        return (
            f'<rect x="{self.x}" y="{self.y}" width="{self.width}" height="{self.height}" '
            f'rx="{self.rx}" ry="{self.ry}" />'
        )
