from setuptools import setup

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(name='opendigger-cli',
      version='1.0.2',
      packages=['opendigger-cli'],
      install_requires=requirements)
