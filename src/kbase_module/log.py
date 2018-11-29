import json
import os
import logging

# TODO add colors to the formatting

_log_level = os.environ.get('LOG_LEVEL', 'WARNING').upper()
logging.basicConfig(format='%(levelname)-8s %(message)s', level=_log_level)

# Get the module name
module_path = os.environ.get('KBASE_MODULE_PATH', '/kb/module')
with open(os.path.join(module_path, 'kbase_module.json'), 'r') as fd:
    module_data = json.load(fd)
module_name = module_data['name']


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
    return module_name + ' - ' + combined
