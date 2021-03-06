import pytest

from voucher_selection.server.config import (
    DBConfig,
    ServerConfig,
    create_db_config,
    create_server_config,
)


def test_create_db_config_error_require_db_password():
    with pytest.raises(ValueError, match="Missing"):
        create_db_config(env={})


def test_create_db_config_ok_defaults():
    env = {
        "APP_DB_HOST": "db-host",
        "APP_DB_USERNAME": "db-username",
        "APP_DB_PASSWORD": "db-password",
    }
    db = create_db_config(env)
    assert db == DBConfig(
        username="db-username",
        password="db-password",
        host="db-host",
        port=5432,
        database="voucher_selection",
        table="orders",
    )


def test_create_db_config_ok_overload():
    env = {
        "APP_SERVER_HOST": "server.localhost",
        "APP_SERVER_PORT": 80,
        "APP_DB_HOST": "db.localhost",
        "APP_DB_PORT": 5678,
        "APP_DB_PASSWORD": "db-password",
        "APP_DB_USERNAME": "db-username",
        "APP_DB_DATABASE": "db-database",
        "APP_DB_TABLE": "db-table",
    }
    db = create_db_config(env)
    assert db == DBConfig(
        password="db-password",
        host="db.localhost",
        port=5678,
        username="db-username",
        database="db-database",
        table="db-table",
    )


def test_create_server_config_ok_defaults():
    env = {}
    server = create_server_config(env)
    assert server == ServerConfig(host="0.0.0.0", port=8080)


def test_create_server_config_ok_overload():
    env = {
        "APP_SERVER_HOST": "server.localhost",
        "APP_SERVER_PORT": 80,
    }
    server = create_server_config(env)
    assert server == ServerConfig(host="server.localhost", port=80)
