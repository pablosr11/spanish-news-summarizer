# -*- coding: utf-8 -*-

"""
 2019 Pablo Sanderson Ramos | spanish-news-summarizer
"""

from setuptools import setup, find_packages


with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='Forocanario',
    version='0.0.2',
    description='Find summaries of your favourite news outlet',
    long_description=readme,
    author='Pablo Sanderson Ramos',
    author_email='pablosr11@gmail.com',
    url='https://github.com/pablosr11/spanish-news-summarizer',
    license=license,
    packages=find_packages(exclude=('tests', 'docs'))
)