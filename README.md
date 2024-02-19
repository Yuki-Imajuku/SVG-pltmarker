![PyPI - Version](https://img.shields.io/pypi/v/svg-pltmarker)
![PyPI - Status](https://img.shields.io/pypi/status/svg-pltmarker)
![PyPI - License](https://img.shields.io/pypi/l/svg-pltmarker)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/svg-pltmarker)
![PyPI - Format](https://img.shields.io/pypi/format/svg-pltmarker)
![PyPI - Downloads](https://img.shields.io/pypi/dd/svg-pltmarker)
[![pytest](https://github.com/Yuki-Imajuku/SVG-pltmarker/actions/workflows/pytest.yml/badge.svg)](https://github.com/Yuki-Imajuku/SVG-pltmarker/actions/workflows/pytest.yml)

# SVG-pltmarker
A Python library for generating matplotlib markers from SVG files.


## Install
```sh
pip install svg-pltmarker
pip install 'svg-pltmarker[dev]'  # for developers
```


## Dependencies
Python version 3.10.0 or higher is required.

Libraries:
- [matplotlib](https://github.com/matplotlib/matplotlib) >= 3.6.0
- [NumPy](https://github.com/numpy/numpy) >= 1.22.0
- [pydantic](https://github.com/pydantic/pydantic) >= 2.0.0


# Usage
[Sample notebook (Colaboratory)](https://colab.research.google.com/drive/1YGBuv989P6mco8-EPWTqPBMccojDAcVa?usp=sharing)

```python
import matplotlib.pyplot as plt
import numpy as np
from svg_pltmarker import get_marker_from_svg


# Generate Maplotlib marker from SVG file.
marker = get_marker_from_svg(url="https://upload.wikimedia.org/wikipedia/commons/8/84/Matplotlib_icon.svg")

# Scatter plot
fig, ax = plt.subplots(figsize=(10, 10))
ax.set_aspect("equal")
ax.set_axis_off()
x, y = np.meshgrid(np.linspace(0, 2, 11), np.linspace(0, 2, 11))
plt.scatter(x, y, marker=marker, s=2500, color="None", edgecolors="black")
plt.xlim(0, 2)
plt.ylim(0, 2)
plt.show()
```

Then get below figure:

![Sample Figure](https://github.com/Yuki-Imajuku/SVG-pltmarker/blob/main/figures/sample_figure.png)


## Reference
1. [https://developer.mozilla.org/ja/docs/Web/SVG/Element](https://developer.mozilla.org/ja/docs/Web/SVG/Element)
2. [https://triple-underscore.github.io/SVG11/shapes.html](https://triple-underscore.github.io/SVG11/shapes.html)
3. [https://github.com/nvictus/svgpath2mpl](https://github.com/nvictus/svgpath2mpl)
