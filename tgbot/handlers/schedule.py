import datetime

from aiogram import Dispatcher, types

from ..exceptions import CantGetCurrentAndNextEvents
from ..models.db import CurrentAndNextEvents
from ..services.repository import Repo


def convert_seconds(seconds: int) -> str:
    hours = seconds // 3600
    minutes = (seconds - hours * 3600) // 60
    return (
        f'{str(hours) + " ч." if hours else ""}'
        f'{str(minutes) + " мин." if minutes else ""}')


def time_delta(t1: datetime.time, t2: datetime.time) -> datetime.timedelta:
    d1 = datetime.datetime.strptime(t1.isoformat(), '%H:%M:%S')
    d2 = datetime.datetime.strptime(t2.isoformat(), '%H:%M:%S')
    return d1 - d2


def format_current_and_next_events(events: CurrentAndNextEvents) -> str:
    text = f'Сейчас _{events.current_event.name}_'

    if events.current_event.clarification is not None:
        text += f' ({events.current_event.clarification})'

    if (events.next_event is not None
            and events.current_event.end == events.next_event.start):
        text += f', {events.next_event.name}'

        if events.next_event.clarification is not None:
            text += f' ({events.next_event.clarification})'
    else:
        text += ', конец'

    current_time = datetime.datetime.today().time().replace(microsecond=0)
    delta = time_delta(events.current_event.end, current_time)
    text += f' через {convert_seconds(delta.seconds)}'

    if (events.next_event is not None
            and events.current_event.end != events.next_event.start):
        text += f'\nДалее по расписанию идет _{events.next_event.name}_' \
                f', начало в {events.next_event.start.isoformat(timespec="minutes")} '

    return text


async def user_get_schedule(m: types.Message, repo: Repo) -> None:
    try:
        current_and_next_events = await repo.get_current_and_next_events(m.chat.id)
        text = format_current_and_next_events(current_and_next_events)
    except CantGetCurrentAndNextEvents:
        text = 'Уроков нет, можно отдохнуть'

    await m.answer(text, parse_mode='Markdown')


def register_schedule(dp: Dispatcher):
    dp.register_message_handler(user_get_schedule, text='Сколько минут до звонка?')
