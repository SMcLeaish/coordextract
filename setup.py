from setuptools import setup, find_packages

setup(
    name='coordextract',
    version='0.1.0',
    author='Sean McLeaish',
    author_email='smcleaish@gmail.com',
    description='A tool for converting coordinates to mgrs',
    packages=find_packages(),
    install_requires=[
        'lxml',
        'requests',
        'mgrs',
    ],
    entry_points={
        'console_scripts': [
            'coordextract=coordextract.cli:main',
        ],
    },
)
