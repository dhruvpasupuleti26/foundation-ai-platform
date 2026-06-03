PYTHON ?= $(shell command -v python3.13 || command -v python3.12 || command -v python3)

.PHONY: init test

init:
	$(PYTHON) -c "import sys; sys.exit('Python 3.12+ is required.') if sys.version_info < (3, 12) else None"
	$(PYTHON) -m pip install -e '.[dev]'
	$(PYTHON) scripts/bootstrap.py

test:
	$(PYTHON) -c "import sys; sys.exit('Python 3.12+ is required.') if sys.version_info < (3, 12) else None"
	$(PYTHON) -m pytest
