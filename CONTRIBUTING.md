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

We use a "Click-to-Release" workflow powered by GitHub Actions.

1. Go to the **[Actions](https://github.com/growthctl/growthctl/actions)** tab in the repository.
2. Select the **Release** workflow on the left sidebar.
3. Click **Run workflow**.
4. Enter the new version number (e.g., `0.1.2`).
5. Click **Run workflow**.

The automated system will:
- Bump the version in `pyproject.toml`
- Update the lockfile
- Commit and tag the release
- Build and publish to PyPI
- Push the new commit and tag back to the `main` branch

