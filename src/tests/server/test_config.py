import pytest

from voucher_selection.server.config import (
    Config,
    DBConfig,
    ServerConfig,
    create_config,
)


def test_create_config_error_require_db_password():
    with pytest.raises(KeyError):
        create_config(env={})


def test_create_config_ok_defaults():
    env = {"DB_USERNAME": "db-username", "DB_PASSWORD": "db-password"}
    config = create_config(env)
    assert config == Config(
        server=ServerConfig(host="0.0.0.0", port=8080),
        db=DBConfig(
            username="db-username",
            password="db-password",
            host="localhost",
            port=5432,
            database="voucher_selection",
            table="orders",
        ),
    )


def test_create_config_ok_overload():
    env = {
        "SERVER_HOST": "server.localhost",
        "SERVER_PORT": 80,
        "DB_HOST": "db.localhost",
        "DB_PORT": 5678,
        "DB_PASSWORD": "db-password",
        "DB_USERNAME": "db-username",
        "DB_DATABASE": "db-database",
        "DB_TABLE": "db-table",
    }
    config = create_config(env)
    assert config == Config(
        server=ServerConfig(host="server.localhost", port=80),
        db=DBConfig(
            password="db-password",
            host="db.localhost",
            port=5678,
            username="db-username",
            database="db-database",
            table="db-table",
        ),
    )
