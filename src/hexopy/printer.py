from colorama import Fore, Style, init

init(autoreset=True)


class ConsoleStyle:
    """Class to print messages in different styles"""

    @staticmethod
    def success(message: str) -> None:
        """Prints a message in green (success)"""
        print(Fore.GREEN + "✅ " + message + Style.RESET_ALL)

    @staticmethod
    def error(message: str) -> None:
        """Prints a message in red (error)"""
        print(Fore.RED + "❌ " + message + Style.RESET_ALL)

    @staticmethod
    def warning(message: str) -> None:
        """Prints a message in yellow (warning)"""
        print(Fore.YELLOW + "⚠️ " + message + Style.RESET_ALL)
