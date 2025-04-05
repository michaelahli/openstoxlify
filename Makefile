PYTHON = python3
VENV_DIR = venv

.PHONY: venv install build test upload clean

venv:
	$(PYTHON) -m venv $(VENV_DIR)

install: venv
	$(VENV_DIR)/bin/pip install --upgrade pip
	$(VENV_DIR)/bin/pip install -r requirements.txt

build:
	$(VENV_DIR)/bin/pip install build twine
	$(VENV_DIR)/bin/python -m build

test:
	$(VENV_DIR)/bin/python -m pytest tests/

upload:
	$(VENV_DIR)/bin/python -m twine upload dist/*

clean:
	rm -rf $(VENV_DIR) dist build *.egg-info

setup: venv install
	$(VENV_DIR)/bin/python setup.py install
