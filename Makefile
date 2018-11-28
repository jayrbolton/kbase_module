.PHONY: test

test:
	pip install -e .
	python -m unittest discover src/test
