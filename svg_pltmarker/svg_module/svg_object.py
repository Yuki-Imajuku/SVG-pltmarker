"""SVG object parser and high-level SVG wrapper."""

import os
from collections import deque
from http import HTTPStatus
from http.client import HTTPConnection, HTTPException, HTTPSConnection
from typing import ClassVar, NoReturn
from urllib.error import URLError
from urllib.parse import ParseResult, unquote, urljoin, urlparse
from xml.dom import minidom
from xml.dom.minidom import Element
from xml.parsers.expat import ExpatError

from svg_pltmarker.svg_module.svg_circle import SVGCircle
from svg_pltmarker.svg_module.svg_ellipse import SVGEllipse
from svg_pltmarker.svg_module.svg_graphic_element_base import SVGGraphicElementBase
from svg_pltmarker.svg_module.svg_line import SVGLine
from svg_pltmarker.svg_module.svg_path import SVGPath
from svg_pltmarker.svg_module.svg_polygon import SVGPolygon
from svg_pltmarker.svg_module.svg_polyline import SVGPolyline
from svg_pltmarker.svg_module.svg_rect import SVGRect


class SVGObject:
    """A class to represent an SVG object.

    If svg element is not found, raise IndexError.
    If svg elements are found, treat the first one as the svg element.

    Attributes:
        contents (list[SVGGraphicElementBase]): The contents of the SVG object.

    """

    SVG_GRAPHIC_ELEMENTS: ClassVar[dict[str, type[SVGGraphicElementBase]]] = {
        "circle": SVGCircle,
        "ellipse": SVGEllipse,
        "line": SVGLine,
        "path": SVGPath,
        "polygon": SVGPolygon,
        "polyline": SVGPolyline,
        "rect": SVGRect,
    }
    _MAX_REDIRECTS: ClassVar[int] = 5
    _REDIRECT_STATUSES: ClassVar[set[HTTPStatus]] = {
        HTTPStatus.MOVED_PERMANENTLY,
        HTTPStatus.FOUND,
        HTTPStatus.SEE_OTHER,
        HTTPStatus.TEMPORARY_REDIRECT,
        HTTPStatus.PERMANENT_REDIRECT,
    }
    _HTTP_SCHEMES: ClassVar[set[str]] = {"http", "https"}

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
        num_contents = sum(1 for arg in (svgstr, filepath, url) if arg is not None)
        if num_contents > 1:
            msg = "Only one of svgstr, filepath, and url can be specified"
            raise ValueError(msg)
        if num_contents == 0:
            msg = "Either svgstr, filepath, or url must be specified"
            raise ValueError(msg)

        # Read SVG file
        doc: minidom.Document | None = None
        if svgstr is not None:
            doc = self._load_from_string(svgstr)
        if filepath is not None:
            doc = self._load_from_filepath(filepath)
        if url is not None:
            doc = self._load_from_url(url)

        if doc is None:
            msg = "Internal error: SVG source resolution failed after argument validation"
            raise RuntimeError(msg)

        # Get SVG element
        try:
            self.svg = doc.getElementsByTagName("svg")[0]
            self.raw_svg = self.svg.toxml()
        except IndexError as exc:
            msg = "SVG element not found"
            raise IndexError(msg) from exc

        self.graphic_elements = self._extract_graphic_elements(self.svg)

    @staticmethod
    def _load_from_string(svgstr: str) -> minidom.Document:
        try:
            return minidom.parseString(svgstr)
        except ExpatError as exc:
            msg = "Invalid SVG string"
            raise ExpatError(msg) from exc

    @staticmethod
    def _load_from_filepath(filepath: str) -> minidom.Document:
        try:
            return minidom.parse(filepath)
        except FileNotFoundError as exc:
            msg = f"File not found: {filepath}"
            raise FileNotFoundError(msg) from exc
        except ExpatError as exc:
            msg = f"Invalid SVG file: {filepath}"
            raise ExpatError(msg) from exc

    @staticmethod
    def _url_not_found(url: str, exc: Exception | None = None) -> NoReturn:
        msg = f"URL not found: {url}"
        if exc is None:
            raise URLError(msg)
        raise URLError(msg) from exc

    @staticmethod
    def _validate_http_url(parsed_url: ParseResult, url: str) -> None:
        scheme = parsed_url.scheme
        hostname = parsed_url.hostname
        if scheme not in SVGObject._HTTP_SCHEMES:
            msg = f"Invalid URL scheme: {scheme}"
            raise ValueError(msg)
        if hostname is None:
            msg = f"Invalid URL: {url}"
            raise ValueError(msg)

    @staticmethod
    def _http_request_target(parsed_url: ParseResult) -> str:
        request_target = parsed_url.path or "/"
        if parsed_url.query:
            request_target += f"?{parsed_url.query}"
        return request_target

    @staticmethod
    def _open_http_connection(parsed_url: ParseResult) -> HTTPConnection | HTTPSConnection:
        host = parsed_url.hostname
        if host is None:
            msg = f"Invalid URL: {parsed_url.geturl()}"
            raise ValueError(msg)
        if parsed_url.scheme == "https":
            return HTTPSConnection(host, parsed_url.port, timeout=10)
        return HTTPConnection(host, parsed_url.port, timeout=10)

    @staticmethod
    def _resolve_redirect_url(current_url: str, location: str, original_url: str) -> str:
        next_url = urljoin(current_url, location)
        parsed_current = urlparse(current_url)
        parsed_next = urlparse(next_url)
        if parsed_current.scheme == "https" and parsed_next.scheme == "http":
            SVGObject._url_not_found(original_url)
        return next_url

    @staticmethod
    def _load_http_bytes(url: str) -> bytes:
        current_url = url
        data: bytes | None = None
        for _ in range(SVGObject._MAX_REDIRECTS + 1):
            parsed_current = urlparse(current_url)
            SVGObject._validate_http_url(parsed_current, current_url)
            connection = SVGObject._open_http_connection(parsed_current)
            try:
                connection.request(
                    "GET",
                    SVGObject._http_request_target(parsed_current),
                    headers={"User-Agent": "Mozilla/5.0"},
                )
                response = connection.getresponse()
                if response.status in SVGObject._REDIRECT_STATUSES:
                    location = response.getheader("Location")
                    if not isinstance(location, str) or not location:
                        SVGObject._url_not_found(url)
                    current_url = SVGObject._resolve_redirect_url(current_url, location, url)
                    continue
                if response.status != HTTPStatus.OK:
                    SVGObject._url_not_found(url)
                data = response.read()
                break
            except URLError:
                raise
            except (HTTPException, OSError, RuntimeError) as exc:
                SVGObject._url_not_found(url, exc)
            finally:
                connection.close()
        else:
            SVGObject._url_not_found(url)

        if data is None:
            SVGObject._url_not_found(url)
        return data

    @staticmethod
    def _load_from_url(url: str) -> minidom.Document:
        parsed_url = urlparse(url)
        if parsed_url.scheme == "file":
            if parsed_url.netloc not in {"", "localhost"} or not parsed_url.path:
                msg = f"Invalid URL: {url}"
                raise ValueError(msg)
            filepath = unquote(parsed_url.path)
            # Windows file URLs are often /C:/...; strip the extra leading slash.
            min_windows_drive_path_len = 3
            if (
                os.name == "nt"
                and len(filepath) >= min_windows_drive_path_len
                and filepath[0] == "/"
                and filepath[1].isalpha()
                and filepath[2] == ":"
            ):
                filepath = filepath[1:]  # Strip leading '/' from '/C:/...'.
            return SVGObject._load_from_filepath(filepath)

        SVGObject._validate_http_url(parsed_url, url)
        data = SVGObject._load_http_bytes(url)

        try:
            return minidom.parseString(data)
        except ExpatError as exc:
            msg = f"Invalid SVG file: {url}"
            raise ExpatError(msg) from exc

    @classmethod
    def _extract_graphic_elements(
        cls,
        svg_node: minidom.Element,
    ) -> list[SVGGraphicElementBase]:
        elements_queue = deque(svg_node.childNodes)
        graphic_elements: list[SVGGraphicElementBase] = []

        while elements_queue:  # DFS
            cur_node = elements_queue.popleft()
            if not isinstance(cur_node, Element):
                continue
            elements_queue.extendleft(reversed(cur_node.childNodes))
            if element := cls._create_graphic_element(cur_node):
                graphic_elements.append(element)

        return graphic_elements

    @classmethod
    def _create_graphic_element(
        cls,
        node: minidom.Element,
    ) -> SVGGraphicElementBase | None:
        model_class = cls.SVG_GRAPHIC_ELEMENTS.get(node.tagName)
        if model_class is None:
            return None
        attributes = {key: val for key, val in node.attributes.items() if key in model_class.model_fields}
        return model_class(**attributes)

    def __repr__(self) -> str:
        """Return the SVG representation of the object.

        Returns:
            str: A string representing the SVG representation of the object.

        """
        repr_str = '<svg xmlns="http://www.w3.org/2000/svg" height="100%" width="100%">\n'
        for element in self.graphic_elements:
            repr_str += element.svg_repr() + "\n"
        repr_str += "</svg>"
        return repr_str
