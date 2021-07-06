import os
from dataclasses import dataclass, field
from typing import Any, Dict


def _get_required(env, name: str):
    val = env.get(name)
    if not val:
        raise ValueError(f"Missing env var: '{name}'")
    return val


@dataclass(frozen=True)
class ServerConfig:
    host: str = "0.0.0.0"
    port: int = 8080


@dataclass(frozen=True)
class DBConfig:
    username: str
    password: str = field(repr=False)  # hide this field from repr
    host: str
    port: int = 5432
    database: str = "voucher_selection"
    table: str = "orders"

    @property
    def url(self) -> str:
        cred = f"{self.username}:{self.password}"
        return f"postgresql://{cred}@{self.host}:{self.port}/{self.database}"


def create_server_config(env: Dict[str, Any] = os.environ) -> ServerConfig:
    config = ServerConfig(
        host=env.get("APP_SERVER_HOST", ServerConfig.host),
        port=int(env.get("APP_SERVER_PORT", ServerConfig.port)),
    )

    return config


def create_db_config(env: Dict[str, Any] = os.environ) -> DBConfig:
    config = DBConfig(
        username=_get_required(env, "APP_DB_USERNAME"),
        password=_get_required(env, "APP_DB_PASSWORD"),
        host=_get_required(env, "APP_DB_HOST"),
        port=int(env.get("APP_DB_PORT", DBConfig.port)),
        database=env.get("APP_DB_DATABASE", DBConfig.database),
        table=env.get("APP_DB_TABLE", DBConfig.table),
    )
    return config
