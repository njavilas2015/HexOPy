from os import getcwd
from sys import path
from asyncio import run

BASE_DIR: str = getcwd()

path.append(BASE_DIR)

from .manager import cli

__all__ = [
    
]


if __name__ == "__main__":
    run(cli())