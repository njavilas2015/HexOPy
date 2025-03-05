from collections import defaultdict
from enum import Enum

class Event(Enum):
    DEFAULT_DISCOUNT = "add_default_discounts"

class EventEmitter:
    def __init__(self):
        self.events = defaultdict(list)

    def on(self, event, callback):
        self.events[event].append(callback)

    def emit(self, event, *args, **kwargs):
        for callback in self.events[event]:
            callback(*args, **kwargs)

emitter: EventEmitter = EventEmitter()