from setuptools import setup, find_packages
from os.path import join, dirname

setup(
    name='nail.ssg.standard',
    version='0.1.4',
    packages=find_packages(),
    long_description=open(join(dirname(__file__), 'README.md')).read(),
    install_requires=[
        'pystache>=0.5.4',
        'markdown>=2.6.8',
        'nail.ssg.base>=0.1.0',
        'blinker>=1.4',
        'ruamel.yaml>=0.13.14'
    ],
    dependency_links=[
        'https://github.com/nail-ssg/nail-ssg-base/archive/develop.zip#egg=nail.ssg.base-0.1.0'
    ]
)
