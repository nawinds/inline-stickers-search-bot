from os import getenv
from typing import Any, Dict, Optional

from aiogram import Bot, Dispatcher
from aiogram.filters.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import TelegramObject
from aiogram.utils.markdown import markdown_decoration, _join
from aiogram_i18n.managers.fsm import FSMManager

storage = MemoryStorage()
dp = Dispatcher(storage=storage)
bot = Bot(token=getenv("TOKEN"))


class NewSetState(StatesGroup):
    title = State()
    sticker = State()
    prompt = State()


class CustomFSMManager(FSMManager):
    async def get_locale(self, event: TelegramObject, data: Dict[str, Any]) -> str:
        state: Optional[FSMContext] = data.get("state")
        locale: Optional[str] = None
        if state:
            fsm_data = await state.get_data()
            locale = fsm_data.get(self.key, None)
        if locale is None:
            locale = "ru" if data["event_from_user"].language_code == "ru" else "en"
            if state:
                await state.update_data(data={self.key: locale})
        return locale


def escape_md(*content, sep: str = " ") -> str:
    return markdown_decoration.quote(_join(*content, sep=sep)).replace("\\.", ".")
