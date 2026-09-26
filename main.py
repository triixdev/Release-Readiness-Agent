"""
main.py — Release Readiness Agent entry point.

Usage:
    python main.py <repo_path> [checklist_path]

Arguments:
    repo_path       Path to the git repository to validate.
    checklist_path  Path to the checklist markdown file.
                    Defaults to RELEASE_CHECKLIST.md in the current directory.

Exit codes:
    0 — all checks passed (safe to release)
    1 — one or more checks failed
    2 — bad arguments or unreadable files
"""

from __future__ import annotations

import sys
from pathlib import Path


def main() -> int:
    # ------------------------------------------------------------------ args
    if len(sys.argv) < 2:
        print(
            "Usage: python main.py <repo_path> [checklist_path]\n"
            "  repo_path       — path to the git repo to validate\n"
            "  checklist_path  — markdown checklist (default: RELEASE_CHECKLIST.md)",
            file=sys.stderr,
        )
        return 2

    repo_path = sys.argv[1]
    checklist_path = sys.argv[2] if len(sys.argv) > 2 else "RELEASE_CHECKLIST.md"

    if not Path(repo_path).is_dir():
        print(f"Error: repo path {repo_path!r} is not a directory.", file=sys.stderr)
        return 2

    if not Path(checklist_path).is_file():
        print(f"Error: checklist file {checklist_path!r} not found.", file=sys.stderr)
        return 2

    # ----------------------------------------------------------- load & run
    from checklist import load_checklist
    from runner import run_all
    from report import print_report

    print(f"Loading checklist from: {checklist_path}")
    print(f"Validating repository:  {Path(repo_path).resolve()}\n")

    items = load_checklist(checklist_path)
    print(f"Running {len(items)} check(s) in parallel...\n")

    results = run_all(items, repo_path)
    all_passed = print_report(results)

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
