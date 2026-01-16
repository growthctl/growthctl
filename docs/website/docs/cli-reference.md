---
sidebar_position: 3
---

# CLI Reference

Complete reference for all growthctl commands.

## Global Options

```bash
growthctl --help
```

## Commands

### plan

Dry-run: Compare local configuration with remote state.

```bash
growthctl plan <file>
```

**Arguments:**
- `file` - Path to campaign YAML file (required)

**Example:**
```bash
growthctl plan campaign.yaml
```

**Output:**
```
╭─ Running Plan for campaign.yaml ─╮
Checking Campaign: Summer Sale 2026
  ~ Update AdSet: US Audience
    budget: 50.0 -> 75.0
    locations: {'US'} -> {'US', 'CA'}
```

The plan command shows:
- `+` Create - New resources to be created
- `~` Update - Existing resources with changes
- `-` Delete - Resources to be archived/deleted

---

### apply

Apply changes to remote ad platform.

```bash
growthctl apply <file> [--force]
```

**Arguments:**
- `file` - Path to campaign YAML file (required)

**Options:**
- `--force, -f` - Skip confirmation prompt

**Example:**
```bash
# With confirmation prompt
growthctl apply campaign.yaml

# Skip confirmation
growthctl apply campaign.yaml --force
```

:::warning
The `apply` command makes live changes to your ad account. Always run `plan` first to review changes.
:::

---

### import

Import existing campaign(s) from remote and save as YAML.

```bash
growthctl import [campaign_keyword] [--output <file>]
```

**Arguments:**
- `campaign_keyword` - Campaign name or ID to search for (optional). If omitted, imports **all campaigns**.

**Options:**
- `--output` - Output file path (default: `imported_campaign.yaml`)

**Example:**
```bash
# Import ALL campaigns
growthctl import --output all-campaigns.yaml

# Import by name
growthctl import "Summer Sale" --output summer-sale.yaml

# Import by ID
growthctl import "123456789" --output campaign.yaml
```

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `META_ACCESS_TOKEN` | Meta Marketing API access token | Yes (for Meta provider) |
| `META_AD_ACCOUNT_ID` | Meta Ad Account ID (without `act_` prefix) | Required for `create` operations |
| `META_APP_ID` | Meta App ID | Optional |
| `META_APP_SECRET` | Meta App Secret | Optional |

## Exit Codes

| Code | Description |
|------|-------------|
| 0 | Success |
| 1 | Error (file not found, validation error, API error) |
