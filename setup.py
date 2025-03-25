from setuptools import setup

"""All package config is done in pyproject.toml.

pip still requires a setup.py file when installing packages in editable mode (i.e. local development/interactive mode),
thus this minimal setup exists.

see https://setuptools.pypa.io/en/latest/userguide/pyproject_config.html
"""
setup()
