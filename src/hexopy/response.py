from typing import Generic
from dataclasses import asdict, is_dataclass
from fastapi.responses import JSONResponse
from .types import T


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
                (asdict(item) if is_dataclass(item) else item)
                for item in content
            ]

        return super().render(content)
