from aiogram import Dispatcher, types
from psycopg2.errors import UniqueViolation

from ..exceptions import CantGetCurrentAndNextEvents
from ..handlers.grades import start_grade, gen_ask_schedule_markup
from ..models.db import CurrentAndNextEvents
from ..services.repository import Repo


async def user_start(m: types.Message, repo: Repo):
    chat_id = m.from_user.id
    first_name = m.from_user.first_name
    last_name = m.from_user.last_name
    user_name = m.from_user.username

    await m.answer(f'Привет, {first_name}')

    try:
        await repo.add_user(chat_id, first_name, last_name, user_name)

        await start_grade(m, repo)

    except UniqueViolation:
        await repo.update_user(chat_id, first_name, last_name, user_name)

        markup = gen_ask_schedule_markup()
        await m.answer(
            'Спроси меня: "Сколько минут до звонка?"', reply_markup=markup)


def convert_seconds(seconds: int) -> str:
    hours = seconds // 3600
    minutes = (seconds - hours * 3600) // 60
    return (
        f'{str(hours) + " ч." if hours else ""}'
        f'{str(minutes) + " мин." if minutes else ""}')


async def user_get_schedule(m: types.Message, repo: Repo) -> None:
    try:
        current_and_next_events = await repo.get_current_and_next_events()
        text = format_current_and_next_events(current_and_next_events)
    except CantGetCurrentAndNextEvents:
        text = 'Уроков нет, можно отдохнуть'

    await m.answer(text)


def format_current_and_next_events(events: CurrentAndNextEvents) -> str:
    text = f'Сейчас {events.current_event.name}'

    if events.current_event.clarification is not None:
        text += f' ({events.current_event.clarification})'

    if events.next_event is not None and events.delta is not None:
        text += f', {events.next_event.name}'
        if events.next_event.clarification is not None:
            text += f' ({events.next_event.clarification})'
        text += f' через {convert_seconds(events.delta.seconds)}'

    return text


def register_user(dp: Dispatcher):
    dp.register_message_handler(user_start, commands=['start'], state='*')
    dp.register_message_handler(
        user_get_schedule, text='Сколько минут до звонка?')
