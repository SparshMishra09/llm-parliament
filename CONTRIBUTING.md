# Contributing to LLM Parliament

Thanks for taking the time to contribute.

## Before you start

- New here? The [roadmap](https://github.com/elarmuzik1993/llm-parliament/issues/15)
  shows where the project is heading, and issues labeled
  [`good first issue`](https://github.com/elarmuzik1993/llm-parliament/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22)
  are scoped for a first contribution — some need no code at all.
- Check [open issues](https://github.com/elarmuzik1993/llm-parliament/issues)
  to avoid duplicating work.
- For significant changes, open an issue first to discuss the approach.
- Read `AGENTS.md` — it covers the architecture, conventions, and key files
  you need to know before touching the code.

## Setup

```bash
git clone https://github.com/elarmuzik1993/llm-parliament.git
cd llm-parliament
pip install -e ".[dev]"
```

## Before submitting a PR

```bash
python -m pytest -q    # the full suite must pass
ruff check .           # must be clean
```

## What makes a good PR

- **Focused** — one logical change per PR.
- **Tested** — new behaviour has tests; bug fixes include a regression test.
- **Clean** — no debug prints, no commented-out code, ruff clean.
- **Described** — PR description explains *why*, not just *what*.

## Reporting bugs

Use the [bug report template](.github/ISSUE_TEMPLATE/bug_report.md).
For security issues, follow [SECURITY.md](SECURITY.md) instead.

## Feature requests

Use the [feature request template](.github/ISSUE_TEMPLATE/feature_request.md).
