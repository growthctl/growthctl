from growthctl.providers.mock import MockProvider


def test_mock_provider_get_all():
    provider = MockProvider()
    campaigns = provider.get_all_campaigns()
    assert len(campaigns) > 0
    assert campaigns[0]["id"] == "summer_promo_2026"


def test_mock_provider_create():
    provider = MockProvider()
    data = {
        "id": "new_campaign",
        "name": "New Campaign",
        "objective": "OUTCOME_SALES",
        "status": "ACTIVE",
        "ad_sets": [
            {
                "id": "adset_1",
                "name": "AdSet 1",
                "status": "ACTIVE",
                "budget_daily": 10000,
                "targeting": {"locations": ["US"], "age_min": 18, "age_max": 65},
            }
        ],
    }
    c_id = provider.create_campaign(data)
    assert c_id == "new_campaign"
    assert provider.get_campaign("new_campaign") is not None


def test_mock_provider_update_success():
    provider = MockProvider()
    result = provider.update_campaign("summer_promo_2026", {"status": "ACTIVE"})
    assert result is True
    campaign = provider.get_campaign("summer_promo_2026")
    assert campaign is not None
    assert campaign["status"] == "ACTIVE"


def test_mock_provider_update_not_found():
    provider = MockProvider()
    result = provider.update_campaign("non_existent", {})
    assert result is False
