.PHONY: test

SHELL := /bin/bash

test:
	pip install -e .
	python -m unittest discover src/test
