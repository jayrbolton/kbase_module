#! /bin/sh

set -e

export KBASE_MODULE_PATH=$(pwd)/src/test/test_app

entrypoint.sh serve
