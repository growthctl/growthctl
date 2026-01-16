import os
import sys

from facebook_business.adobjects.user import User
from facebook_business.api import FacebookAdsApi
from rich.console import Console

console = Console()

token = os.environ.get("META_ACCESS_TOKEN")
if not token:
    console.print("[red]Error:[/red] META_ACCESS_TOKEN not set")
    sys.exit(1)

try:
    FacebookAdsApi.init(access_token=token)
    me = User(fbid="me")
    my_accounts = me.get_ad_accounts(fields=["name", "account_id", "currency"])

    if not my_accounts:
        console.print("[yellow]No ad accounts found for this user.[/yellow]")
    else:
        console.print(f"[green]Found {len(my_accounts)} Ad Account(s):[/green]")
        for acc in my_accounts:
            console.print(
                f"  - {acc['name']} (ID: {acc['account_id']}, Currency: {acc['currency']})"
            )

except Exception as e:
    console.print(f"[red]Error:[/red] {e}")
