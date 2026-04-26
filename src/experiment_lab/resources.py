"""Locate bundled Experiment Lab resource files after installation."""

from __future__ import annotations

import argparse
from importlib.resources import as_file, files
from pathlib import Path


def package_root() -> Path:
    """Return the installed package directory."""
    return Path(__file__).resolve().parent


def skill_md() -> Path:
    """Return a filesystem path for the bundled SKILL.md file."""
    resource = files("experiment_lab").joinpath("SKILL.md")
    with as_file(resource) as path:
        return Path(path)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skill-md", action="store_true", help="Print only the bundled SKILL.md path.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.skill_md:
        print(skill_md())
    else:
        print(f"package_root={package_root()}")
        print(f"skill_md={skill_md()}")
    return 0
