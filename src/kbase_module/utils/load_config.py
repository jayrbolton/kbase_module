import os


def load_config():
    """Load app configuration from the environment."""
    module_path = os.environ.get('KBASE_MODULE_PATH', '/kb/module')
    work_path = os.path.join(module_path, 'work')
    return {
        'log_level': os.environ.get('LOG_LEVEL', 'WARNING').upper(),
        'module_path': module_path,
        'module_src_path': os.path.join(module_path, 'src'),
        'methods_config_path': os.path.join(module_path, 'kbase_methods.yaml'),
        'module_config_path': os.path.join(module_path, 'kbase.yaml'),
        'work_path': work_path,
        'input_json_path': os.path.join(work_path, 'input.json'),
        'output_json_path': os.path.join(work_path, 'output.json'),
        'compile_report_path': os.path.join(work_path, 'compile_report.json'),
        'subjob_runner_url': os.environ.get('SUBJOB_RUNNER_URL', 'http://subjob'),
        'runtime_limit': 3600  # subjob runtime limit
    }
