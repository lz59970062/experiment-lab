"""Install the bundled Experiment Lab skill into local agent skill directories."""

from __future__ import annotations

import argparse
import shutil
import sys
from importlib.resources import files
from pathlib import Path


REPOSITORY_URL = "https://github.com/lz59970062/experiment-lab.git"
PIP_SPEC = f"git+{REPOSITORY_URL}"
SKILL_NAME = "experiment-lab"


def quote_shell(value: str) -> str:
    return "'" + value.replace("'", "'\"'\"'") + "'"


def current_env_install_command() -> str:
    python = quote_shell(sys.executable)
    uv = shutil.which("uv")
    if uv:
        return f"{quote_shell(uv)} pip install --python {python} {PIP_SPEC}"
    return f"{python} -m pip install {PIP_SPEC}"


def install_hint() -> str:
    command = current_env_install_command()
    python = quote_shell(sys.executable)
    lines = [
        "## Python Package Requirement",
        "",
        "This skill uses the installable `experiment-lab` Python package for helper commands such as `lab-queue`.",
        "If `lab-queue` or `experiment-lab-paths` is not available in the active Python environment, ask the user before installing it.",
        "",
        "Preferred install command for the Python environment that generated this skill file:",
        "",
        "```bash",
        command,
        "```",
        "",
        "Equivalent pip command for the same Python interpreter:",
        "",
        "```bash",
        f"{python} -m pip install {PIP_SPEC}",
        "```",
        "",
        "If the project uses `uv`, use the active project interpreter or replace the `--python` value explicitly:",
        "",
        "```bash",
        f"uv pip install --python {python} {PIP_SPEC}",
        "```",
        "",
    ]
    return "\n".join(lines)


def bundled_skill_text() -> str:
    resource = files("experiment_lab").joinpath("SKILL.md")
    return resource.read_text(encoding="utf-8")


def generated_skill_text() -> str:
    text = bundled_skill_text()
    section = "## Python Package Requirement\n"
    next_section = "\nCS experiment management system"
    hint = install_hint()
    if section in text and next_section in text:
        start = text.index(section)
        end = text.index(next_section)
        return text[:start] + hint + text[end:]
    marker = "# Experiment Lab\n"
    if marker in text:
        return text.replace(marker, marker + "\n" + hint, 1)
    return hint + "\n" + text


def default_targets() -> dict[str, Path]:
    home = Path.home()
    return {
        "codex": home / ".codex" / "skills" / SKILL_NAME / "SKILL.md",
        "claude": home / ".claude" / "skills" / SKILL_NAME / "SKILL.md",
    }


def selected_targets(target: str) -> dict[str, Path]:
    targets = default_targets()
    if target == "both":
        return targets
    return {target: targets[target]}


def install_skill(path: Path, text: str, force: bool, dry_run: bool) -> str:
    if path.exists() and not force:
        return f"skip existing {path} (use --force to overwrite)"
    if dry_run:
        action = "overwrite" if path.exists() else "write"
        return f"dry-run {action} {path}"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return f"installed {path}"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--target",
        choices=["codex", "claude", "both"],
        default="both",
        help="Which agent skill directory to install into.",
    )
    parser.add_argument("--force", action="store_true", help="Overwrite an existing SKILL.md.")
    parser.add_argument("--dry-run", action="store_true", help="Print planned writes without changing files.")
    parser.add_argument(
        "--print-install-command",
        action="store_true",
        help="Print the detected install command for the current Python environment and exit.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.print_install_command:
        print(current_env_install_command())
        return 0

    text = generated_skill_text()
    for name, path in selected_targets(args.target).items():
        print(f"{name}: {install_skill(path, text, args.force, args.dry_run)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
