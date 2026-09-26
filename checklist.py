"""
checklist.py — Loads and parses RELEASE_CHECKLIST.md into CheckItem objects.

Each line matching `- [ ] **<slug>** — <description>` becomes one CheckItem.
The slug is used to look up the corresponding check function in checks/.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class CheckItem:
    slug: str          # machine-readable key, e.g. "tests_pass"
    description: str   # human-readable label from the checklist


# Matches:  - [ ] **slug** — description
_ITEM_RE = re.compile(r"-\s+\[\s*\]\s+\*\*([a-z_]+)\*\*\s+[—–-]\s+(.+)")


def load_checklist(path: str | Path) -> list[CheckItem]:
    """Parse *path* and return a list of CheckItems in document order."""
    source = Path(path).read_text(encoding="utf-8")
    items: list[CheckItem] = []
    for line in source.splitlines():
        m = _ITEM_RE.match(line.strip())
        if m:
            items.append(CheckItem(slug=m.group(1), description=m.group(2).strip()))
    if not items:
        raise ValueError(f"No checklist items found in {path!r}. "
                         "Each item must follow the pattern: "
                         "- [ ] **slug** — description")
    return items
