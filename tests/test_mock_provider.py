import pytest
import yaml
from typer.testing import CliRunner

from growthctl.main import app

runner = CliRunner()


@pytest.fixture
def temp_campaign_file(tmp_path):
    """Create a temporary campaign.yaml file."""
    content = {
        "version": "1.0",
        "campaigns": [
            {
                "id": "summer_promo_2026",
                "name": "2026 Summer Sale",
                "objective": "OUTCOME_SALES",
                "status": "PAUSED",
                "ad_sets": [
                    {
                        "id": "summer_seoul_2030",
                        "name": "Seoul 20-30 Targeting",
                        "status": "PAUSED",
                        "budget_daily": 30000,
                        "targeting": {
                            "locations": ["Seoul"],
                            "age_min": 20,
                            "age_max": 30,
                        },
                    }
                ],
            }
        ],
    }
    file_path = tmp_path / "campaign.yaml"
    with open(file_path, "w") as f:
        yaml.dump(content, f)
    return file_path


def test_plan_with_mock_provider(temp_campaign_file):
    """Test 'plan' command using MockProvider (default when no token)."""
    # MockProvider matches 'summer_promo_2026' by default in its _db
    result = runner.invoke(app, ["plan", str(temp_campaign_file)])
    assert result.exit_code == 0
    assert "Running Plan" in result.output
    assert "Checking Campaign: 2026 Summer Sale" in result.output


def test_apply_with_mock_provider(temp_campaign_file):
    """Test 'apply' command using MockProvider."""
    # Using --force to skip confirmation
    result = runner.invoke(app, ["apply", str(temp_campaign_file)], input="y\n")
    # Actually 'apply' uses typer.confirm, but we can pass --force or mock input

    # Try with --force
    result = runner.invoke(app, ["apply", str(temp_campaign_file), "--force"])
    assert result.exit_code == 0
    assert "Applying Plan" in result.output
    assert "Apply Complete!" in result.output
