"""
runner.py — Resolves check slugs to their implementation functions and runs them
in parallel using concurrent.futures.ThreadPoolExecutor.

Each check function lives in checks/<slug>.py and exports a run(repo_path) function
that returns {"passed": bool, "reason": str}.
"""

from __future__ import annotations

import importlib
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass

from checklist import CheckItem


@dataclass
class CheckResult:
    slug: str
    description: str
    passed: bool
    reason: str


def _run_one(item: CheckItem, repo_path: str) -> CheckResult:
    """Import checks/<slug>.py and call its run() function."""
    try:
        module = importlib.import_module(f"checks.{item.slug}")
        result = module.run(repo_path)
        return CheckResult(
            slug=item.slug,
            description=item.description,
            passed=bool(result["passed"]),
            reason=result.get("reason", ""),
        )
    except ModuleNotFoundError:
        return CheckResult(
            slug=item.slug,
            description=item.description,
            passed=False,
            reason=f"No check implementation found for slug '{item.slug}' "
                   f"(expected checks/{item.slug}.py).",
        )
    except Exception as exc:  # noqa: BLE001
        return CheckResult(
            slug=item.slug,
            description=item.description,
            passed=False,
            reason=f"Check raised an unexpected error: {exc}",
        )


def run_all(items: list[CheckItem], repo_path: str) -> list[CheckResult]:
    """
    Run every check in *items* concurrently and return results in the same order
    as the input list.
    """
    results: dict[str, CheckResult] = {}

    with ThreadPoolExecutor(max_workers=min(len(items), 8)) as pool:
        future_to_item = {
            pool.submit(_run_one, item, repo_path): item for item in items
        }
        for future in as_completed(future_to_item):
            result = future.result()
            results[result.slug] = result

    # Return in original checklist order
    return [results[item.slug] for item in items]
