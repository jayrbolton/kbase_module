#!/bin/bash

# Docker container entrypoint script
# When you run `docker run my-app xyz`, then this script is run

set -e

# Set the number of gevent workers to number of cores * 2 + 1
# See: http://docs.gunicorn.org/en/stable/design.html#how-many-workers
calc_workers="$(($(nproc) * 2 + 1))"
# This will also use the WORKERS environment variable, if present
n_workers=${WORKERS:-$calc_workers}

# Persistent server mode (aka "dynamic service"):
# This is run when there are no arguments or with "serve"
if [ $# -eq 0 ] || [ "${1}" = "serve" ]; then
  echo "Running as a dynamic service (persistent server)"
  if [ -f $KBASE_MODULE_PATH/scripts/setup.sh ]; then
    sh $KBASE_MODULE_PATH/scripts/setup.sh
  fi
  gunicorn \
    --worker-class gevent \
    --timeout 1800 \
    --workers $n_workers \
    --bind :5000 \
    ${DEVELOPMENT:+"--reload"} \
    kbase_module.run_service:app

# Run tests
elif [ "${1}" = "test" ] ; then
  flake8 src
  if [ -f $KBASE_MODULE_PATH/scripts/setup.sh ]; then
    sh $KBASE_MODULE_PATH/scripts/setup.sh
  fi
  if [ -f $KBASE_MODULE_PATH/scripts/test.sh ]; then
    sh $KBASE_MODULE_PATH/scripts/test.sh
  fi
  python -m unittest discover $KBASE_MODULE_PATH/src/test

# One-off jobs
elif [ "${1}" = "async" ] ; then
  if [ -f $KBASE_MODULE_PATH/scripts/setup.sh ]; then
    sh $KBASE_MODULE_PATH/scripts/setup.sh
  fi
  python -m kbase_module.run_job

# Initialize the module
elif [ "${1}" = "init" ] ; then
  if [ -f $KBASE_MODULE_PATH/scripts/setup.sh ]; then
    sh $KBASE_MODULE_PATH/scripts/setup.sh
  fi

# Run shell in the container
elif [ "${1}" = "bash" ] || [ "${1}" = "shell" ]; then
  /bin/sh

# Required file for registering the module on the KBase catalog
elif [ "${1}" = "report" ] ; then
  python -m kbase_module.compile_config

else
  echo "Unknown command. Valid commands are: test, async, init, shell, serve, or report"
fi
