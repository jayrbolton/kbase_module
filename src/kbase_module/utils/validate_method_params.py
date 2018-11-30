import os
import json
import jsonschema
from jsonschema.exceptions import ValidationError

module_path = os.environ.get('KBASE_MODULE_PATH', '/kb/module')
schema_path = os.path.join(module_path, 'kbase_methods.json')


def validate_method_params(method_name, params):
    """Load the schema for the method and validate the params."""
    with open(schema_path, 'r', encoding='utf8') as fd:
        schemas = json.load(fd)
    if method_name not in schemas:
        raise RuntimeError('No schema defined in kbase_methods.json named "%s"' % method_name)
    schema = {
        'type': 'object',
        'required': schemas[method_name].get('required_params', []),
        'properties': schemas[method_name].get('params', {})
    }
    try:
        jsonschema.validate(params, schema)
    except ValidationError as err:
        raise RuntimeError('JSON schema validation error on params:\n%s' % err.message)
