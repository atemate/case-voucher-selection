from .config import Config
from .db import PostgresConnection


class VoucherSelectionService:
    def __init__(self, config: Config):
        self._db = PostgresConnection(config.db)

    async def __aenter__(self):
        await self._db_conn.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self._db_conn.__aexit__(exc_type, exc, tb)
