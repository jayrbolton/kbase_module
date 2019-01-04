"""
Find and run a method from within a kbase module.
Also validates the parameters.
"""
import os
import sys
import importlib
from inspect import signature

from kbase_module.utils.validate_methods import validate_method_params

module_path = os.environ.get('KBASE_MODULE_PATH', '/kb/module')
main_module_path = os.path.join(module_path, 'src')
sys.path.insert(0, main_module_path)

try:
    main = importlib.import_module('main')
except Exception:
    raise RuntimeError('Unable to import the main module. Do you have a "main.py" under %s?' % main_module_path)


def run_method(name, params, auth_token=None):
    """
    Dynamically load the main module and a method by name.
    Then run the method on a set of params.
    """
    # Validate the parameters of the method according to the schema
    validate_method_params(name, params)
    try:
        method = getattr(main, name)
    except AttributeError:
        raise RuntimeError('No method found in main.py called %s' % name)
    if not callable(method) or len(signature(method).parameters) != 1:
        raise RuntimeError('Method "%s" should be a function with 2 params.' % name)
    return method(params)
