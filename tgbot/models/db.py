from typing import Union

from dataclasses import dataclass
from datetime import time, timedelta


@dataclass
class Grade:
    grade_number: int
    grade_letter: str


@dataclass
class User:
    chat_id: int
    first_name: str
    last_name: Union[str, None]
    username: Union[str, None]
    grade: Union[Grade, None]


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
    delta: timedelta
