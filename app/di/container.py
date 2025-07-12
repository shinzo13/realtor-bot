from dishka import make_async_container
from dishka.integrations.aiogram import setup_dishka
from .providers import DatabaseProvider

def setup_di(dp):
    container = make_async_container(DatabaseProvider())
    setup_dishka(container, dp)