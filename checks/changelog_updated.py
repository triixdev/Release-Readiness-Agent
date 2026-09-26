"""
checks/changelog_updated.py — Verifies that CHANGELOG.md was modified on this branch.

Strategy:
  1. Ask git whether CHANGELOG.md appears in the diff between HEAD and the
     default remote branch.
  2. If git is unavailable, fall back to checking whether CHANGELOG.md simply
     exists in the repo (a weaker but still useful signal).
"""

from __future__ import annotations

import subprocess
from pathlib import Path


def _changelog_in_diff(repo_path: str) -> bool | None:
    """
    Return True if CHANGELOG.md was changed vs. the default branch,
    False if git ran but CHANGELOG.md was not changed,
    None if git is unavailable.
    """
    root = Path(repo_path).resolve()
    for base in ("origin/main", "origin/master"):
        result = subprocess.run(
            ["git", "diff", "--name-only", f"{base}...HEAD"],
            cwd=str(root),
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            changed = [Path(p.strip()).name.lower() for p in result.stdout.splitlines() if p.strip()]
            return "changelog.md" in changed
    return None


def run(repo_path: str) -> dict:
    """Return {"passed": bool, "reason": str}."""
    root = Path(repo_path).resolve()
    in_diff = _changelog_in_diff(repo_path)

    if in_diff is True:
        return {"passed": True, "reason": "CHANGELOG.md was updated on this branch."}

    if in_diff is False:
        return {
            "passed": False,
            "reason": (
                "CHANGELOG.md was not modified on this branch. "
                "Please document your changes before releasing."
            ),
        }

    # git unavailable — fall back to existence check
    changelog = root / "CHANGELOG.md"
    if changelog.exists():
        return {
            "passed": True,
            "reason": "CHANGELOG.md exists (git unavailable; diff check skipped).",
        }
    return {
        "passed": False,
        "reason": "CHANGELOG.md does not exist in the repository.",
    }
