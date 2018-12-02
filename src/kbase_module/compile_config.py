"""
Compile configuration files from those defined in the module to files that the
KBase catalog service needs for registration.

kbase_module.json -> /kb/module/kbase.yml
kbase_module.json -> /kb/module/compile_report.json
kbase_methods.json -> /kb/module/ui/narrative/methods
"""
import os
import json
import jsonschema

module_path = os.environ.get('KBASE_MODULE_PATH', '/kb/module')

# JSON Schema for the kbase_module.json file
module_schema = {
    'type': 'object',
    'required': ['name', 'owners', 'version'],
    'properties': {
        'name': {
            'type': 'string',
            'examples': ['megahit'],
            'pattern': r'^[a-zA-Z_\-][a-zA-Z_\-0-9]+$',
            'minLength': 3
        },
        'owners': {
            'type': 'array',
            'examples': [['username1', 'username2']],
            'minItems': 1,
            'items': {'type': 'string'}
        },
        'description': {'type': 'string'},
        'version': {
            'type': 'string',
            'examples': ['0.0.1', 'v1.1.1'],
            'pattern': r'v?\d+\.\d+\.\d+'
        }
    }
}

methods_schema = {
    'type': 'object',
    'patternProperties': {
        r'^.+$': {
            'type': 'object',
            'required': ['params'],
            'properties': {
                'params': {
                    'default': {},
                    'type': 'object'
                },
                'required_params': {
                    'type': 'array',
                    'default': [],
                    'items': {'type': 'string'}
                }
            }
        }
    }
}


def compile_module():
    # Open and decode kbase_module.json
    module_json_path = os.path.join(module_path, 'kbase_module.json')
    methods_json_path = os.path.join(module_path, 'kbase_methods.json')
    if not os.path.exists(module_json_path):
        raise RuntimeError('%s does not exist' % module_json_path)
    if not os.path.exists(methods_json_path):
        raise RuntimeError('%s does not exist' % methods_json_path)
    with open(module_json_path, 'r') as fd:
        module = json.load(fd)
    # Validate kbase_module.json
    jsonschema.validate(module, module_schema)
    # Open and decode kbase_methods.json
    with open(methods_json_path, 'r') as fd:
        methods = json.load(fd)
    # Validate kbase_methods.json
    # TODO dupe logic here with utils/validate_method_params
    jsonschema.validate(methods, methods_schema)
    # Write kbase.yml
    with open(os.path.join(module_path, 'kbase.yml'), 'w') as fd:
        content = '\n'.join([
            'module-name: %s' % module['name'],
            'module-description: %s' % module.get('description', ''),
            'service-language: python',
            'module-version: %s' % module['version'],
            'owners: %s' % module['owners']
        ])
        fd.write(content)
    # Write compile_report.json
    with open(os.path.join(module_path, 'compile_report.json'), 'w') as fd:
        compile_report = {
            'function_places': {},
            'functions': {},
            'impl_file_path': '',
            'module_name': module['name'],
            'sdk_git_commit': '0',
            'sdk_version': '2'
        }
        json.dump(compile_report, fd)
    # Write out the ui spec files
    os.makedirs(os.path.join(module_path, 'ui/narrative'), exist_ok=True)
    for (method_name, config) in methods.items():
        _create_ui_spec(method_name, config, module)
    # TODO write out the display.yml files


def _create_ui_spec(method_name, config, module):
    """
    Construct files in /kb/module/ui/narrative/methods/name/spec.json
    Refer to: https://kbase.github.io/kb_sdk_docs/references/UI_spec.html
    """
    spec_dir = os.path.join(module_path, 'ui', 'narrative', 'methods', method_name)
    os.makedirs(spec_dir, exist_ok=True)
    # TODO target type transform for workspace references
    ui_spec = {
        'ver': '0.0.1',
        'authors': [],
        'contact': '',
        'categories': config.get('categories', []),
        'widgets': {},
        'parameters': [],
        'behavior': {
            'service-mapping': {
                'url': '',
                "name": module['name'],
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
    ui_config = config.get('ui', {})
    for (param, schema) in config['params'].items():
        is_required = param in config['required_params']
        ui_spec['behavior']['service-mapping']['input_mapping'].append({
            'input_parameter': param,
            'target_property': param
        })
        ui_spec['parameters'].append({
            'id': param,
            "optional": not is_required,
            "advanced": False,
            "allow_multiple": ui_config.get('allow_multiple', False),
            "default_values": ui_config.get('default'),
            "field_type": ui_config.get('field_type', 'text')
        })
        # TODO translate json schema to UI validations for text_options, dropdown_options, etc
    with open(os.path.join(spec_dir, 'spec.json'), 'w') as fd:
        json.dump(ui_spec, fd)


if __name__ == '__main__':
    compile_module()
