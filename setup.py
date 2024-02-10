from setuptools import setup, find_packages

setup(
    name='mgrs-processing',
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
            'mgrs-processing=mgrs_processing.cli:main',
        ],
    },
)
