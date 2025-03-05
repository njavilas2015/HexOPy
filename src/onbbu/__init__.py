import argparse
import sys
import importlib
import os
import importlib.util
import multiprocessing

from typing import List
from dataclasses import dataclass
from contextlib import asynccontextmanager

from starlette.applications import Starlette

import uvicorn

from onbbu.logger import LogLevel, logger
from onbbu.database import DatabaseManager
from onbbu.http import (
    RouterHttp,
    HTTPMethod,
    EndpointHttpType,
    Response,
    ResponseNotFoundError,
    ResponseValueError,
    ResponseValidationError,
    Request,
    JSONResponse,
)

from onbbu.manager import BaseCommand, Manager, create_module

BASE_DIR: str = os.getcwd()

sys.path.append(BASE_DIR)

environment: str = os.getenv("ENVIRONMENT", "development")


class ConfigLoader:
    def __init__(self, base_dir):
        self.base_dir = base_dir

    def load_python_config(self, relative_path, attribute_name, default=None):
        """Upload a configuration file in Python format"""

        config_path = os.path.join(self.base_dir, *relative_path.split("/"))

        if not os.path.exists(config_path):
            print(
                f"⚠️ Advertencia: No se encontró `{relative_path}`. Se usará el valor por defecto."
            )
            return default

        spec = importlib.util.spec_from_file_location("config_module", config_path)

        config_module = importlib.util.module_from_spec(spec)

        spec.loader.exec_module(config_module)

        return getattr(config_module, attribute_name, default)


installed_apps: List[str] = ConfigLoader(BASE_DIR).load_python_config(
    relative_path="internal/settings.py",
    attribute_name="INSTALLED_APPS",
    default=[],
)


COMMANDS = {}


def register_command(cls: BaseCommand) -> BaseCommand:
    """Decorator to register commands automatically."""
    COMMANDS[cls.name.lower()] = cls()
    return cls


database = DatabaseManager(
    database_url=os.getenv("DATABASE_URL", "sqlite://db.sqlite3"),
    INSTALLED_APPS=installed_apps,
)


class ServerHttp:
    def __init__(self, port=8000):
        self.host = "0.0.0.0"
        self.port = port
        self.environment = environment
        self.reload = self.environment == "development"
        self.workers = 1 if self.reload else max(2, multiprocessing.cpu_count() - 1)

        self.server = Starlette(debug=True, routes=[], lifespan=self._lifespan)

        self.config = ConfigInit(http=self)

    @asynccontextmanager
    async def _lifespan(self, app: Starlette):
        """Gestor de eventos de vida para FastAPI"""
        await database.init()
        yield
        await database.close()

    def include_router(self, router: RouterHttp):
        """Agrega todas las rutas de un RouterHttp a la aplicación"""
        self.server.router.routes.extend(router.get_router())


def create_app(port=8000) -> ServerHttp:
    """Crea y retorna una instancia del servidor."""
    return ServerHttp(port=port)


@dataclass(frozen=True, slots=True)
class ConfigInit:
    http: ServerHttp


server: ServerHttp = ConfigLoader(BASE_DIR).load_python_config(
    relative_path="internal/main.py",
    attribute_name="server",
    default=None,
)


@register_command
class CommandMigrate(BaseCommand):
    """Command to run the server."""

    name: str = "migrate"
    help: str = "Command to run the server."

    # def add_arguments(self, parser):
    #    parser.add_argument(
    #        "--host", type=str, default="0.0.0.0", help="Host for the server"
    #    )
    #    parser.add_argument(
    #        "--port", type=int, default=8000, help="Port for the server"
    #    )

    async def handle(self, args):

        await database.init()

        await database.migrate()

        await database.close()


@register_command
class CommandCreateModule(BaseCommand):
    """Command to run the server."""

    name: str = "create_module"
    help: str = "Comando para crear un nuevo modulo."

    def add_arguments(self, parser):
        parser.add_argument(
            "--name", type=str, default="demo", help="Nombre del moodulo"
        )

    def handle(self, args):
        create_module(path=BASE_DIR, name=args.name)


@register_command
class CommandRunServer(BaseCommand):
    """Command to run the server."""

    name: str = "run"
    help: str = "Command to run the server."

    # def add_arguments(self, parser):
    #    parser.add_argument(
    #        "--host", type=str, default="0.0.0.0", help="Host for the server"
    #    )
    #    parser.add_argument(
    #        "--port", type=int, default=8000, help="Port for the server"
    #    )

    def handle(self, args):

        if hasattr(server, "server"):
            logger.log(
                level=LogLevel.INFO,
                message=f"🚀 Iniciando servidor en {server.host}:{server.port} ...",
            )

            for route in server.server.routes:
                logger.log(
                    level=LogLevel.INFO,
                    message=f"🔗 {route.path} -> {route.name} ({route.methods})",
                )

            uvicorn.run(
                "internal.main:server.server",
                host=server.host,
                port=server.port,
                reload=server.reload,
                workers=server.workers,
            )

        else:
            logger.log(
                level=LogLevel.ERROR,
                message=f"❌ `internal/main.py` no contiene una instancia `server`.",
            )


def cli():
    manager = Manager(INSTALLED_APPS=installed_apps, COMMANDS=COMMANDS)

    commands: list[BaseCommand] = [
        CommandRunServer(),
        CommandMigrate(),
        CommandCreateModule(),
    ]

    manager.internal_command(commands)

    manager.execute()


def main():

    parser = argparse.ArgumentParser(description="CLI para manejar Onbbu")

    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("run", help="Iniciar el servidor")

    subparsers.add_parser("makemigrations", help="Generar una nueva migración")

    subparsers.add_parser("migrate", help="Aplicar migraciones")

    subparsers.add_parser("routes", help="Listar rutas de")

    args = parser.parse_args()

    parser.print_help()

    # if args.command == "run":
    #    run_server(server=server)
    # elif args.command == "routes":
    #    list_routes()
    # else:
    #    parser.print_help()


__all__ = [
    "COMMANDS",
    "BaseCommand",
    "register_command",
    "DatabaseManager",
    "HTTPMethod",
    "EndpointHttpType",
    "Paginate",
    "PaginateDTO",
    "createPaginateResponse",
    "ConsoleStyle",
    "Request",
    "JSONResponse",
    "Response",
    "ResponseNotFoundError",
    "ResponseValidationError",
    "ResponseValueError",
    "HexoServer",
]
