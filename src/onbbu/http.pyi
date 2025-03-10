from dataclasses import dataclass
from enum import Enum
from onbbu.database import DatabaseManager as DatabaseManager, database as database
from starlette.applications import Starlette
from starlette.requests import Request as StarletteRequest
from starlette.responses import JSONResponse as StarletteJSONResponse
from starlette.routing import Route
from typing import Awaitable, Callable, Generic, TypeVar
from pydantic import ValidationError

T = TypeVar("T")

class Request(StarletteRequest): ...
class JSONResponse(StarletteJSONResponse): ...

class ResponseNotFoundError(JSONResponse, Generic[T]):
    def render(self, content: T) -> bytes: ...

class ResponseValueError(JSONResponse):
    def render(self, content: ValueError) -> bytes: ...

class ResponseValidationError(JSONResponse):
    def render(self, content: ValidationError) -> bytes: ...

class Response(JSONResponse, Generic[T]):
    def render(self, content: T) -> bytes: ...

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
    def add_routes(self, dto: list[RouteDTO]) -> None: ...
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
