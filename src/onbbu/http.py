from dataclasses import asdict, is_dataclass
from enum import Enum
from typing import Awaitable, Callable, Generic
from starlette.responses import JSONResponse
from starlette.requests import Request
from starlette.routing import Route

from onbbu.types import T


class Request(Request):
    pass


class ResponseNotFoundError(JSONResponse):

    def render(self, content: Generic[T]) -> bytes:
        content = {"error": str(content)}

        return super().render(content, status_code=404)


class ResponseValueError(JSONResponse):

    def render(self, content: Generic[T]) -> bytes:
        content = {"error": str(content)}

        return super().render(content, status_code=500)


class ResponseValidationError(JSONResponse):

    def render(self, content: Generic[T]) -> bytes:
        content = {"detail": content.errors()}

        return super().render(content, status_code=400)


class Response(JSONResponse):

    def render(self, content: Generic[T]) -> bytes:

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
