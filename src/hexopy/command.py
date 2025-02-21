COMMANDS = {}


class BaseCommand:
    """Base class for all commands."""

    help: str = "Base command description"

    def __init__(self):
        self.parser = None  # Se definirá en el Manager

    def add_arguments(self, parser):
        """Override this method to add custom arguments."""
        pass

    def handle(self, *args, **kwargs):
        """Override this method to implement command logic."""
        raise NotImplementedError("Subclasses must implement handle()")


def register_command(cls):
    """Decorator to register commands automatically."""
    COMMANDS[cls.name.lower()] = cls()
    return cls
