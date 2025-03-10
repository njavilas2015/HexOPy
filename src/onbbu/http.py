from dataclasses import asdict, is_dataclass, dataclass
from enum import Enum
from typing import Awaitable, Callable, Generic, Optional, TypeVar
import multiprocessing
from contextlib import asynccontextmanager
from os import getenv

from starlette.applications import Starlette
from starlette.responses import JSONResponse as StarletteJSONResponse
from starlette.requests import Request as StarletteRequest
from starlette.routing import Route

from onbbu.database import DatabaseManager, database

T = TypeVar("T")


class Request(StarletteRequest):
    pass

class JSONResponse(StarletteJSONResponse):
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
            content = asdict(content)  # type: ignore

        elif isinstance(content, list):
            content = [
                (asdict(item) if is_dataclass(item) else item) for item in content  # type: ignore
            ]

        return super().render(content)


class HTTPMethod(Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"


EndpointHttpType = Callable[[Request], Awaitable[JSONResponse]]


@dataclass(frozen=True, slots=True)
class RouteDTO:
    path: str
    endpoint: EndpointHttpType
    method: HTTPMethod


class RouterHttp:
    __router: list[Route]
    __prefix: str

    def __init__(self, prefix: str = ""):
        self.__router = []
        self.__prefix = prefix.rstrip("/")

    def add_route(self, dto: RouteDTO) -> None:

        full_path: str = f"{self.__prefix}{dto.path}"

        self.__router.append(
            Route(path=full_path, endpoint=dto.endpoint, methods=[dto.method.value])
        )

    def get_router(self) -> list[Route]:
        return self.__router

    def get_routes(self) -> list[str]:
        return [route.path for route in self.__router]


class ServerHttp:
    database: DatabaseManager
    host: str
    port: int
    environment: str
    reload: bool
    workers: int
    server: Starlette

    def __init__(self, environment: str, port: Optional[int]):
        self.host = "0.0.0.0"
        self.port = port or 8000
        self.environment = environment
        self.reload = self.environment == "development"
        self.workers = 1 if self.reload else max(2, multiprocessing.cpu_count() - 1)

        self.server = Starlette(debug=True, routes=[], lifespan=self._lifespan)

        self.database = database

    @asynccontextmanager
    async def _lifespan(self, app: Starlette):
        """Gestor de eventos de vida para FastAPI"""
        await self.database.init()
        yield
        await self.database.close()

    def include_router(self, router: RouterHttp) -> None:
        """Agrega todas las rutas de un RouterHttp a la aplicación"""
        self.server.router.routes.extend(router.get_router())


server_http: ServerHttp = ServerHttp(
    port=int(getenv("HTTP_PORT", "8000")),
    environment=getenv("ENVIRONMENT", "development"),
)
