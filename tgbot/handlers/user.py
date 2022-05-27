from aiogram import Dispatcher
from aiogram.types import Message

from psycopg2.errors import UniqueViolation

from tgbot.services.repository import Repo


async def user_start(m: Message, repo: Repo):
    await m.reply("Hello, user!")

    chat_id = m.from_user.id
    first_name = m.from_user.first_name
    last_name = m.from_user.last_name
    user_name = m.from_user.username
    
    try:
        await repo.add_user(chat_id, first_name, last_name, user_name)
    except UniqueViolation:
        await repo.update_user(chat_id, first_name, last_name, user_name)
        
def register_user(dp: Dispatcher):
    dp.register_message_handler(user_start, commands=["start"], state="*")
