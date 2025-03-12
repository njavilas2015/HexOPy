from dataclasses import dataclass
from enum import Enum
from onbbu.database import DatabaseManager as DatabaseManager, database as database
from onbbu.logger import LogLevel as LogLevel, logger as logger
from pydantic import ValidationError as ValidationError
from starlette.applications import Starlette
from starlette.middleware.base import (
    BaseHTTPMiddleware,
    RequestResponseEndpoint as RequestResponseEndpoint,
)
from starlette.requests import Request as RequestStarlette
from starlette.responses import (
    JSONResponse as JSONResponseStarlette,
    Response as Response,
)
from starlette.routing import Route
from typing import Any, Awaitable, Callable, TypeVar

T = TypeVar("T")

class Request(RequestStarlette): ...
class JSONResponse(JSONResponseStarlette): ...

class ResponseHttp:
    def json(self, content: Any, status_code: int) -> JSONResponse: ...
    def validate_error(self, content: ValidationError) -> JSONResponse: ...
    def value_error(self, content: ValueError) -> JSONResponse: ...
    def not_found(self, content: str) -> JSONResponse: ...
    def unauthorized(self, msg: str = "Unauthorized") -> JSONResponse: ...
    def server_error(self, msg: str = "Internal Server Error") -> JSONResponse: ...

class TimingMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: RequestStarlette, call_next: RequestResponseEndpoint
    ) -> Response: ...

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
    def __init__(self, prefix: str = "") -> None: ...
    def add_route(self, dto: RouteDTO) -> None: ...
    def add_routes(self, dtos: list[RouteDTO]) -> None: ...
    def get_router(self) -> list[Route]: ...
    def get_routes(self) -> list[str]: ...

class ServerHttp:
    database: DatabaseManager
    host: str
    port: int
    environment: str
    reload: bool
    workers: int
    server: Starlette
    def __init__(self, environment: str, port: int | None) -> None: ...
    def include_router(self, router: RouterHttp) -> None: ...

server_http: ServerHttp

def runserver(server_http: ServerHttp) -> None: ...
