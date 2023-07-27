import asyncio
import logging

from aiogram_i18n import I18nMiddleware
from aiogram_i18n.cores.babel_core import BabelCore

from db_models.db_session import global_init, dictionary_init, create_session
from handlers.callbacks import callbacks
from handlers.commands import commands
from handlers.data_processing import data_processing
from handlers.inline import inline
from modules.instances import bot, dp, CustomFSMManager, PRODUCTION
from db_models.sticker_sets import StickerSet


async def update_info_broadcast() -> None:
    session = create_session()
    users = list(set([i[0] for i in session.query(StickerSet.owner_id).all()]))
    with open("update_info.html", encoding="utf-8") as f:
        data = f.read().strip()
    if data:
        for user in users:
            await bot.send_message(user, data, parse_mode="html",
                                   disable_web_page_preview=True)
    if PRODUCTION:
        with open("update_info.html", "w", encoding="utf-8") as wf:
            wf.write("")


async def main() -> None:
    await update_info_broadcast()
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
    dictionary_init("data", "dictionary.txt")
    global_init("data/main.db")
    asyncio.run(main())
