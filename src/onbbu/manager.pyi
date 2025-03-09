from argparse import ArgumentParser, Namespace
from typing import List
from onbbu.database import database as database
from onbbu.http import server_http as server_http
from onbbu.logger import LogLevel as LogLevel, logger as logger

class BaseCommand:
    name: str
    help: str
    def add_arguments(self, parser: ArgumentParser) -> None: ...
    async def handler(self, args: Namespace) -> None: ...

class MigrateCommand(BaseCommand):
    name: str
    help: str
    async def handler(self, args: Namespace) -> None: ...

class CreateModuleCommand(BaseCommand):
    name: str
    help: str
    def add_arguments(self, parser: ArgumentParser) -> None: ...
    async def handler(self, args: Namespace) -> None: ...

class RunServerCommand(BaseCommand):
    name: str
    help: str
    def add_arguments(self, parser: ArgumentParser) -> None: ...
    async def handler(self, args: Namespace) -> None: ...

async def cli() -> None: ...

async def menu_cli(description: str, commands: List[BaseCommand]) -> None: ...