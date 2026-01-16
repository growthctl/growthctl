# Contributing to growthctl

Thank you for your interest in contributing! We use modern Python tooling to keep our development experience fast and reliable.

## Development Setup

We use [uv](https://github.com/astral-sh/uv) for dependency management and package resolution.

1. **Install uv**
   ```bash
   # MacOS / Linux
   curl -LsSf https://astral.sh/uv/install.sh | sh
   
   # Windows
   powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
   ```

2. **Clone and Setup**
   ```bash
   git clone https://github.com/growthctl/growthctl.git
   cd growthctl
   
   # Create virtualenv and install dependencies
   uv sync
   ```

3. **Install Pre-commit Hooks**
   We use pre-commit to ensure code quality (ruff linting & formatting) before every commit.
   ```bash
   uv run pre-commit install
   ```

## Workflow

- **Linting & Formatting**: Handled automatically by pre-commit.
  To run manually:
  ```bash
  uv run ruff check .
  uv run ruff format .
  ```

- **Running the CLI**:
  ```bash
  uv run growthctl --help
  ```

## Documentation

Documentation is built with Docusaurus.

```bash
cd docs/website
npm install
npm start
```

## Release Process

To release a new version of `growthctl` to PyPI:

1. **Bump Version**: Update the version number in `pyproject.toml`.
2. **Update Lockfile**: Run `uv lock` to synchronize the lockfile.
3. **Commit Changes**: Commit the version bump (e.g., `chore: bump version to 0.1.1`).
4. **Push & Tag**:
   ```bash
   git push
   git tag v0.1.1
   git push origin v0.1.1
   ```
   *Note: The GitHub Action will only trigger on tags matching `v*` (e.g., `v0.1.1`). It will NOT trigger on branch pushes.*
