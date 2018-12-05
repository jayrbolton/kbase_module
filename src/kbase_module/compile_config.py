"""
Compile configuration files from those defined in the module to files that the
KBase catalog service needs for registration.

generate /kb/module/compile_report.json
from kbase_methods.yaml, generate /kb/module/ui/narrative/methods (both spec.json and display.yml files)
"""
import os
import json
import yaml
import jsonschema
import markdown2
import shutil

from .utils.validate_methods import validate_methods_config

module_path = os.environ.get('KBASE_MODULE_PATH', '/kb/module')

# JSON Schema for the kbase.yaml file
module_schema = {
    'type': 'object',
    'required': ['module-name', 'service-language', 'owners', 'module-version', ],
    'properties': {
        'module-name': {
            'type': 'string',
            'examples': ['megahit'],
            'pattern': r'^[a-zA-Z_\-][a-zA-Z_\-0-9]+$',
            'minLength': 3
        },
        'owners': {
            'description': 'KBase usernames',
            'type': 'array',
            'examples': [['username1', 'username2']],
            'minItems': 1,
            'items': {'type': 'string'}
        },
        'module-description': {'type': 'string'},
        'module-version': {
            'description': 'Semantic version',
            'type': 'string',
            'examples': ['0.0.1', 'v1.1.1'],
            'pattern': r'v?\d+\.\d+\.\d+'
        }
    }
}


def compile_module():
    module_yaml_path = os.path.join(module_path, 'kbase.yaml')
    methods = validate_methods_config()
    if not os.path.exists(module_yaml_path):
        raise RuntimeError('%s does not exist' % module_yaml_path)
    # Load and validate kbase.yaml
    with open(module_yaml_path, 'r') as fd:
        try:
            module = yaml.load(fd)
        except ValueError as err:
            raise RuntimeError('Unable to parse %s: %s' % (module_yaml_path, str(err)))
    jsonschema.validate(module, module_schema)
    # Write compile_report.json to /kb/module/work/compile_report.json
    os.makedirs(os.path.join(module_path, 'work'), exist_ok=True)
    with open(os.path.join(module_path, 'work', 'compile_report.json'), 'w') as fd:
        compile_report = {
            'function_places': {},
            'functions': {},
            'impl_file_path': '',
            'module_name': module['module-name'],
            'sdk_git_commit': '0',
            'sdk_version': '2'
        }
        json.dump(compile_report, fd)
    # Write out the ui spec files
    os.makedirs(os.path.join(module_path, 'ui/narrative'), exist_ok=True)
    for (method_name, config) in methods.items():
        _create_ui_spec(method_name, config, module)
    for (method_name, config) in methods.items():
        _create_display_yaml(method_name, config, module)


