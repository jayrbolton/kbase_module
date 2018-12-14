#!/usr/bin/env python
from distutils.core import setup

setup(
    name='kbase_module',
    version='0.0.1',
    description='KBase SDK module utilities',
    author='KBase Team',
    author_email='info@kbase.us',
    url='https://github.com/jayrbolton/kbase_module',
    package_dir={'': 'src'},
    packages=[
        'kbase_module',
        'kbase_module.utils'
    ],
    scripts=[
        'src/kbase_module/scripts/entrypoint.sh'
    ],
    install_requires=[
        'requests>=2.20',
        'jsonschema>=2.6',
        'Flask>=1.0',
        'gunicorn>=19.9',
        'gevent>=1.3',
        # TODO use strictyaml or something better
        'pyyaml>=3.13',
        'markdown2>=2.3'
    ],
    python_requires='>3'
)
