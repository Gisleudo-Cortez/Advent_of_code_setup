# Advent of Code Setup

A command-line interface (CLI) tool designed to streamline your participation in the annual [Advent of Code](https://adventofcode.com/) event. This tool creates a folder structure for the given year and day, then downloads and saves the input data and optionally the problem statement for that challenge directly into the corresponding folder. It can also scaffold project setups for Python, Rust, and Go.

## Features

-   Creates directory structures (e.g., `YYYY/DD/`).
-   Downloads puzzle input (`input.txt`).
-   Creates an empty `example.txt` for test cases.
-   Optionally downloads the problem statement as `problem_statement.txt` (uses BeautifulSoup for parsing).
-   Optionally refreshes an existing `problem_statement.txt` to fetch updates (e.g., Part Two), providing specific feedback on whether the file was created, updated, or unchanged.
-   Optionally scaffolds project boilerplates for Python (with `uv` or `venv`), Rust (`cargo new`), and Go (`go mod init`).
-   Supports session token via command-line argument or `.env` file (`AOC_SESSION`).
-   Verbose mode for detailed output.

## Installation

1.  Clone this repository:
    ```bash
    git clone [https://github.com/Gisleudo-Cortez/Advent_of_code_setup.git](https://github.com/Gisleudo-Cortez/Advent_of_code_setup.git)
    cd Advent_of_code_setup
    ```

2.  Install the package using pip (it's recommended to do this in a virtual environment):
    ```bash
    pip install .
    ```
    Or, for editable mode (changes to source code take immediate effect):
    ```bash
    pip install -e .
    ```

## Usage

### Prerequisites

1.  **Session Cookie**: Obtain your session cookie from [Advent of Code](https://adventofcode.com/):
    * Log in to Advent of Code.
    * Open your browser's developer tools (usually F12).
    * Navigate to the `Application` (Chrome/Edge) or `Storage` (Firefox) tab.
    * Look for Cookies > `https://adventofcode.com`.
    * Copy the value of the `session` cookie.

2.  **Set Session Cookie**: You can provide the session cookie in two ways:
    * **Command-line argument**: Use the `-s` or `--session` flag (see below).
    * **`.env` file**: Create a file named `.env` in the directory where you run `aoc-init` (or in your project root) with the following content:
        ```env
        AOC_SESSION=your_actual_session_cookie_value_here
        ```
        The command-line argument will override the `.env` file if both are present.

### Running the Tool

Execute the CLI tool with the required and optional arguments:

```bash
aoc-init -y <YEAR> -d <DAY> [OPTIONS]
```

**Required Arguments:**

-   `-y YEAR`, `--year YEAR`: Challenge year (e.g., 2023). Must be 2015 or later.
-   `-d DAY`, `--day DAY`: Day of the challenge (1-25).

**Optional Arguments:**

-   `-s SESSION`, `--session SESSION`: Your Advent of Code session cookie.
-   `-l LANG [LANG ...]`, `--language LANG [LANG ...]`: Languages to scaffold (e.g., `python`, `rust`, `go`). Default: `all` (if not using `--refresh-instructions`).
-   `-i`, `--instructions`: Download the problem statement as `problem_statement.txt` during the initial setup.
-   `--refresh-instructions`: Re-download and save the problem statement, overwriting any existing version. Useful for fetching Part Two if it was released after initial setup. If this flag is used, other actions like input download and language scaffolding are skipped. The tool will report if the file was created, updated, or remained unchanged.
-   `--base-dir BASE_DIR`: Base directory for creating challenge folders (default: current working directory).
-   `-v`, `--verbose`: Enable verbose output.
-   `-h`, `--help`: Show help message and exit.

**Examples:**

1.  Initial setup for day 5 of 2023, download input, Part One instructions, and scaffold all languages:
    ```bash
    aoc-init -y 2023 -d 5 -i
    ```
    *(Assumes `AOC_SESSION` is in `.env` file)*

2.  Later, to update the instructions for day 5 of 2023 to include Part Two (if available), without affecting other files:
    ```bash
    aoc-init -y 2023 -d 5 --refresh-instructions
    ```
    *(This will now print a message like "Problem statement updated at..." or "Problem statement at... is already up-to-date.")*

3.  Setup day 10 of 2022, download input, scaffold only Python and Rust, providing session via CLI (no initial instruction download):
    ```bash
    aoc-init -y 2022 -d 10 -s "53616c7465645f5f..." -l python rust
    ```

4.  Setup day 1 of 2024, download input and instructions, with verbose output:
    ```bash
    aoc-init -y 2024 -d 1 -i -v
    ```

This command will typically:
1.  Create a folder structure (e.g., `2024/01/`).
2.  If `--refresh-instructions` is **not** used:
    * Download the input data and save it as `input.txt`.
    * Create `example.txt`.
    * If `-i` is used, download and save `problem_statement.txt`.
    * If languages are specified (or by default), create subfolders (e.g., `python/`, `rust/`) with basic project setups.
3.  If `--refresh-instructions` **is** used:
    * Only re-download and save `problem_statement.txt`, with specific feedback on the action's outcome.

## Note

-   Keep your session cookie private.
-   The session cookie is typically valid for about 30 days.
-   Please be mindful of the Advent of Code servers and avoid making excessive automated requests. This tool makes minimal requests per day setup/refresh.

## Requirements

-   Python 3.8 or higher.
-   The following Python libraries (automatically installed via `pip install .`):
    -   `requests`
    -   `beautifulsoup4`

## Development

To contribute or modify the tool:
1.  Clone the repository.
2.  Create and activate a virtual environment:
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # On Windows: .venv\Scripts\activate
    ```
3.  Install in editable mode with development dependencies (if you add any, e.g., for testing like `pytest`):
    ```bash
    pip install -e .[dev] # Assuming you add a [dev] extra in setup.py
    ```
    (Currently, no `[dev]` extras are defined in `setup.py` but this is good practice).

## License
This project is licensed under the MIT License - see the [LICENCE](LICENCE) file for details.
