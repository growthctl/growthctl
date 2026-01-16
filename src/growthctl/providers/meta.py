import os
from typing import Any

from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.adset import AdSet as FbAdSet
from facebook_business.adobjects.campaign import Campaign as FbCampaign
from facebook_business.adobjects.user import User
from facebook_business.api import FacebookAdsApi
from facebook_business.exceptions import FacebookRequestError
from rich.console import Console

from growthctl.utils import match_ad_set

from .base import MarketingProvider


class MetaProvider(MarketingProvider):
    def __init__(self):
        self.console = Console()
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
            raise ConnectionError(f"Failed to initialize Meta API: {e}") from e

    def _search_campaigns(
        self, name_or_id: str, account: AdAccount | None = None
    ) -> list[FbCampaign]:
        target_account = account or getattr(self, "account", None)
        if not target_account:
            return []

        if name_or_id.isdigit():
            # If it's digits, try to get by ID directly first
            try:
                c = FbCampaign(name_or_id).api_get(
                    fields=[FbCampaign.Field.id, FbCampaign.Field.name]
                )
                # We need to verify this campaign belongs to the account if account is specified
                # But remote_read on ID might just work if we have access.
                return [c]
            except FacebookRequestError:
                pass

        params = {
            "filtering": [
                {"field": "name", "operator": "CONTAIN", "value": name_or_id}
            ],
            "fields": [FbCampaign.Field.id, FbCampaign.Field.name],
        }

        campaigns = target_account.get_campaigns(params=params)
        return list(campaigns)

    def _get_campaign_by_name(
        self, name_id: str, account: AdAccount | None = None
    ) -> FbCampaign | None:
        # Deprecated wrapper for backward compatibility if needed,
        # but better to update callsites.
        # This now returns the first match if available, maintaining old behavior
        # but we should upgrade get_campaign to handle multiple.
        results = self._search_campaigns(name_id, account)
        return results[0] if results else None

    def _find_account_with_campaign(self, campaign_id: str) -> AdAccount | None:
        try:
            me = User(fbid="me")
            my_accounts = me.get_ad_accounts(
                fields=[AdAccount.Field.name, AdAccount.Field.account_id]
            )
        except FacebookRequestError as e:
            self.console.print(f"[dim]Warning: Could not list ad accounts: {e}[/dim]")
            return None

        found_accounts = []
        for acct in my_accounts:
            c = self._get_campaign_by_name(campaign_id, account=acct)
            if c:
                found_accounts.append((acct, c))

        if not found_accounts:
            return None

        if len(found_accounts) > 1:
            msg = "Multiple campaigns found. Please set META_AD_ACCOUNT_ID:\n"
            for acct, _c in found_accounts:
                msg += f" - {acct[AdAccount.Field.name]} ({acct[AdAccount.Field.account_id]})\n"
            raise ValueError(msg)

        acct, c = found_accounts[0]
        return acct

    def _process_campaign(self, fb_campaign: FbCampaign) -> dict[str, Any] | None:
        try:
            fb_campaign.api_get(
                fields=[
                    FbCampaign.Field.name,
                    FbCampaign.Field.objective,
                    FbCampaign.Field.status,
                ]
            )

            ad_sets = list(
                fb_campaign.get_ad_sets(
                    fields=[
                        FbAdSet.Field.id,
                        FbAdSet.Field.name,
                        FbAdSet.Field.status,
                        FbAdSet.Field.daily_budget,
                        FbAdSet.Field.targeting,
                    ]
                )
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

                # Use real ID as the key to prevent overwriting duplicate names
                key = ad_set.get(FbAdSet.Field.id)
                mapped_ad_sets[key] = {
                    "id": key,
                    "real_id": ad_set.get(FbAdSet.Field.id),
                    "name": ad_set.get(FbAdSet.Field.name),
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
                "id": fb_campaign[FbCampaign.Field.name],
                "real_id": fb_campaign[FbCampaign.Field.id],
                "name": fb_campaign[FbCampaign.Field.name],
                "objective": fb_campaign[FbCampaign.Field.objective],
                "status": fb_campaign[FbCampaign.Field.status],
                "ad_sets": mapped_ad_sets,
            }
        except FacebookRequestError as e:
            self.console.print(
                f"[Meta API Error] Failed to process campaign {fb_campaign.get(FbCampaign.Field.id, 'unknown')}: {e}"
            )
            return None

    def get_campaign(self, campaign_id: str) -> dict[str, Any] | None:
        if hasattr(self, "account"):
            return self._find_campaign_in_account(campaign_id, self.account)

        try:
            me = User(fbid="me")
            my_accounts = me.get_ad_accounts(
                fields=[AdAccount.Field.name, AdAccount.Field.account_id]
            )
            accounts = list(my_accounts)

            if not accounts:
                raise ValueError("No ad accounts found for this user.")

            for account in accounts:
                result = self._find_campaign_in_account(campaign_id, account)
                if result:
                    return result

            return None
        except ValueError:
            raise
        except FacebookRequestError:
            return None

    def _find_campaign_in_account(
        self, campaign_id: str, account: AdAccount
    ) -> dict[str, Any] | None:
        try:
            candidates = self._search_campaigns(campaign_id, account)
            if not candidates:
                return None

            if len(candidates) > 1:
                exact_matches = [
                    c
                    for c in candidates
                    if c[FbCampaign.Field.name] == campaign_id
                    or c[FbCampaign.Field.id] == campaign_id
                ]
                if len(exact_matches) == 1:
                    fb_campaign = exact_matches[0]
                else:
                    msg = "Multiple campaigns found. Please provide exact ID:\n"
                    for c in candidates:
                        msg += f" - {c[FbCampaign.Field.name]} (ID: {c[FbCampaign.Field.id]})\n"
                    raise ValueError(msg)
            else:
                fb_campaign = candidates[0]

            return self._process_campaign(fb_campaign)
        except ValueError:
            raise
        except FacebookRequestError:
            return None

    def get_all_campaigns(self) -> list[dict[str, Any]]:
        if hasattr(self, "account"):
            return self._get_campaigns_from_account(self.account)

        try:
            me = User(fbid="me")
            my_accounts = me.get_ad_accounts(
                fields=[AdAccount.Field.name, AdAccount.Field.account_id]
            )
            accounts = list(my_accounts)

            if not accounts:
                raise ValueError("No ad accounts found for this user.")

            results = []
            for account in accounts:
                account_name = account.get(AdAccount.Field.name, "Unknown")
                account_id = account.get(AdAccount.Field.account_id)
                self.console.print(
                    f"[dim]Fetching campaigns from account: {account_name} ({account_id})[/dim]"
                )

                campaigns = self._get_campaigns_from_account(
                    account, account_name=account_name, account_id=account_id
                )
                results.extend(campaigns)

            return results
        except ValueError:
            raise
        except FacebookRequestError as e:
            raise ValueError(f"Failed to fetch ad accounts: {e}") from e

    def _get_campaigns_from_account(
        self,
        account: AdAccount,
        account_name: str | None = None,
        account_id: str | None = None,
    ) -> list[dict[str, Any]]:
        params = {
            "fields": [FbCampaign.Field.id, FbCampaign.Field.name],
        }
        campaigns = account.get_campaigns(params=params)

        results = []
        for c in campaigns:
            data = self._process_campaign(c)
            if data:
                if account_name:
                    data["account_name"] = account_name
                if account_id:
                    data["account_id"] = account_id
                results.append(data)

        return results

    def create_campaign(self, campaign_data: dict[str, Any]) -> str:
        if not hasattr(self, "account"):
            raise ValueError("META_AD_ACCOUNT_ID is required to create a new campaign.")

        self.console.print(
            f"   [bold blue][Meta][/bold blue] Creating Campaign: {campaign_data['name']}..."
        )

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
            self.console.print(
                f"   [bold blue][Meta][/bold blue] Campaign Created! ID: {campaign_id}"
            )
        except FacebookRequestError as e:
            self.console.print(f"[red][Error][/red] Failed to create campaign: {e}")
            raise

        # 2. Create Ad Sets
        ad_sets_list = campaign_data.get("ad_sets", [])
        if isinstance(ad_sets_list, dict):
            ad_sets_list = ad_sets_list.values()

        for ad_set_data in ad_sets_list:
            self._create_ad_set(campaign_id, ad_set_data)

        return campaign_id

    def _create_ad_set(self, campaign_id: str, ad_set_data: dict[str, Any]):
        self.console.print(
            f"   [bold blue][Meta][/bold blue] Creating AdSet: {ad_set_data['name']}..."
        )

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
            # Use actual locations from YAML config
            targeting["geo_locations"] = {"countries": locs}

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
            self.console.print(
                f"      -> Created AdSet ID: {created_ad_set[FbAdSet.Field.id]}"
            )
        except FacebookRequestError as e:
            self.console.print(f"      [red][Error][/red] Failed to create ad set: {e}")

    def update_campaign(self, campaign_id: str, campaign_data: dict[str, Any]) -> bool:
        fb_campaign = self._get_campaign_by_name(campaign_id)
        if not fb_campaign:
            return False
        real_c_id = fb_campaign[FbCampaign.Field.id]

        if fb_campaign[FbCampaign.Field.status] != campaign_data["status"]:
            self.console.print(
                f"   [bold blue][Meta][/bold blue] Updating Campaign Status: {fb_campaign[FbCampaign.Field.status]} -> {campaign_data['status']}"
            )
            try:
                fb_campaign[FbCampaign.Field.status] = campaign_data["status"]
                fb_campaign.remote_update()
            except FacebookRequestError as e:
                self.console.print(
                    f"      [red][Error][/red] Failed to update campaign status: {e}"
                )

        self.console.print(
            f"   [bold blue][Meta][/bold blue] Syncing AdSets for Campaign: {campaign_id} ({real_c_id})..."
        )

        existing_ad_sets = fb_campaign.get_ad_sets(
            fields=[FbAdSet.Field.id, FbAdSet.Field.name]
        )
        remote_by_id = {ad[FbAdSet.Field.id]: ad for ad in existing_ad_sets}
        remote_by_name = {ad[FbAdSet.Field.name]: ad for ad in existing_ad_sets}

        local_ad_sets_list = campaign_data.get("ad_sets", [])
        if isinstance(local_ad_sets_list, dict):
            local_ad_sets_list = local_ad_sets_list.values()

        matched_remote_ids = set()

        for data in local_ad_sets_list:
            local_id = data["id"]
            local_name = data["name"]

            remote_ad = match_ad_set(local_id, local_name, remote_by_id, remote_by_name)

            if not remote_ad:
                self._create_ad_set(real_c_id, data)
            else:
                matched_remote_ids.add(remote_ad[FbAdSet.Field.id])
                self._update_ad_set(remote_ad, data)

        for remote_id, remote_ad in remote_by_id.items():
            if remote_id not in matched_remote_ids:
                self._archive_ad_set(remote_ad)

        return True

    def _update_ad_set(self, remote_ad, data: dict[str, Any]):
        ad_id = remote_ad[FbAdSet.Field.id]
        self.console.print(
            f"   [bold blue][Meta][/bold blue] Updating AdSet: {data['name']} ({ad_id})..."
        )

        try:
            remote_ad[FbAdSet.Field.daily_budget] = data["budget_daily"]
            remote_ad[FbAdSet.Field.status] = data["status"]
            remote_ad.remote_update()
            self.console.print("      -> Updated successfully")
        except FacebookRequestError as e:
            self.console.print(f"      [red][Error][/red] Failed to update: {e}")

    def _archive_ad_set(self, remote_ad):
        ad_name = remote_ad[FbAdSet.Field.name]
        self.console.print(
            f"   [bold blue][Meta][/bold blue] Archiving AdSet: {ad_name}..."
        )

        try:
            remote_ad[FbAdSet.Field.status] = "ARCHIVED"
            remote_ad.remote_update()
            self.console.print("      -> Archived successfully")
        except FacebookRequestError as e:
            self.console.print(f"      [red][Error][/red] Failed to archive: {e}")
