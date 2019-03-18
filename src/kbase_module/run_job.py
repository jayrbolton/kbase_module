#!/usr/bin/env python
"""
Run a method as a one-off job from within a docker container for a module.
Input data is dropped into /kb/module/work/input.json, and output is set to /kb/module/work/output.json

This can be run using `./scripts/entrypoint.sh async`
With an input.json file placed at `/kb/module/work/input.json
"""
import sys
import os
import json

from kbase_module.utils.run_method import run_method
from kbase_module.utils.validate_methods import validate_method_params
from kbase_module.utils.load_config import load_config


def main():
    """Run a single method to completion, reading and writing from json files."""
    config = load_config()
    if not os.path.exists(config['input_json_path']):
        _fatal(f"Input JSON does not exist at {config['input_json_path']}")
    with open(config['input_json_path']) as fd:
        input_data = json.load(fd)
    if 'params' not in input_data:
        raise RuntimeError(f"'params' key not found in {config['input_json_path']}")
    if 'method' not in input_data:
        raise RuntimeError(f"'method' key not found in {config['input_json_path']}")
    # For some reason, all params for kbase services seem to be wrapped in an extra array
    params = input_data['params']
    method_name = input_data['method']
    # Validate the params
    validate_method_params(method_name, params)
    # Try to run the method
    output_data = {'id': input_data.get('id'), 'jsonrpc': '2.0'}
    try:
        result = run_method(method_name, params)
        output_data['result'] = result
    except Exception as err:
        output_data['error'] = str(err)
    print(output_data)  # -> stdout
    # Save to /kb/module/work/output.json
    with open(config['output_json_path'], 'w') as fd:
        json.dump(output_data, fd)


def _fatal(msg):
    """Fatal error with log and exit."""
    sys.stderr.write(msg + '\n')
    sys.exit(1)


if __name__ == '__main__':
    main()
