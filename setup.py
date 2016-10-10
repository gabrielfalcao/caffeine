#!/usr/bin/env python
# -*- coding: utf-8 -*-


import ast
import os
from setuptools import setup, find_packages


local_file = lambda *f: \
    open(os.path.join(os.path.dirname(__file__), *f)).read()


class VersionFinder(ast.NodeVisitor):
    VARIABLE_NAME = 'version'

    def __init__(self):
        self.version = None

    def visit_Assign(self, node):
        try:
            if node.targets[0].id == self.VARIABLE_NAME:
                self.version = node.value.s
        except:
            pass


def read_version():
    finder = VersionFinder()
    finder.visit(ast.parse(local_file('caffeine', 'version.py')))
    return finder.version


dependencies = [
    'passlib==1.6.5',
    'docker-py==1.5.0',
    'dockerpty==0.3.4',
    'ansible==1.9.4',
    'requests==2.9.1',
    'ipython==4.1.2',
    'Flask==0.10.1',
    'gunicorn==19.6.0',
    'redis==2.10.5',
    'plant==0.1.2',
    'flask-session==0.2.3',
    'coloredlogs==5.0',
    'Flask-Login==0.2.11',
    'cryptography==1.5',
    'alembic==0.8.7',
    'milieu==0.1.9',
    'PyNaCl==1.0.1',
    'MySQL-python==1.2.5',
    'eyeD3==0.7.9',
]

setup(
    name='caffeine',
    version=read_version(),
    description='Caffeine!',
    entry_points={
        'console_scripts': ['caffeine = caffeine.cli:main'],
    },
    author='Gabriel Falcao',
    author_email='gabriel@livre.org',
    packages=find_packages(exclude=['*tests*']),
    install_requires=dependencies,
    include_package_data=True,
    package_data={
        'angrybirds': 'COPYING *.md caffeine/static caffeine/static/* caffeine/static/dist caffeine/static/dist/* caffeine/static/templates caffeine/static/templates/* ez_setup.py'.split(),
    },
    zip_safe=False,
)
