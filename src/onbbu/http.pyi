from dataclasses import dataclass
from enum import Enum
from onbbu.database import DatabaseManager as DatabaseManager, database as database
from starlette.applications import Starlette
from starlette.requests import Request as StarletteRequest
from starlette.responses import JSONResponse
from starlette.routing import Route
from typing import Awaitable, Callable, Generic, TypeVar

T = TypeVar('T')

class Request(StarletteRequest): ...

class ResponseNotFoundError(JSONResponse, Generic[T]):
    def render(self, content: T) -> bytes: ...

class ResponseValueError(JSONResponse, Generic[T]):
    def render(self, content: T) -> bytes: ...

class ResponseValidationError(JSONResponse, Generic[T]):
    def render(self, content: T) -> bytes: ...

class Response(JSONResponse, Generic[T]):
    def render(self, content: T) -> bytes: ...

class HTTPMethod(Enum):
    GET = 'GET'
    POST = 'POST'
    PUT = 'PUT'
    DELETE = 'DELETE'
EndpointHttpType = Callable[[Request], Awaitable[JSONResponse]]

@dataclass(frozen=True, slots=True)
class RouteDTO:
    path: str
    endpoint: EndpointHttpType
    method: HTTPMethod

class RouterHttp:
    def __init__(self, prefix: str = '') -> None: ...
    def add_route(self, dto: RouteDTO) -> None: ...
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

@dataclass(frozen=True, slots=True)
class ConfigInit:
    http: ServerHttp

servier_http: ServerHttp
