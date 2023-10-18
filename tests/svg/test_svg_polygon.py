from svg_pltmarker import SVGPath, SVGPolygon


if __name__ == "__main__":
    polygon1 = SVGPolygon(points="0,100 50,25 50,75 100,0")
    polygon2 = SVGPolygon(points="150,0 121,90 198,35 102,35 179,90")
    print(SVGPath(d=polygon1.path_repr()).svg_repr())
    print(SVGPath(d=polygon2.path_repr()).svg_repr())

    true_polygon1 = SVGPolygon(points="0,200 50,125 50,175 100,100")
    true_polygon2 = SVGPolygon(points="150,100 121,190 198,135 102,135 179,190")
    print(true_polygon1.svg_repr())
    print(true_polygon2.svg_repr())
