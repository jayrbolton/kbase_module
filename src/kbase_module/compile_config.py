import yaml
import os

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

_kbase_module_path = os.environ.get('KBASE_MODULE_PATH', '/kb/module')
_module_config_path = os.path.join(_kbase_module_path, 'kbase.yaml')
_compile_report_path = os.path.join(_kbase_module_path, 'work', 'compile_report.json')

if __name__ == '__main__':
    with open(_module_config_path, 'r') as fd:
        module = yaml.load(fd.read())
    compile_report_json = compile_report_template.replace("$module_name", module['module-name'])
    with open(_compile_report_path, 'w') as fd:
        fd.write(compile_report_json)
