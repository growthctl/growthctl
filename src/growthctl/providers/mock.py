from typing import Any

from rich.console import Console

from .base import MarketingProvider


class MockProvider(MarketingProvider):
    def __init__(self):
        self.console = Console()
        # Simulate remote state:
        # Campaign exists, but has different Ad Sets (Drift!)
        self._db = {
            "summer_promo_2026": {
                "id": "summer_promo_2026",
                "real_id": "real_campaign_123",
                "name": "2026 Summer Sale",
                "objective": "OUTCOME_SALES",
                "status": "PAUSED",
                "ad_sets": {
                    "summer_seoul_2030": {
                        "id": "summer_seoul_2030",
                        "real_id": "real_adset_123",
                        "name": "Seoul 20-30 Targeting",
                        "status": "PAUSED",
                        "budget_daily": 15000,  # Remote is cheaper (15k vs 30k)
                        "targeting": {
                            "locations": ["Seoul"],
                            "age_min": 20,
                            "age_max": 30,
                            "interests": ["SaaS"],
                        },
                    }
                    # "summer_busan_broad" is missing in Remote!
                },
            }
        }

    def get_campaign(self, campaign_id: str) -> dict[str, Any] | None:
        return self._db.get(campaign_id)

    def get_all_campaigns(self) -> list[dict[str, Any]]:
        return list(self._db.values())

    def create_campaign(self, campaign_data: dict[str, Any]) -> str:
        c_id = campaign_data.get("id", "unknown")
        # Convert list of adsets to dict for mock storage
        ad_sets_list = campaign_data.pop("ad_sets", [])
        campaign_data["ad_sets"] = {a["id"]: a for a in ad_sets_list}

        self._db[c_id] = campaign_data
        self.console.print(
            f"[bold magenta][Remote][/bold magenta] Created campaign: {c_id} with {len(ad_sets_list)} ad sets"
        )
        return str(c_id)

    def update_campaign(self, campaign_id: str, campaign_data: dict[str, Any]) -> bool:
        if campaign_id in self._db:
            # Simple mock update
            self._db[campaign_id].update(campaign_data)
            self.console.print(
                f"[bold magenta][Remote][/bold magenta] Updated campaign: {campaign_id}"
            )
            return True
        return False
