from os import getenv

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters.state import State, StatesGroup


storage = MemoryStorage()
dp = Dispatcher(storage=storage)
bot = Bot(token=getenv("TOKEN"))


class NewSetState(StatesGroup):
    title = State()
    sticker = State()
    prompt = State()
