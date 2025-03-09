import os
import asyncio
from argparse import ArgumentParser, HelpFormatter, Namespace
from typing import List
from onbbu.database import database
from onbbu.http import servier_http
from onbbu.logger import logger, LogLevel
import uvicorn


class BaseCommand:
    name: str
    help: str

    def add_arguments(self, parser: ArgumentParser) -> None:
        """Método para que cada comando defina sus propios argumentos."""
        pass

    async def handler(self, args: Namespace) -> None:
        """Método asíncrono que ejecutará la lógica del comando."""
        pass


class MigrateCommand(BaseCommand):
    name: str = "migrate"
    help: str = "Ejecuta migraciones"

    async def handler(self, args: Namespace) -> None:
        print("Ejecutando migraciones...")

        await database.init()

        await database.migrate()

        await database.close()

        logger.log(
            level=LogLevel.INFO,
            message=f"✅ End command migrate..",
            extra_data={},
        )


class CreateModuleCommand(BaseCommand):
    name: str = "create_module"
    help: str = "Crea un módulo"

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("-n", "--nombre", help="Nombre del módulo", required=True)
        parser.add_argument(
            "-a", "--notify", action="store_true", help="Notificar inmediatamente"
        )

    async def handler(self, args: Namespace) -> None:
        """Ejecuta la lógica asíncrona de creación del módulo."""
        path = os.getcwd()
        name = args.nombre

        folders: list[str] = [
            "domain",
            "domain/entities",
            "domain/services",
            "application/dto",
            "application/commands",
            "application/use_cases",
            "infrastructure/adapters",
            "infrastructure/cache",
            "infrastructure/logger",
            "infrastructure/messaging",
            "infrastructure/persistence/models",
            "infrastructure/persistence/repositories",
            "infrastructure/services",
            "infrastructure/storage",
            "infrastructure/transformers",
        ]

        async def create_folder(folder: str):
            dir_path = os.path.join(path, "pkg", name, folder)
            await asyncio.to_thread(os.makedirs, dir_path, exist_ok=True)

        await asyncio.gather(*(create_folder(folder) for folder in folders))

        print(f"Módulo '{name}' creado en {path}/pkg/{name}")


class RunServerCommand(BaseCommand):
    name: str = "runserver"
    help: str = "Inicia el servidor"

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("-n", "--nombre", help="Nombre del módulo", required=True)
        parser.add_argument(
            "-a", "--notify", action="store_true", help="Notificar inmediatamente"
        )

    async def handler(self, args: Namespace) -> None:
        logger.log(
            level=LogLevel.INFO,
            message=f"🚀 Iniciando servidor en {servier_http.host}:{servier_http.port} ...",
            extra_data={},
        )

        for route in servier_http.server.routes:
            logger.log(
                level=LogLevel.INFO,
                message=f"🔗 {route.path} -> {route.name} ({route.methods})",  # type: ignore
                extra_data={},
            )

        uvicorn.run(
            "servier_http",
            host=servier_http.host,
            port=servier_http.port,
            reload=servier_http.reload,
            workers=servier_http.workers,
        )


async def cli() -> None:
    commands: List[BaseCommand] = [
        CreateModuleCommand(),
        MigrateCommand(),
        RunServerCommand(),
    ]

    parser = ArgumentParser(
        description="Onbbu Management script",
        formatter_class=lambda prog: HelpFormatter(prog, max_help_position=30),
    )

    subparsers = parser.add_subparsers(dest="command", metavar="command")

    for command in commands:
        command_parser = subparsers.add_parser(command.name, help=command.help)
        command.add_arguments(command_parser)
        command_parser.set_defaults(func=command.handler)

    args: Namespace = parser.parse_args()

    if hasattr(args, "func"):
        await args.func(args)
    else:
        parser.print_help()
