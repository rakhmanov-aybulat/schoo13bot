from os import environ
from dataclasses import dataclass


@dataclass
class DbConfig:
    host: str
    database: str
    user: str
    port: str
    password: str


@dataclass
class TgBot:
    token: str
    admin_id: int


@dataclass
class Config:
    tg_bot: TgBot
    db: DbConfig


def cast_bool(value: str) -> bool:
    if not value:
        return False
    return value.lower() in ("true", "t", "1", "yes")


def load_config():
    return Config(
        tg_bot=TgBot(
            token=environ['TGBOT_TOKEN'],
            admin_id=int(environ['TGBOT_ADMIN_ID']),
        ),
        db=DbConfig(
            host=environ['DB_HOST'],
            database=environ['DB_DATABASE'],
            user=environ['DB_USER'],
            port=environ['DB_PORT'],
            password=environ['DB_PASSWORD']
        )
    )
