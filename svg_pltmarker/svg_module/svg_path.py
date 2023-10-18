from .svg_graphic_element_base import SVGGraphicElementBase


class SVGPath(SVGGraphicElementBase):
    """A class to represent a SVG path.

    Attributes:
        d (str): The path data.
    """

    d: str

    def path_repr(self) -> str:
        """Return the SVG path representation of the path.

        Returns:
            str: A string representing the SVG path representation of the path.
        """
        return self.d

    def svg_repr(self) -> str:
        """Return the SVG element representation of the path.

        Returns:
            str: A string representing the SVG element representation of the path.
        """
        return f'<path d="{self.d}"/>'
