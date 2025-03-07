from collections import defaultdict
from enum import Enum
from typing import Callable, List

class Event(Enum):
    DEFAULT_DISCOUNT = "add_default_discounts"

class EventEmitter:
    def __init__(self) -> None:
        self.events: defaultdict[str, List[Callable[..., None]]] = defaultdict(list)

    def on(self, event: Event, callback: Callable[..., None]) -> None:
        self.events[event.value].append(callback)

    def emit(self, event: Event, *args: object, **kwargs: object) -> None:
        for callback in self.events[event.value]:
            callback(*args, **kwargs)

emitter: EventEmitter = EventEmitter()
