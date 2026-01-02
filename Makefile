PYTHON = python3
VENV_DIR = venv

.PHONY: venv install build test upload clean setup release check-version

venv:
	$(PYTHON) -m venv $(VENV_DIR)

install: venv
	$(VENV_DIR)/bin/pip install --upgrade pip
	$(VENV_DIR)/bin/pip install -r requirements.txt

build: venv
	$(VENV_DIR)/bin/pip install build twine
	$(VENV_DIR)/bin/python -m build

test: venv install
	$(VENV_DIR)/bin/python -m pytest tests/ -v

check: build
	$(VENV_DIR)/bin/python -m twine check dist/*

upload: check
	@echo "Uploading to PyPI..."
	$(VENV_DIR)/bin/python -m twine upload dist/*

upload-test: check
	@echo "Uploading to TestPyPI..."
	$(VENV_DIR)/bin/python -m twine upload --repository testpypi dist/*

release: clean test build upload
	@echo "Release completed successfully!"

clean:
	rm -rf $(VENV_DIR) dist build *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name .pytest_cache -exec rm -rf {} +

setup: venv install
	$(VENV_DIR)/bin/python setup.py install

check-version:
	@echo "Current version in pyproject.toml:"
	@grep '^version = ' setup.cfg || echo "Version not found!"
