from collections import deque
from urllib.error import URLError
from urllib.request import Request, urlopen
from xml.dom import minidom
from xml.parsers.expat import ExpatError

from .svg_circle import SVGCircle
from .svg_ellipse import SVGEllipse
from .svg_graphic_element_base import SVGGraphicElementBase
from .svg_line import SVGLine
from .svg_path import SVGPath
from .svg_polygon import SVGPolygon
from .svg_polyline import SVGPolyline
from .svg_rect import SVGRect


class SVGObject:
    """A class to represent a SVG object.

    If svg element is not found, raise IndexError.
    If svg elements are found, treat the first one as the svg element.

    Attributes:
        contents (List[SVGGraphicElementBase]): The contents of the SVG object.
    """

    SVG_GRPAHIC_ELEMENTS: dict[str, type[SVGGraphicElementBase]] = {
        "circle": SVGCircle,
        "ellipse": SVGEllipse,
        "line": SVGLine,
        "path": SVGPath,
        "polygon": SVGPolygon,
        "polyline": SVGPolyline,
        "rect": SVGRect,
    }

    def __init__(
        self,
        svgstr: str | None = None,
        filepath: str | None = None,
        url: str | None = None,
    ) -> None:
        """Initialize the SVGObject class.

        Args:
            svgstr (str, optional): The SVG string. Defaults to None.
            filepath (str, optional): The path to the SVG file. Defaults to None.
            url (str, optional): The URL to the SVG file. Defaults to None.

        Raises:
            ExpatError: Invalid SVG file.
            FileNotFoundError: File not found.
            IndexError: SVG element not found.
            URLError: URL not found.
            ValueError: Either svgstr, filepath, or url must be specified.
        """
        # Check arguments
        num_contents = sum(1 for arg in [svgstr, filepath, url] if arg is not None)
        if num_contents > 1:
            raise ValueError("Only one of svgstr, filepath, and url can be specified")
        elif num_contents == 0:
            raise ValueError("Either svgstr, filepath, or url must be specified")

        # Read SVG file
        if svgstr is not None:
            try:
                doc = minidom.parseString(svgstr)
            except ExpatError:
                raise ExpatError("Invalid SVG string")
        if filepath is not None:
            try:
                doc = minidom.parse(filepath)
            except FileNotFoundError:
                raise FileNotFoundError(f"File not found: {filepath}")
            except ExpatError:
                raise ExpatError(f"Invalid SVG file: {filepath}")
        if url is not None:
            try:
                request = Request(
                    url, headers={"User-Agent": "Mozilla/5.0"}
                )  # Avoid 403 error
                http_response = urlopen(request)
            except URLError:
                raise URLError(f"URL not found: {url}")
            try:
                doc = minidom.parseString(http_response.read())
            except ExpatError:
                raise ExpatError(f"Invalid SVG file: {url}")

        # Get SVG element
        try:
            self.svg = doc.getElementsByTagName("svg")[0]
            self.raw_svg = self.svg.toxml()
        except IndexError:
            raise IndexError("SVG element not found")

        # Get graphic elements
        self.graphic_elements: list[SVGGraphicElementBase] = []
        elements_queue = deque(self.svg.childNodes)
        while elements_queue:  # DFS
            cur_node = elements_queue.popleft()
            if cur_node.nodeType == cur_node.ELEMENT_NODE:
                elements_queue.extendleft(reversed(cur_node.childNodes))
                if cur_node.tagName in self.SVG_GRPAHIC_ELEMENTS:
                    attributes = {}
                    for key, val in cur_node.attributes.items():
                        if (
                            key
                            in self.SVG_GRPAHIC_ELEMENTS[
                                cur_node.tagName
                            ].model_fields.keys()
                        ):
                            attributes[key] = val
                    self.graphic_elements.append(
                        self.SVG_GRPAHIC_ELEMENTS[cur_node.tagName](**attributes)
                    )

    def __repr__(self) -> str:
        """Return the SVG representation of the object.

        Returns:
            str: A string representing the SVG representation of the object.
        """
        repr_str = (
            '<svg xmlns="http://www.w3.org/2000/svg" height="100%" width="100%">\n'
        )
        for element in self.graphic_elements:
            repr_str += element.svg_repr() + "\n"
        repr_str += "</svg>"
        return repr_str
