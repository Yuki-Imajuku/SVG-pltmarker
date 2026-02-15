"""Internal helpers for circle/ellipse path generation."""


def ellipse_arc_path(cx: float, cy: float, rx: float, ry: float) -> str:
    """Build a closed ellipse-like arc path."""
    return (
        f"M {cx + rx},{cy} "
        f"A {rx},{ry} 0,1,0 {cx},{cy + ry} "
        f"A {rx},{ry} 0,1,0 {cx - rx},{cy} "
        f"A {rx},{ry} 0,1,0 {cx},{cy - ry} "
        f"A {rx},{ry} 0,1,0 {cx + rx},{cy} Z"
    )
