from dataclasses import dataclass
from enum import Enum
import time
from typing import Any, Awaitable, Callable, Optional, TypeVar
import multiprocessing
from contextlib import asynccontextmanager
from os import getenv

from starlette.applications import Starlette
from starlette.responses import JSONResponse as JSONResponseStarlette, Response
from starlette.requests import Request as RequestStarlette
from starlette.routing import Route
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

import uvicorn

from onbbu.database import DatabaseManager, database

from pydantic import ValidationError

from onbbu.logger import LogLevel, logger

T = TypeVar("T")


class Request(RequestStarlette):
    pass


class JSONResponse(JSONResponseStarlette):
    pass


class ResponseHttp:

    def json(self, content: Any, status_code: int) -> JSONResponse:

        return JSONResponse(content=content, status_code=status_code)

    def validate_error(self, content: ValidationError) -> JSONResponse:

        def format_errors_json(errors: ValidationError) -> dict[int | str, str]:
            return {error["loc"][0]: error["msg"] for error in errors.errors()}

        return JSONResponse(content=format_errors_json(content), status_code=400)

    def value_error(self, content: ValueError) -> JSONResponse:

        return JSONResponse(content={"error": str(content)}, status_code=500)

    def not_found(self, content: str) -> JSONResponse:

        return JSONResponse(content={"error": content}, status_code=404)

    def unauthorized(self, msg: str = "Unauthorized") -> JSONResponse:

        return JSONResponse(content={"error": msg}, status_code=401)

    def server_error(self, msg: str = "Internal Server Error") -> JSONResponse:

        return JSONResponse(content={"error": msg}, status_code=500)


class TimingMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: RequestStarlette, call_next: RequestResponseEndpoint
    ) -> Response:
        start_time: float = time.time()

        response: Response = await call_next(request)

        process_time: float = time.time() - start_time

        response.headers["X-Process-Time"] = str(process_time)

        return response


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

    def add_routes(self, dtos: list[RouteDTO]) -> None:
        for dto in dtos:
            self.add_route(dto)

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

        self.server.add_middleware(TimingMiddleware)

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


def runserver(server_http: ServerHttp) -> None:
    logger.log(
        level=LogLevel.INFO,
        message=f"🚀 Iniciando servidor en {server_http.host}:{server_http.port} ...",
        extra_data={},
    )

    for route in server_http.server.routes:
        logger.log(
            level=LogLevel.INFO,
            message=f"🔗 {route.path} -> {route.name} ({route.methods})",  # type: ignore
            extra_data={},
        )

    uvicorn.run(server_http.server, host=server_http.host, port=server_http.port)
