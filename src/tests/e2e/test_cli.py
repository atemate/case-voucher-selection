import tempfile
from pathlib import Path

from typer.testing import CliRunner

from voucher_selection.cli import app


runner = CliRunner()


def test_cli_data_clean_ok(raw_data_path: Path):
    input_file = raw_data_path
    output_file = Path(tempfile.mktemp())
    assert input_file.exists()
    assert not output_file.exists()
    result = runner.invoke(
        app,
        [
            "data",
            "clean",
            "--input-parquet",
            input_file,
            "--output-csv",
            output_file,
        ],
    )
    assert result.exit_code == 0, (result, result.output)
    assert output_file.exists()


def test_cli_data_clean_invalid_missing_input_missing_output():
    result = runner.invoke(app, ["data", "clean"])
    assert result.exit_code == 2
    assert "Usage:" in result.output


def test_cli_data_clean_invalid_missing_input():
    result = runner.invoke(app, ["data", "clean", "--output-csv", "/tmp/out.csv"])
    assert result.exit_code == 2
    assert "Usage:" in result.output


def test_cli_data_clean_invalid_missing_output():
    result = runner.invoke(
        app, ["data", "clean", "--input-parquet", "/tmp/input.parquet"]
    )
    assert result.exit_code == 2
    assert "Usage:" in result.output


def test_cli_data_clean_invalid_input_not_exists():
    input_file = Path(tempfile.mktemp())
    output_file = Path(tempfile.mktemp())
    output_file.write_text("")
    result = runner.invoke(
        app,
        [
            "data",
            "clean",
            "--input-parquet",
            input_file,
            "--output-csv",
            output_file,
        ],
    )
    assert result.exit_code == 1
    assert "Input dataset not found:" in str(result.exception)


def test_cli_data_clean_invalid_output_exists():
    input_file = Path(tempfile.mktemp())
    output_file = Path(tempfile.mktemp())
    input_file.write_text("")
    output_file.write_text("")
    result = runner.invoke(
        app,
        [
            "data",
            "clean",
            "--input-parquet",
            input_file,
            "--output-csv",
            output_file,
        ],
    )
    assert result.exit_code == 1
    assert "Output dataset already exists:" in str(result.exception)


def test_cli_db_seed_invalid_file_not_found():
    input_file = Path(tempfile.mktemp())
    assert not input_file.exists()

    result = runner.invoke(
        app,
        [
            "db",
            "seed",
            "--input-csv",
            input_file,
        ],
    )
    assert result.exit_code == 1
    assert "Input dataset not found" in str(result.exception)


def test_cli_db_seed_invalid_missing_env_vars(monkeypatch):
    monkeypatch.delenv("APP_DB_HOST", raising=False)
    monkeypatch.delenv("APP_DB_USERNAME", raising=False)
    monkeypatch.delenv("APP_DB_PASSWORD", raising=False)
    input_file = Path(tempfile.mktemp())
    input_file.write_text("")

    result = runner.invoke(
        app,
        [
            "db",
            "seed",
            "--input-csv",
            input_file,
        ],
    )
    assert result.exit_code == 1
    assert "Missing env var" in str(result.exception)
