# import yaml
# import os
import logging

from kbase_module.utils.load_config import load_config

# TODO add colors to the formatting
config = load_config()
logging.basicConfig(format='%(levelname)-8s %(message)s', level=config['log_level'])

# Get the module name
# with open(os.path.join(config['module_path'], 'kbase.yaml'), 'r') as fd:
#     module_data = yaml.load(fd)
# module_name = module_data['module-name']


def warning(*msgs):
    return logging.warning(_combine(msgs))


def info(*msgs):
    return logging.info(_combine(msgs))


def debug(*msgs):
    return logging.debug(_combine(msgs))


def error(*msgs):
    return logging.error(_combine(msgs))


def _combine(msgs):
    combined = ' '.join([str(m) for m in msgs])
    return combined
