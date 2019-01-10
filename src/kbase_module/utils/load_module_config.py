import os
import yaml

_module_config_path = os.path.join(os.environ.get('KBASE_MODULE_PATH', '/kb/module'), 'kbase.yaml')


def load_module_config():
    with open(_module_config_path, 'r') as fd:
        return yaml.load(fd.read())
