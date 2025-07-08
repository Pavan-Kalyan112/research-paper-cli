import subprocess
import pytest


def run_cli_command(*args):
    """Run the CLI command using Poetry and return the result."""
    result = subprocess.run(
        ["poetry", "run", "python", "-m", "pubmed_fetcher.cli", *args],
        capture_output=True,
        text=True
    )
    return result


def test_basic_query_runs():
    """Check if the CLI runs successfully with a basic query."""
    result = run_cli_command("covid vaccine")
    assert result.returncode == 0
    assert "Paper" in result.stdout


def test_output_contains_expected_keywords():
    """Check that the output has expected fields like Title, Authors, Abstract."""
    result = run_cli_command("covid vaccine")
    assert "Authors:" in result.stdout
    assert "Abstract:" in result.stdout


def test_empty_query_does_not_crash():
    """Ensure that providing an empty query does not crash the CLI."""
    result = run_cli_command("")
    assert result.returncode == 0
    # Even with empty input, we expect some safe output or help message
    assert "Please enter a search query" in result.stdout or "Paper" not in result.stdout


@pytest.mark.skip(reason="LLM summary feature not implemented or stable yet")
def test_query_with_llm_flag():
    """Test CLI with LLM flag enabled (skipped if not implemented)."""
    result = run_cli_command("covid vaccine", "--llm")
    assert result.returncode == 0
    assert "Summary:" in result.stdout
