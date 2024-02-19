import pytest

from svg_pltmarker import SVGRect


class TestSVGRect:
    @pytest.mark.parametrize(
        ("x", "y", "width", "height", "rx", "ry"),
        [
            (50.0, 40.0, 30.0, 20.0, 2.0, 1.0),
            (20.0, 10.0, 20.0, 10.0, 0.0, 0.0),
        ],
        ids=["case1", "case2"],
    )
    def test_constructor_default(
        self,
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
        self,
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
        self,
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
        self,
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
        self,
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
        self,
        width: float,
        height: float,
        rx: float,
        ry: float,
    ) -> None:
        with pytest.warns(Warning) as record:
            rect = SVGRect(width=width, height=height, rx=rx, ry=ry)
            if not record:
                pytest.fail("Expected a warning.")
            assert record[0].message.args[0] == "rx is greater than half of width."
        assert rect.rx == width / 2

    @pytest.mark.parametrize(
        ("width", "height", "rx", "ry"),
        [
            (30.0, 20.0, 2.0, 10.001),
        ],
        ids=["case1"],
    )
    def test_constructor_large_ry(
        self,
        width: float,
        height: float,
        rx: float,
        ry: float,
    ) -> None:
        with pytest.warns(Warning) as record:
            rect = SVGRect(width=width, height=height, rx=rx, ry=ry)
            if not record:
                pytest.fail("Expected a warning.")
            assert record[0].message.args[0] == "ry is greater than half of height."
        assert rect.ry == height / 2

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
        self,
        width: float,
        height: float,
        rx: float,
        ry: float,
    ) -> None:
        with pytest.raises(ValueError):
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
                "M 52.0,40.0 L 78.0,40.0 A 2.0,1.0 0,0,1 80.0,41.0 L 80.0,59.0 A 2.0,1.0 0,0,1 78.0,60.0 L 52.0,60.0 A 2.0,1.0 0,0,1 50.0,59.0 L 50.0,41.0 A 2.0,1.0 0,0,1 52.0,40.0 Z",
            ),
        ],
        ids=["case1"],
    )
    def test_path_repr(
        self,
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
        self,
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
