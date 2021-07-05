LINT_DIRS = setup.py src/voucher_selection src/tests

setup:
	pip install -r requirements-dev.txt

test:
	pytest -v src/tests

format:
	black $(LINT_DIRS)
	isort --recursive $(LINT_DIRS)

lint: format
	black --check $(LINT_DIRS)
	flake8 $(LINT_DIRS)
	isort --check --recursive $(LINT_DIRS)
