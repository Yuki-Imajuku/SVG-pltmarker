.PHONY: help lint format typecheck test build release

help:
	@echo "lint - run ruff check"
	@echo "format - format code with ruff"
	@echo "typecheck - run ty check"
	@echo "test - run pytest"
	@echo "build - package the project"
	@echo "release - package and upload a release"

lint:
	uv run ruff check .

format:
	uv run ruff format .

typecheck:
	uv run ty check

test:
	uv run pytest --cov=svg_pltmarker --cov-report=term-missing --cov-report=json:coverage.json --cov-fail-under=90

build:
	python -m build --wheel

release:
	twine upload dist/*
