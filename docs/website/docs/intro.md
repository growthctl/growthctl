---
sidebar_position: 1
---

# Introduction

[![PyPI version](https://badge.fury.io/py/growthctl.svg)](https://badge.fury.io/py/growthctl)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**growthctl** is a CLI tool that brings Infrastructure-as-Code principles to marketing campaign management. Define your ad campaigns in YAML, version control them, and deploy with confidence.

## Why growthctl?

Managing ad campaigns through web UIs is error-prone and doesn't scale:

- **No version control** - Changes are hard to track and rollback
- **No code review** - Team members can't review changes before they go live
- **No automation** - Manual processes lead to human errors
- **No consistency** - Different team members set up campaigns differently

growthctl solves these problems by treating marketing campaigns as code.

## Key Features

- **Declarative YAML** - Define campaigns, ad sets, and targeting in simple YAML files
- **Plan & Apply** - Preview changes before applying them (like Terraform)
- **Import existing** - Import your current campaigns to YAML and start managing them as code
- **Multi-provider** - Support for Meta (Facebook/Instagram) with more platforms coming

## Quick Example

```yaml
version: "1.0"
campaigns:
  - id: summer-sale-2025
    name: Summer Sale 2025
    objective: OUTCOME_SALES
    status: ACTIVE
    ad_sets:
      - id: us-audience
        name: US Audience
        status: ACTIVE
        budget_daily: 50.00
        targeting:
          locations: ["US"]
          age_min: 25
          age_max: 54
          interests: ["online shopping", "fashion"]
```

```bash
# Preview changes
growthctl plan campaign.yaml

# Apply to live
growthctl apply campaign.yaml
```

## Installation

```bash
pip install growthctl
```

Or install from source:

```bash
git clone https://github.com/growthctl/growthctl.git
cd growthctl
pip install -e .
```

## Next Steps

- [Getting Started](./getting-started) - Set up your first campaign
- [CLI Reference](./cli-reference) - Full command documentation
- [Configuration](./configuration) - YAML schema and options
