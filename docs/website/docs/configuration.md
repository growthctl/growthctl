---
sidebar_position: 4
---

# Configuration

Complete reference for the campaign YAML schema.

## Schema Overview

```yaml
version: "1.0"
campaigns:
  - id: string           # Unique identifier
    name: string         # Display name
    objective: string    # Campaign objective
    status: string       # ACTIVE or PAUSED
    ad_sets:
      - id: string
        name: string
        status: string
        budget_daily: number
        targeting:
          locations: [string]
          age_min: number
          age_max: number
          interests: [string]
```

## Fields Reference

### MarketingPlan

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `version` | string | Yes | Schema version (currently "1.0") |
| `campaigns` | array | Yes | List of campaigns |

### Campaign

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | Yes | Unique identifier for the campaign |
| `name` | string | Yes | Display name |
| `objective` | string | Yes | Campaign objective |
| `status` | string | Yes | `ACTIVE` or `PAUSED` |
| `ad_sets` | array | Yes | List of ad sets |

**Objectives:**
- `OUTCOME_SALES` - Conversions and sales
- `OUTCOME_TRAFFIC` - Website traffic
- `OUTCOME_AWARENESS` - Brand awareness

### AdSet

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | Yes | Unique identifier |
| `name` | string | Yes | Display name |
| `status` | string | Yes | `ACTIVE` or `PAUSED` |
| `budget_daily` | number | Yes | Daily budget in account currency |
| `targeting` | object | Yes | Targeting configuration |

### Targeting

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `locations` | array | Yes | - | List of country codes |
| `age_min` | number | No | 18 | Minimum age |
| `age_max` | number | No | 65 | Maximum age |
| `interests` | array | No | [] | List of interests |

## Complete Example

```yaml
version: "1.0"
campaigns:
  - id: summer-sale-2025
    name: Summer Sale 2025
    objective: OUTCOME_SALES
    status: ACTIVE
    ad_sets:
      - id: us-millennials
        name: US Millennials
        status: ACTIVE
        budget_daily: 100.00
        targeting:
          locations: ["US"]
          age_min: 25
          age_max: 40
          interests: ["online shopping", "fashion", "deals"]
      
      - id: canada-broad
        name: Canada Broad
        status: ACTIVE
        budget_daily: 50.00
        targeting:
          locations: ["CA"]
          age_min: 18
          age_max: 65
          interests: []

  - id: brand-awareness-q1
    name: Brand Awareness Q1
    objective: OUTCOME_AWARENESS
    status: PAUSED
    ad_sets:
      - id: global-reach
        name: Global Reach
        status: PAUSED
        budget_daily: 200.00
        targeting:
          locations: ["US", "CA", "GB", "AU"]
          age_min: 18
          age_max: 54
```

## Validation

growthctl validates your YAML against the schema before any operation. Common validation errors:

```bash
# Missing required field
Validation Error: field required: 'objective'

# Invalid status value
Validation Error: value is not a valid enumeration member: 'active'
# Fix: Use 'ACTIVE' (uppercase)

# Invalid objective
Validation Error: value is not a valid enumeration member: 'SALES'
# Fix: Use 'OUTCOME_SALES'
```
