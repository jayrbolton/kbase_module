"""
Run a module as a persistent JSON RPC server using Flask.

Start this server using `./scripts/entrypoint.sh`.
"""
import os
import sys
import flask
import json
import jsonschema
from jsonschema.exceptions import ValidationError

from kbase_module.utils.run_method import run_method

app = flask.Flask(__name__)

# Schema for the top-level RPC request
rpcschema = {
    'type': 'object',
    'required': ['method'],
    # Let's be pretty loose here for backwards compatibility
    'additionalProperties': True,
    'properties': {
        'method': {'type': 'string'},
        'params': {},
        'id': {},
        'jsonrpc': {'const': '2.0'}
    }
}


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
    if method_name == 'BREW':
        return _err("I'm a teapot", 418)
    # Get the module and method from /kb/module
    os.environ['KB_AUTH_TOKEN'] = flask.request.headers.get('Authorization', '')
    try:
        result = run_method(method_name, params)
        return _ok(result)
    except Exception as err:
        return _err(str(err))


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


@app.errorhandler(404)
def not_found(err):
    return _err('404 - Not found', 404)


@app.errorhandler(405)
def method_not_allowed(err):
    return _err('405 - Method not allowed', 405)


@app.errorhandler(Exception)
@app.errorhandler(500)
def server_err(err):
    """Generic error catch-all."""
    if hasattr(err, 'status_code'):
        status_code = err.status_code
    else:
        status_code = 500
    return _err(str(err), status_code)


@app.after_request
def after_request(resp):
    # Enable CORS
    resp.headers['Access-Control-Allow-Origin'] = '*'
    env_allowed_headers = os.environ.get('HTTP_ACCESS_CONTROL_REQUEST_HEADERS', 'authorization')
    resp.headers['Access-Control-Allow-Headers'] = env_allowed_headers
    # Set JSON content type and response length
    resp.headers['Content-Type'] = 'application/json'
    resp.headers['Content-Length'] = resp.calculate_content_length()
    return resp


if __name__ == '__main__':
    app.run()
