#!/usr/bin/env python3
"""Compatibility wrapper for the installable experiment_lab package."""

from __future__ import annotations

import sys
from pathlib import Path

src = Path(__file__).resolve().parents[1] / "src"
if src.exists():
    sys.path.insert(0, str(src))

from experiment_lab.lab_queue import main


if __name__ == "__main__":
    raise SystemExit(main())
