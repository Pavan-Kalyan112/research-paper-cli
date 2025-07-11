import subprocess
import os
import sys
import pytest
from unittest.mock import patch

CLI_COMMAND = ["poetry", "run", "pubmed-fetcher"]

def run_cli(args=None):
    args = args or []

    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    env["LC_ALL"] = "C.UTF-8"  # optional but helps in some edge cases

    result = subprocess.run(
        CLI_COMMAND + args,
        capture_output=True,
        text=True,
        env=env,
        encoding="utf-8",  # <--- force encoding explicitly
        errors="replace"   # <--- avoids crash on undecodable characters
    )
    return result


def test_cli_help_output():
    result = run_cli(["--help"])
    assert result.returncode == 0
    assert "usage" in result.stdout.lower()

def test_cli_invalid_flag():
    result = run_cli(["--invalid"])
    assert result.returncode != 0
    assert "error" in result.stderr.lower()

def test_cli_no_arguments():
    # Simulate user typing "exit" when prompted
    with patch("builtins.input", return_value="exit"):
        result = subprocess.run(
            CLI_COMMAND,
            input="exit\n",
            text=True,
            capture_output=True
        )
        assert result.returncode == 0 or "session ended" in result.stdout.lower()

@pytest.mark.skipif("CI" in os.environ, reason="Avoid network/API tests in CI")
def test_cli_basic_query_run():
    with patch("builtins.input", return_value="exit"):
        result = subprocess.run(
            CLI_COMMAND + ["--query", "hair loss", "--limit", "1"],
            input="exit\n",
            text=True,
            capture_output=True
        )
        assert result.returncode == 0 or "pubmed id" in result.stdout.lower()
