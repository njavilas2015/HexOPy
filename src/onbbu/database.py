import importlib
import pkgutil
from types import ModuleType
from typing import Any

from tortoise import Tortoise
from onbbu.logger import LogLevel, logger
from aerich import Command # type: ignore

class DatabaseManager:
    def __init__(self, database_url: str, INSTALLED_APPS: list[str]):
        self.database_url = database_url
        self.model_modules: list[str] = []
        self.INSTALLED_APPS = INSTALLED_APPS

    async def load_models(self) -> None:
        """Dynamically load models from installed applications."""
        for app in self.INSTALLED_APPS:
            model_path: str = f"pkg.{app}.infrastructure.persistence.models"

            try:
                module: ModuleType = importlib.import_module(model_path)

                logger.log(
                    level=LogLevel.INFO,
                    message=f"📦 Base module found: {model_path}",
                    extra_data={},
                )

                if hasattr(module, "__path__"):
                    for _, module_name, _ in pkgutil.iter_modules(module.__path__):
                        full_module_name = f"{model_path}.{module_name}"
                        self.model_modules.append(full_module_name)

                        logger.log(
                            level=LogLevel.INFO,
                            message=f"✅ Loaded model: {full_module_name}",
                            extra_data={},
                        )

            except ModuleNotFoundError as e:
                logger.log(
                    level=LogLevel.INFO,
                    message=f"⚠️ Warning: Could not import {model_path}: {e}",
                    extra_data={},
                )

    def get_config(self):

        tortoise_config: dict[str, Any] = {
            "connections": {
                "default": self.database_url,
            },
            "apps": {
                "models": {
                    "models": self.model_modules,
                    "default_connection": "default",
                },
            },
        }

        return tortoise_config

    async def init(self) -> None:
        """Initialize the database and apply the migrations."""

        await self.load_models()

        if not self.model_modules:
            logger.log(
                level=LogLevel.ERROR,
                message="❌ No models found. Check Check `INSTALLED_APPS`.",
                extra_data={},
            )

            return

        logger.log(
            level=LogLevel.INFO,
            message=f"🔄 Initializing Tortoise with models: {self.model_modules}",
            extra_data={},
        )

        await Tortoise.init(config=self.get_config())

        self.command = Command(tortoise_config=self.get_config())

        logger.log(
            level=LogLevel.INFO,
            message="✅ Connected database. Generating schematics...",
            extra_data={},
        )

        await Tortoise.generate_schemas(safe=True)

        logger.log(
            level=LogLevel.INFO,
            message="🎉 Schemes generated successfully.",
            extra_data={},
        )

        await Tortoise.close_connections()

    async def migrate(self) -> None:
        """Generate new migrations."""

        await self.command.init()

        await self.command.migrate()

    async def upgrade(self) -> None:
        """Apply pending migrations."""

        await self.command.init()

        await self.command.upgrade()

    async def downgrade(self, steps: int = 1) -> None:
        """Revert migrations (default: 1 step)."""

        await self.command.init()

        await self.command.downgrade(steps, delete=False)

    async def history(self) -> None:
        """Show the history of applied migrations."""

        await self.command.init()

        await self.command.history()

    async def create_database(self) -> None:
        """Create the database if it does not exist."""

        logger.log(
            level=LogLevel.INFO,
            message=f"🛠️ Creating database...",
            extra_data={},
        )

        await Tortoise.init(
            db_url=self.database_url, modules={"models": self.model_modules}
        )

        await Tortoise.generate_schemas()

        await Tortoise.close_connections()

    async def drop_database(self) -> None:
        """Delete all tables from the database."""

        logger.log(
            level=LogLevel.INFO,
            message="🗑️ Dropping database...",
            extra_data={},
        )

        await Tortoise.init(config=self.get_config())

        await Tortoise.generate_schemas(safe=False)

        await Tortoise.close_connections()

    async def reset_database(self) -> None:
        """Delete and recreate the database."""

        logger.log(
            level=LogLevel.INFO,
            message=f"🔄 Resetting database...",
            extra_data={},
        )

        await self.drop_database()

        await self.create_database()

    async def show_status(self) -> None:
        """Show the current status of the database."""

        await self.command.init()

        applied = await self.command.history()

        logger.log(
            level=LogLevel.INFO,
            message=f"📜 Applied migrations:\n{applied}",
            extra_data={},
        )

    async def apply_all_migrations(self) -> None:
        """Generate and apply all migrations in a single step."""

        logger.log(
            level=LogLevel.INFO,
            message=f"🚀 Applying all migrations...",
            extra_data={},
        )

        await self.migrate()

        await self.upgrade()

    async def rollback_all_migrations(self) -> None:
        """Revert all migrations to the initial state."""

        logger.log(
            level=LogLevel.INFO,
            message=f"⏪ Rolling back all migrations...",
            extra_data={},
        )

        await self.command.init()

        while True:
            try:

                await self.command.downgrade(1, delete=False)

            except Exception:

                logger.log(
                    level=LogLevel.INFO,
                    message=f"✅ No more migrations to revert.",
                    extra_data={},
                )

                break

    async def seed_data(self) -> None:
        """Insert initial data into the database."""

        logger.log(
            level=LogLevel.INFO,
            message=f"🌱 Seeding initial data...",
            extra_data={},
        )

        await Tortoise.init(config=self.get_config())

        await Tortoise.close_connections()

    async def close(self) -> None:
        """Close the database connections."""

        logger.log(
            level=LogLevel.INFO,
            message=f"🔌 Closing database connections...",
            extra_data={},
        )

        await Tortoise.close_connections()

        logger.log(
            level=LogLevel.INFO,
            message=f"✅ Database connections closed..",
            extra_data={},
        )
