import pytest
from pydantic import ValidationError

from growthctl.schema import MarketingPlan, Targeting


def test_valid_marketing_plan():
    """Test that a valid plan can be instantiated."""
    data = {
        "version": "1.0",
        "campaigns": [
            {
                "id": "test-id",
                "name": "Test Campaign",
                "objective": "OUTCOME_SALES",
                "status": "ACTIVE",
                "ad_sets": [
                    {
                        "id": "adset-1",
                        "name": "AdSet 1",
                        "status": "PAUSED",
                        "budget_daily": 1000,
                        "targeting": {
                            "locations": ["US"],
                            "age_min": 25,
                            "age_max": 50,
                        },
                    }
                ],
            }
        ],
    }
    plan = MarketingPlan(**data)
    assert plan.version == "1.0"
    assert len(plan.campaigns) == 1
    assert plan.campaigns[0].id == "test-id"


def test_invalid_budget():
    """Test that a negative budget raises ValidationError."""
    data = {
        "version": "1.0",
        "campaigns": [
            {
                "id": "test-id",
                "name": "Test Campaign",
                "objective": "OUTCOME_SALES",
                "ad_sets": [
                    {
                        "id": "adset-1",
                        "name": "AdSet 1",
                        "budget_daily": -500,  # Invalid
                        "targeting": {"locations": ["US"]},
                    }
                ],
            }
        ],
    }
    with pytest.raises(ValidationError):
        MarketingPlan(**data)


def test_invalid_age():
    """Test that invalid age range raises ValidationError."""
    data = {
        "locations": ["US"],
        "age_min": 10,  # Below minimum 13
        "age_max": 65,
    }
    with pytest.raises(ValidationError):
        Targeting(**data)
