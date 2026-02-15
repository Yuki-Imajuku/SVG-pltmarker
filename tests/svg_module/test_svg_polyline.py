import pytest

from svg_pltmarker import SVGPolyline


@pytest.mark.parametrize(
    ("points", "expected"),
    [
        ("0,100 50,25 50,75 100,0", "M 0,100 L 50,25 L 50,75 L 100,0"),
        ("150,0", "M 150,0"),
        ("1e2,0 2e2,1e1", "M 1e2,0 L 2e2,1e1"),
        (
            "+50.0,-.0 +21.,-90 98.0 -35.0 +.2-35 79-90.",
            "M +50.0,-.0 L +21,-90 L 98.0,-35.0 L +.2,-35 L 79,-90",
        ),
    ],
    ids=["simple", "single-pair", "exponent", "complex"],
)
def test_path_repr(points: str, expected: str) -> None:
    polyline = SVGPolyline(points=points)
    assert polyline.path_repr() == expected


@pytest.mark.parametrize(
    "points",
    [
        "0,100 50,25 50,75 100,",
        "150",
        "150,0 121,",
        "",
        "0,100;50,25",
        "0,100 a 50,25",
    ],
    ids=["odd number", "invalid pair", "trailing separator", "empty", "invalid separator", "invalid character"],
)
def test_path_repr_invalid(points: str) -> None:
    polyline = SVGPolyline(points=points)
    with pytest.raises(ValueError, match="Invalid polyline points"):
        polyline.path_repr()


@pytest.mark.parametrize(
    ("points", "expected"),
    [
        ("0,100 50,25 50,75 100,0", '<polyline points="0,100 50,25 50,75 100,0"/>'),
        (
            "150,0 121,90 198,35 102,35 179,90",
            '<polyline points="150,0 121,90 198,35 102,35 179,90"/>',
        ),
    ],
    ids=["simple", "complex"],
)
def test_svg_repr(points: str, expected: str) -> None:
    polyline = SVGPolyline(points=points)
    assert polyline.svg_repr() == expected
