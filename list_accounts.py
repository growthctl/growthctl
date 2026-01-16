import os
import sys
from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.user import User

token = os.environ.get('META_ACCESS_TOKEN')
if not token:
    print("Error: META_ACCESS_TOKEN not set")
    sys.exit(1)

try:
    FacebookAdsApi.init(access_token=token)
    me = User(fbid='me')
    my_accounts = me.get_ad_accounts(fields=['name', 'account_id', 'currency'])
    
    if not my_accounts:
        print("No ad accounts found for this user.")
    else:
        print(f"Found {len(my_accounts)} Ad Account(s):")
        for acc in my_accounts:
            print(f"- {acc['name']} (ID: {acc['account_id']}, Currency: {acc['currency']})")
            
except Exception as e:
    print(f"Error: {e}")
