from svg_pltmarker import SVGCircle, SVGPath


if __name__ == "__main__":
    circle1 = SVGCircle(cx=50, cy=50, r=30)
    circle2 = SVGCircle(cx=150, cy=50, r=10)
    print(SVGPath(d=circle1.path_repr()).svg_repr())
    print(SVGPath(d=circle2.path_repr()).svg_repr())

    true_circle1 = SVGCircle(cx=50, cy=150, r=30)
    true_circle2 = SVGCircle(cx=150, cy=150, r=10)
    print(true_circle1.svg_repr())
    print(true_circle2.svg_repr())
