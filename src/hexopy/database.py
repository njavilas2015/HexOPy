import importlib
import pkgutil
from types import ModuleType
from tortoise import Tortoise
import os


class DatabaseManager:
    def __init__(self, INSTALLED_APPS: list[str]):
        self.database_url = os.getenv("DATABASE_URL", "sqlite://db.sqlite3")
        self.model_modules: list[str] = []
        self.INSTALLED_APPS = INSTALLED_APPS

    def load_models(self):
        """Dynamically load models from installed applications."""
        for app in self.INSTALLED_APPS:
            model_path: str = f"pkg.{app}.infrastructure.persistence.models"

            try:
                module: ModuleType = importlib.import_module(model_path)
                print(f"📦 Base module found: {model_path}")

                if hasattr(module, "__path__"):
                    for _, module_name, _ in pkgutil.iter_modules(module.__path__):
                        full_module_name = f"{model_path}.{module_name}"
                        self.model_modules.append(full_module_name)
                        print(f"✅ Loaded model: {full_module_name}")

            except ModuleNotFoundError as e:
                print(f"⚠️ Warning: Could not import {model_path}: {e}")

    async def init_db(self):
        """Initializes the database with the loaded models."""
        self.load_models()

        if not self.model_modules:
            print("❌ No models found. Check Check `INSTALLED_APPS`.")
            return

        print("🔄 Initializing Tortoise with models:", self.model_modules)

        await Tortoise.init(
            db_url=self.database_url, modules={"models": self.model_modules}
        )
        print("✅ Connected database. Generating schematics...")

        await Tortoise.generate_schemas()
        print("🎉 Schemes generated successfully.")

    async def close_db(self):
        """Close the connection to the database."""

        print("🛑 Closing connection with the database...")

        await Tortoise.close_connections()

        print("✅ Closed connection.")

    async def run(self):
        """Run database initialization and shutdown"""

        await self.init_db()
        await self.close_db()
