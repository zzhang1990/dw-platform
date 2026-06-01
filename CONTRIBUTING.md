# Contributing to DW Platform

Thank you for considering a contribution to DW Platform. The project is currently an early
preview, so focused documentation, examples, tests, and small implementation slices are
especially useful.

## Development Setup

```bash
git clone https://github.com/zzhang1990/dw-platform.git
cd dw-platform

python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

## Run Checks

Run the unit tests:

```bash
python -m pytest -q
```

Run a lightweight ETL entry-point smoke check:

```bash
python scripts/etl/etl.py --dt 2024-01-01 --layer all
```

## Contribution Workflow

1. Search the existing [Issues](https://github.com/zzhang1990/dw-platform/issues) before
   starting work.
2. Create a focused branch, for example `feat/starrocks-ddl-examples`.
3. Keep the change scoped and add or update the most relevant tests.
4. Run the checks above.
5. Open a Pull Request with a concise summary and verification notes.

Use `Fixes #issue_number` or `Closes #issue_number` in the Pull Request description when
the change resolves an existing Issue.

## Areas Where Contributions Help

- StarRocks table DDL and layered modeling examples.
- DolphinScheduler workflow samples.
- CloudCanal and DataX setup examples.
- Data quality checks and automated tests.
- Documentation corrections and deployment notes.

## Code Style

- Use Python type annotations for new or changed functions.
- Keep SQL keywords uppercase and format longer queries for readability.
- Prefer small, reviewable changes that match the existing project structure.
