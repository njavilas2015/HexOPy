from os import getcwd
from sys import path

BASE_DIR: str = getcwd()

path.append(BASE_DIR)


def main():
    import asyncio
    from .manager import cli

    asyncio.run(cli())
