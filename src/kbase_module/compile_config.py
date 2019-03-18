import os
import yaml

from kbase_module.utils.load_config import load_config

compile_report_template = """{
  "function_places": {},
  "functions": {},
  "impl_file_path": "",
  "module_name": "$module_name",
  "sdk_git_commit": "0",
  "sdk_version": "0",
  "spec_files": [{"content": "", "is_main": 1}]
}
"""

if __name__ == '__main__':
    config = load_config()
    with open(config['module_config_path']) as fd:
        module = yaml.load(fd.read(), Loader=yaml.SafeLoader)
    compile_report_json = compile_report_template.replace("$module_name", module['module-name'])
    # TODO insert the git commit hash
    # TODO insert the SDK version
    os.makedirs(config['work_path'], exist_ok=True)
    with open(config['compile_report_path'], 'w') as fd:
        fd.write(compile_report_json)
