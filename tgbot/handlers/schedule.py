import datetime

from aiogram import Dispatcher, types

from ..exceptions import CantGetCurrentAndNextEvents
from ..models.db import CurrentAndNextEvents, Event
from ..services.repository import Repo


def convert_seconds(seconds: int) -> str:
    hours = seconds // 3600
    minutes = (seconds - hours * 3600) // 60
    seconds -= minutes * 60

    time = ''
    if hours:
        time += f'{hours} ч.'
        if minutes == 0:
            return time
        time += ' '
    if minutes:
        time += f'{minutes} мин.'
    else:
        time += f'{seconds} сек.'

    return time


def time_delta(t1: datetime.time, t2: datetime.time) -> datetime.timedelta:
    d1 = datetime.datetime.strptime(t1.isoformat(), '%H:%M:%S')
    d2 = datetime.datetime.strptime(t2.isoformat(), '%H:%M:%S')

    return d1 - d2


def format_current_and_next_events(events: CurrentAndNextEvents) -> str:
    current_time = datetime.datetime.today().time().replace(microsecond=0)

    if events.current_event:
        ce_delta = time_delta(events.current_event.end, current_time)
        ce_delta = convert_seconds(ce_delta.seconds)

        text = f'Сейчас _{events.current_event.name}_'
        if events.current_event.clarification:
            text += f' ({events.current_event.clarification})'

        if events.next_event:
            # does events follow one another
            if events.current_event.end == events.next_event.start:
                text += f', {events.next_event.name}'
                if events.next_event.clarification:
                    text += f' ({events.next_event.clarification})'

                text += f' через {ce_delta}'

                return text
            else:
                text += f' конец через {ce_delta}'
        else:
            text += f' конец через {ce_delta}'
            return text
    else:
        text = 'Уроков нет, можно отдохнуть'

    ne_delta = time_delta(events.next_event.start, current_time)
    ne_delta = convert_seconds(ne_delta.seconds)

    text += f'\nДалее по расписанию идет _{events.next_event.name}_'
    if events.next_event.clarification:
        text += f' ({events.next_event.clarification}),'

    text += f'\nначало в {events.next_event.start.isoformat(timespec="minutes")}' \
            f' (через {ne_delta})'

    return text


async def user_get_schedule(m: types.Message, repo: Repo) -> None:
    try:
        current_and_next_events = await repo.get_current_and_next_events(m.chat.id)
        text = format_current_and_next_events(current_and_next_events)
    except CantGetCurrentAndNextEvents:
        text = 'Уроков нет, можно отдохнуть'

    await m.answer(text, parse_mode='Markdown')


def register_schedule(dp: Dispatcher):
    dp.register_message_handler(user_get_schedule, text='Сколько минут до звонка?', state='*')
