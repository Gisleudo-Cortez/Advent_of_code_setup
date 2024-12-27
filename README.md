# Advent of Code Setup

A command-line interface (CLI) tool designed to streamline your participation in the annual [Advent of Code](https://adventofcode.com/) event. This tool creates a folder structure for the given year and day, then downloads and saves the input data for that challenge directly into the corresponding folder.

## Installation

1. Clone this repository:

```bash
git clone https://github.com/Gisleudo-Cortez/Advent_of_code_setup.git
```

2. Install the package using pip with the following command (navigate to the project directory first):

```bash
pip install -e .
```

The `-e` flag installs the package in 'editable' mode, meaning changes made to the local source code will take effect immediately.

## Usage

1. Obtain your session cookie from [Advent of Code](https://adventofcode.com/): Open a challenge input file (e.g., `https://adventofcode.com/2024/day/1/input`), and check your browser's cookies for the `session` key.

2. Run the CLI tool with the required arguments:

```bash
aoc -d <DAY> -y <YEAR> -s <SESSION_COOKIE>
```

Replace `<DAY>` with the desired day (e.g., `1`, `25`), `<YEAR>` with the challenge year (e.g., `2024`), and `<SESSION_COOKIE>` with your session cookie value.

For example:

```bash
aoc -d 1 -y 2024 -s "ins_123abcdefg"
```

This command will create a folder structure for the given year and day (e.g., `2024/1/`), download the input data, and save it as `input.txt` within that folder.
