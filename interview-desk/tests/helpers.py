import subprocess
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent


def run_script(name, *args, stdin=None):
    return subprocess.run(
        [sys.executable, str(PROJECT / "scripts" / name), *args],
        capture_output=True, text=True, input=stdin,
    )
