from contextlib import AbstractContextManager, nullcontext as does_not_raise
from http import HTTPStatus
from http.client import HTTPConnection, HTTPSConnection
from pathlib import Path
from urllib.error import URLError
from urllib.parse import ParseResult, urlparse
from xml.parsers.expat import ExpatError

import pytest

from svg_pltmarker import SVGObject

file_dir = Path(__file__).absolute().parent.parent / "files"

TEST_SVG_URL = (file_dir / "test.svg").as_uri()
BROKEN_SVG_URL = (file_dir / "broken.svg").as_uri()
NONEXISTENT_SVG_URL = (file_dir / "nonexistent.svg").as_uri()
TEST_XML_URL = (file_dir / "test.xml").as_uri()

TEST_SVG_CONTENT = """<svg xmlns="http://www.w3.org/2000/svg" height="100%" width="100%">
    <circle cx="50" cy="40" r="30" stroke="black" stroke-width="2"/>
    <ellipse cx="50" cy="40" rx="30" ry="20" style="fill:yellow"/>
    <g>
        <line x1="50.0" y1="40.0" x2="30.0" y2="20.0" style="stroke:rgb(255,0,0);stroke-width:2"/>
        <path d="M 5.0,4.0 L 3.0,2.0"/>
    </g>
    <polygon points="0.0,30.0 15.0,7.5 15.0,22.5 30.0,0.0"/>
    <polyline points="0,100 50,25 50,75 100,0" fill="none" stroke="blue"/>
</svg>"""
BROKEN_SVG_CONTENT = '<svg height="100%" width="100%" xmlns="http://www.w3.org/2000/svg">'
XML_CONTENT = """<?xml version="1.0" encoding="UTF-8"?>
<test>
    <name>Test</name>
    <value>Value</value>
</test>"""

TEST_SVG_REPR = """<svg xmlns="http://www.w3.org/2000/svg" height="100%" width="100%">
<circle cx="50.0" cy="40.0" r="30.0"/>
<ellipse cx="50.0" cy="40.0" rx="30.0" ry="20.0"/>
<line x1="50.0" y1="40.0" x2="30.0" y2="20.0"/>
<path d="M 5.0,4.0 L 3.0,2.0"/>
<polygon points="0.0,30.0 15.0,7.5 15.0,22.5 30.0,0.0"/>
<polyline points="0,100 50,25 50,75 100,0"/>
</svg>"""


@pytest.mark.parametrize(
    ("svg_str", "expected"),
    [
        (TEST_SVG_CONTENT, does_not_raise()),
        (BROKEN_SVG_CONTENT, pytest.raises(ExpatError, match="Invalid SVG string")),
        (XML_CONTENT, pytest.raises(IndexError, match="SVG element not found")),
    ],
    ids=["test", "broken", "not svg"],
)
def test_init_svgstr(svg_str: str, expected: AbstractContextManager[object]) -> None:
    with expected:
        svg_object = SVGObject(svgstr=svg_str)
        assert svg_object.raw_svg == svg_str


@pytest.mark.parametrize(
    ("svg_filepath", "expected", "expected_svg"),
    [
        (
            str(file_dir / "test.svg"),
            does_not_raise(),
            TEST_SVG_CONTENT,
        ),
        (
            str(file_dir / "broken.svg"),
            pytest.raises(
                ExpatError,
                match="Invalid SVG file: ",
            ),
            "",
        ),
        (
            str(file_dir / "nonexistent.svg"),
            pytest.raises(FileNotFoundError, match="File not found: "),
            "",
        ),
        (
            str(file_dir / "test.xml"),
            pytest.raises(IndexError, match="SVG element not found"),
            "",
        ),
    ],
    ids=["test.svg", "broken.svg", "nonexistent.svg", "test.xml"],
)
def test_init_filepath(
    svg_filepath: str,
    expected: AbstractContextManager[object],
    expected_svg: str,
) -> None:
    with expected:
        svg_object = SVGObject(filepath=svg_filepath)
        assert svg_object.raw_svg == expected_svg


