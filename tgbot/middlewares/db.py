import logging

from aiogram import types
from aiogram.dispatcher.middlewares import LifetimeControllerMiddleware
from aiogram.dispatcher.handler import CancelHandler
from psycopg2.pool import PoolError

from ..services.repository import Repo


logger = logging.getLogger(__name__)


class DbMiddleware(LifetimeControllerMiddleware):
    skip_patterns = ["error", "update"]

    def __init__(self, pool):
        super().__init__()
        self.pool = pool

    async def pre_process(self, obj, data, *args):
        try:
            db = self.pool.getconn()
            data["db"] = db
            data["repo"] = Repo(db)
        except PoolError as e:
            logger.error(e)

            if isinstance(obj, types.Message):
                await obj.answer('Ошибка, попробуй снова')
            elif isinstance(obj, types.CallbackQuery):
                await obj.message.edit_text('Ошибка, попробуй снова')
                await obj.answer('Слишком много подключений к базе')

            raise CancelHandler()

    async def post_process(self, obj, data, *args):
        del data["repo"]
        db = data.get("db")
        if db:
            self.pool.putconn(db)
