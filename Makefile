help:
	@echo "lint - check style with flake8"
	@echo "format - format code with isort and black"
	@echo "build - package the project"
	@echo "test - run tests"
	@echo "release - package and upload a release"

lint:
	flake8 --exclude=env,venv,build,dist,*.egg-info,.eggs

format:
	isort -rc . && black .

test:
	pytest -v tests/

build:
	python -m build --wheel

release:
	twine upload dist/*
