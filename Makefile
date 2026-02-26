install:
	python3 -m venv .venv
	.venv/bin/pip install -e ".[dev]"
	.venv/bin/pre-commit install

check:
	.venv/bin/ruff check .
	.venv/bin/ruff format --check .

format:
	.venv/bin/ruff check --fix .
	.venv/bin/ruff format .

test:
	.venv/bin/pytest -v

test-all-checks:
	.venv/bin/pytest -v -k "all-checks"

practical-test:
	.venv/bin/docalign docs/ --fix

changelog:
	.venv/bin/towncrier build --yes --version $(shell python3 -c "import tomllib; print(tomllib.load(open('pyproject.toml','rb'))['project']['version'])")

changelog-draft:
	.venv/bin/towncrier build --draft --version $(shell python3 -c "import tomllib; print(tomllib.load(open('pyproject.toml','rb'))['project']['version'])")

build:
	.venv/bin/pip install hatch
	.venv/bin/hatch build

clean:
	rm -rf .venv dist build *.egg-info src/*.egg-info

.PHONY: install check format test test-all-checks practical-test changelog changelog-draft build clean
