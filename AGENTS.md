# AGENTS.md

## Purpose
This file gives coding agents a practical guide for working in `clir`.
It documents build/lint/test commands, single-test workflows, and repository coding conventions.

## Project Snapshot
- Language: Python (Poetry-managed)
- CLI entrypoint: `clir = "clir.cli:cli"` in `pyproject.toml`
- Main modules:
  - `clir/cli.py`
  - `clir/command.py`
  - `clir/utils/config.py`
  - `clir/utils/db.py`
  - `clir/utils/core.py`, `clir/utils/filters.py`
- Tests: `tests/1-init_clir.py` ... `tests/7-import_export_command.py`
- CI workflow: `.github/workflows/test-clir.yml`

## Cursor and Copilot Rules
- `.cursor/rules/`: not present
- `.cursorrules`: not present
- `.github/copilot-instructions.md`: not present

If these files are added later, treat them as higher-priority constraints and update this document.

## Environment and Tooling
- Python target: `^3.9`
- Dependency/build tool: Poetry
- Test framework: `pytest`
- CLI framework: `rich-click` + `click`
- Output formatting: `rich`
- Clipboard testing in CI: `pyperclip`

## Install and Build Commands
Run from repository root.

1. Install dependencies:
   - `poetry install`
2. Build package:
   - `poetry build`
3. Install local package:
   - `pip install .`
4. Publish-workflow build path:
   - `python -m pip install --upgrade pip`
   - `pip install build`
   - `python -m build`

## Test Commands
### Full suite (CI-like order)
- `pytest -v -s tests/1-init_clir.py tests/2-add_command.py tests/3-copy_command.py tests/4-run_command.py tests/5-remove_command.py tests/6-list_command.py tests/7-import_export_command.py`

Use this order for realistic validation; tests share state in `~/.clir`.

### Run all tests
- `pytest -v -s tests`

### Run a single test file
- `pytest -v -s tests/2-add_command.py`

### Run a single test function
- `pytest -v -s tests/2-add_command.py::test_add_new_command`

### Run by keyword expression
- `pytest -v -s -k "import or export" tests`

### Optional coverage
- `pytest --cov=clir --cov-report=term-missing -v -s tests`

## Lint, Format, and Type Checks
No enforced lint/format/type configuration is committed (`ruff`, `flake8`, `black`, `isort`, `mypy`, `pyright`, `tox`, `nox` configs are absent).

Recommended ad-hoc checks:
- Syntax sanity: `python -m compileall clir tests`
- Optional formatter: `black clir tests`
- Optional import sort: `isort clir tests`
- Optional type check: `mypy clir`

Assume these are optional unless CI is updated to enforce them.

## Test State and Isolation Notes
Tests are stateful and use real files under `~/.clir`.

Examples:
- Migration checks in `tests/1-init_clir.py`
- Run/copy side effects using `~/.clir/test-file.txt`
- Temporary files in import/export tests

Agent guidance:
- Prefer CI-like ordering for broad validation.
- For one-off debugging, confirm whether earlier tests are prerequisites.
- If isolation is needed, use a temporary HOME in a subshell.
- Do not perform destructive cleanup unless requested.

## Code Style Guidelines
### Imports
- Order imports: stdlib, third-party, local (`clir.*`).
- Prefer one import per line where practical.
- Remove unused imports.
- Prefer explicit imports over wildcard imports.

### Formatting
- Follow PEP 8 baseline.
- 4-space indentation.
- Keep lines reasonably short (target <= 100 chars).
- Keep blank lines between top-level defs/classes.
- Keep SQL and shell strings readable.
- Avoid new non-ASCII unless file already uses it intentionally.

### Types
- Extend type hints incrementally in touched code.
- Add hints to new/changed public functions and methods.
- Use concrete return types when known.
- Avoid `Any` unless unavoidable.

### Naming
- `snake_case` for variables/functions/methods/helpers.
- `PascalCase` for classes (`Command`, `CommandTable`, `DbIntegrity`).
- `UPPER_SNAKE_CASE` for constants.
- Tests should be named `test_<behavior>`.

### CLI Conventions
- Add commands in `clir/cli.py` with Click decorators.
- Keep flags consistent with existing style (`-t/--tag`, `-g/--grep`).
- Ensure `init_config()` runs before DB-dependent logic.

### Database and Persistence
- Use parameterized SQL (`?` placeholders), never interpolated values.
- Preserve integrity across `commands`, `tags`, and `commands_tags`.
- Preserve migration behavior from legacy `commands.json`.

### Error Handling
- Prefer specific exceptions (`FileNotFoundError`, `ValueError`, `sqlite3.Error`, etc.).
- Avoid bare `except:` in new code.
- Raise errors with actionable context.
- Keep CLI error output clear and exit behavior consistent.

### Side Effects and Execution
- Be careful with `os.system` and subprocess behavior.
- Changes that run user commands must preserve current safety expectations.
- Preserve OS-specific clipboard behavior (Darwin/Linux paths).

### Output
- Use existing `rich.print`/Rich table patterns.
- Keep output concise and user-focused.
- Avoid noisy debug output in committed code.

## Testing Expectations for Changes
- For non-trivial changes:
  - run targeted affected test files
  - run at least one specific test function for regressions
- For config/init/db/CLI flow changes:
  - run full CI-like ordered suite
- For new behavior:
  - add or update tests in `tests/` using existing `CliRunner` patterns

## Change Hygiene for Agents
- Keep diffs focused and behavior-oriented.
- Avoid broad style rewrites in unrelated files.
- Preserve public CLI names/options unless explicitly requested.
- Update docs and tests with behavior changes.
- If introducing tooling, document it and update CI in the same PR.

## Quick Command Reference
- Install deps: `poetry install`
- Build: `poetry build`
- Install package: `pip install .`
- Full CI-like tests: `pytest -v -s tests/1-init_clir.py tests/2-add_command.py tests/3-copy_command.py tests/4-run_command.py tests/5-remove_command.py tests/6-list_command.py tests/7-import_export_command.py`
- Single file: `pytest -v -s tests/4-run_command.py`
- Single test: `pytest -v -s tests/4-run_command.py::test_run_command`
- By keyword: `pytest -v -s -k "remove_command" tests`

## Maintenance Note
When standards evolve (CI gates, lints, Cursor rules, Copilot instructions), update this file promptly.
