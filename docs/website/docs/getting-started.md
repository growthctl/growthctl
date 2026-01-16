---
sidebar_position: 2
---

# Getting Started

This guide walks you through setting up growthctl and managing your first campaign.

## Prerequisites

- Python 3.10 or higher
- A Meta (Facebook) Business account with Marketing API access

## Installation

```bash
pip install growthctl
```

## Configuration

### Meta Provider Setup

To connect to Meta's Marketing API, set the following environment variable:

```bash
export META_ACCESS_TOKEN="your-access-token"
```

You can get an access token from the [Meta Business Suite](https://business.facebook.com/settings/system-users).

### Mock Mode

If no credentials are set, growthctl runs in mock mode - perfect for testing and learning:

```bash
# No credentials = mock mode
growthctl plan campaign.yaml
```

## Your First Campaign

### 1. Create a Campaign File

Create a file called `campaign.yaml`:

```yaml
version: "1.0"
campaigns:
  - id: my-first-campaign
    name: My First Campaign
    objective: OUTCOME_TRAFFIC
    status: PAUSED
    ad_sets:
      - id: test-audience
        name: Test Audience
        status: PAUSED
        budget_daily: 10.00
        targeting:
          locations: ["US"]
          age_min: 18
          age_max: 65
```

### 2. Preview Changes

Run `plan` to see what would change:

```bash
growthctl plan campaign.yaml
```

Output:
```
╭─ Running Plan for campaign.yaml ─╮
+ Create Campaign: My First Campaign (ID: my-first-campaign)
  + Create AdSet: Test Audience
```

### 3. Apply Changes

When ready, apply to your ad account:

```bash
growthctl apply campaign.yaml
```

You'll be prompted for confirmation before any changes are made to your live account.

## Importing Existing Campaigns

Already have campaigns running? Import them to YAML:

```bash
growthctl import "Summer Sale" --output summer-sale.yaml
```

This creates a YAML file from your existing campaign that you can then version control and manage with growthctl.

## Next Steps

- [CLI Reference](./cli-reference) - Detailed command documentation
- [Configuration](./configuration) - Full YAML schema reference
- [Providers](./providers) - Provider-specific setup guides