@pytest.mark.parametrize(
    ("svg_url", "expected", "expected_svg"),
    [
        (TEST_SVG_URL, does_not_raise(), TEST_SVG_CONTENT),
        (BROKEN_SVG_URL, pytest.raises(ExpatError, match="Invalid SVG file: "), ""),
        (NONEXISTENT_SVG_URL, pytest.raises(FileNotFoundError, match="File not found: "), ""),
        (TEST_XML_URL, pytest.raises(IndexError, match="SVG element not found"), ""),
    ],
    ids=["test", "broken", "nonexistent", "not svg"],
)
def test_init_url(
    svg_url: str,
    expected: AbstractContextManager[object],
    expected_svg: str,
) -> None:
    with expected:
        svg_object = SVGObject(url=svg_url)
        assert svg_object.raw_svg == expected_svg


@pytest.mark.parametrize(
    ("svg_url", "message"),
    [
        ("file://", "Invalid URL: file://"),
        ("ftp://example.com/example.svg", "Invalid URL scheme: ftp"),
        ("http:///not-found", "Invalid URL: http:///not-found"),
    ],
    ids=["file path missing", "unsupported scheme", "missing hostname"],
)
def test_init_url_invalid_urls(
    svg_url: str,
    message: str,
) -> None:
    with pytest.raises(ValueError, match=message):
        SVGObject(url=svg_url)


def test_load_from_url_file_windows_path_is_normalized(monkeypatch: pytest.MonkeyPatch) -> None:
    called: dict[str, str] = {}
    original_load_from_filepath = SVGObject._load_from_filepath

    def _mock_load_from_filepath(filepath: str) -> object:
        called["filepath"] = filepath
        return original_load_from_filepath(str(file_dir / "test.svg"))

    monkeypatch.setattr("svg_pltmarker.svg_module.svg_object.os.name", "nt", raising=False)
    monkeypatch.setattr(SVGObject, "_load_from_filepath", staticmethod(_mock_load_from_filepath))

    SVGObject._load_from_url("file:///D:/a/SVG-pltmarker/SVG-pltmarker/tests/files/test.svg")
    assert called["filepath"] == "D:/a/SVG-pltmarker/SVG-pltmarker/tests/files/test.svg"


def test_open_http_connection_returns_connection_by_scheme() -> None:
    http_connection = SVGObject._open_http_connection(urlparse("http://example.com/path"))
    https_connection = SVGObject._open_http_connection(urlparse("https://example.com/path"))
    assert isinstance(http_connection, HTTPConnection)
    assert isinstance(https_connection, HTTPSConnection)
    http_connection.close()
    https_connection.close()


def test_open_http_connection_rejects_missing_hostname() -> None:
    with pytest.raises(ValueError, match=r"Invalid URL: https:///missing-host"):
        SVGObject._open_http_connection(urlparse("https:///missing-host"))


def test_init_url_http_error(monkeypatch: pytest.MonkeyPatch) -> None:
    class _DummyResponse:
        status = 500

        def __init__(self, content: bytes) -> None:
            self._content = content

        def read(self) -> bytes:
            return self._content

    class _MockHTTPConnection:
        def __init__(self, *_args: object, **_kwargs: object) -> None:
            self._response = _DummyResponse(b"")

        def request(self, *_args: object, **_kwargs: object) -> None:
            return None

        def getresponse(self) -> _DummyResponse:
            return self._response

        def close(self) -> None:
            return None

    monkeypatch.setattr("svg_pltmarker.svg_module.svg_object.HTTPConnection", _MockHTTPConnection)

    with pytest.raises(URLError, match=r"URL not found: http://example\.com/missing"):
        SVGObject(url="http://example.com/missing")


