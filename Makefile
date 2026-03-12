.PHONY: build install run test clean

VENV = .venv
PYTHON = $(VENV)/bin/python
PIP = $(VENV)/bin/pip

build: $(VENV)
	$(PIP) install -r requirements.txt

install: $(VENV)
	$(PIP) install -e .

$(VENV):
	python3 -m venv $(VENV)

run:
	$(PYTHON) -m plaid_cli $(ARGS)

test:
	$(PYTHON) -m pytest tests/ -v

clean:
	rm -rf $(VENV) __pycache__ plaid_cli/__pycache__ tests/__pycache__ *.db
