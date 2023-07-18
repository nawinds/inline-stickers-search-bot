import asyncio
import logging

from aiogram_i18n import I18nMiddleware
from aiogram_i18n.cores.babel_core import BabelCore

from data.db_session import global_init
from handlers.callbacks import callbacks
from handlers.commands import commands
from handlers.data_processing import data_processing
from handlers.inline import inline
from instances import bot, dp, CustomFSMManager


async def main() -> None:
    i18n = I18nMiddleware(
        core=BabelCore(path="locales/{locale}/LC_MESSAGES"),
        manager=CustomFSMManager(default_locale="en", key="locale")
    )

    dp.include_router(commands)
    dp.include_router(callbacks)
    dp.include_router(inline)
    dp.include_router(data_processing)

    i18n.setup(dispatcher=dp)
    await dp.start_polling(bot)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    global_init("data/db/main.db")
    asyncio.run(main())
