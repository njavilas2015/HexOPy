from concurrent.futures import ThreadPoolExecutor
from enum import Enum
import json
import logging
from logging.handlers import RotatingFileHandler
from typing import Optional

import requests
from rich.console import Console
from rich.text import Text
from rich.traceback import install

install()

class LogLevel(Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


DEFAULT_SERVER_URL: str = "https://api.onbbu.ar/logs"

class Logger:
    def __init__(self, log_file: Optional[str], server_url: Optional[str]):
        log_file = log_file or "onbbu.log"
        self.server_url = server_url
        self.executor = ThreadPoolExecutor(max_workers=5)

        self.logger = logging.getLogger("app_logger")
        self.logger.setLevel(logging.DEBUG)
        self.console = Console()

        class JsonFormatter(logging.Formatter):
            def format(self, record):
                log_entry = {
                    "timestamp": self.formatTime(record, "%Y-%m-%d %H:%M:%S"),
                    "level": record.levelname,
                    "message": record.getMessage(),
                }
                if hasattr(record, "extra_data") and record.extra_data:
                    log_entry["extra"] = record.extra_data
                return json.dumps(log_entry, ensure_ascii=False)

        log_format = JsonFormatter()

        file_handler = RotatingFileHandler(log_file, maxBytes=5000000, backupCount=3)
        file_handler.setFormatter(log_format)
        self.logger.addHandler(file_handler)

    def log(self, level: LogLevel, message: str, extra_data=None):
        """Logs a message and prints it nicely in the terminal."""
        log_function = {
            LogLevel.DEBUG: self.logger.debug,
            LogLevel.INFO: self.logger.info,
            LogLevel.WARNING: self.logger.warning,
            LogLevel.ERROR: self.logger.error,
            LogLevel.CRITICAL: self.logger.critical,
        }.get(level, self.logger.info)

        log_data = {"level": level.value, "message": message, "extra": extra_data or {}}

        self.pretty_print(level, message, extra_data)

        log_function(message, extra={"extra_data": extra_data})

        if self.server_url:
            self.executor.submit(self.send_log, log_data)

    def pretty_print(self, level: LogLevel, message: str, extra_data: dict):
        """Prints logs in the terminal with colors and nice formatting using Rich."""
        level_colors = {
            LogLevel.DEBUG: "cyan",
            LogLevel.INFO: "green",
            LogLevel.WARNING: "yellow",
            LogLevel.ERROR: "red",
            LogLevel.CRITICAL: "bold red",
        }
        color = level_colors.get(level, "white")

        text = Text(f"[{level.value}] ", style=color)
        text.append(message, style="bold white")

        if extra_data:
            extra_json = json.dumps(extra_data, indent=2, ensure_ascii=False)
            text.append(f"\n{extra_json}", style="dim")

        self.console.print(text)

    def send_log(self, log_data):
        """Sends logs to the server asynchronously."""
        try:
            headers = {"Content-Type": "application/json"}
            requests.post(self.server_url, json=log_data, headers=headers, timeout=3)
        except requests.RequestException as e:
            self.logger.error(f"Error sending log to server: {e}")

logger: Logger = Logger(log_file=None, server_url=None)
