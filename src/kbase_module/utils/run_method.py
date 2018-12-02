"""
Find and run a method from within a kbase module.
Also validates the parameters.
"""
import os
import sys
import importlib
from inspect import signature

from kbase_module.utils import validate_method_params

module_path = os.environ.get('KBASE_MODULE_PATH', '/kb/module')
sys.path.insert(0, os.path.join(module_path, 'src'))


def run_method(name, params):
    """
    Dynamically load the main module and a method by name.
    Then run the method on a set of params.
    """
    main = importlib.import_module("main")
    try:
        method = getattr(main, name)
    except AttributeError:
        raise RuntimeError('No method found in main.py called %s' % name)
    if not callable(method) or len(signature(method).parameters) != 1:
        raise RuntimeError('Method "%s" should be a function with 1 parameter.' % name)
    # Validate the parameters of the method according to the schema
    validate_method_params(name, params)
    return method(params)