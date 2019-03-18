#!/bin/sh

set -e

export KBASE_MODULE_PATH=$(pwd)/src/test/test_app

pip install -e .
pip install -r dev-requirements.txt
flake8 src
mypy --ignore-missing-imports src
bandit -r src
python -m unittest discover src/test/
