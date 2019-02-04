#!/bin/bash

# Docker container entrypoint script
# When you run `docker run my-app xyz`, then this script is run

set -e

# Set the number of gevent workers to number of cores * 2 + 1
# See: http://docs.gunicorn.org/en/stable/design.html#how-many-workers
calc_workers="$(($(nproc) * 2 + 1))"
# This will also use the WORKERS environment variable, if present
workers=${WORKERS:-$calc_workers}

# Persistent server mode (aka "dynamic service"):
# This is run when there are no arguments
if [ $# -eq 0 ] || [ "${1}" = "serve" ]; then
  echo "Running as a dynamic service"
  gunicorn \
    --worker-class gevent \
    --timeout 1800 \
    --workers $n_workers \
    --bind :5000 \
    ${DEVELOPMENT:+"--reload"} \
    src.server:app

# Run tests
elif [ "${1}" = "test" ] ; then
  flake8 src
  python -m unittest discover src/test

# One-off jobs
elif [ "${1}" = "async" ] ; then
  python -m kbase_module.run_job

# Initialize the module
elif [ "${1}" = "init" ] ; then
  echo "Nothing to do."

# Run shell in the container
elif [ "${1}" = "bash" ] || [ "${1}" = "shell" ]; then
  /bin/sh

# Required file for registering the module on the KBase catalog
elif [ "${1}" = "report" ] ; then
  python -m kbase_module.compile_config

else
  echo "Unknown command. Valid commands are: test, async, init, shell, serve, or report"
fi
