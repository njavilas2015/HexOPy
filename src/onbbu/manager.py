import argparse
import asyncio
import importlib
import os
import pkgutil
from typing import Dict, List


async def create_module(path: str, name: str):

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

    for folder in folders:
        dir_path = os.path.join(path, "pkg", name, folder)
        os.makedirs(dir_path, exist_ok=True)


class BaseCommand:
    """Base class for all commands."""

    name: str
    help: str = "Base command description"

    def __init__(self):
        self.parser = None

    def add_arguments(self, parser):
        """Override this method to add custom arguments."""
        pass

    def handle(self, *args, **kwargs):
        """Override this method to implement command logic."""
        raise NotImplementedError("Subclasses must implement handle()")


class Manager:
    """Command-line manager for executing various tasks."""

    def __init__(self, INSTALLED_APPS: List[str], COMMANDS: Dict[str, BaseCommand]):
        self.parser = argparse.ArgumentParser(
            description="Management script",
            formatter_class=lambda prog: argparse.HelpFormatter(
                prog, max_help_position=30
            ),
        )

        self.subparsers = self.parser.add_subparsers(dest="command", metavar="command")

        self.INSTALLED_APPS = INSTALLED_APPS
        self.COMMANDS = COMMANDS

        self.load_commands()

    def internal_command(self, commands: list[BaseCommand]):
        """Execute a system command."""

        for command in commands:
            self.COMMANDS[command.name] = command

    def load_commands(self):
        """Dynamically load commands from installed apps."""
        for app in self.INSTALLED_APPS:
            commands_path = f"pkg.{app}.application.commands"
            try:
                module = importlib.import_module(commands_path)

                if hasattr(module, "__path__"):
                    for _, module_name, _ in pkgutil.iter_modules(module.__path__):

                        full_module_name = f"{commands_path}.{module_name}"

                        command_module = importlib.import_module(full_module_name)

                        if hasattr(command_module, "Command"):
                            command_instance: BaseCommand = command_module.Command()
                            self.COMMANDS[command_instance.name] = command_instance

            except ModuleNotFoundError as e:
                print(f"Warning: Could not import {commands_path}: {e}")

        for name, command in self.COMMANDS.items():
            command_parser = self.subparsers.add_parser(name, help=command.help)
            command.add_arguments(command_parser)
            command.parser = command_parser

    def execute(self):
        """Parse and execute commands dynamically."""
        args = self.parser.parse_args()
        command = self.COMMANDS.get(args.command)

        if command:
            command.handle(args)
        else:
            self.parser.print_help()
