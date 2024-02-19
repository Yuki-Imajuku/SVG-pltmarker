import pytest

from svg_pltmarker import SVGLine


class TestSVGLine:
    @pytest.mark.parametrize(
        ("x1", "y1", "x2", "y2"),
        [
            (50.0, 40.0, 30.0, 20.0),
            (30.0, 30.0, 10.0, 10.0),
        ],
        ids=["case1", "case2"],
    )
    def test_constructor_default(
        self,
        x1: float,
        y1: float,
        x2: float,
        y2: float,
    ) -> None:
        line = SVGLine(x1=x1, y1=y1, x2=x2, y2=y2)
        assert line.x1 == x1
        assert line.y1 == y1
        assert line.x2 == x2
        assert line.y2 == y2

    @pytest.mark.parametrize(
        ("y1", "x2", "y2"),
        [
            (40.0, 30.0, 20.0),
        ],
        ids=["case1"],
    )
    def test_constructor_null_x1(
        self,
        y1: float,
        x2: float,
        y2: float,
    ) -> None:
        line = SVGLine(y1=y1, x2=x2, y2=y2)
        assert line.x1 == 0.0
        assert line.y1 == y1
        assert line.x2 == x2
        assert line.y2 == y2

    @pytest.mark.parametrize(
        ("x1", "x2", "y2"),
        [
            (50.0, 30.0, 20.0),
        ],
        ids=["case1"],
    )
    def test_constructor_null_y1(
        self,
        x1: float,
        x2: float,
        y2: float,
    ) -> None:
        line = SVGLine(x1=x1, x2=x2, y2=y2)
        assert line.x1 == x1
        assert line.y1 == 0.0
        assert line.x2 == x2
        assert line.y2 == y2

    @pytest.mark.parametrize(
        ("x1", "y1", "y2"),
        [
            (50.0, 40.0, 20.0),
        ],
        ids=["case1"],
    )
    def test_constructor_null_x2(
        self,
        x1: float,
        y1: float,
        y2: float,
    ) -> None:
        line = SVGLine(x1=x1, y1=y1, y2=y2)
        assert line.x1 == x1
        assert line.y1 == y1
        assert line.x2 == 0.0
        assert line.y2 == y2

    @pytest.mark.parametrize(
        ("x1", "y1", "x2"),
        [
            (50.0, 40.0, 30.0),
        ],
        ids=["case1"],
    )
    def test_constructor_null_y2(
        self,
        x1: float,
        y1: float,
        x2: float,
    ) -> None:
        line = SVGLine(x1=x1, y1=y1, x2=x2)
        assert line.x1 == x1
        assert line.y1 == y1
        assert line.x2 == x2
        assert line.y2 == 0.0

    def test_constructor_null(self) -> None:
        line = SVGLine()
        assert line.x1 == 0.0
        assert line.y1 == 0.0
        assert line.x2 == 0.0
        assert line.y2 == 0.0

    @pytest.mark.parametrize(
        ("x1", "y1", "x2", "y2", "expected"),
        [
            (50.0, 40.0, 30.0, 20.0, "M 50.0,40.0 L 30.0,20.0"),
        ],
        ids=["case1"],
    )
    def test_path_repr(
        self,
        x1: float,
        y1: float,
        x2: float,
        y2: float,
        expected: str,
    ) -> None:
        line = SVGLine(x1=x1, y1=y1, x2=x2, y2=y2)
        assert line.path_repr() == expected

    @pytest.mark.parametrize(
        ("x1", "y1", "x2", "y2", "expected"),
        [
            (50.0, 40.0, 30.0, 20.0, '<line x1="50.0" y1="40.0" x2="30.0" y2="20.0"/>'),
        ],
        ids=["case1"],
    )
    def test_svg_repr(
        self,
        x1: float,
        y1: float,
        x2: float,
        y2: float,
        expected: str,
    ) -> None:
        line = SVGLine(x1=x1, y1=y1, x2=x2, y2=y2)
        assert line.svg_repr() == expected
