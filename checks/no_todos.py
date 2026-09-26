"""
checks/no_todos.py — Scans files changed in the current branch for TODO/FIXME comments.

Strategy:
  1. Use `git diff --name-only origin/main...HEAD` (or the default branch) to get
     the list of files changed on this branch.
  2. For each changed file, inspect only lines that contain a comment marker
     (# // -- <!-- * %) followed by TODO/FIXME.  This avoids false positives
     from string literals or documentation that merely mentions those words.
  3. If git is unavailable or there is no diff base, fall back to scanning the
     whole repo (excluding .git, node_modules, __pycache__, and binary files).

Files skipped unconditionally:
  - checks/no_todos.py  (this file — contains the words for matching purposes)
  - RELEASE_CHECKLIST.md (lists check names that include "TODO"/"FIXME")
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

# Match TODO/FIXME only when preceded by a comment-introducing character sequence.
# Supported markers: # (Python/Shell/Ruby/YAML), // (JS/TS/Go/Java/C/C++/Rust/Swift),
# -- (SQL/Lua/Haskell), <!-- (HTML/XML), * (block-comment body), % (TeX/Erlang).
# The marker may be followed by optional whitespace and/or other comment content
# before the keyword appears.
_PATTERN = re.compile(
    r"(?:#|//|--|<!--|%|\*)\s.*?\b(TODO|FIXME)\b"
    r"|"
    r"(?:#|//|--|<!--|%|\*)\s*(TODO|FIXME)\b",
    re.IGNORECASE,
)

_SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", "venv", ".tox"}
_TEXT_SUFFIXES = {
    ".py", ".js", ".ts", ".jsx", ".tsx", ".java", ".go", ".rb", ".rs",
    ".c", ".cpp", ".h", ".cs", ".swift", ".kt", ".sh", ".yaml", ".yml",
    ".toml", ".md", ".txt", ".html", ".css", ".json",
}

# Files that must never be flagged (they reference TODO/FIXME as words, not markers).
_SKIP_FILES = {"checks/no_todos.py", "RELEASE_CHECKLIST.md"}


def _changed_files(repo_path: str) -> list[Path] | None:
    """Return paths of files changed vs. the default remote branch, or None on failure."""
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
            return [p for p in paths if p.is_file()]
    return None


def _all_text_files(repo_path: str) -> list[Path]:
    root = Path(repo_path).resolve()
    files = []
    for p in root.rglob("*"):
        if any(part in _SKIP_DIRS for part in p.parts):
            continue
        if p.is_file() and p.suffix in _TEXT_SUFFIXES:
            files.append(p)
    return files


def run(repo_path: str) -> dict:
    """Return {"passed": bool, "reason": str}."""
    files = _changed_files(repo_path)
    scope = "changed files"
    if files is None:
        files = _all_text_files(repo_path)
        scope = "all repository files (git diff unavailable)"

    root = Path(repo_path).resolve()
    hits: list[str] = []
    for path in files:
        # Skip this check's own source file and the release checklist.
        try:
            rel = path.relative_to(root)
        except ValueError:
            rel = path
        if rel.as_posix() in _SKIP_FILES or path.name in {Path(s).name for s in _SKIP_FILES}:
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for lineno, line in enumerate(text.splitlines(), 1):
            if _PATTERN.search(line):
                hits.append(f"  {rel}:{lineno}: {line.strip()}")

    if not hits:
        return {"passed": True, "reason": f"No TODO/FIXME found in {scope}."}

    sample = "\n".join(hits[:10])
    extra = f"\n  … and {len(hits) - 10} more." if len(hits) > 10 else ""
    return {
        "passed": False,
        "reason": f"Found {len(hits)} TODO/FIXME comment(s) in {scope}:\n{sample}{extra}",
    }
