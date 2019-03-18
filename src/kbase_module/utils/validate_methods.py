import os
import yaml
import jsonschema
from jsonschema.exceptions import ValidationError

from kbase_module.utils.load_config import load_config


def _validate(name, data, schema):
    """Validate method params using a jsonschema with error handling."""
    try:
        jsonschema.validate(data, schema)
    except ValidationError as err:
        path = ['root'] + list(err.path)
        raise RuntimeError('\n'.join([
            'Validation error on %s' % name,
            '  Message: ' + err.message,
            '  Path: ' + str(path)
        ]))


def load_method_config():
    """Validate kbase_methods.yaml and return it as a dict."""
    config = load_config()
    p = config['methods_config_path']
    if not os.path.exists(p):
        raise RuntimeError(f'{p} does not exist')
    with open(p) as fd:
        try:
            schemas = yaml.load(fd.read(), Loader=yaml.SafeLoader)
        except Exception as err:
            raise RuntimeError(f'Unable to parse YAML in {p}: {err}')
    return schemas


def validate_method_params(method_name, params):
    """Load the schema for the method and validate the params."""
    schemas = load_method_config()
    if method_name not in schemas:
        raise RuntimeError(f'No method defined in kbase_methods.yaml named "{method_name}"')
    schema = {'type': 'object'}
    if 'required_params' in schemas[method_name]:
        schema['required'] = schemas[method_name]['required_params']
    if 'params' in schemas[method_name]:
        schema['properties'] = schemas[method_name]['params']
    _validate(f'params to "{method_name}"', params, schema)
