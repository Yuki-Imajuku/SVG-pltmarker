from contextlib import nullcontext as does_not_raise
from pathlib import Path
from typing import Any
from urllib.error import URLError
from xml.parsers.expat import ExpatError

import pytest

from svg_pltmarker import SVGObject

file_dir = Path(__file__).absolute().parent.parent / "files"

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
BROKEN_SVG_CONTENT = (
    '<svg height="100%" width="100%" xmlns="http://www.w3.org/2000/svg">'
)
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


class TestSVGObject:
    @pytest.mark.parametrize(
        ("svg_str", "expected"),
        [
            (TEST_SVG_CONTENT, does_not_raise()),
            (BROKEN_SVG_CONTENT, pytest.raises(ExpatError, match="Invalid SVG string")),
            (XML_CONTENT, pytest.raises(IndexError, match="SVG element not found")),
        ],
        ids=["test", "broken", "not svg"],
    )
    def test_init_svgstr(self, svg_str: str, expected: Any) -> None:
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
        self,
        svg_filepath: str,
        expected: Any,
        expected_svg: str,
    ) -> None:
        with expected:
            svg_object = SVGObject(filepath=svg_filepath)
            assert svg_object.raw_svg == expected_svg

    @pytest.mark.parametrize(
        ("svg_url", "expected", "expected_svg"),
        [
            (
                "https://raw.githubusercontent.com/Yuki-Imajuku/SVG-pltmarker/main/tests/files/test.svg",
                does_not_raise(),
                TEST_SVG_CONTENT,
            ),
            (
                "https://raw.githubusercontent.com/Yuki-Imajuku/SVG-pltmarker/main/tests/files/broken.svg",
                pytest.raises(ExpatError, match="Invalid SVG file: "),
                "",
            ),
            (
                "https://raw.githubusercontent.com/Yuki-Imajuku/SVG-pltmarker/main/tests/files/nonexistent.svg",
                pytest.raises(URLError, match="URL not found: "),
                "",
            ),
            (
                "https://raw.githubusercontent.com/Yuki-Imajuku/SVG-pltmarker/main/tests/files/test.xml",
                pytest.raises(IndexError, match="SVG element not found"),
                "",
            ),
        ],
        ids=["test", "broken", "nonexistent", "not svg"],
    )
    def test_init_url(
        self,
        svg_url: str,
        expected: Any,
        expected_svg: str,
    ) -> None:
        with expected:
            svg_object = SVGObject(url=svg_url)
            assert svg_object.raw_svg == expected_svg

    @pytest.mark.parametrize(
        ("svg_str", "svg_filepath", "svg_url"),
        [
            (TEST_SVG_CONTENT, str(file_dir / "test.svg"), None),
            (
                TEST_SVG_CONTENT,
                None,
                "https://raw.githubusercontent.com/Yuki-Imajuku/SVG-pltmarker/main/tests/files/test.svg",
            ),
            (
                None,
                str(file_dir / "test.svg"),
                "https://raw.githubusercontent.com/Yuki-Imajuku/SVG-pltmarker/main/tests/files/test.svg",
            ),
            (
                TEST_SVG_CONTENT,
                str(file_dir / "test.svg"),
                "https://raw.githubusercontent.com/Yuki-Imajuku/SVG-pltmarker/main/tests/files/test.svg",
            ),
        ],
        ids=["svgstr&filepath", "svgstr&url", "filepath&url", "all"],
    )
    def test_init_multiple_args(
        self, svg_str: str | None, svg_filepath: str | None, svg_url: str | None
    ) -> None:
        with pytest.raises(
            ValueError, match="Only one of svgstr, filepath, and url can be specified"
        ):
            SVGObject(svgstr=svg_str, filepath=svg_filepath, url=svg_url)

    @pytest.mark.parametrize(
        ("svg_str", "svg_filepath", "svg_url"),
        [
            (None, None, None),
        ],
        ids=["none"],
    )
    def test_init_no_args(
        self, svg_str: None, svg_filepath: None, svg_url: None
    ) -> None:
        with pytest.raises(
            ValueError, match="Either svgstr, filepath, or url must be specified"
        ):
            SVGObject(svgstr=svg_str, filepath=svg_filepath, url=svg_url)

    @pytest.mark.parametrize(
        ("svg_str", "svg_filepath", "svg_url", "expected"),
        [
            (TEST_SVG_CONTENT, None, None, TEST_SVG_REPR),
            (None, str(file_dir / "test.svg"), None, TEST_SVG_REPR),
            (
                None,
                None,
                "https://raw.githubusercontent.com/Yuki-Imajuku/SVG-pltmarker/main/tests/files/test.svg",
                TEST_SVG_REPR,
            ),
        ],
        ids=["svgstr", "filepath", "url"],
    )
    def test_repr(
        self,
        svg_str: str | None,
        svg_filepath: str | None,
        svg_url: str | None,
        expected: str,
    ) -> None:
        svg_object = SVGObject(svgstr=svg_str, filepath=svg_filepath, url=svg_url)
        assert repr(svg_object) == expected
