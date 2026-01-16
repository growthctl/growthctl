import os
import sys
from pathlib import Path
from typing import Annotated

import typer
import yaml
from rich.console import Console
from rich.panel import Panel

from growthctl.providers.meta import MetaProvider
from growthctl.providers.mock import MockProvider
from growthctl.schema import AdSet, Campaign, MarketingPlan, Targeting

app = typer.Typer(help="growthctl - Marketing as Code CLI")
console = Console()

# Select Provider based on env vars
try:
    if os.environ.get("META_ACCESS_TOKEN"):
        provider = MetaProvider()
        console.print("[bold green]Connected to Meta Marketing API[/bold green]")
    else:
        raise ValueError("No token")
except Exception:
    console.print(
        "[dim]Meta credentials not found (META_ACCESS_TOKEN). Using Mock Provider.[/dim]"
    )
    provider = MockProvider()


def load_plan(file_path: Path) -> MarketingPlan:
    if not file_path.exists():
        console.print(f"[red]Error: File {file_path} not found[/red]")
        sys.exit(1)

    with open(file_path) as f:
        try:
            data = yaml.safe_load(f)
            return MarketingPlan(**data)
        except Exception as e:
            console.print(f"[red]Validation Error:[/red] {e}")
            sys.exit(1)


def diff_ad_set(local: dict, remote: dict) -> list:
    changes = []
    if local["budget_daily"] != remote["budget_daily"]:
        changes.append(
            f"  [cyan]budget[/cyan]: {remote['budget_daily']} -> [green]{local['budget_daily']}[/green]"
        )

    loc_local = set(local["targeting"]["locations"])
    loc_remote = set(remote["targeting"]["locations"])

    if loc_local != loc_remote:
        changes.append(
            f"  [cyan]locations[/cyan]: {loc_remote} -> [green]{loc_local}[/green]"
        )

    return changes


@app.command()
def plan(
    file: Annotated[Path, typer.Argument(help="Path to campaign.yaml")],
):
    """
    Dry-run: Compare local configuration with remote state.
    """
    console.print(Panel(f"Running Plan for [bold]{file}[/bold]", style="blue"))
    marketing_plan = load_plan(file)

    for campaign in marketing_plan.campaigns:
        remote_campaign = provider.get_campaign(campaign.id)

        if not remote_campaign:
            console.print(
                f"[green]+ Create Campaign:[/green] {campaign.name} (ID: {campaign.id})"
            )
            for ad_set in campaign.ad_sets:
                console.print(f"  [green]+ Create AdSet:[/green] {ad_set.name}")
            continue

        console.print(f"[bold]Checking Campaign:[/bold] {campaign.name}")

        remote_ad_sets = remote_campaign.get("ad_sets", {})
        # Build lookup maps for matching
        # 1. Match by ID (Preferred, stable)
        remote_by_id = dict(remote_ad_sets.items())
        # 2. Match by Name (Fallback, ambiguous if duplicates)
        remote_by_name = {v["name"]: v for v in remote_ad_sets.values()}

        # Track which remote ad sets have been matched to detect deletions
        matched_remote_ids = set()

        for ad_set in campaign.ad_sets:
            # Try to find matching remote ad set
            remote_ad_set = None

            # Strategy 1: Match by ID
            if ad_set.id in remote_by_id:
                remote_ad_set = remote_by_id[ad_set.id]
            # Strategy 2: Match by Name (if ID match failed)
            elif ad_set.name in remote_by_name:
                remote_ad_set = remote_by_name[ad_set.name]

            if not remote_ad_set:
                console.print(f"  [green]+ Create AdSet:[/green] {ad_set.name} (New)")
            else:
                matched_remote_ids.add(
                    remote_ad_set["real_id"]
                )  # Track matched real ID
                # If we matched by name but IDs differ, we might want to note it, but diff logic handles content
                changes = diff_ad_set(ad_set.model_dump(), remote_ad_set)
                if changes:
                    console.print(f"  [yellow]~ Update AdSet:[/yellow] {ad_set.name}")
                    for change in changes:
                        console.print(f"    {change}")

        # Detect deletions (Remote ad sets that were not matched by any local ad set)
        for _remote_id, remote_ad in remote_ad_sets.items():
            if remote_ad["real_id"] not in matched_remote_ids:
                console.print(
                    f"  [red]- Delete (Archive) AdSet:[/red] {remote_ad['name']}"
                )


