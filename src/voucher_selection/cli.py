import logging
from pathlib import Path

import pandas as pd
import typer

from .data_cleaning import clean_orders_raw


app = typer.Typer()
data_app = typer.Typer()


app.add_typer(data_app, name="data")


def _setup_logger(level=logging.INFO):
    for handler in logging.root.handlers:
        logging.root.removeHandler(handler)
    logging.basicConfig(level=level)


@app.callback()
def main(verbose: bool = False):
    """ Voucher selection app """
    level = logging.DEBUG if verbose else logging.INFO
    _setup_logger(level)


@data_app.command("clean")
def data_clean(
    input_parquet: Path = typer.Option(
        ..., help="Path to the input file in parquet format"
    ),
    output_csv: Path = typer.Option(..., help="Path to the output file in csv format"),
):
    """ Clean input raw dataset"""
    typer.echo(f"Reading input dataset from: {input_parquet}")
    if not input_parquet.exists():
        raise ValueError(f"Input dataset not found: {input_parquet}")
    if output_csv.exists():
        raise ValueError(f"Output dataset already exists: {output_csv}")
    df = pd.read_parquet(input_parquet, engine="fastparquet")
    df = clean_orders_raw(df)
    typer.echo(f"Saving output dataset to: {output_csv}")
    df.to_csv(output_csv, index=False)
