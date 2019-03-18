"""
Find and run a method from within a kbase module.
Also validates the parameters.
"""
import sys
import importlib
from inspect import signature

from kbase_module.utils.load_config import load_config
from kbase_module.utils.validate_methods import validate_method_params

config = load_config()
sys.path.insert(0, config['module_path'])

try:
    main = importlib.import_module('src.main')
except Exception:
    p = config['module_src_path']
    raise RuntimeError(f'Unable to import the main module. Do you have a "main.py" under {p}?')


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
        raise RuntimeError(f'No method found in main.py called {name}')
    if not callable(method) or len(signature(method).parameters) != 1:
        raise RuntimeError(f'Method "{name}" should be a function with 2 params.')
    return method(params)