@app.command()
def apply(
    file: Annotated[Path, typer.Argument(help="Path to campaign.yaml")],
    force: Annotated[
        bool, typer.Option("--force", "-f", help="Skip confirmation")
    ] = False,
):
    """
    Apply changes to remote.
    """
    console.print(Panel(f"Applying Plan for [bold]{file}[/bold]", style="red"))
    marketing_plan = load_plan(file)

    # Simple prompt
    if not force:
        confirm = typer.confirm(
            "Are you sure you want to apply these changes to the LIVE ad account?"
        )
        if not confirm:
            console.print("[red]Aborted.[/red]")
            raise typer.Abort()

    for campaign in marketing_plan.campaigns:
        remote_campaign = provider.get_campaign(campaign.id)
        local_data = campaign.model_dump()

        if not remote_campaign:
            console.print(f"Creating Campaign: {campaign.name}...")
            provider.create_campaign(local_data)
        else:
            console.print(f"Updating Campaign: {campaign.name}...")
            provider.update_campaign(campaign.id, local_data)

    console.print("[bold green]Apply Complete![/bold green]")


@app.command("import")
def import_campaign(
    campaign_keyword: Annotated[
        str | None, typer.Argument(help="Campaign name or ID to import")
    ] = None,
    output: Annotated[Path, typer.Option(help="Output file path")] = Path(
        "imported_campaign.yaml"
    ),
):
    """
    Import existing campaign from remote and save as YAML.
    """
    if campaign_keyword:
        console.print(
            Panel(
                f"Importing campaign: [bold]{campaign_keyword}[/bold]", style="magenta"
            )
        )
    else:
        console.print(Panel("Importing [bold]ALL[/bold] campaigns", style="magenta"))

    # 1. Fetch from Provider
    if campaign_keyword:
        remote_data = provider.get_campaign(campaign_keyword)
        if not remote_data:
            console.print(f"[red]Campaign not found matching: {campaign_keyword}[/red]")
            sys.exit(1)
        campaigns_data = [remote_data]
        console.print(
            f"[green]Found campaign:[/green] {remote_data['name']} (Real ID: {remote_data.get('real_id', remote_data.get('id'))})"
        )
    else:
        campaigns_data = provider.get_all_campaigns()
        if not campaigns_data:
            console.print("[red]No campaigns found.[/red]")
            sys.exit(1)
        console.print(f"[green]Found {len(campaigns_data)} campaigns.[/green]")
        for c in campaigns_data:
            account_info = ""
            if c.get("account_name"):
                account_info = f" [dim]({c['account_name']})[/dim]"
            console.print(f"  - {c['name']}{account_info}")

    # 2. Convert Dict to Pydantic Models
    campaigns = []

    for remote_data in campaigns_data:
        ad_sets = []
        # Track used IDs to ensure uniqueness in YAML
        seen_ids = set()

        for _ad_set_key, ad_set_data in remote_data["ad_sets"].items():
            t = ad_set_data["targeting"]
            targeting = Targeting(
                locations=t.get("locations") or [],
                age_min=t.get("age_min", 18),
                age_max=t.get("age_max", 65),
                interests=t.get("interests") or [],
            )

            # Use Real ID as YAML ID to ensure uniqueness and stability
            yaml_id = ad_set_data.get("real_id", ad_set_data.get("id"))

            # If somehow real_id is missing or duplicate (unlikely for Meta), fallback
            if yaml_id in seen_ids:
                yaml_id = f"{ad_set_data['name']}_{_ad_set_key}"
            seen_ids.add(yaml_id)

            ad_set = AdSet(
                id=yaml_id,
                name=ad_set_data["name"],
                status=ad_set_data["status"],
                budget_daily=ad_set_data["budget_daily"],
                targeting=targeting,
            )
            ad_sets.append(ad_set)

        campaign = Campaign(
            id=remote_data["real_id"],
            name=remote_data["name"],
            objective=remote_data["objective"],
            status=remote_data["status"],
            ad_sets=ad_sets,
        )
        campaigns.append(campaign)

    plan = MarketingPlan(version="1.0", campaigns=campaigns)

    # 3. Dump to YAML
    with open(output, "w") as f:
        yaml.dump(plan.model_dump(), f, sort_keys=False, allow_unicode=True)

    console.print(f"[bold green]✨ Successfully imported to {output}[/bold green]")
    console.print(f"Now you can run: [dim]python main.py plan {output}[/dim]")


if __name__ == "__main__":
    app()
