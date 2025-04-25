"""
Advent-of-Code bootstrapper.

Creates ⟨year⟩/⟨day⟩, downloads the puzzle input and
optionally scaffolds solution folders for Rust, Go and Python.

Usage
-----
    aoc-init -y 2025 -d 7 -s "$AOC_SESSION"     # scaffold all three
    aoc-init -y 2025 -d 7 -s "$AOC_SESSION" -l rust go
"""

from __future__ import annotations
import argparse
import os
import subprocess
import sys
from pathlib import Path
import requests 

# ––––– Supported languages –––––
LANGUAGES = ("rust", "go", "python")

# ---------- core helpers -----------------------------------------------
def create_day_folder(year: str, day: str) -> Path:
    root = Path.cwd()
    target = (root / day) if year in root.parts else (root / year / day)
    target.mkdir(parents=True, exist_ok=True)
    return target

def fetch_input(year: str, day: str, session: str, dst: Path) -> None:
    url = f"https://adventofcode.com/{year}/day/{int(day)}/input"
    r = requests.get(url, cookies={"session": session}, timeout=15)
    r.raise_for_status()
    (dst / "input.txt").write_text(r.text)
    (dst / "example.txt").touch()

# ---------- language scaffolding ---------------------------------------
def rust_project(dst: Path, year: str, day: str) -> None:
    rust_dir = dst / "rust"
    if rust_dir.exists():
        return
    subprocess.run(["cargo", "new", "rust", "--vcs", "none"], check=True, cwd=dst)
    toml = rust_dir / "Cargo.toml"
    toml.write_text(
        toml.read_text().replace(
            'name = "rust"',
            f'name = "aoc_AdventOfCode_{year}_day_{day}_rust"'
        )
    )

def go_project(dst: Path, year: str, day: str) -> None:
    go_dir = dst / "go"
    if go_dir.exists():
        return
    go_dir.mkdir()
    subprocess.run(
        ["go", "mod", "init", f"aoc_AdventOfCode_{year}_day_{day}_go"],
        check=True, cwd=go_dir
    )
    (go_dir / "main.go").write_text(
        f'package main\n\nimport "fmt"\n\nfunc main() {{\n'
        f'\tfmt.Println("Day {day} — Advent of Code {year}")\n}}\n'
    )

def python_project(dst: Path, *_args) -> None:
    py_dir = dst / "python"
    if py_dir.exists():
        return
    py_dir.mkdir()
    subprocess.run([sys.executable, "-m", "venv", ".venv"], check=True, cwd=py_dir)
    (py_dir / "main.py").write_text(
        'def main():\n    print("Solve me!")\n\n'
        'if __name__ == "__main__":\n    main()\n'
    )

CREATORS = {"rust": rust_project, "go": go_project, "python": python_project}

def main() -> None:
    p = argparse.ArgumentParser(prog="aoc-init", description="AoC day bootstrapper")
    p.add_argument("-d", "--day", required=True, help="Day 1-25 (no zero-padding)")
    p.add_argument("-y", "--year", required=True, help="Challenge year (2015-…)") 
    p.add_argument("-s", "--session", required=True, help="AoC session cookie")
    p.add_argument("-l", "--language", nargs="+", default=["all"],
                   choices=list(LANGUAGES) + ["all"],
                   help="Languages to scaffold (default = all)")
    args = p.parse_args()

    day = args.day.zfill(2)
    day_dir = create_day_folder(args.year, day)
    fetch_input(args.year, day, args.session, day_dir)

    langs = LANGUAGES if "all" in args.language else args.language
    for lang in langs:
        CREATORS[lang](day_dir, args.year, day)

if __name__ == "__main__":
    main()

