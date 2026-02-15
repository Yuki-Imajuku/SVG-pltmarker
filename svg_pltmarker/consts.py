"""Shared constants for svg_pltmarker internals."""

# Generic x/y pair length used across SVG coordinate parsing.
POINT_PAIR_COUNT = 2
# Number token including optional exponent notation (e.g. 1e-3).
PATH_NUMBER_PATTERN = r"[-+]?(?:\d+\.\d*|\.\d+|\d+)(?:[eE][-+]?\d+)?"

PATH_COMMAND_PATTERN = r"[MmLlHhVvCcSsQqTtAaZz]"
PATH_COMMAND_POINTS = POINT_PAIR_COUNT
PATH_CURVE4_POINTS = 6
PATH_CURVE3_POINTS = 4
PATH_ARC_POINTS = 7

PATH_ARC_RADIUS_X_INDEX = 0
PATH_ARC_RADIUS_Y_INDEX = 1
PATH_ARC_ANGLE_INDEX = 2
PATH_ARC_FLAG_LARGE_INDEX = 3
PATH_ARC_FLAG_SWEEP_INDEX = 4
PATH_ARC_END_X_INDEX = 5
PATH_ARC_END_Y_INDEX = 6

PATH_FULL_ROTATION_DEGREE = 360.0
