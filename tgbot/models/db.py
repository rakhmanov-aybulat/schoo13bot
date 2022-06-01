from dataclasses import dataclass
from typing import Union

from datetime import time


@dataclass
class Event:
    id: int
    name: str
    clarification: Union[str, None]
    weekday: int
    start: time
    end: time
    next_event_id: Union[int, None]


@dataclass()
class CurrentAndNextEvents:
    current_event: Event
    next_event: Union[Event, None]
