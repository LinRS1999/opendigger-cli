from setuptools import setup, find_packages

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(name='opendigger_cli',
      version='2.0.1',
      packages=find_packages(),
      entry_points={
          'console_scripts': [
              'opendigger-cli = opendigger_cli.main:main'
          ],
      },
      install_requires=requirements)
