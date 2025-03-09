from enum import Enum
from typing import Awaitable, Callable, Dict, List, Union
import inspect


Listener = Union[Callable[..., None], Callable[..., Awaitable[None]]]


class Event(Enum):
    DEFAULT_DISCOUNT = "add_default_discounts"


class EventEmitter:
    """Simple EventEmitter for handling events."""

    def __init__(self):
        self._listeners: Dict[str, List[Listener]] = {}

    def on(self, event: str, listener: Listener) -> None:
        """Register an event listener."""
        if event not in self._listeners:
            self._listeners[event] = []
        self._listeners[event].append(listener)

    async def emit(self, event: str, *args: object, **kwargs: object) -> None:
        """Emit an event to all listeners."""
        listeners = self._listeners.get(event, [])

        for listener in listeners:
            # Check if the listener is a coroutine function before awaiting
            if inspect.iscoroutinefunction(listener):
                await listener(*args, **kwargs)
            else:
                listener(*args, **kwargs)


emitter: EventEmitter = EventEmitter()
