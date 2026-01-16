---
sidebar_position: 5
---

# Providers

growthctl supports multiple ad platforms through a provider system.

## Available Providers

| Provider | Status | Platforms |
|----------|--------|-----------|
| Meta | ✅ Available | Facebook, Instagram |
| Mock | ✅ Available | Testing/Development |
| Google Ads | 🚧 Planned | Google Search, Display, YouTube |
| TikTok | 🚧 Planned | TikTok |

## Meta Provider

### Setup

1. **Create a Meta App**
   - Go to [Meta for Developers](https://developers.facebook.com/)
   - Create a new app with "Business" type
   - Add the Marketing API product

2. **Get Access Token**
   - Navigate to your app's Marketing API settings
   - Generate a System User access token
   - Grant the token `ads_management` and `ads_read` permissions

3. **Configure growthctl**
   ```bash
   export META_ACCESS_TOKEN="your-access-token"
   ```

### Permissions Required

| Permission | Description |
|------------|-------------|
| `ads_management` | Create, edit, and delete campaigns |
| `ads_read` | Read campaign data (for plan/import) |

### Rate Limits

Meta's Marketing API has rate limits. growthctl handles these automatically with exponential backoff, but for large accounts:

- Spread bulk operations across time
- Use `plan` to preview before `apply`
- Monitor your app's API usage in Meta Business Suite

## Mock Provider

The Mock provider is perfect for:
- Learning growthctl without real credentials
- Testing CI/CD pipelines
- Developing new features

### Usage

Simply don't set any provider credentials:

```bash
# No META_ACCESS_TOKEN = mock mode
growthctl plan campaign.yaml
```

The mock provider simulates a remote state that you can plan and apply against.

## Creating Custom Providers

Providers implement a simple interface:

```python
from providers.base import MarketingProvider

class CustomProvider(MarketingProvider):
    def get_campaign(self, campaign_id: str) -> dict | None:
        """Fetch campaign from remote."""
        pass
    
    def create_campaign(self, campaign_data: dict) -> str:
        """Create a new campaign. Returns the new ID."""
        pass
    
    def update_campaign(self, campaign_id: str, campaign_data: dict) -> bool:
        """Update an existing campaign. Returns success status."""
        pass
```

See `providers/meta.py` for a complete implementation example.