def test_init_internal_source_resolution_guard(monkeypatch: pytest.MonkeyPatch) -> None:
    def _mock_load_from_string(_svgstr: str) -> None:
        return None

    monkeypatch.setattr(SVGObject, "_load_from_string", staticmethod(_mock_load_from_string))
    with pytest.raises(RuntimeError, match="Internal error: SVG source resolution failed"):
        SVGObject(svgstr=TEST_SVG_CONTENT)


def test_init_url_request_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    class _MockHTTPConnection:
        def __init__(self, *_args: object, **_kwargs: object) -> None:
            return None

        def request(self, *_args: object, **_kwargs: object) -> None:
            message = "connection failed"
            raise RuntimeError(message)

        def getresponse(self) -> None:
            return None

        def close(self) -> None:
            return None

    monkeypatch.setattr("svg_pltmarker.svg_module.svg_object.HTTPConnection", _MockHTTPConnection)

    with pytest.raises(URLError, match=r"URL not found: http://example\.com/connection-error"):
        SVGObject(url="http://example.com/connection-error")


def test_init_url_invalid_xml(monkeypatch: pytest.MonkeyPatch) -> None:
    class _DummyResponse:
        status = 200

        def __init__(self, content: bytes) -> None:
            self._content = content

        def read(self) -> bytes:
            return self._content

    class _MockHTTPConnection:
        def __init__(self, *_args: object, **_kwargs: object) -> None:
            self._response = _DummyResponse(b"<svg><path></svg>")

        def request(self, *_args: object, **_kwargs: object) -> None:
            return None

        def getresponse(self) -> _DummyResponse:
            return self._response

        def close(self) -> None:
            return None

    monkeypatch.setattr("svg_pltmarker.svg_module.svg_object.HTTPConnection", _MockHTTPConnection)

    with pytest.raises(ExpatError, match=r"Invalid SVG file: http://example\.com/invalid-xml"):
        SVGObject(url="http://example.com/invalid-xml")


def test_init_url_rejects_none_payload(monkeypatch: pytest.MonkeyPatch) -> None:
    class _DummyResponse:
        status = 200

        def read(self) -> None:
            return None

    class _MockHTTPConnection:
        def __init__(self, *_args: object, **_kwargs: object) -> None:
            self._response = _DummyResponse()

        def request(self, *_args: object, **_kwargs: object) -> None:
            return None

        def getresponse(self) -> _DummyResponse:
            return self._response

        def close(self) -> None:
            return None

    monkeypatch.setattr("svg_pltmarker.svg_module.svg_object.HTTPConnection", _MockHTTPConnection)
    with pytest.raises(URLError, match=r"URL not found: http://example\.com/none-payload"):
        SVGObject(url="http://example.com/none-payload")


def test_init_url_with_query_path(monkeypatch: pytest.MonkeyPatch) -> None:
    request_payload: dict[str, str] = {}

    class _DummyResponse:
        status = 200

        def __init__(self, content: bytes) -> None:
            self._content = content

        def read(self) -> bytes:
            return self._content

    class _MockHTTPConnection:
        def __init__(self, *_args: object, **_kwargs: object) -> None:
            self._response = _DummyResponse(
                b"<svg xmlns='http://www.w3.org/2000/svg'><path d='M 0,0 L 1,1'/></svg>",
            )

        def request(self, _method: str, target: str, **_kwargs: object) -> None:
            request_payload["target"] = target

        def getresponse(self) -> _DummyResponse:
            return self._response

        def close(self) -> None:
            return None

    monkeypatch.setattr("svg_pltmarker.svg_module.svg_object.HTTPConnection", _MockHTTPConnection)

    svg_object = SVGObject(url="http://example.com/path?x=1&y=2")
    assert request_payload["target"] == "/path?x=1&y=2"
    assert svg_object.raw_svg == '<svg xmlns="http://www.w3.org/2000/svg"><path d="M 0,0 L 1,1"/></svg>'


