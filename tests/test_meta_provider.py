import os
from unittest.mock import MagicMock, patch

import pytest

from growthctl.providers.meta import MetaProvider


@pytest.fixture
def mock_meta_env():
    with patch.dict(
        os.environ,
        {
            "META_ACCESS_TOKEN": "fake_token",
            "META_APP_ID": "fake_app_id",
            "META_APP_SECRET": "fake_app_secret",
            "META_AD_ACCOUNT_ID": "fake_account_id",
        },
    ):
        yield


@patch("growthctl.providers.meta.FacebookAdsApi")
@patch("growthctl.providers.meta.AdAccount")
def test_meta_provider_init(mock_ad_account, mock_api, mock_meta_env):
    provider = MetaProvider()
    mock_api.init.assert_called_once_with(
        "fake_app_id", "fake_app_secret", "fake_token"
    )
    mock_ad_account.assert_called_once_with("act_fake_account_id")
    assert provider.ad_account_id == "fake_account_id"


@patch("growthctl.providers.meta.FacebookAdsApi")
@patch("growthctl.providers.meta.AdAccount")
def test_meta_provider_search_campaigns_by_id(mock_ad_account, mock_api, mock_meta_env):
    provider = MetaProvider()

    with patch("growthctl.providers.meta.FbCampaign") as mock_fb_campaign:
        mock_instance = mock_fb_campaign.return_value
        mock_instance.api_get.return_value = mock_instance

        results = provider._search_campaigns("12345")

        mock_fb_campaign.assert_called_with("12345")
        assert len(results) == 1
        assert results[0] == mock_instance


@patch("growthctl.providers.meta.FacebookAdsApi")
@patch("growthctl.providers.meta.AdAccount")
def test_meta_provider_get_campaign_not_found(mock_ad_account, mock_api, mock_meta_env):
    provider = MetaProvider()
    provider.account.get_campaigns.return_value = []

    with patch.object(provider, "_search_campaigns", return_value=[]):
        result = provider.get_campaign("non_existent")
        assert result is None


@patch("growthctl.providers.meta.FacebookAdsApi")
@patch("growthctl.providers.meta.AdAccount")
def test_meta_provider_process_campaign(mock_ad_account, mock_api, mock_meta_env):
    provider = MetaProvider()

    mock_campaign = MagicMock()
    mock_campaign.get.side_effect = lambda k, default=None: {
        "id": "c123",
        "name": "Campaign 1",
    }.get(k, default)
    mock_campaign.__getitem__.side_effect = lambda k: {
        "id": "c123",
        "name": "Campaign 1",
        "objective": "OUTCOME_SALES",
        "status": "PAUSED",
    }[k]

    mock_ad_set = MagicMock()
    mock_ad_set.get.side_effect = lambda k, default=None: {
        "id": "as123",
        "name": "AdSet 1",
        "status": "PAUSED",
        "daily_budget": "1000",
        "targeting": {"age_min": 20, "geo_locations": {"countries": ["US"]}},
    }.get(k, default)

    mock_campaign.get_ad_sets.return_value = [mock_ad_set]

    result = provider._process_campaign(mock_campaign)

    assert result is not None
    assert result["id"] == "Campaign 1"
    assert result["real_id"] == "c123"
    assert result["ad_sets"]["as123"]["budget_daily"] == 1000
    assert result["ad_sets"]["as123"]["targeting"]["locations"] == ["US"]
