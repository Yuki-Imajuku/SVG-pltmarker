import matplotlib.pyplot as plt
import numpy as np

from svg_pltmarker import get_marker_from_svg

# Generate Maplotlib marker from SVG file.
marker = get_marker_from_svg(
    url="https://upload.wikimedia.org/wikipedia/commons/8/84/Matplotlib_icon.svg"
)

# Scatter plot
fig, ax = plt.subplots(figsize=(10, 10))
ax.set_aspect("equal")
ax.set_axis_off()
x, y = np.meshgrid(np.linspace(0, 2, 11), np.linspace(0, 2, 11))
plt.scatter(x, y, marker=marker, s=2500, color="None", edgecolors="black")
plt.xlim(0, 2)
plt.ylim(0, 2)
plt.show()
