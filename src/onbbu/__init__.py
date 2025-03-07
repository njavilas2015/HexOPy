from argparse import ArgumentParser, Namespace
import sys
import os

from typing import Any, List
import uvicorn

from onbbu.logger import LogLevel, logger
from onbbu.database import DatabaseManager
from onbbu.manager import BaseCommand, Manager, create_module, COMMANDS, register_command
from onbbu.config_loader import ConfigLoader
from onbbu.paginate import PaginateDTO, createPaginateResponse, Paginate
from onbbu.http import (
    HTTPMethod,
    EndpointHttpType,
    Response,
    ResponseNotFoundError,
    ResponseValueError,
    ResponseValidationError,
    Request,
    JSONResponse,
    ServerHttp,
)

BASE_DIR: str = os.getcwd()

sys.path.append(BASE_DIR)

environment: str = os.getenv("ENVIRONMENT", "development")

installed_apps: List[str] = ConfigLoader(BASE_DIR).load_python_config(
    path="internal/settings.py",
    attribute="INSTALLED_APPS",
    default=[],
) # type: ignore

server: ServerHttp = ConfigLoader(BASE_DIR).load_python_config(
    path="internal/main.py",
    attribute="server",
    default=None,
) # type: ignore


database = DatabaseManager(
    database_url=os.getenv("DATABASE_URL", "sqlite://db.sqlite3"),
    INSTALLED_APPS=installed_apps,
)

def create_app(port: int = 8000) -> ServerHttp:
    """Crea y retorna una instancia del servidor."""
    return ServerHttp(port=port, database=database, environment=environment)


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

    async def handle(self, *args: Namespace, **kwargs: dict[str, Any]) -> None:

        await database.init()

        await database.migrate()

        await database.close()


@register_command
class CommandCreateModule(BaseCommand):
    """Command to run the server."""

    name: str = "create_module"
    help: str = "Comando para crear un nuevo modulo."

    async def add_arguments(self, parser: ArgumentParser):
        parser.add_argument(
            "--name", type=str, default="demo", help="Nombre del moodulo"
        )

    async def handle(self, *args: Namespace, **kwargs: dict[str, Any]) -> None:
        await create_module(path=BASE_DIR, name=args.name) # type: ignore


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

    async def handle(self, *args: Namespace, **kwargs: dict[str, Any]) -> None:

        if hasattr(server, "server"):
            logger.log(
                level=LogLevel.INFO,
                message=f"🚀 Iniciando servidor en {server.host}:{server.port} ...",
                extra_data={},
            )

            for route in server.server.routes:
                logger.log(
                    level=LogLevel.INFO,
                    message=f"🔗 {route.path} -> {route.name} ({route.methods})", # type: ignore
                    extra_data={},
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
                extra_data={},
            )


async def cli():

    manager: Manager = Manager(INSTALLED_APPS=installed_apps, COMMANDS=COMMANDS)

    commands: list[BaseCommand] = [
        CommandRunServer(),
        CommandMigrate(),
        CommandCreateModule(),
    ]

    await manager.load_commands()

    await manager.internal_command(commands)

    await manager.execute()


#def main():
#
#    parser: ArgumentParser = ArgumentParser(description="CLI para manejar Onbbu")
#
#    subparsers = parser.add_subparsers(dest="command")
#
#    subparsers.add_parser("run", help="Iniciar el servidor")
#
#    subparsers.add_parser("makemigrations", help="Generar una nueva migración")
#
#    subparsers.add_parser("migrate", help="Aplicar migraciones")
#
#    subparsers.add_parser("routes", help="Listar rutas de")
#
#    args: Namespace = parser.parse_args()
#
#    parser.print_help()
#
#    # if args.command == "run":
#    #    run_server(server=server)
#    # elif args.command == "routes":
#    #    list_routes()
#    # else:
#    #    parser.print_help()


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
    "Request",
    "JSONResponse",
    "Response",
    "ResponseNotFoundError",
    "ResponseValidationError",
    "ResponseValueError",
]
