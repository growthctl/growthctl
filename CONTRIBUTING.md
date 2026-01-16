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

## Pull Requests

1. Fork the repo and create your branch from `main`.
2. Ensure `uv run pre-commit run --all-files` passes.
3. If you changed documentation, ensure it builds locally.
4. Open a PR!
