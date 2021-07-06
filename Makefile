LINT_DIRS = setup.py src/voucher_selection src/tests

setup:
	pip install -r requirements-dev.txt

test_unit:
	pytest -vs src/tests/unit -k test_api_voucher_ok_country_code_and_recency_segment

test_e2e:
	pytest -v src/tests/e2e

test: unit test_e2e
	@echo OK

format:
	black $(LINT_DIRS)
	isort $(LINT_DIRS)

lint: format
	black --check $(LINT_DIRS)
	flake8 $(LINT_DIRS)
	isort --check $(LINT_DIRS)
