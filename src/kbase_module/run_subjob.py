"""
Run another module method from within a running SDK module docker container.

Most likely, the subjob runner service will have been started in another,
sibling docker container accessible via http://subjob
"""
import time
import requests
import json

from kbase_module.utils.load_config import load_config

config = load_config()


def run_module(module, method, params, version='latest', tag='release', asynchronous=False):
    # kbase_url = os.environ.get('KBASE_ENDPOINT', 'https://ci.kbase.us/services')
    # Make a call to the subjob runner to start the job
    payload = {
        'method': '%s._%s_submit' % (module, method),
        'params': {
            'module': module,
            'method': method,
            'version': version,
            'tag': tag,
            'params': params
        },
        'version': 1.1
    }
    resp = requests.post(
        config['subjob_runner_url'],
        data=json.dumps(payload)
    ).json()
    # TODO check the callback server implementation for proper response format
    job_id = resp['job_id']
    if asynchronous:
        return job_id
    return wait_for_job(job_id)


def check_job(job_id):
    """
    Check the status of a running job on the subjob runner.
    Returns a dict like {'finished': boolean, 'result': data}
    """
    payload = {'method': 'X._check_job', 'params': {'job_id': job_id}}
    resp = requests.post(config['subjob_runner_url'], data=json.dumps(payload)).json()
    # TODO handle error response
    return resp


def wait_for_job(job_id):
    """
    Synchronously poll the subjob runner until a job finishes with a result or error.
    """
    wait_interval = 1
    total_wait = 0
    max_wait = config['runtime_limit']  # 60 mins
    while total_wait < max_wait:
        resp = check_job(job_id)
        # TODO handle error result from job
        if resp['finished']:
            if len(resp['result']) == 1:
                return resp['result'][0]
            return resp['result']
        wait_interval += 5
        time.sleep(wait_interval)
    # TODO return failure value rather than raising
    raise RuntimeError(f"Job failed to complete in {max_wait} seconds")
