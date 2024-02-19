import pytest

from svg_pltmarker import SVGCircle


class TestSVGCircle:
    @pytest.mark.parametrize(
        ("cx", "cy", "r"),
        [
            (
                50.0,
                40.0,
                30.0,
            ),
            (50.0, 50.0, 10.0),
        ],
        ids=["case1", "case2"],
    )
    def test_constructor_default(
        self,
        cx: float,
        cy: float,
        r: float,
    ) -> None:
        circle = SVGCircle(cx=cx, cy=cy, r=r)
        assert circle.cx == cx
        assert circle.cy == cy
        assert circle.r == r

    @pytest.mark.parametrize(
        ("cy", "r"),
        [
            (40.0, 30.0),
        ],
        ids=["case1"],
    )
    def test_constructor_null_cx(
        self,
        cy: float,
        r: float,
    ) -> None:
        circle = SVGCircle(cy=cy, r=r)
        assert circle.cx == 0.0
        assert circle.cy == cy
        assert circle.r == r

    @pytest.mark.parametrize(
        ("cx", "r"),
        [
            (50.0, 30.0),
        ],
        ids=["case1"],
    )
    def test_constructor_null_cy(
        self,
        cx: float,
        r: float,
    ) -> None:
        circle = SVGCircle(cx=cx, r=r)
        assert circle.cx == cx
        assert circle.cy == 0.0
        assert circle.r == r

    @pytest.mark.parametrize(
        ("r",),
        [
            (30.0,),
        ],
        ids=["case1"],
    )
    def test_constructor_only_r(
        self,
        r: float,
    ) -> None:
        circle = SVGCircle(r=r)
        assert circle.cx == 0.0
        assert circle.cy == 0.0
        assert circle.r == r

    @pytest.mark.parametrize(
        ("r",),
        [
            (-0.001,),
            (0.0,),
        ],
        ids=["negative", "zero"],
    )
    def test_constructor_invalid_r(
        self,
        r: float,
    ) -> None:
        with pytest.raises(ValueError):
            SVGCircle(r=r)

    @pytest.mark.parametrize(
        ("cx", "cy", "r", "expected"),
        [
            (
                50.0,
                40.0,
                30.0,
                "M 80.0,40.0 A 30.0,30.0 0,1,0 50.0,70.0 A 30.0,30.0 0,1,0 20.0,40.0 A 30.0,30.0 0,1,0 50.0,10.0 A 30.0,30.0 0,1,0 80.0,40.0 Z",
            ),
        ],
        ids=["case1"],
    )
    def test_path_repr(
        self,
        cx: float,
        cy: float,
        r: float,
        expected: str,
    ) -> None:
        circle = SVGCircle(cx=cx, cy=cy, r=r)
        assert circle.path_repr() == expected

    @pytest.mark.parametrize(
        ("cx", "cy", "r", "expected"),
        [
            (50.0, 50.0, 30.0, '<circle cx="50.0" cy="50.0" r="30.0"/>'),
        ],
        ids=["case1"],
    )
    def test_svg_repr(
        self,
        cx: float,
        cy: float,
        r: float,
        expected: str,
    ) -> None:
        circle = SVGCircle(cx=cx, cy=cy, r=r)
        assert circle.svg_repr() == expected
