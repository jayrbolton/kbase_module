import os
import json
import jsonschema
from jsonschema.exceptions import ValidationError

module_path = os.environ.get('KBASE_MODULE_PATH', '/kb/module')
schema_path = os.path.join(module_path, 'kbase_methods.json')

# Schema for the kbase_methods.json file
methods_schema = {
    'type': 'object',
    'patternProperties': {
        r'^.+$': {
            'type': 'object',
            'required': ['label'],
            'properties': {
                'label': {'type': 'string'},
                'description': {'type': 'string'},
                'required_params': {
                    'type': 'array',
                    'items': {'type': 'string'}
                },
                'params': {
                    'type': 'object'
                }
            }
        }
    }
}


def _validate(name, data, schema):
    """Validate a jsonschema with error handling."""
    try:
        jsonschema.validate(data, schema)
    except ValidationError as err:
        path = ['root'] + list(err.path)
        raise RuntimeError('\n'.join([
            'Validation error on %s' % name,
            '  Message: %s' % err.message,
            '  Path: %s' % '.'.join(path)
        ]))


def validate_method_params(method_name, params):
    """Load the schema for the method and validate the params."""
    with open(schema_path, 'r', encoding='utf8') as fd:
        try:
            schemas = json.load(fd)
        except ValueError:
            raise RuntimeError('Unable to parse JSON in %s' % schema_path)
    _validate('kbase_methods.json', schemas, methods_schema)
    if method_name not in schemas:
        raise RuntimeError('No method defined in kbase_methods.json named "%s"' % method_name)
    schema = {'type': 'object'}
    if 'required_params' in schemas[method_name]:
        schema['required'] = schemas[method_name]['required_params']
    if 'params' in schemas[method_name]:
        schema['properties'] = schemas[method_name]['params']
    _validate('params to "%s"' % method_name, params, schema)
