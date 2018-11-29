#!/usr/bin/env python
"""
Run a method as a one-off job from within a docker container for a module.
Input data is dropped into /kb/module/work/input.json, and output is set to /kb/module/work/output.json

Simply run this with `python run_job.py`
    or `python -m kbase_module.run_job` if the package is installed
"""
import sys
import os
import jsonschema
from jsonschema.exceptions import ValidationError
import json
import importlib

module_path = os.environ.get('KBASE_MODULE_PATH', '/kb/module')
sys.path.insert(0, os.path.join(module_path, 'src'))


def _fatal(msg):
    """Fatal error with log and exit."""
    sys.stderr.write(msg + '\n')
    sys.exit(1)


if __name__ == '__main__':
    input_path = os.path.join(module_path, 'work', 'input.json')
    if not os.path.exists(input_path):
        _fatal('Input JSON does not exist at %s' % input_path)
    output_path = os.path.join(module_path, 'work', 'output.json')
    schema_path = os.path.join(module_path, 'kbase_methods.json')
    if not os.path.exists(schema_path):
        _fatal('%s does not exist' % schema_path)
    with open(input_path, 'r', encoding='utf8') as fd:
        input_data = json.load(fd)
    with open(schema_path, 'r', encoding='utf8') as fd:
        schemas = json.load(fd)
    method_name = input_data['method']
    if method_name not in schemas:
        raise Exception('No schema defined for method name: ' + method_name)
    # For some reason, all params for kbase services seem to be wrapped in an extra array
    params = input_data['params'][0]
    schema = {
        'type': 'object',
        'required': schemas[method_name].get('required_params', []),
        'properties': schemas[method_name].get('params', {})
    }
    try:
        jsonschema.validate(params, schema)
    except ValidationError as err:
        _fatal("JSON schema validation error on parameters:\n%s" % str(err))
    # Get the method from the module (TODO add error handling here)
    main = importlib.import_module("main")
    try:
        method = getattr(main, method_name)
    except AttributeError:
        _fatal('No method found in main.py called %s' % method_name)
    try:
        result = method(params)
        error = None
    except Exception as err:
        result = None
        error = str(err)
    output_data = {
        "id": input_data.get('id'),
        "result": result,
        "cancelled": 0,
        "error": error
    }
    with open(output_path, 'w', encoding='utf8') as fd:
        json.dump(output_data, fd)
