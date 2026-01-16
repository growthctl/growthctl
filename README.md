![growthctl logo](docs/website/static/img/logo_readme.svg)


# growthctl

[![standard-readme compliant](https://img.shields.io/badge/readme%20style-standard-brightgreen.svg?style=flat-square)](https://github.com/RichardLitt/standard-readme)
[![PyPI version](https://badge.fury.io/py/growthctl.svg)](https://badge.fury.io/py/growthctl)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Project Status: Active – The project has reached a stable, usable state and is being actively developed.](https://www.repostatus.org/badges/latest/active.svg)](https://www.repostatus.org/#active)

> Marketing as Code CLI for managing ad campaigns declaratively using YAML and Git.
>
> **Note**: This project is currently in active development. APIs and configuration schemas are subject to change.

Plan and apply campaign changes safely with Terraform-style dry runs. Version control your ad strategy and collaborate using standard Git workflows. Manage Meta (Facebook/Instagram) ads with built-in provider support.

![growthctl demo](docs/website/static/img/terminal-demo.svg)

## Table of Contents

- [Install](#install)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)

## Install

Install using uv (recommended):

```bash
uv tool install growthctl
```

Install using pipx:

```bash
pipx install growthctl
```

Or using pip:

```bash
pip install growthctl
```

## Usage

Define your campaign in `campaign.yaml`:

```yaml
version: "1.0"
campaigns:
  - id: summer-sale
    name: Summer Sale 2026
    objective: OUTCOME_SALES
    status: ACTIVE
    ad_sets:
      - id: us-audience
        name: US Audience
        status: ACTIVE
        budget_daily: 5000
        targeting:
          locations: ["US"]
          age_min: 25
          age_max: 54
```

Preview and apply changes:

```bash
# Preview changes
growthctl plan campaign.yaml

# Apply to live
growthctl apply campaign.yaml
```

## Contributing

See [the contributing file](CONTRIBUTING.md) for details.

## License

[MIT](LICENSE) © growthctl contributors

## Contact

For questions or feedback, please reach out to [growthctl@gmail.com](mailto:growthctl@gmail.com).
