from svg_pltmarker import SVGEllipse, SVGPath


if __name__ == "__main__":
    ellipse1 = SVGEllipse(cx=50, cy=150, rx=20, ry=30)
    ellipse2 = SVGEllipse(cx=150, cy=150, rx=30, ry=30)
    ellipse3 = SVGEllipse(cx=250, cy=150, rx=40, ry=30)
    print(SVGPath(d=ellipse1.path_repr()).svg_repr())
    print(SVGPath(d=ellipse2.path_repr()).svg_repr())
    print(SVGPath(d=ellipse3.path_repr()).svg_repr())

    true_ellipse1 = SVGEllipse(cx=50, cy=50, rx=20, ry=30)
    true_ellipse2 = SVGEllipse(cx=150, cy=50, rx=30, ry=30)
    true_ellipse3 = SVGEllipse(cx=250, cy=50, rx=40, ry=30)
    print(true_ellipse1.svg_repr())
    print(true_ellipse2.svg_repr())
    print(true_ellipse3.svg_repr())
