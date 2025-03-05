import importlib
import pkgutil
from types import ModuleType

from tortoise import Tortoise
from onbbu.logger import LogLevel, logger
from aerich import Command

class DatabaseManager:
    def __init__(self, database_url, INSTALLED_APPS: list[str]):
        self.database_url = database_url
        self.model_modules: list[str] = []
        self.INSTALLED_APPS = INSTALLED_APPS

    async def load_models(self) -> None:
        """Dynamically load models from installed applications."""
        for app in self.INSTALLED_APPS:
            model_path: str = f"pkg.{app}.infrastructure.persistence.models"

            try:
                module: ModuleType = importlib.import_module(model_path)
                logger.log(LogLevel.INFO, f"📦 Base module found: {model_path}")

                if hasattr(module, "__path__"):
                    for _, module_name, _ in pkgutil.iter_modules(module.__path__):
                        full_module_name = f"{model_path}.{module_name}"
                        self.model_modules.append(full_module_name)
                        logger.log(
                            LogLevel.INFO, f"✅ Loaded model: {full_module_name}"
                        )

            except ModuleNotFoundError as e:
                logger.log(
                    LogLevel.WARNING, f"⚠️ Warning: Could not import {model_path}: {e}"
                )

    async def init(self) -> None:
        """Initialize the database and apply the migrations."""

        await self.load_models()

        if not self.model_modules:
            logger.log(
                level=LogLevel.ERROR,
                message="❌ No models found. Check Check `INSTALLED_APPS`.",
            )

            return

        logger.log(
            level=LogLevel.INFO,
            message=f"🔄 Initializing Tortoise with models: {self.model_modules}",
        )

        tortoise_config = {
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

        await Tortoise.init(config=tortoise_config)

        self.command = Command(tortoise_config=tortoise_config)

        logger.log(LogLevel.INFO, "✅ Connected database. Generating schematics...")

        await Tortoise.generate_schemas()

        logger.log(LogLevel.INFO, "🎉 Schemes generated successfully.")

        await Tortoise.close_connections()

    async def migrate(self) -> None:
        """Generate new migrations."""

        await self.command.init()

        await self.command.migrate()

    async def upgrade(self) -> None:
        """Apply pending migrations."""

        await self.command.init()

        await self.command.upgrade()

    async def downgrade(self, steps=1) -> None:
        """Revert migrations (default: 1 step)."""

        await self.command.init()

        await self.command.downgrade(steps)

    async def history(self) -> None:
        """Show the history of applied migrations."""

        await self.command.init()

        await self.command.history()

    async def create_database(self) -> None:
        """Create the database if it does not exist."""

        logger.log(LogLevel.INFO, f"🛠️ Creating database...")

        await Tortoise.init(
            db_url=self.database_url, modules={"models": self.model_modules}
        )

        await Tortoise.generate_schemas()

        await Tortoise.close_connections()

    async def drop_database(self) -> None:
        """Delete all tables from the database."""

        logger.log(LogLevel.INFO, "🗑️ Dropping database...")

        await Tortoise.init(
            db_url=self.database_url, modules={"models": self.model_modules}
        )

        await Tortoise._drop_databases()

        await Tortoise.close_connections()

    async def reset_database(self) -> None:
        """Delete and recreate the database."""

        logger.log(LogLevel.INFO, "🔄 Resetting database...")

        await self.drop_database()

        await self.create_database()

    async def show_status(self) -> None:
        """Show the current status of the database."""

        await self.command.init()

        applied = await self.command.history()

        logger.log(LogLevel.INFO, f"📜 Applied migrations:\n{applied}")

    async def apply_all_migrations(self) -> None:
        """Generate and apply all migrations in a single step."""

        logger.log(LogLevel.INFO, "🚀 Applying all migrations...")

        await self.migrate()

        await self.upgrade()

    async def rollback_all_migrations(self) -> None:
        """Revert all migrations to the initial state."""

        logger.log(LogLevel.INFO, "⏪ Rolling back all migrations...")

        await self.command.init()

        while True:
            try:
                await self.command.downgrade(1)
            except Exception:
                logger.log(LogLevel.INFO, "✅ No more migrations to revert.")
                break

    async def seed_data(self) -> None:
        """Insert initial data into the database."""

        logger.log(LogLevel.INFO, "🌱 Seeding initial data...")

        await Tortoise.init(
            db_url=self.database_url, modules={"models": self.model_modules}
        )

        await Tortoise.close_connections()

    async def close(self) -> None:
        """Close the database connections."""
        logger.log(LogLevel.INFO, "🔌 Closing database connections...")
        await Tortoise.close_connections()
        logger.log(LogLevel.INFO, "✅ Database connections closed.")
