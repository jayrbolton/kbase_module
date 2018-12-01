#!/bin/bash

# Docker container entrypoint script
# When you run `docker run my-app xyz`, then this script is run

set -e

# Set the number of gevent workers to number of cores * 2 + 1
# See: http://docs.gunicorn.org/en/stable/design.html#how-many-workers
calc_workers="$(($(nproc) * 2 + 1))"
# You can also use the WORKERS environment variable, if present
workers=${WORKERS:-$calc_workers}

# Persistent server mode (aka "dynamic service"):
# This is run when there are no arguments
if [ $# -eq 0 ] ; then
  echo "Running in persistent server mode"
  gunicorn --worker-class gevent --timeout 1800 --workers $workers -b :5000 --reload kbase_module.run_service:app

# Run tests
elif [ "${1}" = "test" ] ; then
  echo "Running tests..."
  flake8 src
  python -m unittest discover src/test
  echo "...done"

# One-off jobs
elif [ "${1}" = "async" ] ; then
  echo "Running a method to completion..."
  python -m kbase_module.run_job
  echo "..done"

# Initialize the module
elif [ "${1}" = "init" ] ; then
  echo "Initializing module... nothing to do."

# Bash shell in the container
elif [ "${1}" = "bash" ] ; then
  echo "Launching a bash shell in the docker container."
  /bin/bash

# Required file for registering the module on the KBase catalog
elif [ "${1}" = "report" ] ; then
  echo "Generating configuration for the catalog..."
  python -m kbase_module.compile_config
  echo "...done"

else
  echo "Unknown command. Valid commands are: test, async, init, bash, or report"
fi
