.PHONY: setup data features fit simulate all test clean

PY := .venv/bin/python

setup:
	python3 -m venv .venv
	$(PY) -m pip install --upgrade pip
	$(PY) -m pip install -r requirements.txt
	$(PY) -m pip install -e .

data:
	$(PY) scripts/01_generate_data.py

features:
	$(PY) scripts/02_build_features.py

fit:
	$(PY) scripts/03_fit_model.py

simulate:
	$(PY) scripts/04_simulate_tournament.py

# Full pipeline, in order.
all: data features fit simulate

test:
	$(PY) -m pytest

clean:
	rm -rf data/raw/* data/interim/* data/processed/* artifacts/*
	find . -name __pycache__ -type d -prune -exec rm -rf {} +
