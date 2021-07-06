# Showcase: Voucher selection API

Sample project involving data manipulations and REST API serving.


## Quickstart

Install a virtual environment (optional):
```
python -m venv ./venv
source ./venv/bin/activate
```

Install the package and its requirements, run tests
```
make setup
make test
```

Once you have changed the code, you can run linters:
```
make format  # auto-format
make lint    # auto-format and then verify
```

## Configuration

Some commands use environment variables for configuration:
1. Database:
  - `APP_DB_USERNAME` (not set)
  - `APP_DB_PASSWORD` (not set)
  - `APP_DB_HOST` (not set)
  - `APP_DB_PORT` (default value `5432`)
  - `APP_DB_DATABASE` (default value `"voucher_selection"`)
  - `APP_DB_TABLE` (default value `"orders"`)
2. Server:
  - `APP_SERVER_HOST` (default value `"0.0.0.0"`)
  - `APP_SERVER_PORT` (default value `8080`)


## Development steps

### Step 1. Exploratory data cleaning

See [notebooks](notebooks).


### Step 2. Extracting the cleaning code to Python

For this purpose, we organised code as a proper Python package [`voucher_selection`](src/voucher_selection) and tested it (see [tests](src/tests)):
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

### Step 3: Setting up an SQL database for the app
At this step, we added database connectors and created a command to "seed" values to the DB from a file.

### Step 4: Setting up the REST (HTTP) API server connected to SQL
At this step, we implemented the logic of computing segments (on-the-fly, without caching), and exposed it via a FastAPI server (similar to Flask).


## CLI Commands


### Command group: `voucher_selection data`
This command group is supposed to contain project-specific data transformations:
- modular so that can be tested better,
- versioned together with the code,

Ideally, the artifacts (datasets: csv, parquet) should be stored in another registry (not in Git) and be produced in a CI/CD pipeline.


#### Subcommand: `clean`
```
$ voucher_selection data clean --help
Usage: voucher_selection data clean [OPTIONS]

  Clean input raw dataset

Options:
  --input-parquet PATH  Path to the input file in parquet format  [required]
  --output-csv PATH     Path to the output file in csv format  [required]
  --help                Show this message and exit.
```

Turns raw (original) dataframe into a cleaned one. This command needs to be run manually (no CI for now).

Example:

```
$ voucher_selection data clean --input-parquet data/data.parquet --output-csv data/data_clean.csv
Reading input dataset from: data/data.parquet
INFO:/plain/github/mine/case-voucher-selection/src/voucher_selection/data_cleaning.py:Cleaning raw dataset of size: 3068562
Saving output dataset to: data/data_clean.csv
```

Tests:
- data cleaning logic: [tests/test_data_cleaning.py](tests/test_data_cleaning.py)
- CLI: [tests/test_cli.py](tests/test_cli.py)


### Command group: `voucher_selection db`
This command group contains all operations with the database.

> NB: The idea of the data pipeline is that we apply data transformations to immutible data snapshots (pandas `DataFrame`s) and then load them to a PostgreSQL in order to use SQL to compute live aggregations while the REST API is working. This database is read-only and thus fault-tolerant.


## Subcommand: `seed`

Load dataset from a (csv) file to the PostgreSQL.
```
$ voucher_selection db seed --help
Usage: voucher_selection db seed [OPTIONS]

Options:
  --input-csv PATH  Path to the dataset in csv format  [required]
  --help            Show this message and exit.
```

This command requires environment variables setup for the Database (see above).

Example:
```
$ APP_DB_HOST=localhost APP_DB_USERNAME=alice APP_DB_PASSWORD=password voucher_selection db seed --input-csv data/data_clean.csv
Database config: DBConfig(username='alice', host='localhost', port=5432, database='voucher_selection', table='orders')
Creating DB table if not exists...
Loading values to DB from file: data/data_clean.csv
INFO:root:Loading dataset from csv file: data/data_clean.csv
INFO:root:Building the query of 511427 rows
INFO:root:Executing the query
INFO:root:Successfully inserted 511427 rows from data/data_clean.csv
```


### Command group: `voucher_selection api`
This command group contains all operations with the HTTP (REST) API server.

## Subcommand: `run`

```
$ voucher_selection api run --help
Usage: voucher_selection api run [OPTIONS]

Options:
  --help  Show this message and exit.
```

This command requires environment variables setup for the Database and the Server (see above).

Example:
```
APP_DB_HOST=localhost APP_DB_USERNAME=alice APP_DB_PASSWORD=password voucher_selection api run
Database config: DBConfig(username='alice', host='localhost', port=5432, database='voucher_selection', table='orders')
Server config: ServerConfig(host='0.0.0.0', port=8080)
INFO:     Started server process [4139580]
INFO:uvicorn.error:Started server process [4139580]
INFO:     Waiting for application startup.
INFO:uvicorn.error:Waiting for application startup.
INFO:     Application startup complete.
INFO:uvicorn.error:Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8080 (Press CTRL+C to quit)
INFO:uvicorn.error:Uvicorn running on http://0.0.0.0:8080 (Press CTRL+C to quit)

INFO:root:Found 3 distinct voucher values for `WHERE country_code = 'Peru' AND last_order_ts >= (NOW() - INTERVAL '601 days') AND last_order_ts <= (NOW() - INTERVAL '600 days') AND total_orders >= 3 AND total_orders <= 4`: mean=3520
INFO:     127.0.0.1:58910 - "POST /voucher HTTP/1.1" 200 OK
```

To test:
```
$ curl http://0.0.0.0:8080/voucher -X POST -H "Content-type: application/json" -d '{"frequency_segment": "3-4", "recency_segment": "600-601", "country_code": "Peru"}'
{"voucher_amount":3520}
```
