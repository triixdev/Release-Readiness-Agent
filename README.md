# Release Readiness Agent

A lightweight CLI tool that validates a Git repository against a configurable
checklist of release criteria before you ship.  Run it at the end of a feature
branch and get a clear pass/fail verdict for every gate in seconds.

---

## Why it exists

Releasing broken code usually comes down to one of a handful of recurring
oversights: tests were skipped, a CHANGELOG entry was forgotten, a leftover
debug comment slipped through, or a database migration was never reviewed.
Rather than relying on memory or a manual checklist, this tool codifies those
gates and runs them automatically — in parallel — against any local repository.

---

## How it works

```
main.py
  └─ checklist.py      — parses RELEASE_CHECKLIST.md into check slugs
  └─ runner.py         — imports checks/<slug>.py and runs them concurrently
  └─ report.py         — prints the colour-coded pass/fail summary
  └─ checks/
       ├─ tests_pass.py
       ├─ no_todos.py
       ├─ changelog_updated.py
       └─ no_unreviewed_migrations.py
```

1. **`RELEASE_CHECKLIST.md`** lists the checks to run, one per line:
   ```
   - [ ] **slug** — Human-readable description
   ```
2. **`checklist.py`** reads that file and produces a list of `CheckItem` objects.
3. **`runner.py`** imports `checks/<slug>.py` for each item and calls its
   `run(repo_path)` function in a thread pool.  Each check returns
   `{"passed": bool, "reason": str}`.
4. **`report.py`** prints the results and exits `0` (all passed) or `1` (any failed).

---

## Project structure

```
release-readiness-agent/
├── main.py                        # Entry point
├── checklist.py                   # Checklist parser
├── runner.py                      # Parallel check runner
├── report.py                      # Console report formatter
├── RELEASE_CHECKLIST.md           # Defines which checks to run
├── checks/
│   ├── __init__.py
│   ├── tests_pass.py              # Runs pytest (falls back to unittest)
│   ├── no_todos.py                # Finds TODO/FIXME in code comments
│   ├── changelog_updated.py       # Verifies CHANGELOG.md was modified
│   └── no_unreviewed_migrations.py# Flags unreviewed DB migration files
└── demo-project/                  # Sample project for demoing the tool
    ├── app.py                     # Simple Python module (has a leftover TODO)
    ├── test_app.py                # Passing pytest test suite
    └── CHANGELOG.md
```

---

## Built-in checks

| Slug | What it validates |
|---|---|
| `tests_pass` | Runs `pytest` (falls back to `unittest discover`). Passes only if exit code is 0. |
| `no_todos` | Scans changed files for `# TODO` / `// FIXME` in code comments. Skips string literals and documentation prose. |
| `changelog_updated` | Confirms `CHANGELOG.md` was modified on this branch (falls back to an existence check when git is unavailable). |
| `no_unreviewed_migrations` | Flags migration files in `migrations/` or `alembic/versions/` that lack a `# reviewed` marker or a `.reviewed` sentinel file. |

---

## Requirements

- Python 3.10+
- `pytest` (optional — `tests_pass` falls back to `unittest` if absent)
- Git (optional — checks fall back to whole-repo scanning if absent)

No third-party packages are required for the agent itself.

---

## Installation

```bash
git clone <repo-url>
cd release-readiness-agent
# Optional: create a virtual environment
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install pytest   # only needed if the target project uses pytest
```

---

## Usage

```bash
python main.py <repo_path> [checklist_path]
```

| Argument | Default | Description |
|---|---|---|
| `repo_path` | *(required)* | Path to the Git repository to validate |
| `checklist_path` | `RELEASE_CHECKLIST.md` | Checklist file to use |

### Exit codes

| Code | Meaning |
|---|---|
| `0` | All checks passed — safe to release |
| `1` | One or more checks failed |
| `2` | Bad arguments or unreadable files |

### Examples

```bash
# Validate the current directory using the default checklist
python main.py .

# Validate the demo project (expects failures — it has a TODO and no CHANGELOG)
python main.py demo-project/

# Use a custom checklist
python main.py /path/to/my-service checklist-staging.md
```

---

## Adding a new check

1. Create `checks/<slug>.py` with a single `run(repo_path: str) -> dict` function
   that returns `{"passed": bool, "reason": str}`.
2. Add a line to `RELEASE_CHECKLIST.md`:
   ```
   - [ ] **<slug>** — Description shown in the report
   ```

That's it — no registration or wiring needed.  The runner resolves slugs to
modules by name automatically.

---

## Demo

The `demo-project/` directory contains a small fake project that intentionally
fails two checks out of the box:

```bash
python main.py demo-project/
```

Expected output:
- ❌ `no_todos` — `app.py` contains a `# TODO` comment
- ❌ `changelog_updated` — `CHANGELOG.md` was not modified on this branch
- ✅ `tests_pass` — all 10 tests pass
- ✅ `no_unreviewed_migrations` — no migration files present

Fix both failures to see the tool report a clean release:
1. Remove (or resolve) the `# TODO` comment in `demo-project/app.py`
2. Add an entry to `demo-project/CHANGELOG.md` and commit it

---

## License

See [LICENSE](LICENSE).
