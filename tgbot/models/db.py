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


@dataclass()
class CurrentAndNextEvents:
    current_event: Event
    next_event: Union[Event, None]


@dataclass()
class EventClarification:
    event_id: int
    grade: str
    clarification: str