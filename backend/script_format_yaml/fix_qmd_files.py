#!/usr/bin/env python3
"""fix_qmd_files.py — alias de compatibilidad (FS3, 2026-09-07): la suite vive en main.py + config.py + lib/formato.py."""
import runpy
import sys
from pathlib import Path

sys.argv[0] = str(Path(__file__).with_name("main.py"))
runpy.run_path(sys.argv[0], run_name="__main__")
