"""
Run a module as a persistent JSON RPC server using Flask.

Start this server using the ./scripts/run_service.sh script.
"""
import sys
import flask
import json
import jsonschema
from jsonschema.exceptions import ValidationError

from kbase_module.utils.validate_method_params import validate_method_params
from kbase_module.utils.find_and_run_method import find_and_run_method

app = flask.Flask(__name__)

# Schema for the top-level RPC request
rpcschema = {
    'type': 'object',
    'required': ['method'],
    'additionalProperties': False,
    'properties': {
        'method': {'type': 'string'},
        'params': {},
        'id': {},
        'jsonrpc': {'const': '2.0'}
    }
}


def _err(msg, status=400):
    """Generic error response"""
    sys.stderr.write("Error: %s\n" % msg)
    return (flask.jsonify({
        'error': msg,
        'id': flask.g.request_id,
        'jsonrpc': '2.0'
    }), status)


def _ok(data, status=200):
    """Generic valid result."""
    sys.stdout.write("Response: %s\n" % str(data))
    return (flask.jsonify({
        'result': data,
        'id': flask.g.request_id,
        'jsonrpc': '2.0'
    }), status)


@app.route('/', methods=['POST', 'GET'])
def root():
    """
    JSON RPC 2.0 method call.
    Reference: https://www.jsonrpc.org/specification
    """
    flask.g.request_id = None
    try:
        reqdata = json.loads(flask.request.get_data())
    except ValueError as err:
        return _err('Unable to decode JSON: %s' % str(err))
    # Validate RPC structure
    try:
        jsonschema.validate(reqdata, rpcschema)
    except ValidationError as err:
        return _err('Invalid RPC format: %s' % err.message)
    flask.g.request_id = reqdata.get('id')
    params = reqdata.get('params')
    method_name = reqdata['method']
    # Load and validate the schema
    try:
        validate_method_params(method_name, params)
    except RuntimeError as err:
        return _err(str(err))
    # Get the module and method from /kb/module
    try:
        result = find_and_run_method(method_name, params)
        return _ok(result)
    except Exception as err:
        return _err(str(err))


@app.errorhandler(404)
def not_found(err):
    return _err('404 - Not found', 404)


@app.errorhandler(Exception)
@app.errorhandler(500)
def server_err(err):
    return _err(str(err), 500)


if __name__ == '__main__':
    app.run()
