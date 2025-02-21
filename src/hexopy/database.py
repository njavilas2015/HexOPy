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
        """Carga dinámicamente los modelos desde las aplicaciones instaladas."""
        for app in self.INSTALLED_APPS:
            model_path: str = f"pkg.{app}.infrastructure.persistence.models"

            try:
                module: ModuleType = importlib.import_module(model_path)
                print(f"📦 Módulo base encontrado: {model_path}")

                if hasattr(module, "__path__"):
                    for _, module_name, _ in pkgutil.iter_modules(module.__path__):
                        full_module_name = f"{model_path}.{module_name}"
                        self.model_modules.append(full_module_name)
                        print(f"✅ Modelo cargado: {full_module_name}")

            except ModuleNotFoundError as e:
                print(f"⚠️ Warning: No se pudo importar {model_path}: {e}")

    async def init_db(self):
        """Inicializa la base de datos con los modelos cargados."""
        self.load_models()

        if not self.model_modules:
            print("❌ No se encontraron modelos. Verifica `INSTALLED_APPS`.")
            return

        print("🔄 Inicializando Tortoise con modelos:", self.model_modules)

        await Tortoise.init(
            db_url=self.database_url, modules={"models": self.model_modules}
        )
        print("✅ Base de datos conectada. Generando esquemas...")

        await Tortoise.generate_schemas()
        print("🎉 Esquemas generados exitosamente.")

    async def close_db(self):
        """Cierra la conexión con la base de datos."""

        print("🛑 Cerrando conexión con la base de datos...")

        await Tortoise.close_connections()

        print("✅ Conexión cerrada.")

    async def run(self):
        """Ejecuta la inicialización y cierre de la base de datos."""

        await self.init_db()
        await self.close_db()
