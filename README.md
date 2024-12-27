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

1. Obtain your session cookie from [Advent of Code](https://adventofcode.com/):
   - Log in to Advent of Code
   - Open a challenge input file (e.g., `https://adventofcode.com/2024/day/1/input`)
   - Open your browser's developer tools (usually F12)
   - Navigate to the Application/Storage tab
   - Look for Cookies > adventofcode.com
   - Copy the value of the `session` cookie

2. Run the CLI tool with the required arguments:
```bash
aoc -d <DAY> -y <YEAR> -s <SESSION_COOKIE>
```

Replace:
- `<DAY>` with the desired day (1-25)
- `<YEAR>` with the challenge year (2015 or later)
- `<SESSION_COOKIE>` with your session cookie value

For example:
```bash
aoc -d 1 -y 2024 -s "53616c7465645f5f..."
```

This command will:
1. Create a folder structure (e.g., `2024/1/`)
2. Download the input data
3. Save it as `input.txt` within that folder

## Note

Keep your session cookie private and do not share it with others. The session cookie is valid for a limited time, make sure it is valid before running the program.

Be careful when performing requests to the [adventofcode](https://adventofcode.com/) site to no overload the servers.

## Requirements

- Python 3 or higher (made on version 3.13.1)
- requests library (automatically installed during setup)