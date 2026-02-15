import pytest

from svg_pltmarker import SVGRect


@pytest.mark.parametrize(
    ("x", "y", "width", "height", "rx", "ry"),
    [
        (50.0, 40.0, 30.0, 20.0, 2.0, 1.0),
        (20.0, 10.0, 20.0, 10.0, 0.0, 0.0),
    ],
    ids=["case1", "case2"],
)
def test_constructor_default(
    x: float,
    y: float,
    width: float,
    height: float,
    rx: float,
    ry: float,
) -> None:
    rect = SVGRect(x=x, y=y, width=width, height=height, rx=rx, ry=ry)
    assert rect.x == x
    assert rect.y == y
    assert rect.width == width
    assert rect.height == height
    assert rect.rx == rx
    assert rect.ry == ry


@pytest.mark.parametrize(
    ("y", "width", "height", "rx", "ry"),
    [
        (40.0, 30.0, 20.0, 2.0, 1.0),
    ],
    ids=["case1"],
)
def test_constructor_null_x(
    y: float,
    width: float,
    height: float,
    rx: float,
    ry: float,
) -> None:
    rect = SVGRect(y=y, width=width, height=height, rx=rx, ry=ry)
    assert rect.x == 0.0
    assert rect.y == y
    assert rect.width == width
    assert rect.height == height
    assert rect.rx == rx
    assert rect.ry == ry


@pytest.mark.parametrize(
    ("x", "width", "height", "rx", "ry"),
    [
        (50.0, 30.0, 20.0, 2.0, 1.0),
    ],
    ids=["case1"],
)
def test_constructor_null_y(
    x: float,
    width: float,
    height: float,
    rx: float,
    ry: float,
) -> None:
    rect = SVGRect(x=x, width=width, height=height, rx=rx, ry=ry)
    assert rect.x == x
    assert rect.y == 0.0
    assert rect.width == width
    assert rect.height == height
    assert rect.rx == rx
    assert rect.ry == ry


@pytest.mark.parametrize(
    ("x", "y", "width", "height", "ry"),
    [
        (50.0, 40.0, 30.0, 20.0, 1.0),
    ],
    ids=["case1"],
)
def test_constructor_null_rx(
    x: float,
    y: float,
    width: float,
    height: float,
    ry: float,
) -> None:
    rect = SVGRect(x=x, y=y, width=width, height=height, ry=ry)
    assert rect.x == x
    assert rect.y == y
    assert rect.width == width
    assert rect.height == height
    assert rect.rx == ry  # rx is set to ry
    assert rect.ry == ry


@pytest.mark.parametrize(
    ("x", "y", "width", "height", "rx"),
    [
        (50.0, 40.0, 30.0, 20.0, 2.0),
    ],
    ids=["case1"],
)
def test_constructor_null_ry(
    x: float,
    y: float,
    width: float,
    height: float,
    rx: float,
) -> None:
    rect = SVGRect(x=x, y=y, width=width, height=height, rx=rx)
    assert rect.x == x
    assert rect.y == y
    assert rect.width == width
    assert rect.height == height
    assert rect.rx == rx
    assert rect.ry == rx  # ry is set to rx


@pytest.mark.parametrize(
    ("width", "height", "rx", "ry"),
    [
        (30.0, 20.0, 15.001, 1.0),
    ],
    ids=["case1"],
)
def test_constructor_large_rx(
    width: float,
    height: float,
    rx: float,
    ry: float,
) -> None:
    with pytest.warns(UserWarning, match=r"^rx is greater than half of width\.$") as record:
        rect = SVGRect(width=width, height=height, rx=rx, ry=ry)
    assert str(record[0].message) == "rx is greater than half of width."
    assert rect.rx == width / 2


@pytest.mark.parametrize(
    ("width", "height", "rx", "ry"),
    [
        (30.0, 20.0, 2.0, 10.001),
    ],
    ids=["case1"],
)
def test_constructor_large_ry(
    width: float,
    height: float,
    rx: float,
    ry: float,
) -> None:
    with pytest.warns(UserWarning, match=r"^ry is greater than half of height\.$") as record:
        rect = SVGRect(width=width, height=height, rx=rx, ry=ry)
    assert str(record[0].message) == "ry is greater than half of height."
    assert rect.ry == height / 2


def test_constructor_sync_radius_and_reclamp() -> None:
    with pytest.warns(UserWarning, match=r"(rx|ry) is greater than half of (width|height)\.") as record:
        rect = SVGRect(width=10.0, height=2.0, rx=8.0, ry=0.0)
    warning_messages = [str(message.message) for message in record]
    assert "rx is greater than half of width." in warning_messages
    assert "ry is greater than half of height." in warning_messages
    assert rect.rx == 5.0
    assert rect.ry == 1.0


@pytest.mark.parametrize(
    ("width", "height", "rx", "ry"),
    [
        (-0.001, 20.0, 2.0, 1.0),
        (0.0, 20.0, 2.0, 1.0),
        (30.0, -0.001, 2.0, 1.0),
        (30.0, 0.0, 2.0, 1.0),
        (30.0, 20.0, -0.001, 1.0),
        (30.0, 20.0, 2.0, -0.001),
    ],
    ids=[
        "negative_width",
        "zero_width",
        "negative_height",
        "zero_height",
        "negative_rx",
        "negative_ry",
    ],
)
def test_constructor_invalid_input(
    width: float,
    height: float,
    rx: float,
    ry: float,
) -> None:
    with pytest.raises(ValueError, match=r"Input should be .*0"):
        SVGRect(width=width, height=height, rx=rx, ry=ry)


@pytest.mark.parametrize(
    ("x", "y", "width", "height", "rx", "ry", "expected"),
    [
        (
            50.0,
            40.0,
            30.0,
            20.0,
            2.0,
            1.0,
            (
                "M 52.0,40.0 L 78.0,40.0 A 2.0,1.0 0,0,1 80.0,41.0 "
                "L 80.0,59.0 A 2.0,1.0 0,0,1 78.0,60.0 "
                "L 52.0,60.0 A 2.0,1.0 0,0,1 50.0,59.0 "
                "L 50.0,41.0 A 2.0,1.0 0,0,1 52.0,40.0 Z"
            ),
        ),
    ],
    ids=["case1"],
)
def test_path_repr(
    x: float,
    y: float,
    width: float,
    height: float,
    rx: float,
    ry: float,
    expected: str,
) -> None:
    rect = SVGRect(x=x, y=y, width=width, height=height, rx=rx, ry=ry)
    assert rect.path_repr() == expected


def test_path_repr_without_rounded_corners() -> None:
    rect = SVGRect(x=10.0, y=20.0, width=30.0, height=40.0, rx=0.0, ry=0.0)
    assert rect.path_repr() == "M 10.0,20.0 L 40.0,20.0 L 40.0,60.0 L 10.0,60.0 L 10.0,20.0 Z"


@pytest.mark.parametrize(
    ("x", "y", "width", "height", "rx", "ry", "expected"),
    [
        (
            50.0,
            40.0,
            30.0,
            20.0,
            2.0,
            1.0,
            '<rect x="50.0" y="40.0" width="30.0" height="20.0" rx="2.0" ry="1.0" />',
        ),
    ],
    ids=["case1"],
)
def test_svg_repr(
    x: float,
    y: float,
    width: float,
    height: float,
    rx: float,
    ry: float,
    expected: str,
) -> None:
    rect = SVGRect(x=x, y=y, width=width, height=height, rx=rx, ry=ry)
    assert rect.svg_repr() == expected