def test_init_url_success(monkeypatch: pytest.MonkeyPatch) -> None:
    class _DummyResponse:
        status = 200

        def __init__(self, content: bytes) -> None:
            self._content = content

        def read(self) -> bytes:
            return self._content

    class _MockHTTPConnection:
        def __init__(self, *_args: object, **_kwargs: object) -> None:
            self._response = _DummyResponse(
                b"<svg xmlns='http://www.w3.org/2000/svg'><path d='M 0,0 L 1,1'/></svg>",
            )

        def request(self, *_args: object, **_kwargs: object) -> None:
            return None

        def getresponse(self) -> _DummyResponse:
            return self._response

        def close(self) -> None:
            return None

    monkeypatch.setattr("svg_pltmarker.svg_module.svg_object.HTTPConnection", _MockHTTPConnection)

    svg_object = SVGObject(url="http://example.com/valid")
    assert svg_object.raw_svg == '<svg xmlns="http://www.w3.org/2000/svg"><path d="M 0,0 L 1,1"/></svg>'


def test_init_url_redirect(monkeypatch: pytest.MonkeyPatch) -> None:
    requested_targets: list[str] = []

    class _DummyResponse:
        def __init__(self, status: int, content: bytes, location: str | None = None) -> None:
            self.status = status
            self._content = content
            self._location = location

        def read(self) -> bytes:
            return self._content

        def getheader(self, name: str, default: object | None = None) -> object | None:
            if name.lower() == "location":
                return self._location
            return default

    class _MockHTTPConnection:
        def __init__(self, *_args: object, **_kwargs: object) -> None:
            self._target = "/"

        def request(self, _method: str, target: str, **_kwargs: object) -> None:
            self._target = target
            requested_targets.append(target)

        def getresponse(self) -> _DummyResponse:
            if self._target == "/redirect":
                return _DummyResponse(HTTPStatus.FOUND, b"", "/final")
            return _DummyResponse(
                HTTPStatus.OK,
                b"<svg xmlns='http://www.w3.org/2000/svg'><path d='M 0,0 L 1,1'/></svg>",
            )

        def close(self) -> None:
            return None

    monkeypatch.setattr("svg_pltmarker.svg_module.svg_object.HTTPConnection", _MockHTTPConnection)

    svg_object = SVGObject(url="http://example.com/redirect")
    assert requested_targets == ["/redirect", "/final"]
    assert svg_object.raw_svg == '<svg xmlns="http://www.w3.org/2000/svg"><path d="M 0,0 L 1,1"/></svg>'


def test_init_url_redirect_missing_location_header(monkeypatch: pytest.MonkeyPatch) -> None:
    class _DummyResponse:
        status = HTTPStatus.FOUND

        def read(self) -> bytes:
            return b""

        def getheader(self, _name: str, default: object | None = None) -> object | None:
            return default

    class _MockHTTPConnection:
        def __init__(self, *_args: object, **_kwargs: object) -> None:
            self._response = _DummyResponse()

        def request(self, *_args: object, **_kwargs: object) -> None:
            return None

        def getresponse(self) -> _DummyResponse:
            return self._response

        def close(self) -> None:
            return None

    monkeypatch.setattr("svg_pltmarker.svg_module.svg_object.HTTPConnection", _MockHTTPConnection)

    with pytest.raises(URLError, match=r"URL not found: http://example\.com/redirect-without-location"):
        SVGObject(url="http://example.com/redirect-without-location")


def test_init_url_redirect_exceeds_maximum(monkeypatch: pytest.MonkeyPatch) -> None:
    requested_targets: list[str] = []

    class _DummyResponse:
        status = HTTPStatus.FOUND

        def read(self) -> bytes:
            return b""

        def getheader(self, name: str, default: object | None = None) -> object | None:
            if name.lower() == "location":
                return "/redirect"
            return default

    class _MockHTTPConnection:
        def __init__(self, *_args: object, **_kwargs: object) -> None:
            self._response = _DummyResponse()

        def request(self, _method: str, target: str, **_kwargs: object) -> None:
            requested_targets.append(target)

        def getresponse(self) -> _DummyResponse:
            return self._response

        def close(self) -> None:
            return None

    monkeypatch.setattr("svg_pltmarker.svg_module.svg_object.HTTPConnection", _MockHTTPConnection)

    with pytest.raises(URLError, match=r"URL not found: http://example\.com/redirect"):
        SVGObject(url="http://example.com/redirect")
    assert len(requested_targets) == SVGObject._MAX_REDIRECTS + 1


