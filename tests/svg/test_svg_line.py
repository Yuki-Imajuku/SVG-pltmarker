from svg_pltmarker import SVGLine, SVGPath


if __name__ == "__main__":
    line1 = SVGLine(x1=10, y1=150, x2=10, y2=190)
    line2 = SVGLine(x1=150, y1=150, x2=110, y2=190)
    line3 = SVGLine(x1=290, y1=150, x2=210, y2=190)
    print(SVGPath(d=line1.path_repr()).svg_repr())
    print(SVGPath(d=line2.path_repr()).svg_repr())
    print(SVGPath(d=line3.path_repr()).svg_repr())

    true_line1 = SVGLine(x1=10, y1=50, x2=10, y2=90)
    true_line2 = SVGLine(x1=150, y1=50, x2=110, y2=90)
    true_line3 = SVGLine(x1=290, y1=50, x2=210, y2=90)
    print(true_line1.svg_repr())
    print(true_line2.svg_repr())
    print(true_line3.svg_repr())
