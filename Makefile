# Makefile for P&G Advertisement Budget Optimizer (pg_ad_optimizer)

.PHONY: help install ingest features metrics recommendations test quality dashboard all clean

PYTHON := python
PIP := pip
STREAMLIT := streamlit
PYTEST := pytest

help:
	@echo "P&G Advertisement Budget Optimizer CLI"
	@echo "Available commands:"
	@echo "  make install         Install dependencies from requirements.txt"
	@echo "  make all             Run end-to-end data pipeline & generate reports"
	@echo "  make sample          Run pipeline with sample fixture data"
	@echo "  make test            Run complete pytest test suite"
	@echo "  make dashboard       Launch interactive Streamlit decision dashboard"
	@echo "  make clean           Clean cache and temporary files"

install:
	$(PIP) install -r requirements.txt

all:
	$(PYTHON) run_pipeline.py --all

sample:
	$(PYTHON) run_pipeline.py --sample

test:
	$(PYTEST) tests/ -v

dashboard:
	$(STREAMLIT) run src/dashboard/app.py

clean:
	rm -rf data/cache/*.csv data/cache/raw_temp logs/*.log .pytest_cache