def test_init_url_redirect_reject_https_to_http_downgrade(monkeypatch: pytest.MonkeyPatch) -> None:
    requested_targets: list[str] = []

    class _DummyResponse:
        status = HTTPStatus.FOUND

        def read(self) -> bytes:
            return b""

        def getheader(self, _name: str, default: object | None = None) -> object | None:
            return "http://secure.example.com/final" if default is None else default

    class _MockHTTPSConnection:
        def __init__(self, *_args: object, **_kwargs: object) -> None:
            self._response = _DummyResponse()

        def request(self, _method: str, target: str, **_kwargs: object) -> None:
            requested_targets.append(target)

        def getresponse(self) -> _DummyResponse:
            return self._response

        def close(self) -> None:
            return None

    def _mock_open_http_connection(parsed_url: ParseResult) -> _MockHTTPSConnection:
        assert parsed_url.scheme == "https"
        return _MockHTTPSConnection()

    monkeypatch.setattr("svg_pltmarker.svg_module.svg_object.HTTPSConnection", _MockHTTPSConnection)
    monkeypatch.setattr(
        "svg_pltmarker.svg_module.svg_object.SVGObject._open_http_connection",
        _mock_open_http_connection,
    )

    with pytest.raises(URLError, match=r"URL not found: https://secure\.example\.com/redirect"):
        SVGObject(url="https://secure.example.com/redirect")
    assert requested_targets == ["/redirect"]


@pytest.mark.parametrize(
    ("svg_str", "svg_filepath", "svg_url"),
    [
        (TEST_SVG_CONTENT, str(file_dir / "test.svg"), None),
        (TEST_SVG_CONTENT, None, TEST_SVG_URL),
        (None, str(file_dir / "test.svg"), TEST_SVG_URL),
        (TEST_SVG_CONTENT, str(file_dir / "test.svg"), TEST_SVG_URL),
    ],
    ids=["svgstr&filepath", "svgstr&url", "filepath&url", "all"],
)
def test_init_multiple_args(svg_str: str | None, svg_filepath: str | None, svg_url: str | None) -> None:
    with pytest.raises(ValueError, match="Only one of svgstr, filepath, and url can be specified"):
        SVGObject(svgstr=svg_str, filepath=svg_filepath, url=svg_url)


@pytest.mark.parametrize(
    ("svg_str", "svg_filepath", "svg_url"),
    [
        (None, None, None),
    ],
    ids=["none"],
)
def test_init_no_args(svg_str: None, svg_filepath: None, svg_url: None) -> None:
    with pytest.raises(ValueError, match="Either svgstr, filepath, or url must be specified"):
        SVGObject(svgstr=svg_str, filepath=svg_filepath, url=svg_url)


@pytest.mark.parametrize(
    ("svg_str", "svg_filepath", "svg_url", "expected"),
    [
        (TEST_SVG_CONTENT, None, None, TEST_SVG_REPR),
        (None, str(file_dir / "test.svg"), None, TEST_SVG_REPR),
        (None, None, TEST_SVG_URL, TEST_SVG_REPR),
    ],
    ids=["svgstr", "filepath", "url"],
)
def test_repr(
    svg_str: str | None,
    svg_filepath: str | None,
    svg_url: str | None,
    expected: str,
) -> None:
    svg_object = SVGObject(svgstr=svg_str, filepath=svg_filepath, url=svg_url)
    assert repr(svg_object) == expected
