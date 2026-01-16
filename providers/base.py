from abc import ABC, abstractmethod
from typing import Optional, Dict, Any

class MarketingProvider(ABC):
    @abstractmethod
    def get_campaign(self, campaign_id: str) -> Optional[Dict[str, Any]]:
        """Fetch current state of a campaign from the remote platform."""
        pass

    @abstractmethod
    def create_campaign(self, campaign_data: Dict[str, Any]) -> str:
        """Create a new campaign."""
        pass

    @abstractmethod
    def update_campaign(self, campaign_id: str, campaign_data: Dict[str, Any]) -> bool:
        """Update an existing campaign."""
        pass
