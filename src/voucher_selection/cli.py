import logging
import os
from pathlib import Path

import pandas as pd
import typer

from .data_cleaning import clean_orders_raw
from .server.config import create_db_config, create_server_config
from .server.db import DBManager, get_connection


app = typer.Typer()
data_app = typer.Typer()
db_app = typer.Typer()


app.add_typer(data_app, name="data")
app.add_typer(db_app, name="db")


def _setup_logger(level=logging.INFO):
    for handler in logging.root.handlers:
        logging.root.removeHandler(handler)
    logging.basicConfig(level=level)


@app.callback()
def app_callback(verbose: bool = False):
    """Voucher selection app"""
    level = logging.DEBUG if verbose else logging.INFO
    _setup_logger(level)


@data_app.command("clean")
def data_clean(
    input_parquet: Path = typer.Option(
        ..., help="Path to the input file in parquet format"
    ),
    output_csv: Path = typer.Option(..., help="Path to the output file in csv format"),
):
    """Clean input raw dataset"""
    typer.echo(f"Reading input dataset from: {input_parquet}")
    if not input_parquet.exists():
        raise ValueError(f"Input dataset not found: {input_parquet}")
    if output_csv.exists():
        raise ValueError(f"Output dataset already exists: {output_csv}")
    df = pd.read_parquet(input_parquet, engine="fastparquet")
    df = clean_orders_raw(df)
    typer.echo(f"Saving output dataset to: {output_csv}")
    df.to_csv(output_csv, index=False)


# server_host: str = typer.Option("0.0.0.0", envvar="SERVER_HOST"),
# server_port: int = typer.Option(8080, envvar="SERVER_PORT"),


@db_app.command("seed")
def db_seed(
    input_csv: Path = typer.Option(..., help="Path to the dataset in csv format")
):
    if not input_csv.is_file():
        raise ValueError(f"Input dataset not found: {input_csv}")

    db_config = create_db_config()
    typer.echo(f"Database config: {db_config}")

    conn = get_connection(db_config)
    db = DBManager(conn)
    typer.echo(f"Creating DB table if not exists...")
    db.create_table()
    typer.echo(f"Loading values to DB from file: {input_csv}")
    db.insert_from_csv(input_csv)
