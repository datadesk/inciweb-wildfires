import os
from setuptools import setup


def read(fname):
    with open(os.path.join(os.path.dirname(__file__), fname)) as f:
        return f.read()


setup(
    name='inciweb-wildfires',
    version='0.0.1',
    description="gather data from inciweb on active fires",
    long_description=read('README.rst'),
    author='Los Angeles Times Data Desk',
    author_email='datadesk@latimes.com',
    url='http://www.github.com/datadesk/inciweb-wildfires',
    license="MIT",
    packages=("inciweb_wildfires",),
    install_requires=[
        "requests",
        "geojson",
        "click",
    ],
    entry_points="""
        [console_scripts]
        inciwebwildfires=inciweb_wildfires.cli:cmd
    """,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'License :: OSI Approved :: MIT License',
    ],
    project_urls={
        'Maintainer': 'https://github.com/datadesk',
        'Source': 'https://github.com/datadesk/inciweb-wildfires',
        'Tracker': 'https://github.com/datadesk/inciweb-wildfires/issues'
    },
)
