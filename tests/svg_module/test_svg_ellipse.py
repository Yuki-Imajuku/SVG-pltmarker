import pytest

from svg_pltmarker import SVGEllipse


class TestSVGEllipse:
    @pytest.mark.parametrize(
        ("cx", "cy", "rx", "ry"),
        [
            (50.0, 40.0, 30.0, 20.0),
            (20.0, 10.0, 20.0, 10.0),
        ],
        ids=["case1", "case2"],
    )
    def test_constructor_default(
        self,
        cx: float,
        cy: float,
        rx: float,
        ry: float,
    ) -> None:
        ellipse = SVGEllipse(cx=cx, cy=cy, rx=rx, ry=ry)
        assert ellipse.cx == cx
        assert ellipse.cy == cy
        assert ellipse.rx == rx
        assert ellipse.ry == ry

    @pytest.mark.parametrize(
        ("cy", "rx", "ry"),
        [
            (50.0, 30.0, 20.0),
        ],
        ids=["case1"],
    )
    def test_constructor_null_cx(
        self,
        cy: float,
        rx: float,
        ry: float,
    ) -> None:
        ellipse = SVGEllipse(cy=cy, rx=rx, ry=ry)
        assert ellipse.cx == 0.0
        assert ellipse.cy == cy
        assert ellipse.rx == rx
        assert ellipse.ry == ry

    @pytest.mark.parametrize(
        ("cx", "rx", "ry"),
        [
            (50.0, 30.0, 20.0),
        ],
        ids=["case1"],
    )
    def test_constructor_null_cy(
        self,
        cx: float,
        rx: float,
        ry: float,
    ) -> None:
        ellipse = SVGEllipse(cx=cx, rx=rx, ry=ry)
        assert ellipse.cx == cx
        assert ellipse.cy == 0.0
        assert ellipse.rx == rx
        assert ellipse.ry == ry

    @pytest.mark.parametrize(
        ("rx", "ry"),
        [
            (30.0, 20.0),
        ],
        ids=["case1"],
    )
    def test_constructor_only_r(
        self,
        rx: float,
        ry: float,
    ) -> None:
        ellipse = SVGEllipse(rx=rx, ry=ry)
        assert ellipse.cx == 0.0
        assert ellipse.cy == 0.0
        assert ellipse.rx == rx
        assert ellipse.ry == ry

    @pytest.mark.parametrize(
        ("rx", "ry"),
        [
            (-0.001, 0.001),
            (0.0, 0.001),
            (0.001, -0.001),
            (0.001, 0.0),
            (-0.001, 0.0),
        ],
        ids=["negative_rx", "zero_rx", "negative_ry", "zero_ry", "negative_rx_zero_ry"],
    )
    def test_constructor_invalid_r(
        self,
        rx: float,
        ry: float,
    ) -> None:
        with pytest.raises(ValueError):
            SVGEllipse(rx=rx, ry=ry)

    @pytest.mark.parametrize(
        ("cx", "cy", "rx", "ry", "expected"),
        [
            (
                50.0,
                40.0,
                30.0,
                20.0,
                "M 80.0,40.0 A 30.0,20.0 0,1,0 50.0,60.0 A 30.0,20.0 0,1,0 20.0,40.0 A 30.0,20.0 0,1,0 50.0,20.0 A 30.0,20.0 0,1,0 80.0,40.0 Z",
            ),
        ],
        ids=["case1"],
    )
    def test_path_repr(
        self,
        cx: float,
        cy: float,
        rx: float,
        ry: float,
        expected: str,
    ) -> None:
        ellipse = SVGEllipse(cx=cx, cy=cy, rx=rx, ry=ry)
        assert ellipse.path_repr() == expected

    @pytest.mark.parametrize(
        ("cx", "cy", "rx", "ry", "expected"),
        [
            (
                50.0,
                40.0,
                30.0,
                20.0,
                '<ellipse cx="50.0" cy="40.0" rx="30.0" ry="20.0"/>',
            ),
        ],
        ids=["case1"],
    )
    def test_svg_repr(
        self,
        cx: float,
        cy: float,
        rx: float,
        ry: float,
        expected: str,
    ) -> None:
        ellipse = SVGEllipse(cx=cx, cy=cy, rx=rx, ry=ry)
        assert ellipse.svg_repr() == expected
