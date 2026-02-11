install:
	python3 -m venv .venv
	.venv/bin/pip install -e ".[dev]"

test:
	.venv/bin/pytest -v

check:
	.venv/bin/ruff check .
	.venv/bin/ruff format --check .
