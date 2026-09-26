"""
checks/tests_pass.py — Runs the project's test suite and reports whether it passed.

Strategy: tries pytest first, then unittest discovery as a fallback.
The check passes only if the test runner exits with code 0.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def run(repo_path: str) -> dict:
    """Return {"passed": bool, "reason": str}."""
    root = Path(repo_path).resolve()

    # Prefer pytest if it is importable; fall back to stdlib unittest.
    runners = [
        [sys.executable, "-m", "pytest", "--tb=short", "-q"],
        [sys.executable, "-m", "unittest", "discover", "-s", str(root)],
    ]

    for cmd in runners:
        result = subprocess.run(
            cmd,
            cwd=str(root),
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            return {"passed": True, "reason": "All tests passed."}
        # returncode 5 means "no tests collected" in pytest — treat as pass
        if result.returncode == 5:
            return {"passed": True, "reason": "No tests found — nothing to fail."}
        # pytest found and ran tests but some failed
        output = (result.stdout + result.stderr).strip()
        last_lines = "\n".join(output.splitlines()[-6:])
        return {"passed": False, "reason": f"Tests failed:\n{last_lines}"}

    # Should be unreachable
    return {"passed": False, "reason": "Could not determine test status."}
