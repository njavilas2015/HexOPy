from dataclasses import asdict, is_dataclass, dataclass
from enum import Enum
from typing import Awaitable, Callable, Generic
import multiprocessing
from contextlib import asynccontextmanager

from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.requests import Request as StarletteRequest
from starlette.routing import Route

from onbbu.database import DatabaseManager
from onbbu.types import T


class Request(StarletteRequest):
    pass


class ResponseNotFoundError(Generic[T], JSONResponse):

    def render(self, content: T) -> bytes:
        content = {"error": str(content)}  # type: ignore

        return super().render(content, status_code=404)  # type: ignore


class ResponseValueError(Generic[T], JSONResponse):

    def render(self, content: T) -> bytes:
        content = {"error": str(content)}  # type: ignore

        return super().render(content, status_code=500)  # type: ignore


class ResponseValidationError(Generic[T], JSONResponse):

    def render(self, content: T) -> bytes:
        content = {"detail": content.errors()}  # type: ignore

        return super().render(content, status_code=400)  # type: ignore


class Response(Generic[T], JSONResponse):

    def render(self, content: T) -> bytes:  # type: ignore

        if is_dataclass(content):
            content = asdict(content)

        elif isinstance(content, list):
            content = [
                (asdict(item) if is_dataclass(item) else item) for item in content
            ]

        return super().render(content)


class HTTPMethod(Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"


EndpointHttpType = Callable[[Request], Awaitable[JSONResponse]]


class RouterHttp:
    __router: list[Route]
    __prefix: str

    def __init__(self, prefix: str = ""):
        self.__router = []
        self.__prefix = prefix.rstrip("/")

    def add_route(self, path: str, endpoint: EndpointHttpType, method: HTTPMethod):

        full_path: str = f"{self.__prefix}{path}"

        self.__router.append(
            Route(path=full_path, endpoint=endpoint, methods=[method.value])
        )

    def get_router(self):
        return self.__router

    def get_routes(self):
        return [route.path for route in self.__router]

    def get_endpoints(self):
        return [route.endpoint for route in self.__router]


class ServerHttp:
    database: DatabaseManager

    def __init__(self, environment: str, database: DatabaseManager, port: int = 8000):
        self.host = "0.0.0.0"
        self.port = port
        self.environment = environment
        self.reload = self.environment == "development"
        self.workers = 1 if self.reload else max(2, multiprocessing.cpu_count() - 1)

        self.server = Starlette(debug=True, routes=[], lifespan=self._lifespan)

        self.config = ConfigInit(http=self)

        self.database = database

    @asynccontextmanager
    async def _lifespan(self, app: Starlette):
        """Gestor de eventos de vida para FastAPI"""
        await self.database.init()
        yield
        await self.database.close()

    def include_router(self, router: RouterHttp):
        """Agrega todas las rutas de un RouterHttp a la aplicación"""
        self.server.router.routes.extend(router.get_router())

@dataclass(frozen=True, slots=True)
class ConfigInit:
    http: ServerHttp