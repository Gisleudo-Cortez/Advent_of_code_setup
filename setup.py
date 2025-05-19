from setuptools import setup, find_packages

# Read the contents of your README file
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(
    encoding="utf-8"
)  # Ensure correct encoding

setup(
    name="advent-of-code-setup",
    version="0.4.0",  # Incremented version for BeautifulSoup integration
    description="A CLI tool to bootstrap Advent of Code daily challenges: creates directories, fetches input, problem statements, and scaffolds language projects.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Gisleudo-Cortez",
    url="https://github.com/Gisleudo-Cortez/Advent_of_code_setup",
    py_modules=["main"],
    entry_points={
        "console_scripts": [
            "aoc-init=main:main_logic",  # Entry point
        ],
    },
    install_requires=[
        "requests>=2.25.0",
        "beautifulsoup4>=4.9.3",  # Added BeautifulSoup4, specifying a reasonable minimum version
    ],
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    keywords="adventofcode aoc cli setup bootstrap automation beautifulsoup",
    project_urls={
        "Bug Reports": "https://github.com/Gisleudo-Cortez/Advent_of_code_setup/issues",
        "Source": "https://github.com/Gisleudo-Cortez/Advent_of_code_setup/",
    },
)
