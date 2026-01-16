# growthctl

Marketing as Code - Manage ad campaigns like infrastructure.

## Installation

```bash
pip install growthctl
```

## Quick Start

```yaml
# campaign.yaml
version: "1.0"
campaigns:
  - id: summer-sale
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
```

```bash
# Preview changes
growthctl plan campaign.yaml

# Apply to live
growthctl apply campaign.yaml

# Import existing campaign
growthctl import "My Campaign" --output my-campaign.yaml
```

## Configuration

Set your Meta access token:

```bash
export META_ACCESS_TOKEN="your-token"
```

## License

MIT
