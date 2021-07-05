# Showcase: Voucher selection API

Sample project involving data manipulations and REST API serving.


## Quickstart

```
python -m venv ./venv
make setup  # install package and dependencies
make test   # run python tests
```

Once you have changed the code, you can run linters:
```
make format  # auto-format
make lint    # auto-format and then verify
```


## Development steps

### Step 1. Exploratory data cleaning

see [notebooks](notebooks).


### Step 2. Extracting the cleaning code to Python

For this purpose, we organised code as a proper Python package [`voucher_selection`](src/voucher_selection) and tested it (see [tests](tests)):
```
$ voucher_selection
Usage: voucher_selection [OPTIONS] COMMAND [ARGS]...

  Voucher selection app

Options:
  --verbose / --no-verbose        [default: False]
  --install-completion [bash|zsh|fish|powershell|pwsh]
                                  Install completion for the specified shell.
  --show-completion [bash|zsh|fish|powershell|pwsh]
                                  Show completion for the specified shell, to
                                  copy it or customize the installation.

  --help                          Show this message and exit.

Commands:
  data
```

#### Commands

1. Command: `voucher_selection data clean ...`

Turns raw (original) dataframe into a cleaned one. This command needs to be run manually (no CI for now).

Example:

```
$ voucher_selection data clean --input-parquet data/orders_raw.parquet  --output-csv data/orders_cleaned.csv
Reading input dataset from: data/orders_raw.parquet
INFO:/plain/github/mine/case-voucher-selection/src/voucher_selection/data_cleaning.py:Cleaning raw dataset of size: 3068562
Saving output dataset to: data/orders_cleaned.csv
```

Tests:
- logic: [tests/test_data_cleaning.py](tests/test_data_cleaning.py)
- cli: [tests/test_cli.py](tests/test_cli.py)
