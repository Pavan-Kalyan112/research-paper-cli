import subprocess
import os
from pathlib import Path

# Define the project root path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
CLI_COMMAND = "poetry run pubmed-cli"

def run_command(command):
    """Helper to run a command in the project directory."""
    result = subprocess.run(
        command,
        shell=True,
        capture_output=True,
        text=True,
        cwd=PROJECT_ROOT,
        encoding="utf-8",     # <-- ADD THIS
        errors="replace"      # <-- ADD THIS to avoid crashing
    )
    return result


def test_basic_search():
    """Test a basic PubMed search command."""
    cmd = f'{CLI_COMMAND} "covid vaccine" --limit 1'
    result = run_command(cmd)
    assert result.returncode == 0
    assert "Paper" in result.stdout or "Title" in result.stdout


def test_csv_output():
    """Test saving results to CSV."""
    output_file = PROJECT_ROOT / "test_output.csv"
    if output_file.exists():
        os.remove(output_file)

    cmd = f'{CLI_COMMAND} "covid vaccine" --file test_output --format csv --limit 1'
    result = run_command(cmd)
    assert result.returncode == 0
    assert output_file.exists()

    output_file.unlink()


def test_pdf_output():
    """Test saving results to PDF."""
    output_file = PROJECT_ROOT / "test_output.pdf"
    if output_file.exists():
        os.remove(output_file)

    cmd = f'{CLI_COMMAND} "covid vaccine" --file test_output --format pdf --limit 1'
    result = run_command(cmd)
    assert result.returncode == 0
    assert output_file.exists()

    output_file.unlink()


def test_markdown_output():
    """Test saving results to Markdown."""
    output_file = PROJECT_ROOT / "test_output.md"
    if output_file.exists():
        os.remove(output_file)

    cmd = f'{CLI_COMMAND} "covid vaccine" --file test_output --format md --limit 1'
    result = run_command(cmd)
    assert result.returncode == 0
    assert output_file.exists()

    output_file.unlink()


def test_download_json():
    """Test raw JSON download option."""
    json_file = PROJECT_ROOT / "test_data.json"
    if json_file.exists():
        os.remove(json_file)

    cmd = f'{CLI_COMMAND} "covid vaccine" --download --file test_data'
    result = run_command(cmd)
    assert result.returncode == 0
    assert json_file.exists()

    json_file.unlink()


def test_debug_flag():
    """Test debug flag output."""
    cmd = f'{CLI_COMMAND} "covid vaccine" --debug --limit 1'
    result = run_command(cmd)
    assert result.returncode == 0
    assert "Searching PubMed" in result.stdout or "Summary" in result.stdout


def test_filter_keyword():
    """Test filtering papers by keyword."""
    cmd = f'{CLI_COMMAND} "covid vaccine" --filter-keyword vaccine --limit 2'
    result = run_command(cmd)
    assert result.returncode == 0
    assert "Paper" in result.stdout or "Title" in result.stdout


def test_llm_summary():
    """Test LLM summarization option."""
    cmd = f'{CLI_COMMAND} "covid vaccine" --llm --limit 1'
    result = run_command(cmd)
    assert result.returncode == 0
    assert "Summary" in result.stdout


def test_missing_filename_for_download():
    """Test missing --file when using --download."""
    cmd = f'{CLI_COMMAND} "covid vaccine" --download'
    result = run_command(cmd)
    assert "Please specify a filename" in result.stdout
