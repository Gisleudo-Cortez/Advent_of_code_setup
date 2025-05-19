"""
Advent-of-Code bootstrapper.

Creates <year>/<day> directory structure, downloads puzzle input,
optionally fetches/refreshes the problem statement using BeautifulSoup,
and optionally scaffolds solution folders for supported languages.
Looks for AOC_SESSION in .env file or takes it via -s/--session argument.

Usage examples:
    aoc-init -y 2025 -d 7
    aoc-init -y 2025 -d 7 -i
    aoc-init -y 2025 -d 7 --refresh-instructions
    aoc-init -y 2025 -d 7 -s "YOUR_AOC_SESSION_COOKIE" -l rust go
    aoc-init -y 2025 -d 7 -l python --verbose --instructions
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path
import requests
from datetime import datetime
import re

try:
    from bs4 import BeautifulSoup
except ImportError:
    print(
        "Error: BeautifulSoup library not found. Please ensure it's installed.",
        file=sys.stderr,
    )
    print("You might need to run: pip install beautifulsoup4", file=sys.stderr)
    print(
        "If you installed this tool via setup.py, this dependency should have been handled.",
        file=sys.stderr,
    )
    sys.exit(1)


# --- Constants ---
LANGUAGES = ("rust", "go", "python")
AOC_BASE_URL = "https://adventofcode.com"
USER_AGENT = "aoc-init_script/0.3"
DOTENV_PATH = Path.cwd() / ".env"


# --- .env File Loader ---
def load_dotenv(dotenv_path: Path) -> dict[str, str]:
    """
    Loads key-value pairs from a .env file.
    Handles basic lines like KEY=VALUE, ignores lines starting with #.
    Strips leading/trailing whitespace from keys and values.
    Removes surrounding quotes (single or double) from values.
    """
    env_vars = {}
    if dotenv_path.exists() and dotenv_path.is_file():
        try:
            with open(dotenv_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#") or "=" not in line:
                        continue
                    key, value = line.split("=", 1)
                    key = key.strip()
                    value = value.strip()
                    if (value.startswith("'") and value.endswith("'")) or (
                        value.startswith('"') and value.endswith('"')
                    ):
                        value = value[1:-1]
                    env_vars[key] = value
        except OSError as e:
            print(
                f"Warning: Could not read .env file at {dotenv_path}. {e}",
                file=sys.stderr,
            )
    return env_vars


# --- Core Helper Functions ---


def create_day_folder(
    year: str, day_str_padded: str, base_path: Path, verbose: bool
) -> Path:
    """Creates the directory for the specified year and day."""
    if year in base_path.parts:
        target_dir = base_path / day_str_padded
    else:
        target_dir = base_path / year / day_str_padded
    try:
        target_dir.mkdir(parents=True, exist_ok=True)
        if verbose:
            print(f"Ensured directory exists: {target_dir.resolve()}")
        else:
            print(f"Using directory: {target_dir}")
        return target_dir
    except OSError as e:
        print(f"Error: Could not create directory {target_dir}. {e}", file=sys.stderr)
        sys.exit(1)


def fetch_input(
    year: str,
    day_str_unpadded: str,
    session_cookie: str,
    destination_path: Path,
    verbose: bool,
) -> None:
    """Downloads the puzzle input and creates an empty example.txt."""
    input_url = f"{AOC_BASE_URL}/{year}/day/{int(day_str_unpadded)}/input"
    headers = {"User-Agent": USER_AGENT}
    cookies = {"session": session_cookie}
    try:
        if verbose:
            print(f"Fetching puzzle input from: {input_url}")
        response = requests.get(input_url, cookies=cookies, headers=headers, timeout=15)
        response.raise_for_status()
        input_file = destination_path / "input.txt"
        input_file.write_text(response.text, encoding="utf-8")
        print(f"Input saved to {input_file}")
        example_file = destination_path / "example.txt"
        example_file.touch()
        print(f"Empty example file created at {example_file}")
    except requests.exceptions.HTTPError as e:
        print(
            f"Error: HTTP {e.response.status_code} fetching puzzle input from {input_url}.",
            file=sys.stderr,
        )
        if (
            e.response.status_code == 400
            and "Please don't repeatedly request this endpoint before it unlocks!"
            in e.response.text
        ):
            print(
                "Detail: It seems the puzzle for this day/year might not be unlocked yet.",
                file=sys.stderr,
            )
        elif e.response.status_code == 401 or e.response.status_code == 403:
            print(
                "Detail: Check if your AOC_SESSION cookie is valid or has expired.",
                file=sys.stderr,
            )
        elif verbose:
            print(f"Response content:\n{e.response.text}", file=sys.stderr)
        sys.exit(1)
    except requests.exceptions.RequestException as e:
        print(f"Error: Failed to fetch puzzle input. {e}", file=sys.stderr)
        sys.exit(1)
    except OSError as e:
        print(f"Error: Could not write input/example file. {e}", file=sys.stderr)
        sys.exit(1)


def fetch_and_save_instructions(
    year: str,
    day_str_unpadded: str,
    session_cookie: str,
    destination_path: Path,
    verbose: bool,
) -> str:
    """
    Fetches the problem statement HTML, parses it with BeautifulSoup, and saves it as a text file.
    Returns a status string: "CREATED", "UPDATED", "UNCHANGED", "NOT_FOUND", "FAILED_FETCH", "FAILED_WRITE".
    """
    problem_url = f"{AOC_BASE_URL}/{year}/day/{int(day_str_unpadded)}"
    input_file_url = f"{problem_url}/input"
    headers = {"User-Agent": USER_AGENT}
    cookies = {"session": session_cookie}

    instructions_file = destination_path / "problem_statement.txt"
    old_content: str | None = None
    if instructions_file.exists():
        try:
            old_content = instructions_file.read_text(encoding="utf-8")
        except OSError as e:
            print(
                f"Warning: Could not read existing instructions file at {instructions_file} for comparison. {e}",
                file=sys.stderr,
            )
            # Continue, old_content will be None

    try:
        if verbose:
            print(f"Fetching problem statement from: {problem_url}")
        response = requests.get(
            problem_url, cookies=cookies, headers=headers, timeout=15
        )
        response.raise_for_status()
        html_content = response.text
        soup = BeautifulSoup(html_content, "html.parser")
        problem_articles = soup.find_all("article", class_="day-desc")

        if not problem_articles:
            print(
                f'Warning: Could not find problem description articles (<article class="day-desc">) on {problem_url}.',
                file=sys.stderr,
            )
            print(
                "The page structure might have changed, or the problem is not yet available.",
                file=sys.stderr,
            )
            if verbose:
                debug_html_path = (
                    destination_path
                    / f"problem_page_raw_{year}_{day_str_unpadded}.html"
                )
                debug_html_path.write_text(html_content, encoding="utf-8")
                print(
                    f"Raw HTML saved to {debug_html_path} for inspection.",
                    file=sys.stderr,
                )
            return "NOT_FOUND"

        full_problem_text = (
            f"Problem Statement for Advent of Code {year} Day {day_str_unpadded}\n"
        )
        full_problem_text += f"Source: {problem_url}\n"
        full_problem_text += f"Input File URL: {input_file_url}\n\n"
        part_titles = ["--- Part One ---", "--- Part Two ---"]

        for i, article in enumerate(problem_articles):
            if i < len(part_titles):
                full_problem_text += f"{part_titles[i]}\n"
            else:
                full_problem_text += f"--- Part {i + 1} ---\n"
            part_text = article.get_text(separator="\n", strip=True)
            part_text = re.sub(r"\n\s*\n", "\n\n", part_text)
            full_problem_text += part_text.strip() + "\n\n"

        new_content = full_problem_text.strip()

        try:
            instructions_file.write_text(new_content, encoding="utf-8")
        except OSError as e_write:
            print(
                f"Error: Could not write problem statement file to {instructions_file}. {e_write}",
                file=sys.stderr,
            )
            return "FAILED_WRITE"

        if old_content is None:
            print(f"Problem statement newly saved to {instructions_file}")
            return "CREATED"
        elif old_content == new_content:
            print(f"Problem statement at {instructions_file} is already up-to-date.")
            return "UNCHANGED"
        else:  # old_content existed and is different from new_content
            print(f"Problem statement updated at {instructions_file}.")
            return "UPDATED"

    except requests.exceptions.HTTPError as e:
        print(
            f"Error: HTTP {e.response.status_code} fetching problem statement from {problem_url}.",
            file=sys.stderr,
        )
        if verbose:
            print(f"Response content:\n{e.response.text}", file=sys.stderr)
        return "FAILED_FETCH"
    except requests.exceptions.RequestException as e:
        print(f"Error: Failed to fetch problem statement. {e}", file=sys.stderr)
        return "FAILED_FETCH"
    # OSError for writing is handled above
    except Exception as e:  # Catch other potential errors, e.g. from BeautifulSoup
        print(
            f"An unexpected error occurred while fetching/parsing instructions: {e}",
            file=sys.stderr,
        )
        if verbose:
            import traceback

            traceback.print_exc()
        return "FAILED_UNEXPECTED"


# --- Language Scaffolding Functions ---
def scaffold_rust_project(
    dst_path: Path, year: str, day_str_padded: str, verbose: bool
) -> None:
    rust_dir = dst_path / "rust"
    if rust_dir.exists():
        print(f"Rust project already exists at {rust_dir}, skipping.")
        return
    print(f"Scaffolding Rust project in {rust_dir}...")
    try:
        cmd_cargo_new = ["cargo", "new", "rust", "--vcs", "none"]
        if verbose:
            print(f"Running: {' '.join(cmd_cargo_new)} in {dst_path}")
        process_result = subprocess.run(
            cmd_cargo_new,
            check=True,
            cwd=dst_path,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        if verbose and process_result.stdout:
            print(f"Cargo new stdout:\n{process_result.stdout}")
        toml_path = rust_dir / "Cargo.toml"
        if toml_path.exists():
            content = toml_path.read_text(encoding="utf-8")
            new_name = f'name = "aoc_{year}_day_{day_str_padded}_rust"'
            if verbose:
                print(
                    f"Updating Cargo.toml: replacing 'name = \"rust\"' with '{new_name}'"
                )
            new_content = content.replace('name = "rust"', new_name)
            toml_path.write_text(new_content, encoding="utf-8")
        print("Rust project scaffolded.")
    except subprocess.CalledProcessError as e:
        print(
            f"Error: Rust scaffolding failed. `{' '.join(e.cmd)}` exited with {e.returncode}.",
            file=sys.stderr,
        )
        if verbose:
            if e.stdout:
                print(f"Stdout:\n{e.stdout}", file=sys.stderr)
            if e.stderr:
                print(f"Stderr:\n{e.stderr}", file=sys.stderr)
        else:
            if e.stderr:
                print(f"Cargo stderr: {e.stderr.strip()}", file=sys.stderr)
    except FileNotFoundError:
        print(
            "Error: `cargo` command not found. Is Rust installed and in your PATH?",
            file=sys.stderr,
        )
    except OSError as e:
        print(f"Error: Could not write/modify Rust project files. {e}", file=sys.stderr)


def scaffold_go_project(
    dst_path: Path, year: str, day_str_padded: str, verbose: bool
) -> None:
    go_dir = dst_path / "go"
    if go_dir.exists():
        print(f"Go project already exists at {go_dir}, skipping.")
        return
    print(f"Scaffolding Go project in {go_dir}...")
    try:
        go_dir.mkdir()
        module_name = f"aoc_{year}_day_{day_str_padded}_go"
        cmd_go_mod_init = ["go", "mod", "init", module_name]
        if verbose:
            print(f"Running: {' '.join(cmd_go_mod_init)} in {go_dir}")
        process_result = subprocess.run(
            cmd_go_mod_init,
            check=True,
            cwd=go_dir,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        if verbose and process_result.stdout:
            print(f"Go mod init stdout:\n{process_result.stdout}")
        main_go_content = (
            f'package main\n\nimport "fmt"\n\nfunc main() {{\n'
            f'\tfmt.Println("Day {day_str_padded} — Advent of Code {year}")\n}}\n'
        )
        main_go_file = go_dir / "main.go"
        if verbose:
            print(f"Writing main.go to {main_go_file}")
        main_go_file.write_text(main_go_content, encoding="utf-8")
        print("Go project scaffolded.")
    except subprocess.CalledProcessError as e:
        print(
            f"Error: Go scaffolding failed. `{' '.join(e.cmd)}` exited with {e.returncode}.",
            file=sys.stderr,
        )
        if verbose:
            if e.stdout:
                print(f"Stdout:\n{e.stdout}", file=sys.stderr)
            if e.stderr:
                print(f"Stderr:\n{e.stderr}", file=sys.stderr)
        else:
            if e.stderr:
                print(f"Go stderr: {e.stderr.strip()}", file=sys.stderr)
    except FileNotFoundError:
        print(
            "Error: `go` command not found. Is Go installed and in your PATH?",
            file=sys.stderr,
        )
    except OSError as e:
        print(f"Error: Could not create Go project files. {e}", file=sys.stderr)


def scaffold_python_project(
    dst_path: Path, year: str, day_str_padded: str, verbose: bool
) -> None:
    py_dir = dst_path / "python"
    if py_dir.exists():
        print(f"Python project already exists at {py_dir}, skipping.")
        return
    print(f"Scaffolding Python project in {py_dir}...")
    try:
        py_dir.mkdir()
        _ = year
        _ = day_str_padded
        venv_created = False
        cmd_uv_venv = ["uv", "venv"]
        try:
            if verbose:
                print(
                    f"Attempting to create venv with `uv`: {' '.join(cmd_uv_venv)} in {py_dir}"
                )
            process_result = subprocess.run(
                cmd_uv_venv,
                check=True,
                cwd=py_dir,
                capture_output=True,
                text=True,
                encoding="utf-8",
            )
            if verbose and process_result.stdout:
                print(f"uv venv stdout:\n{process_result.stdout}")
            print("Python venv created successfully with `uv`.")
            venv_created = True
        except FileNotFoundError:
            if verbose:
                print("`uv` command not found. Will try standard `venv` module.")
        except subprocess.CalledProcessError as e_uv:
            print(
                f"Failed to create venv with `uv` (exited with {e_uv.returncode}). Falling back to standard `venv` module.",
                file=sys.stderr,
            )
            if verbose:
                if e_uv.stdout:
                    print(f"uv stdout:\n{e_uv.stdout}", file=sys.stderr)
                if e_uv.stderr:
                    print(f"uv stderr:\n{e_uv.stderr}", file=sys.stderr)
        if not venv_created:
            cmd_std_venv = [sys.executable, "-m", "venv", ".venv"]
            if verbose:
                print(
                    f"Attempting to create venv with standard library: {' '.join(cmd_std_venv)} in {py_dir}"
                )
            try:
                process_result = subprocess.run(
                    cmd_std_venv,
                    check=True,
                    cwd=py_dir,
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                )
                if verbose and process_result.stdout:
                    print(f"Standard venv stdout:\n{process_result.stdout}")
                print("Python venv created successfully with standard `venv` module.")
                venv_created = True
            except subprocess.CalledProcessError as e_venv:
                print(
                    f"Error: Python venv creation with standard library failed. `{' '.join(e_venv.cmd)}` exited with {e_venv.returncode}.",
                    file=sys.stderr,
                )
                if verbose:
                    if e_venv.stdout:
                        print(f"Stdout:\n{e_venv.stdout}", file=sys.stderr)
                    if e_venv.stderr:
                        print(f"Stderr:\n{e_venv.stderr}", file=sys.stderr)
            except FileNotFoundError:
                print(
                    f"Error: sys.executable not found ('{sys.executable}'). Cannot create standard venv.",
                    file=sys.stderr,
                )
        if not venv_created:
            print(
                "Warning: Failed to create Python virtual environment.", file=sys.stderr
            )
        main_py_content = (
            'def main():\n    print("Solve me!")\n\n'
            'if __name__ == "__main__":\n    main()\n'
        )
        main_py_file = py_dir / "main.py"
        if verbose:
            print(f"Writing main.py to {main_py_file}")
        main_py_file.write_text(main_py_content, encoding="utf-8")
        print("Python project scaffolded.")
    except OSError as e:
        print(
            f"Error: Could not create Python project directory or files. {e}",
            file=sys.stderr,
        )


LANGUAGE_SCAFFOLDERS = {
    "rust": scaffold_rust_project,
    "go": scaffold_go_project,
    "python": scaffold_python_project,
}

# --- Argument Parsing and Main Logic ---


def year_type(value: str) -> int:
    try:
        year = int(value)
        if year < 2015:
            raise argparse.ArgumentTypeError(
                f"Year must be 2015 or later. You provided: {year}"
            )
        current_year = datetime.now().year
        if year > current_year + 1:
            raise argparse.ArgumentTypeError(
                f"Year {year} is too far in the future (current: {current_year})."
            )
        return year
    except ValueError:
        raise argparse.ArgumentTypeError(
            f"Invalid year format: '{value}'. Must be an integer."
        )


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="aoc-init",
        description="Advent of Code day bootstrapper. Sets up directories, "
        "fetches input and problem statements, and scaffolds language-specific projects.",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "-y",
        "--year",
        required=True,
        type=year_type,
        help="Challenge year (e.g., 2023). Must be 2015 or later.",
    )
    parser.add_argument(
        "-d",
        "--day",
        required=True,
        type=int,
        choices=range(1, 26),
        metavar="DAY[1-25]",
        help="Day of the challenge (1-25, no zero-padding).",
    )
    parser.add_argument(
        "-s",
        "--session",
        default=None,
        help="Advent of Code session cookie value. \n"
        "Overrides AOC_SESSION from .env file if provided.\n"
        f"Alternatively, set AOC_SESSION in a '{DOTENV_PATH.name}' file in the current directory.",
    )
    parser.add_argument(
        "-l",
        "--language",
        nargs="+",
        default=["all"],
        choices=list(LANGUAGES) + ["all"],
        metavar="LANG",
        help="Languages to scaffold project structures for. \n"
        f"Supported: {', '.join(LANGUAGES)}. \n"
        "Default: 'all' (scaffolds for all supported languages if not refreshing instructions).",
    )
    parser.add_argument(
        "-i",
        "--instructions",
        action="store_true",
        help="Download the problem statement/instructions as a text file during setup.",
    )
    parser.add_argument(
        "--refresh-instructions",
        action="store_true",
        help="Re-download and save the problem statement, overwriting any existing version. \n"
        "Useful for fetching Part Two if it was released after initial setup. \n"
        "If this flag is used, other actions like input download and language scaffolding are skipped.",
    )
    parser.add_argument(
        "--base-dir",
        type=Path,
        default=Path.cwd(),
        help="Base directory for creating challenge folders (default: current working directory).",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose output for more detailed information.",
    )
    args = parser.parse_args()
    return args


def main_logic() -> None:
    args = parse_arguments()

    if args.verbose:
        print("Verbose mode enabled.")
        print(f"Parsed arguments: {args}")

    env_vars = load_dotenv(DOTENV_PATH)
    session_cookie = args.session
    if not session_cookie:
        session_cookie = env_vars.get("AOC_SESSION")
        if session_cookie and args.verbose:
            print(f"Loaded AOC_SESSION from {DOTENV_PATH.name}.")

    if not session_cookie:
        print("Error: Advent of Code session cookie not found.", file=sys.stderr)
        print(
            f"Please provide it using the -s/--session argument, or by setting AOC_SESSION in '{DOTENV_PATH.name}'.",
            file=sys.stderr,
        )
        sys.exit(1)

    if args.session and args.session == "YOUR_AOC_SESSION_COOKIE":
        print(
            "Warning: The provided session cookie 'YOUR_AOC_SESSION_COOKIE' looks like a placeholder.",
            file=sys.stderr,
        )

    year_str = str(args.year)
    day_str_unpadded = str(args.day)
    day_str_padded = day_str_unpadded.zfill(2)

    if args.verbose:
        print(f"Year: {year_str}, Day: {day_str_padded} (unpadded: {day_str_unpadded})")
        print(f"Base directory for project: {args.base_dir.resolve()}")

    day_project_dir = create_day_folder(
        year_str, day_str_padded, args.base_dir, args.verbose
    )

    if args.refresh_instructions:
        print("\nAttempting to refresh instructions only...")
        # The fetch_and_save_instructions function now prints its own detailed status.
        _ = fetch_and_save_instructions(
            year_str, day_str_unpadded, session_cookie, day_project_dir, args.verbose
        )
        print("Instructions refresh operation finished.")
        sys.exit(0)

    fetch_input(
        year_str, day_str_unpadded, session_cookie, day_project_dir, args.verbose
    )

    if args.instructions:
        _ = fetch_and_save_instructions(
            year_str, day_str_unpadded, session_cookie, day_project_dir, args.verbose
        )

    selected_languages = args.language
    langs_to_scaffold = (
        list(LANGUAGES)
        if "all" in selected_languages
        else [lang for lang in selected_languages if lang in LANGUAGES]
    )

    if not langs_to_scaffold and "all" not in selected_languages and selected_languages:
        print(
            f"Warning: No valid languages selected from: {', '.join(selected_languages)}. Valid: {', '.join(LANGUAGES)}",
            file=sys.stderr,
        )

    if langs_to_scaffold:
        print(f"\nScaffolding for languages: {', '.join(langs_to_scaffold)}")
        for lang_name in langs_to_scaffold:
            scaffolder_func = LANGUAGE_SCAFFOLDERS.get(lang_name)
            if scaffolder_func:
                print(f"--- {lang_name.capitalize()} ---")
                scaffolder_func(day_project_dir, year_str, day_str_padded, args.verbose)
    elif not ("all" in selected_languages) and not any(
        lang in LANGUAGES for lang in selected_languages
    ):
        print("No valid languages specified for scaffolding.", file=sys.stderr)

    print("\nSetup complete.")


if __name__ == "__main__":
    try:
        main_logic()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.", file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
        is_verbose = "--verbose" in sys.argv or "-v" in sys.argv
        if is_verbose:
            import traceback

            traceback.print_exc()
        sys.exit(1)
