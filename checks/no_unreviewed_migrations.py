"""
checks/no_unreviewed_migrations.py — Flags database migration files added on this
branch that lack a corresponding review marker.

Convention (configurable below):
  - Migration files live in directories named "migrations" or "migrate".
  - A migration is considered *reviewed* if the file contains the marker string
    `# reviewed` (case-insensitive) anywhere in it, or if a sibling file named
    `<filename>.reviewed` exists next to it.

This gives teams a lightweight, code-based review gate without needing a
separate approval system.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

_MIGRATION_DIRS = {"migrations", "migrate", "db/migrate", "alembic/versions"}
_REVIEW_MARKER = "# reviewed"


def _new_migration_files(repo_path: str) -> list[Path] | None:
    """
    Return migration files added/changed on this branch, or None if git is
    unavailable.
    """
    root = Path(repo_path).resolve()
    for base in ("origin/main", "origin/master"):
        result = subprocess.run(
            ["git", "diff", "--name-only", "--diff-filter=ACMR", f"{base}...HEAD"],
            cwd=str(root),
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            paths = [root / p.strip() for p in result.stdout.splitlines() if p.strip()]
            return [
                p for p in paths
                if p.is_file() and any(d in p.parts for d in _MIGRATION_DIRS)
            ]
    return None


def _all_migration_files(repo_path: str) -> list[Path]:
    root = Path(repo_path).resolve()
    files = []
    for migration_dir in _MIGRATION_DIRS:
        target = root / migration_dir
        if target.is_dir():
            files.extend(f for f in target.rglob("*") if f.is_file())
    return files


def _is_reviewed(path: Path) -> bool:
    # Check for a sibling .reviewed sentinel file
    if path.with_suffix(path.suffix + ".reviewed").exists():
        return True
    # Check for the inline marker comment
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
        return _REVIEW_MARKER in text.lower()
    except OSError:
        return False


def run(repo_path: str) -> dict:
    """Return {"passed": bool, "reason": str}."""
    files = _new_migration_files(repo_path)
    scope = "changed migration files"
    if files is None:
        files = _all_migration_files(repo_path)
        scope = "all migration files (git diff unavailable)"

    if not files:
        return {"passed": True, "reason": f"No migration files found in {scope}."}

    unreviewed = [p for p in files if not _is_reviewed(p)]

    if not unreviewed:
        return {
            "passed": True,
            "reason": f"All {len(files)} migration file(s) in {scope} are reviewed.",
        }

    root = Path(repo_path).resolve()
    names = "\n".join(f"  {p.relative_to(root)}" for p in unreviewed)
    return {
        "passed": False,
        "reason": (
            f"{len(unreviewed)} unreviewed migration file(s) in {scope}:\n{names}\n"
            f"Add `{_REVIEW_MARKER}` to each file or create a `.reviewed` sentinel."
        ),
    }
