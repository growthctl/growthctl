import yaml
from typer.testing import CliRunner

from growthctl.main import app

runner = CliRunner()


def test_cli_help():
    """Verify that the CLI help command works."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "growthctl - Marketing as Code CLI" in result.output


def test_cli_plan_help():
    """Verify that the plan subcommand help works."""
    result = runner.invoke(app, ["plan", "--help"])
    assert result.exit_code == 0
    assert "Dry-run: Compare local configuration with remote state." in result.output


def test_cli_import_all(tmp_path):
    output_file = tmp_path / "imported.yaml"
    result = runner.invoke(app, ["import", "--output", str(output_file)])
    assert result.exit_code == 0
    assert "Importing ALL campaigns" in result.output
    assert "Successfully imported to" in result.output
    assert output_file.exists()

    with open(output_file) as f:
        data = yaml.safe_load(f)
        assert "campaigns" in data
        assert len(data["campaigns"]) > 0


def test_cli_import_specific(tmp_path):
    output_file = tmp_path / "specific.yaml"
    result = runner.invoke(
        app, ["import", "summer_promo_2026", "--output", str(output_file)]
    )
    assert result.exit_code == 0
    assert "Importing campaign: summer_promo_2026" in result.output
    assert "Found campaign: 2026 Summer Sale" in result.output
    assert output_file.exists()


def test_cli_import_not_found():
    result = runner.invoke(app, ["import", "non_existent_campaign"])
    assert result.exit_code == 1
    assert "Campaign not found matching: non_existent_campaign" in result.output


def test_cli_load_plan_not_found():
    result = runner.invoke(app, ["plan", "non_existent.yaml"])
    assert result.exit_code == 1
    assert "Error: File non_existent.yaml not found" in result.output


def test_cli_load_plan_invalid_yaml(tmp_path):
    invalid_file = tmp_path / "invalid.yaml"
    with open(invalid_file, "w") as f:
        f.write("invalid: [yaml")
    result = runner.invoke(app, ["plan", str(invalid_file)])
    assert result.exit_code == 1
    assert "Validation Error:" in result.output


def test_cli_load_plan_validation_error(tmp_path):
    invalid_file = tmp_path / "invalid.yaml"
    with open(invalid_file, "w") as f:
        f.write("version: '1.0'\ncampaigns: [{'id': 123}]")
    result = runner.invoke(app, ["plan", str(invalid_file)])
    assert result.exit_code == 1
    assert "Validation Error:" in result.output


def test_cli_apply_abort(tmp_path):
    campaign_file = tmp_path / "campaign.yaml"
    with open(campaign_file, "w") as f:
        yaml.dump({"version": "1.0", "campaigns": []}, f)
    result = runner.invoke(app, ["apply", str(campaign_file)], input="n\n")
    assert result.exit_code == 1
    assert "Aborted." in result.output
