#!/usr/bin/env python
"""
Run a module as a persistent JSON RPC server using http.server.

Simply run this with the `run_service` command
    (requires this module to be installed)
"""
import os
import sys
import flask

module_path = os.environ.get('KBASE_MODULE_PATH', '/kb/module')
sys.path.insert(0, os.path.join(module_path, 'src'))
app = flask.Flask(__name__)

# Load the main module

@app.route('/', methods=['POST', 'GET'])
def root():
    """
    JSON RPC v1.1 method call.
    Reference: https://jsonrpc.org/historical/json-rpc-1-1-wd.html
    """
    return flask.jsonify({'result': {}})
