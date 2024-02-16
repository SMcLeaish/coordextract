from setuptools import setup, find_packages

setup(
    name='coordextract',
    version='0.1.1',
    author='Sean McLeaish',
    author_email='smcleaish@gmail.com',
    description='A tool for parsing and manipulating coordinates from a number of different filetypes',
    packages=find_packages(),
    install_requires=[
        'lxml',
        'requests',
        'mgrs',
    ],
    entry_points={
        'console_scripts': [
            'coordextract=coordextract.cli.main:app',
        ],
    },
)
