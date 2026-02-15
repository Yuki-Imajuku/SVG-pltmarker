# Contributing

Thank you for your interest in contributing to `svg-pltmarker`.

## Setup

```bash
git clone https://github.com/Yuki-Imajuku/SVG-pltmarker.git
cd SVG-pltmarker
uv sync --dev
```

## Code Quality Checks

### Format

```bash
uv run ruff format .
```

### Lint

```bash
uv run ruff check .
```

### Type Check

```bash
uv run ty check
```

### Tests

```bash
uv run pytest
```

## Recommended Workflow

1. `uv run ruff format .`
2. `uv run ruff check .`
3. `uv run ty check`
4. `uv run pytest`

Equivalent Makefile targets are also available:
`make format`, `make lint`, `make typecheck`, `make test`.

## Pull Request Flow

- Run all checks before opening a pull request, even for small changes.
- Update `README.md` when behavior, public API, or usage examples are changed.
- When public APIs are modified, include corresponding test updates.
