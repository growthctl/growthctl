from abc import ABC, abstractmethod
from typing import Any


class MarketingProvider(ABC):
    @abstractmethod
    def get_campaign(self, campaign_id: str) -> dict[str, Any] | None:
        """Fetch current state of a campaign from the remote platform."""
        pass

    @abstractmethod
    def get_all_campaigns(self) -> list[dict[str, Any]]:
        """Fetch all campaigns from the remote platform."""
        pass

    @abstractmethod
    def create_campaign(self, campaign_data: dict[str, Any]) -> str:
        """Create a new campaign."""
        pass

    @abstractmethod
    def update_campaign(self, campaign_id: str, campaign_data: dict[str, Any]) -> bool:
        """Update an existing campaign."""
        pass
