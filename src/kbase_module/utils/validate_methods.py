import os
import yaml
import jsonschema
from jsonschema.exceptions import ValidationError

module_path = os.environ.get('KBASE_MODULE_PATH', '/kb/module')
schema_path = os.path.join(module_path, 'kbase_methods.yaml')

# Schema for the kbase_methods.yaml file
methods_schema = {
    'type': 'object',
    'patternProperties': {
        r'^.+$': {
            'type': 'object',
            'properties': {
                'label': {'type': 'string'},
                'description': {'type': 'string'},
                'required_params': {
                    'type': 'array',
                    'default': [],
                    'items': {'type': 'string'}
                },
                'params': {
                    'default': {},
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


def validate_methods_config():
    """Validate kbase_methods.yaml and return it as a dict."""
    if not os.path.exists(schema_path):
        raise RuntimeError('%s does not exist' % schema_path)
    with open(schema_path, 'r') as fd:
        try:
            schemas = yaml.load(fd)
        except Exception as err:
            raise RuntimeError('Unable to parse YAML in %s: %s' % (schema_path, str(err)))
    _validate('kbase_methods.yaml', schemas, methods_schema)
    return schemas


def validate_method_params(method_name, params):
    """Load the schema for the method and validate the params."""
    schemas = validate_methods_config()
    if method_name not in schemas:
        raise RuntimeError('No method defined in kbase_methods.yaml named "%s"' % method_name)
    schema = {'type': 'object'}
    if 'required_params' in schemas[method_name]:
        schema['required'] = schemas[method_name]['required_params']
    if 'params' in schemas[method_name]:
        schema['properties'] = schemas[method_name]['params']
    _validate('params to "%s"' % method_name, params, schema)
