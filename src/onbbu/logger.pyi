import logging
from concurrent.futures import ThreadPoolExecutor
from enum import Enum
from logging import Logger as Logging
from rich.console import Console

class LogLevel(Enum):
    DEBUG = 'DEBUG'
    INFO = 'INFO'
    WARNING = 'WARNING'
    ERROR = 'ERROR'
    CRITICAL = 'CRITICAL'

DEFAULT_SERVER_URL: str

class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str: ...

class Logger:
    console: Console
    server_url: str | None
    executor: ThreadPoolExecutor
    logger: Logging
    def __init__(self, log_file: str, server_url: str) -> None: ...
    def log(self, level: LogLevel, message: str, extra_data: dict[str, str]) -> None: ...
    def pretty_print(self, level: LogLevel, message: str, extra_data: dict[str, str]) -> None: ...
    def send_log(self, log_data: dict[str, str]) -> None: ...

logger: Logger
