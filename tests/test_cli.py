import subprocess
import os
from pathlib import Path

# Root directory of your project
PROJECT_ROOT = Path(__file__).resolve().parent.parent

def run_command(command):
    """Helper to run a command in the project directory."""
    result = subprocess.run(
        command,
        shell=True,
        capture_output=True,
        text=True,
        cwd=PROJECT_ROOT
    )
    return result

def test_basic_search():
    """Test a basic PubMed search command."""
    cmd = 'poetry run pubmed-cli "covid vaccine" --limit 1'
    result = run_command(cmd)
    assert result.returncode == 0
    assert "Paper" in result.stdout or "Title" in result.stdout

def test_csv_output():
    """Test saving results to CSV."""
    output_file = PROJECT_ROOT / "test_output.csv"
    if output_file.exists():
        os.remove(output_file)

    cmd = f'poetry run pubmed-cli "covid vaccine" --file test_output.csv --format csv --limit 1'
    result = run_command(cmd)
    assert result.returncode == 0
    assert output_file.exists()

    # Clean up
    output_file.unlink()

def test_pdf_output():
    """Test saving results to PDF."""
    output_file = PROJECT_ROOT / "test_output.pdf"
    if output_file.exists():
        os.remove(output_file)

    cmd = f'poetry run pubmed-cli "covid vaccine" --file test_output.pdf --format pdf --limit 1'
    result = run_command(cmd)
    assert result.returncode == 0
    assert output_file.exists()

    # Clean up
    output_file.unlink()

def test_markdown_output():
    """Test saving results to Markdown."""
    output_file = PROJECT_ROOT / "test_output.md"
    if output_file.exists():
        os.remove(output_file)

    cmd = f'poetry run pubmed-cli "covid vaccine" --file test_output.md --format md --limit 1'
    result = run_command(cmd)
    assert result.returncode == 0
    assert output_file.exists()

    # Clean up
    output_file.unlink()

def test_download_json():
    """Test raw JSON download option."""
    json_file = PROJECT_ROOT / "test_data.json"
    if json_file.exists():
        os.remove(json_file)

    cmd = f'poetry run pubmed-cli "covid vaccine" --download --file test_data'
    result = run_command(cmd)
    assert result.returncode == 0
    assert json_file.exists()

    # Clean up
    json_file.unlink()

def test_debug_flag_does_not_crash():
    """Test that --debug mode runs without error."""
    cmd = 'poetry run pubmed-cli "covid vaccine" --debug --limit 1'
    result = run_command(cmd)
    assert result.returncode == 0
    assert "Searching for" in result.stdout or "Limit:" in result.stdout
