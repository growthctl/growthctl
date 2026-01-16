import os
import sys
from typing import Optional, Dict, Any, List
from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.campaign import Campaign as FbCampaign
from facebook_business.adobjects.adset import AdSet as FbAdSet
from .base import MarketingProvider


class MetaProvider(MarketingProvider):
    def __init__(self):
        self.access_token = os.environ.get("META_ACCESS_TOKEN")
        self.app_id = os.environ.get("META_APP_ID")
        self.app_secret = os.environ.get("META_APP_SECRET")
        self.ad_account_id = os.environ.get("META_AD_ACCOUNT_ID")

        if not self.access_token:
            raise ValueError("META_ACCESS_TOKEN environment variable is required.")

        try:
            FacebookAdsApi.init(self.app_id, self.app_secret, self.access_token)
            if self.ad_account_id:
                self.account = AdAccount(f"act_{self.ad_account_id}")
        except Exception as e:
            raise ConnectionError(f"Failed to initialize Meta API: {e}")

    def _get_campaign_by_name(self, name_id: str) -> Optional[FbCampaign]:
        if not hasattr(self, "account"):
            return None
        params = {
            "filtering": [{"field": "name", "operator": "CONTAIN", "value": name_id}],
            "fields": [FbCampaign.Field.id, FbCampaign.Field.name],
        }
        campaigns = self.account.get_campaigns(params=params)
        return campaigns[0] if campaigns else None

    def get_campaign(self, campaign_id: str) -> Optional[Dict[str, Any]]:
        if not hasattr(self, "account"):
            raise ValueError("META_AD_ACCOUNT_ID is required.")

        try:
            fb_campaign = self._get_campaign_by_name(campaign_id)
            if not fb_campaign:
                return None

            fb_campaign.remote_read(
                fields=[
                    FbCampaign.Field.name,
                    FbCampaign.Field.objective,
                    FbCampaign.Field.status,
                ]
            )

            ad_sets = fb_campaign.get_ad_sets(
                fields=[
                    FbAdSet.Field.id,
                    FbAdSet.Field.name,
                    FbAdSet.Field.status,
                    FbAdSet.Field.daily_budget,
                    FbAdSet.Field.targeting,
                ]
            )

            mapped_ad_sets = {}
            for ad_set in ad_sets:
                budget = int(ad_set.get(FbAdSet.Field.daily_budget, 0))
                targeting_raw = ad_set.get(FbAdSet.Field.targeting, {})

                geo = targeting_raw.get("geo_locations", {})
                locations = []
                if "cities" in geo:
                    locations = [city.get("name") for city in geo["cities"]]
                elif "countries" in geo:
                    locations = geo["countries"]

                key = ad_set.get(FbAdSet.Field.name)
                mapped_ad_sets[key] = {
                    "id": key,
                    "real_id": ad_set.get(FbAdSet.Field.id),
                    "name": key,
                    "status": ad_set.get(FbAdSet.Field.status),
                    "budget_daily": budget,
                    "targeting": {
                        "locations": locations,
                        "age_min": targeting_raw.get("age_min", 18),
                        "age_max": targeting_raw.get("age_max", 65),
                        "interests": [],
                    },
                }

            return {
                "id": campaign_id,
                "real_id": fb_campaign[FbCampaign.Field.id],
                "name": fb_campaign[FbCampaign.Field.name],
                "objective": fb_campaign[FbCampaign.Field.objective],
                "status": fb_campaign[FbCampaign.Field.status],
                "ad_sets": mapped_ad_sets,
            }
        except Exception as e:
            # print(f"[Meta API Error] {e}")
            return None

    def create_campaign(self, campaign_data: Dict[str, Any]) -> str:
        print(f"   [Meta] Creating Campaign: {campaign_data['name']}...")

        # 1. Create Campaign
        # We use explicit string keys to avoid SDK constant missing issues
        params = {
            "name": campaign_data["name"],
            "objective": campaign_data["objective"],
            "status": campaign_data["status"],
            "special_ad_categories": ["NONE"],
            "buying_type": "AUCTION",
            # Critical Fix: Explicitly disable Ad Set Budget Sharing (CBO)
            "is_adset_budget_sharing_enabled": False,
        }

        try:
            created_campaign = self.account.create_campaign(params=params)
            campaign_id = created_campaign[FbCampaign.Field.id]
            print(f"   [Meta] Campaign Created! ID: {campaign_id}")
        except Exception as e:
            print(f"[Error] Failed to create campaign: {e}")
            raise e

        # 2. Create Ad Sets
        ad_sets_list = campaign_data.get("ad_sets", [])
        if isinstance(ad_sets_list, dict):
            ad_sets_list = ad_sets_list.values()

        for ad_set_data in ad_sets_list:
            self._create_ad_set(campaign_id, ad_set_data)

        return campaign_id

    def _create_ad_set(self, campaign_id: str, ad_set_data: Dict[str, Any]):
        print(f"   [Meta] Creating AdSet: {ad_set_data['name']}...")

        targeting = {
            "age_min": ad_set_data["targeting"]["age_min"],
            "age_max": ad_set_data["targeting"]["age_max"],
            # Fix: Explicitly disable Advantage+ Audience automation
            "targeting_automation": {
                "advantage_audience": 0  # 0 = Off (Manual Targeting), 1 = On
            },
        }

        locs = ad_set_data["targeting"]["locations"]
        if locs:
            # Safe default for MVP
            targeting["geo_locations"] = {"countries": ["KR"]}

        params = {
            FbAdSet.Field.name: ad_set_data["name"],
            FbAdSet.Field.campaign_id: campaign_id,
            FbAdSet.Field.daily_budget: ad_set_data["budget_daily"],
            FbAdSet.Field.status: ad_set_data["status"],
            FbAdSet.Field.targeting: targeting,
            FbAdSet.Field.billing_event: "IMPRESSIONS",
            FbAdSet.Field.optimization_goal: "REACH",
            FbAdSet.Field.bid_strategy: "LOWEST_COST_WITHOUT_CAP",
        }

        try:
            created_ad_set = self.account.create_ad_set(params=params)
            print(f"      -> Created AdSet ID: {created_ad_set[FbAdSet.Field.id]}")
        except Exception as e:
            print(f"      [Error] Failed to create ad set: {e}")

    def update_campaign(self, campaign_id: str, campaign_data: Dict[str, Any]) -> bool:
        fb_campaign = self._get_campaign_by_name(campaign_id)
        if not fb_campaign:
            return False
        real_c_id = fb_campaign[FbCampaign.Field.id]

        print(f"   [Meta] Syncing AdSets for Campaign: {campaign_id} ({real_c_id})...")

        existing_ad_sets = fb_campaign.get_ad_sets(
            fields=[FbAdSet.Field.id, FbAdSet.Field.name]
        )
        remote_map = {ad[FbAdSet.Field.name]: ad for ad in existing_ad_sets}

        local_ad_sets = campaign_data.get("ad_sets", [])
        if isinstance(local_ad_sets, dict):
            local_ad_sets = local_ad_sets.values()
        local_map = {ad["name"]: ad for ad in local_ad_sets}

        for name, data in local_map.items():
            if name not in remote_map:
                self._create_ad_set(real_c_id, data)

        for name, data in local_map.items():
            if name in remote_map:
                remote_ad = remote_map[name]
                self._update_ad_set(remote_ad, data)

        for name, remote_ad in remote_map.items():
            if name not in local_map:
                self._archive_ad_set(remote_ad)

        return True

    def _update_ad_set(self, remote_ad, data: Dict[str, Any]):
        ad_id = remote_ad[FbAdSet.Field.id]
        print(f"   [Meta] Updating AdSet: {data['name']} ({ad_id})...")

        try:
            remote_ad[FbAdSet.Field.daily_budget] = data["budget_daily"]
            remote_ad[FbAdSet.Field.status] = data["status"]
            remote_ad.remote_update()
            print(f"      -> Updated successfully")
        except Exception as e:
            print(f"      [Error] Failed to update: {e}")

    def _archive_ad_set(self, remote_ad):
        ad_name = remote_ad[FbAdSet.Field.name]
        print(f"   [Meta] Archiving AdSet: {ad_name}...")

        try:
            remote_ad[FbAdSet.Field.status] = "ARCHIVED"
            remote_ad.remote_update()
            print(f"      -> Archived successfully")
        except Exception as e:
            print(f"      [Error] Failed to archive: {e}")
