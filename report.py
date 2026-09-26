"""
report.py — Formats CheckResult objects into a readable console pass/fail summary.

Uses only stdlib — no third-party dependencies.
Terminal colour codes are used when stdout is a TTY; stripped otherwise.
"""

from __future__ import annotations

import sys
from runner import CheckResult

# --- colour helpers ----------------------------------------------------------

_IS_TTY = sys.stdout.isatty()


def _c(code: str, text: str) -> str:
    return f"\033[{code}m{text}\033[0m" if _IS_TTY else text


def green(t: str) -> str:  return _c("32", t)
def red(t: str) -> str:    return _c("31", t)
def bold(t: str) -> str:   return _c("1",  t)
def dim(t: str) -> str:    return _c("2",  t)
def yellow(t: str) -> str: return _c("33", t)


# --- public API --------------------------------------------------------------

def print_report(results: list[CheckResult]) -> bool:
    """
    Print a formatted report to stdout.
    Returns True if all checks passed, False otherwise.
    """
    width = 60
    print()
    print(bold("=" * width))
    print(bold("  Release Readiness Report"))
    print(bold("=" * width))

    passed_count = 0
    failed_count = 0

    for r in results:
        icon = green("✔ PASS") if r.passed else red("✘ FAIL")
        label = bold(r.description)
        slug_hint = dim(f"[{r.slug}]")
        print(f"\n  {icon}  {label} {slug_hint}")

        # Indent the reason under the check line
        if r.reason:
            for line in r.reason.splitlines():
                print(f"       {dim(line)}")

        if r.passed:
            passed_count += 1
        else:
            failed_count += 1

    print()
    print(bold("-" * width))
    total = passed_count + failed_count
    summary = f"  {passed_count}/{total} checks passed"

    if failed_count == 0:
        verdict = green(bold("✔ READY TO RELEASE"))
        print(f"{green(summary)}")
        print(f"\n  {verdict}")
    else:
        verdict = red(bold(f"✘ NOT READY — {failed_count} check(s) failed"))
        print(f"{yellow(summary)}")
        print(f"\n  {verdict}")

    print(bold("=" * width))
    print()

    return failed_count == 0
