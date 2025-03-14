from aerich import Command  # type: ignore
from onbbu.logger import LogLevel as LogLevel, logger as logger
from tortoise import Model as Model
from typing import Any

class DatabaseManager:
    database_url: str
    command: Command
    models: list[str]
    def __init__(self, database_url: str) -> None: ...
    def register_models(self, model: type[Model]) -> None: ...
    def get_config(self) -> dict[str, Any]: ...
    async def init(self) -> None: ...
    async def migrate(self) -> None: ...
    async def upgrade(self) -> None: ...
    async def downgrade(self, steps: int = 1) -> None: ...
    async def history(self) -> None: ...
    async def create_database(self) -> None: ...
    async def drop_database(self) -> None: ...
    async def reset_database(self) -> None: ...
    async def show_status(self) -> None: ...
    async def apply_all_migrations(self) -> None: ...
    async def rollback_all_migrations(self) -> None: ...
    async def seed_data(self) -> None: ...
    async def close(self) -> None: ...

database: DatabaseManager
