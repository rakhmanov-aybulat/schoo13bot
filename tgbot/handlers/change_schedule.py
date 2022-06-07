import os

from aiogram import Bot, Dispatcher, types

from ..models.role import UserRole
from ..services.repository import Repo
from ..services.excel import create_events_clarification_excel_template, parse_events_clarification_excel


async def send_events_clarification_excel_template(m: types.Message, repo: Repo):
    grade_list = await repo.get_grade_list()
    event_list = await repo.get_event_list()
    clarification_list = await repo.get_clarification_list()
    file_name = 'events.xlsx'
    create_events_clarification_excel_template(file_name, grade_list, event_list, clarification_list)

    file = types.InputFile(file_name, 'Расписание Шаблон.xlsx')
    await m.answer_document(file)


async def start_changing_schedule(m: types.Message):
    await m.answer('Отправь excel файл нового расписания.\n'
                   '/schedule_template - чтобы посмотреть шаблон')


async def change_events_clarification(m: types.Message, repo: Repo):
    file_name = 'clarification.xlsx'

    bot = Bot.get_current()
    await bot.download_file_by_id(m.document.file_id, file_name)

    clarification_list = parse_events_clarification_excel(file_name)

    await repo.truncate_table('events_clarification')
    try:
        await repo.add_events_clarification(clarification_list)
    except Exception:
        await m.answer('Что-то пошло не так ')
    else:
        await m.answer('Уточнения событий изменены')

    if os.path.exists(file_name):
        os.remove(file_name)


def register_change_schedule(dp: Dispatcher):
    dp.register_message_handler(send_events_clarification_excel_template, commands=['schedule_template'], state='*', role=UserRole.ADMIN)
    dp.register_message_handler(
        change_events_clarification, content_types=types.message.ContentType.DOCUMENT, state='*', role=UserRole.ADMIN)
