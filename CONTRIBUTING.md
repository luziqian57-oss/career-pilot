# Contributing to CareerPilot

Thanks for helping improve CareerPilot. Contributions of code, tests, documentation, issue reports, and design feedback are welcome.

## Before you start

- Search existing issues before opening a new one.
- Use a GitHub issue for significant features so the approach can be discussed first.
- Never include real resumes, API keys, personal data, or proprietary job descriptions in issues or tests.
- For vulnerabilities, follow [SECURITY.md](SECURITY.md) instead of opening a public issue.

## Development setup

CareerPilot requires Python 3.12.

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
cp .env.example .env
```

The default `mock` LLM provider works without an API key. Run the checks before submitting a pull request:

```bash
ruff check .
ruff format --check .
pytest -q
python -m build
```

## Pull requests

1. Create a focused branch from `main`.
2. Add or update tests for behavior changes.
3. Update the README or changelog when user-facing behavior changes.
4. Keep commits small and use clear imperative messages.
5. Complete the pull request template and link related issues.

By contributing, you agree that your contribution is licensed under the project's MIT License.
