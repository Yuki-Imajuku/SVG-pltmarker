![PyPI - Version](https://img.shields.io/pypi/v/svg-pltmarker)
![PyPI - Status](https://img.shields.io/pypi/status/svg-pltmarker)
![PyPI - License](https://img.shields.io/pypi/l/svg-pltmarker)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/svg-pltmarker)
![PyPI - Format](https://img.shields.io/pypi/format/svg-pltmarker)
![PyPI - Downloads](https://img.shields.io/pypi/dd/svg-pltmarker)
[![Coverage >=90%](https://img.shields.io/badge/coverage-%E2%89%A590%25-brightgreen)](https://github.com/Yuki-Imajuku/SVG-pltmarker/actions/workflows/test.yml)
[![test](https://github.com/Yuki-Imajuku/SVG-pltmarker/actions/workflows/test.yml/badge.svg)](https://github.com/Yuki-Imajuku/SVG-pltmarker/actions/workflows/test.yml)
[![lint](https://github.com/Yuki-Imajuku/SVG-pltmarker/actions/workflows/lint.yml/badge.svg)](https://github.com/Yuki-Imajuku/SVG-pltmarker/actions/workflows/lint.yml)


# SVG-pltmarker

Convert SVG graphics into Matplotlib marker paths.


## Install

```bash
pip install svg-pltmarker
```

For development:

```bash
uv sync --dev
```


## Usage

```python
import matplotlib.pyplot as plt
import numpy as np
from svg_pltmarker import get_marker_from_svg

marker = get_marker_from_svg(
    url="https://upload.wikimedia.org/wikipedia/commons/8/84/Matplotlib_icon.svg"
)

fig, ax = plt.subplots(figsize=(6, 6))
ax.set_aspect("equal")
ax.set_axis_off()
x, y = np.meshgrid(np.linspace(0, 2, 11), np.linspace(0, 2, 11))
plt.scatter(x, y, marker=marker, s=2500, color="None", edgecolors="black")
plt.show()
```


## Project links

- [Reference: MDN SVG Elements](https://developer.mozilla.org/ja/docs/Web/SVG/Element)
- [SVG 1.1 Shapes](https://triple-underscore.github.io/SVG11/shapes.html)
- [svgpath2mpl](https://github.com/nvictus/svgpath2mpl)
- [Sample Notebook (Colaboratory)](https://colab.research.google.com/drive/1YGBuv989P6mco8-EPWTqPBMccojDAcVa?usp=sharing)


## Dependencies

- Python >= 3.10
- matplotlib >= 3.6.0
- numpy >= 1.22.0
- pydantic >= 2.0.0


## Development

```bash
# Format code
uv run ruff format .

# Lint
uv run ruff check .

# Type check
uv run ty check

# Tests
uv run pytest
```

Equivalent targets are also available in `Makefile` (`make format`, `make lint`, `make typecheck`, `make test`).

See [CONTRIBUTING.md](CONTRIBUTING.md) for contribution workflow details.
