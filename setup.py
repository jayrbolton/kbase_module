#!/usr/bin/env python
from distutils.core import setup

setup(
    name='kbase_module',
    version='0.0.1',
    description='KBase SDK module utilities',
    author='KBase Team',
    author_email='info@kbase.us',
    url='https://github.com/jayroblton/kbase_module',
    package_dir={'': 'src'},
    packages=['kbase_module'],
    install_requires=[
        'requests>=2',
        'jsonschema>=2',
        'Flask>=1',
        'gunicorn>19',
        'gevent>1'
    ],
    python_requires='>3'
)
