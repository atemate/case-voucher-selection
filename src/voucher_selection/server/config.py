import os
from dataclasses import dataclass
from typing import Any, Dict


@dataclass(frozen=True)
class ServerConfig:
    host: str = "0.0.0.0"
    port: int = 8080


@dataclass(frozen=True)
class DBConfig:
    username: str
    password: str
    host: str = "localhost"
    port: int = 5432
    database: str = "voucher_selection"
    table: str = "orders"

    @property
    def url(self) -> str:
        cred = f"{self.user}:{self.password}"
        return f"postgresql://{cred}@{self.host}:{self.port}/{self.database}"


@dataclass(frozen=True)
class Config:
    server: ServerConfig
    db: DBConfig


def create_config(env: Dict[str, Any] = os.environ) -> Config:
    server = ServerConfig(
        host=env.get("SERVER_HOST", ServerConfig.host),
        port=int(env.get("SERVER_PORT", ServerConfig.port)),
    )
    db = DBConfig(
        username=env["DB_USERNAME"],
        password=env["DB_PASSWORD"],
        host=env.get("DB_HOST", DBConfig.host),
        port=int(env.get("DB_PORT", DBConfig.port)),
        database=env.get("DB_DATABASE", DBConfig.database),
        table=env.get("DB_TABLE", DBConfig.table),
    )
    return Config(server=server, db=db)
