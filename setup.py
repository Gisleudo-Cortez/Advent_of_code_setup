from setuptools import setup

setup(
    name='advent-of-code-setup',
    version='0.1',
    description='Create a folder and download input for the day and year provided.',
    author='Gisleudo-Cortez',
    url='https://github.com/Gisleudo-Cortez/Advent_of_code_setup',
    py_modules=['main'],
    entry_points={
        'console_scripts': [
            'aoc=main:main',
        ],
    },
    install_requires=[
        'requests>=2.32.3'
    ]
)