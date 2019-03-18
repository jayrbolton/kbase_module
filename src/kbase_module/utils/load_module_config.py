import yaml

from kbase_module.utils.load_config import load_config

config = load_config()


def load_module_config():
    with open(config['module_config_path']) as fd:
        return yaml.load(fd.read(), Loader=yaml.SafeLoader)
