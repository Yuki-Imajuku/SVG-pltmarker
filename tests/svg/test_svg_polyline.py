from svg_pltmarker import SVGPath, SVGPolyline


if __name__ == "__main__":
    polyline1 = SVGPolyline(points="0,100 50,25 50,75 100,0")
    polyline2 = SVGPolyline(points="150,0 121,90 198,35 102,35 179,90")
    print(SVGPath(d=polyline1.path_repr()).svg_repr())
    print(SVGPath(d=polyline2.path_repr()).svg_repr())

    true_polyline1 = SVGPolyline(points="0,200 50,125 50,175 100,100")
    true_polyline2 = SVGPolyline(points="150,100 121,190 198,135 102,135 179,190")
    print(true_polyline1.svg_repr())
    print(true_polyline2.svg_repr())
