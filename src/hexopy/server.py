from fastapi import APIRouter, FastAPI


class Server:
    """Abstracts FastAPI to allow flexibility in case of future changes."""

    def __init__(self):
        self.app = FastAPI()
        self.router = APIRouter()

    def add_route(self, path: str, methods: list, endpoint):
        """Adds a new route to the application."""
        self.app.add_api_route(path=path, methods=methods, endpoint=endpoint)

    def include_router(self, prefix: str, tags: list):
        """Includes a router with a prefix and tags."""
        self.app.include_router(self.router, prefix=prefix, tags=tags)

    def get_app(self):
        """Returns the FastAPI application instance."""
        return self.app
