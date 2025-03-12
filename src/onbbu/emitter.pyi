from enum import Enum
from typing import Awaitable, Callable

Listener = Callable[..., None] | Callable[..., Awaitable[None]]

class Event(Enum):
    DEFAULT_DISCOUNT = "add_default_discounts"

class EventEmitter:
    def __init__(self) -> None: ...
    def on(self, event: str, listener: Listener) -> None: ...
    async def emit(self, event: str, *args: object, **kwargs: object) -> None: ...

emitter: EventEmitter
