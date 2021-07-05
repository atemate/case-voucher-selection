import tempfile
from pathlib import Path

from typer.testing import CliRunner

from voucher_selection.cli import app


runner = CliRunner()


def test_cli_ok(all_orders_raw_path: Path):
    input_file = all_orders_raw_path
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


def test_cli_invalid_missing_input_missing_output():
    result = runner.invoke(app, ["data", "clean"])
    assert result.exit_code == 2
    assert "Usage:" in result.output


def test_cli_invalid_missing_input():
    result = runner.invoke(app, ["data", "clean", "--output-csv", "/tmp/out.csv"])
    assert result.exit_code == 2
    assert "Usage:" in result.output


def test_cli_invalid_missing_output():
    result = runner.invoke(
        app, ["data", "clean", "--input-parquet", "/tmp/input.parquet"]
    )
    assert result.exit_code == 2
    assert "Usage:" in result.output


def test_cli_invalid_input_not_exists():
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


def test_cli_invalid_output_exists():
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
