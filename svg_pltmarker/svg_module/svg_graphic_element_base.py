from abc import ABC, abstractmethod

from pydantic import BaseModel


class SVGGraphicElementBase(ABC, BaseModel):
    """A base class for SVG graphic elements."""

    @abstractmethod
    def path_repr(self) -> str:
        """Return the SVG path representation of the graphic element.

        Returns:
            str: A string representing the SVG path representation of the graphic element.
        """
        pass

    @abstractmethod
    def svg_repr(self) -> str:
        """Return the SVG element representation of the graphic element.

        Returns:
            str: A string representing the SVG element representation of the graphic element.
        """
        pass
