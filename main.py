import asyncio
import logging

from data.db_session import global_init
from handlers.callbacks import callbacks
from handlers.commands import commands
from handlers.data_processing import data_processing
from handlers.inline import inline
from instances import bot, dp


async def main() -> None:
    dp.include_router(commands)
    dp.include_router(callbacks)
    dp.include_router(inline)
    dp.include_router(data_processing)
    await dp.start_polling(bot)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    global_init("data/db/main.db")
    asyncio.run(main())
