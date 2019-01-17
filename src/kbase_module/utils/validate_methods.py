import os
import yaml
import jsonschema
from jsonschema.exceptions import ValidationError

module_path = os.environ.get('KBASE_MODULE_PATH', '/kb/module')
methods_config_path = os.path.join(module_path, 'kbase_methods.yaml')


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
    if not os.path.exists(methods_config_path):
        raise RuntimeError('%s does not exist' % methods_config_path)
    with open(methods_config_path, 'r') as fd:
        try:
            schemas = yaml.load(fd.read())
        except Exception as err:
            raise RuntimeError('Unable to parse YAML in %s: %s' % (methods_config_path, str(err)))
    return schemas


def validate_method_params(method_name, params):
    """Load the schema for the method and validate the params."""
    schemas = load_method_config()
    if method_name not in schemas:
        raise RuntimeError('No method defined in kbase_methods.yaml named "%s"' % method_name)
    schema = {'type': 'object'}
    if 'required_params' in schemas[method_name]:
        schema['required'] = schemas[method_name]['required_params']
    if 'params' in schemas[method_name]:
        schema['properties'] = schemas[method_name]['params']
    _validate('params to "%s"' % method_name, params, schema)
