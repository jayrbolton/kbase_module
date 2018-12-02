#!/usr/bin/env python
"""
Run a method as a one-off job from within a docker container for a module.
Input data is dropped into /kb/module/work/input.json, and output is set to /kb/module/work/output.json

Simply run this with `python run_job.py`
    or `python -m kbase_module.run_job` if the package is installed
"""
import sys
import os
import json

from kbase_module.utils.run_method import run_method

module_path = os.environ.get('KBASE_MODULE_PATH', '/kb/module')
sys.path.insert(0, os.path.join(module_path, 'src'))


def _fatal(msg):
    """Fatal error with log and exit."""
    sys.stderr.write(msg + '\n')
    sys.exit(1)


def main():
    """Run a single method to completion, reading and writing from json files."""
    input_path = os.path.join(module_path, 'work', 'input.json')
    if not os.path.exists(input_path):
        _fatal('Input JSON does not exist at %s' % input_path)
    output_path = os.path.join(module_path, 'work', 'output.json')
    schema_path = os.path.join(module_path, 'kbase_methods.json')
    if not os.path.exists(schema_path):
        _fatal('%s does not exist' % schema_path)
    with open(input_path, 'r', encoding='utf8') as fd:
        input_data = json.load(fd)
    # For some reason, all params for kbase services seem to be wrapped in an extra array
    params = input_data['params'][0]
    method_name = input_data['method']
    # Try to run the method
    output_data = {'id': input_data.get('id'), 'jsonrpc': '2.0'}
    try:
        result = run_method(method_name, params)
        output_data['result'] = result
    except Exception as err:
        output_data['error'] = str(err)
    print(output_data)  # -> stdout
    # Save to /kb/module/work/output.json
    with open(output_path, 'w', encoding='utf8') as fd:
        json.dump(output_data, fd)


if __name__ == '__main__':
    main()
