# Contributing to FastAPI Transaction Classifier

## Development Setup

1. **Install dependencies:**
   ```bash
   pip install -r dev-requirements.txt
   ```

2. **Install pre-commit hooks (recommended):**
   ```bash
   pre-commit install
   ```

## Code Quality Standards

This project enforces code quality through automated checks in CI. Before submitting a PR, ensure your code passes all checks:

### Code Formatting with Black

We use [Black](https://black.readthedocs.io/) for consistent code formatting.

**To check formatting:**
```bash
python -m black --check --diff .
```

**To apply formatting:**
```bash
python -m black .
```

### Linting with Ruff

We use [Ruff](https://docs.astral.sh/ruff/) for fast Python linting.

**To check for linting issues:**
```bash
python -m ruff check .
```

### Type Checking with MyPy

We use [MyPy](https://mypy.readthedocs.io/) for static type checking.

**To run type checking:**
```bash
python -m mypy .
```

### Running Tests

```bash
pytest --maxfail=1 --disable-warnings --quiet
```

## Pre-commit Hooks

The easiest way to ensure your code meets our standards is to install pre-commit hooks:

```bash
pip install pre-commit
pre-commit install
```

This will automatically run Black, Ruff, and MyPy before each commit, preventing CI failures.

## CI/CD Pipeline

Our GitHub Actions CI pipeline will:

1. **Install dependencies** (including spaCy models)
2. **Run tests** with pytest
3. **Check code formatting** with Black (fails if not formatted)
4. **Lint code** with Ruff
5. **Type check** with MyPy

**If the Black step fails**, it means your code needs formatting. Run `python -m black .` locally, commit the changes, and push again.

## Common Issues

### "Black formatting check failed"

If CI fails with a black formatting error:

1. Run `python -m black .` in your local repository
2. Commit the formatting changes: `git add . && git commit -m "Apply black formatting"`
3. Push the changes: `git push`

### Pre-commit hooks not running

If you've installed pre-commit but hooks aren't running:

1. Make sure you're in the repository root
2. Run `pre-commit install` again
3. Try running `pre-commit run --all-files` manually

## Questions?

If you have questions about the development setup or contributing guidelines, please open an issue for discussion.
