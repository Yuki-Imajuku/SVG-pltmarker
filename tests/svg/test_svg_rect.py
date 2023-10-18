from svg_pltmarker import SVGPath, SVGRect


if __name__ == "__main__":
    rect1 = SVGRect(x=20, y=120, width=60, height=60, rx=0, ry=15)
    rect2 = SVGRect(x=120, y=120, width=60, height=60, rx=15, ry=15)
    rect3 = SVGRect(x=220, y=120, width=60, height=60, rx=150, ry=15)
    print(SVGPath(d=rect1.path_repr()).svg_repr())
    print(SVGPath(d=rect2.path_repr()).svg_repr())
    print(SVGPath(d=rect3.path_repr()).svg_repr())

    true_rect1 = SVGRect(x=20, y=20, width=60, height=60, rx=0, ry=15)
    true_rect2 = SVGRect(x=120, y=20, width=60, height=60, rx=15, ry=15)
    true_rect3 = SVGRect(x=220, y=20, width=60, height=60, rx=150, ry=15)
    print(true_rect1.svg_repr())
    print(true_rect2.svg_repr())
    print(true_rect3.svg_repr())
