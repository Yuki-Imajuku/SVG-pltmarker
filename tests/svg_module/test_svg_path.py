import pytest

from svg_pltmarker import SVGPath


@pytest.mark.parametrize(
    "d",
    [
        "M 50.0,40.0 L 30.0,20.0",
    ],
    ids=["case1"],
)
def test_path_repr(
    d: str,
) -> None:
    path = SVGPath(d=d)
    assert path.path_repr() == d


@pytest.mark.parametrize(
    ("d", "expected"),
    [
        ("M 50.0,40.0 L 30.0,20.0", '<path d="M 50.0,40.0 L 30.0,20.0"/>'),
    ],
    ids=["case1"],
)
def test_svg_repr(
    d: str,
    expected: str,
) -> None:
    path = SVGPath(d=d)
    assert path.svg_repr() == expected
