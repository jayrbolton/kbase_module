"""General full app lifecycle integration tests."""
import os
import sys
import json
import unittest
import subprocess  # nosec
import requests
import shutil

# source env/bin/activate
# pip install - e.

_MOD_PATH = os.path.join(os.getcwd(), 'src/test/test_app')
# Test method input json
_INPUT_JSON = """{
  "method": "echo",
  "params": {"message": "wassup"}
}"""


def _run(cmd):
    """Run a shell command for testing."""
    out = ""
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)  # nosec
    # print("Running ", cmd)
    # print("*" * 80)
    for line in proc.stdout:
        line_str = line.decode()
        sys.stdout.write(line_str)
        out += line_str
    for line in proc.stderr:
        line_str = line.decode()
        sys.stderr.write(line_str)
        out += line_str
    proc.wait()
    proc.stdout.close()
    proc.stderr.close()
    # print("Finished ", cmd)
    # print("*" * 80)
    return out


# TODO
# entrypoint.sh commands
#  - runs scripts/setup.sh script if present
#    - init, test, async, serve
#  - scripts/test.sh runs on test
#  - report command does something
#  - serve command launches server


class IntegrationTest(unittest.TestCase):

    def tearDown(self):
        # Remove the test app's work directory
        shutil.rmtree(os.path.join(_MOD_PATH, 'work'), ignore_errors=True)

    def test_entrypoint_script(self):
        """Test that entrypoint.sh is built into the path."""
        out = _run("which entrypoint.sh")
        self.assertTrue('entrypoint.sh' in out)

    def test_app_test(self):
        """Test the `entrypoint.sh test` command."""
        out = _run("entrypoint.sh test")
        self.assertTrue("Ran 2 tests" in out)

    def test_app_job_without_input(self):
        """Test the `entrypoint.sh serve` command."""
        out = _run("entrypoint.sh async")
        self.assertTrue("does not exist" in out)

    def test_app_job(self):
        """Test the `entrypoint.sh async` command."""
        out_path = os.path.join(_MOD_PATH, 'work', 'output.json')
        os.makedirs(os.path.join(_MOD_PATH, 'work'), exist_ok=True)
        with open(os.path.join(_MOD_PATH, 'work', 'input.json'), 'w') as fd:
            fd.write(_INPUT_JSON)
        _run("entrypoint.sh async")
        with open(out_path) as fd:
            output_json = json.load(fd)
        self.assertEqual(output_json['result'], 'wassup')

    def test_report(self):
        """Test the `entrypoint.sh report` command."""
        _run("entrypoint.sh report")
        report_path = os.path.join(_MOD_PATH, 'work', 'compile_report.json')
        with open(report_path) as fd:
            report_json = json.load(fd)
        self.assertEqual(report_json['function_places'], {})
        self.assertEqual(report_json['functions'], {})
        self.assertEqual(report_json['module_name'], 'echo_test')
        # TODO insert hash and sdk version here
        self.assertEqual(report_json['sdk_git_commit'], '0')
        self.assertEqual(report_json['sdk_version'], '0')

    def test_server_request(self):
        data = {'method': 'echo', 'params': {'message': 'xyzhi'}}
        resp = requests.post('http://localhost:5000', data=json.dumps(data))
        resp_json = resp.json()
        self.assertEqual(resp_json['result'], 'xyzhi')

    def test_server_not_found(self):
        data = {'method': 'notfound', 'params': {}}
        resp = requests.post('http://localhost:5000', data=json.dumps(data))
        resp_json = resp.json()
        self.assertTrue('No method' in resp_json['error'])

    def test_server_invalid_params(self):
        data = {'method': 'echo', 'params': {'message': 10}}
        resp = requests.post('http://localhost:5000', data=json.dumps(data))
        resp_json = resp.json()
        self.assertTrue('Validation error' in resp_json['error'])

    def test_server_invalid_prc(self):
        data = {'function': 'echo', 'params': {'message': 10}}
        resp = requests.post('http://localhost:5000', data=json.dumps(data))
        resp_json = resp.json()
        self.assertTrue('Invalid RPC format' in resp_json['error'])