def _create_ui_spec(method_name, config, module):
    """
    Construct files in /kb/module/ui/narrative/methods/name/spec.json
    Refer to: https://kbase.github.io/kb_sdk_docs/references/UI_spec.html
    """
    spec_dir = os.path.join(module_path, 'ui', 'narrative', 'methods', method_name)
    os.makedirs(spec_dir, exist_ok=True)
    ui_spec = {
        'ver': module['module-version'],
        'authors': module['owners'],
        'contact': '',
        'categories': config.get('categories', []),
        'widgets': {},
        'parameters': [],  # set below
        'behavior': {  # modified below
            'service-mapping': {
                'url': '',
                "name": config.get('title', method_name),
                "method": method_name,
                "input_mapping": [
                    {
                        "narrative_system_variable": "workspace_id",
                        "target_property": "workspace_id"
                    }
                ],
                "output_mapping": [
                    {
                        "service_method_output_path": [0, "report_name"],
                        "target_property": "report_name"
                    },
                    {
                        "service_method_output_path": [0, "report_ref"],
                        "target_property": "report_ref"
                    }
                ]
            }
        },
        'job_id_output_field': 'docker'
    }
    # Set the parameter data in behavior/service-mapping and behavior/parameters
    for (param, schema) in config['params'].items():
        input_mapping = {
            'input_parameter': param,
            'target_property': param
        }
        if schema.get('type') == 'integer':
            input_mapping['target_type_transform'] = 'int'
        if schema.get('type') == 'array' and schema.get('items', {}).get('type') == 'integer':
            input_mapping['target_type_transform'] = 'list<int>'
        ui_spec['behavior']['service-mapping']['input_mapping'].append(input_mapping)
        # If it's scalar then item_schema is just the schema. If it's an array, then it's the .items schema
        item_schema = schema
        if schema.get('type') == 'array' and 'items' in schema:
            item_schema = schema['items']
        # Data for spec.json/parameters
        parameters_entry = {
            'id': param,
            'optional': param not in config['required_params'],
            'advanced': schema.get('advanced_field', False),
            'allow_multiple': schema.get('type') == 'array',
            'field_type': 'text'
        }
        # Get some default values either from the top level schema or from the array item schema
        # Note that this can't handle defaults for lists of lists of values, or any further nesting
        if 'default' in schema:
            if isinstance(schema['default'], list):
                parameters_entry['default_values'] = schema['default']
            else:
                parameters_entry['default_values'] = [schema['default']]
        elif schema.get('type') == 'array' and 'default' in item_schema:
            parameters_entry['default_values'] = [item_schema['default']]
        # Render a boolean as a checkbox
        if item_schema.get('type') == 'boolean':
            parameters_entry['field_type'] = 'checkbox'
        # Render an enum as a dropdown
        if item_schema.get('type') == 'string' and 'enum' in item_schema:
            parameters_entry['field_type'] = 'dropdown'
            parameters_entry['dropdown_options'] = {
                # TODO this doesn't support separate display/values
                'options': [{'value': s, 'display': s} for s in item_schema['enum']]
            }
        # Valid workspace types
        if item_schema.get('type') == 'string' and 'workspace_types' in item_schema:
            parameters_entry.setdefault('text_options', {})
            parameters_entry['text_options']['valid_ws_types'] = item_schema['workspace_types']
        # Integer and float minimum and maximums
        if item_schema.get('type') == 'integer' or item_schema.get('type') == 'number':
            # Translate from JSON Schema to KBase Thing
            translate = {'integer': 'int', 'number': 'float'}
            parameters_entry['field_type'] = 'text'
            parameters_entry.setdefault('text_options', {})
            key = translate[item_schema['type']]  # eg. if it's a number, we get "float"
            if 'maximum' in item_schema:
                parameters_entry['text_options']['max_' + key] = item_schema['maximum']
            if 'minimum' in item_schema:
                parameters_entry['text_options']['min_' + key] = item_schema['minimum']
        # TODO handle textareas
        # TODO handle dynamic dropdowns (schema['text_search'], schema['text_search']['module_method'], etc)
        # TODO handle param groups, if necessary
        ui_spec['parameters'].append(parameters_entry)
    with open(os.path.join(spec_dir, 'spec.json'), 'w') as fd:
        json.dump(ui_spec, fd)


def _create_display_yaml(method_name, config, module):
    """
    Transpile our kbase_methods.yaml into:
      ui/narrative/methods/name/display.yaml
      ui/narrative/methods/name/spec.json
    """
    spec_dir = os.path.join(module_path, 'ui', 'narrative', 'methods', method_name)
    os.makedirs(spec_dir, exist_ok=True)
    publications = [
        {'display-text': p['text'], 'link': p['url']}
        for p in config.get('publications', [])
    ]
    # We just generate some blank stuff for now to get it to work with the catalog
    suggestions = {
        'apps': {'related': [], 'next': []},
        'methods': {'related': [], 'next': []}
    }  # type: dict
    # Generate the parameters key, which has ui-name, short-hint, and long-hint
    parameters = {}  # type: dict
    for (param_name, param_config) in config.get('params', {}).items():
        parameters[param_name] = {
            'refs': {
                'ui-name': param_config.get('title', param_name),
                'short-hint': param_config.get('description', ''),
                'long-hint': param_config.get('long_description', '')
            }
        }
    # Move any screenshot files into ui/narrative/methods/name/img
    for path in config.get('screenshots', []):
        _copy_img_file(path, spec_dir)
    display_yaml = {
        'name': config.get('title', method_name),
        'tooltip': config.get('description', ''),
        'screenshots': config.get('screenshots', []),
        'publications': publications,
        'suggestions': suggestions,
        'parameters': parameters,
    }
    # Move the icon file into ui/narrative/methods/name/img
    if config.get('icon'):
        _copy_img_file(config['icon'], spec_dir)
        display_yaml['icon'] = config['icon']
    # Decode any markdown from the path in /readme into html
    if 'readme' in config:
        readme_path = os.path.join(module_path, config['readme'])
        if not os.path.exists(readme_path):
            raise RuntimeError('Method readme path does not exist: %s' % readme_path)
        display_yaml['description'] = str(markdown2.markdown_path(readme_path))
    with open(os.path.join(spec_dir, 'display.yaml'), 'w') as fd:
        yaml.dump(display_yaml, fd)


def _copy_img_file(path, spec_dir):
    """Copy image file from /kb/module/path to /kb/module/ui/narrative/methods/name/img/path"""
    src_path = os.path.join(module_path, path)
    if not os.path.exists(src_path):
        raise RuntimeError('Image file does not exist at %s' % src_path)
    dest_path = os.path.join(spec_dir, 'img', path)
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    shutil.copyfile(src_path, dest_path)


if __name__ == '__main__':
    compile_module()
